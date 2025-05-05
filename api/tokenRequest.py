# gets temporary constantly refreshing tokens from ably using flask
# gemini also helped me, thanks again!
# supermaven too but shes a little too annoying tbh might just ditch her and go with gemini only

import flask
import os
import asyncio
from dotenv import load_dotenv
from ably import AblyRest
import json

# dotenv for local hosting and testing
load_dotenv()
apiKey = os.getenv("apiKey")

ably_client = None
initialization_error = None
if not apiKey:
    initialization_error = "Error: Ably api key ('apiKey') not found in environment variables."
    print(initialization_error)
else:
    try:
        # Use AblyRest for backend operations like token generation
        ably_client = AblyRest(apiKey)
        print("Ably REST client initialized")
    except Exception as e:
        initialization_error = f"Error initializing Ably client: {e}"
        print(initialization_error)
        ably_client = None # Ensure it's None if init fails

app = flask.Flask(__name__)
@app.route('/api/tokenRequest', methods=['GET'])
async def token_request():
    if ably_client:
        try:
            # Generate a token for the channel
            token_params = {
                "clientId": "client@example.com",  # User's specified clientId
                "capability": {
                    "the_park": ["publish", "subscribe"]  # User's specified capabilities
                },
                'ttl': 60 * 20  # User's specified TTL (20 minutes)
            }
            token = await ably_client.auth.create_token_request(token_params)
            print(f"Token request generated successfully for clientId: {token_params['clientId']}")
            print(f"Token generated: {token}")
            # troubleshooted this with gemini and she gave me the code so thank u
            token_dict = {
                "keyName": token['keyName'],
                "expires": token['expires'],
                "issued": token['issued'],
                "capability": json.dumps(token['capability']), # Capability needs to be a JSON string
                "clientId": token['clientId'],
                "nonce": token['nonce'],
                "timestamp": token['timestamp'],
                "mac": token['mac']
            }
            return token_dict
        except Exception as e:
            print(f"Error generating token: {e}")
            return "Error generating token", 500