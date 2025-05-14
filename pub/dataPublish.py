# gets data from the serial port and publishes it to an ably channel
# gemini helped a lot, thanks gemini!!

import os
from time import sleep

from ably import AblyRealtime
import serial
from dotenv import load_dotenv
import asyncio

load_dotenv()
apiKey = os.getenv("apiKey")

print("Connecting to Ably...")
async def main():
    thing = True
    try:
        # Use AblyRest for publishing from a backend script
        ably = AblyRealtime(apiKey)
        channel = ably.channels.get('the_park')
        print("Successfully connected to Ably channel: the_park")
    except Exception as e:
        print(f"Error connecting to Ably: {e}")
        exit()
    while thing == True:
        try:
            ser = serial.Serial('COM3', 9600, timeout=1)
            print("Starting to listen for Arduino data...")
            thing = False
        except Exception as e:
            print(f"Something went wrong with the serial port: {e}")
            sleep(6)
    while True:
        try:
            # Check if there's data waiting on the serial port
            if ser.in_waiting > 0:
                # Read a line from the serial port (up to the newline character)
                # Decode from bytes to string and remove leading/trailing whitespace
                line = await asyncio.to_thread(ser.readline)
                line = line.decode('utf-8').strip()

                if line:  # Only process if the line is not empty
                    print(f"Received from Arduino: {line}")
                    gandalf = []
                    for i in tuple(line):
                        if i == '1':
                            gandalf.append("Closed")
                        else:
                            gandalf.append("Open")
                    status = dict(zip(("Lot 1", "Lot 2", "Lot 3"), gandalf))
                    print(status)
                    # Publish the data to Ably
                    print(f"Publishing status update to Ably")
                    try:
                        await channel.publish("Status update.", status)
                    except Exception as e:
                        print(f"An error occured: {e}")
        except ValueError:
            print(f"Warning: Received data in unexpected format")
        except serial.SerialException:
            print(f"Something went wrong with the serial port, trying to reconnect in 15 seconds")
            ser = None
            await asyncio.sleep(15)
            ser = await asyncio.to_thread(serial.Serial,'COM3', 9600, timeout=1)
        except Exception as e:
            print(f"An error occurred during data parsing or validation: {e}")
        except KeyboardInterrupt:
            print("Keyboard interrupt received.")
            if ser and ser.is_open:
                try:
                    ser.close()
                    print("Serial port closed.")
                except Exception as e_close:
                    print(f"Error closing serial port during cleanup: {e_close}")
            if ably:
                try:
                    print("Closing Ably client...")
                    await ably.close()  # Use await for async close
                    print("Ably client closed.")
                except Exception as e_ably_close:
                    print(f"Error closing Ably client: {e_ably_close}")
            print("Cleanup finished.")

asyncio.run(main())