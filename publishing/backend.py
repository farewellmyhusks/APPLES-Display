import time
import os
from ably import AblyRest
import serial
from dotenv import load_dotenv

load_dotenv()
apiKey = os.getenv("apiKey")

print("Connecting to Ably...")
try:
    # Use AblyRest for publishing from a backend script
    ably = AblyRest(apiKey)
    channel = ably.channels.get("the_park")
    print("Successfully connected to Ably channel: the_park")
except Exception as e:
    print(f"Error connecting to Ably: {e}")
    exit()

ser = serial.Serial('COM3', 9600)
print("Starting to listen for Arduino data...")
while True:
    try:
        # Check if there's data waiting on the serial port
        if ser.in_waiting > 0:
            # Read a line from the serial port (up to the newline character)
            # Decode from bytes to string and remove leading/trailing whitespace
            line = ser.readline().decode('utf-8').strip()

            if line:  # Only process if the line is not empty
                print(f"Received from Arduino: {line}")
                gandalf = []
                for i in tuple(line):
                    if i == '1':
                        gandalf.append("Open")
                    else:
                        gandalf.append("Closed")
                status = dict(zip(("Lot 1", "Lot 2", "Lot 3"), gandalf))
                # Publish the data to Ably
                print(f"Publishing status update to Ably")
                channel.publish("Status update", status)
    except ValueError:
        print(f"Warning: Received data in unexpected format")
    except serial.SerialException:
        print(f"Something went wrong with the serial port, trying to reconnect in 15 seconds")
        ser = None
        time.sleep(15)
        ser = serial.Serial('COM3', 9600)
    except Exception as e:
        print(f"An error occurred during data parsing or validation: {e}")
