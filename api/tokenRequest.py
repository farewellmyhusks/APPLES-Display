## api/tokenRequest.py
# (Handles TokenRequest serialization)

import flask # Use flask directly as imported by user
import os
from dotenv import load_dotenv
from ably import AblyRest
import asyncio # Keep asyncio import as the route is async
import logging # Import logging

# --- Logging Configuration ---
# Set up basic logging to see messages from the Ably library and our script
logging.basicConfig(level=logging.INFO, # Changed level to INFO for less noise now
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__) # Get a logger for this module

# --- Load Environment Variables ---
# dotenv for local hosting and testing
load_dotenv() # Assumes .env is in the same directory or parent
apiKey = os.getenv("apiKey")

# --- Ably Initialization ---
ably_client = None
initialization_error = None
if not apiKey:
    initialization_error = "Error: Ably API key ('apiKey') not found in environment variables."
    log.error(initialization_error) # Use logger
else:
    try:
        # Use AblyRest for backend operations like token generation
        ably_client = AblyRest(apiKey)
        log.info("Ably REST client initialized successfully.") # Use logger
    except Exception as e:
        initialization_error = f"Error initializing Ably client: {e}"
        log.exception(initialization_error) # Use logger, log exception details
        ably_client = None # Ensure it's None if init fails

# --- Flask App Initialization ---
# The 'app' variable is what Vercel/Hypercorn looks for by default
app = flask.Flask(__name__)

# --- API Route ---
# Defines the endpoint that the frontend will call
@app.route('/api/tokenRequest', methods=['GET'])
async def token_request(): # Route handler is async
    """
    Handles GET requests from the frontend Ably library to get an Ably TokenRequest.
    """
    log.info("Received request at /api/tokenRequest") # Log entry

    # Check if Ably client failed to initialize
    if initialization_error:
         log.error(f"Ably client initialization error: {initialization_error}")
         # Use flask.jsonify
         return flask.jsonify({"error": "Server configuration error", "details": initialization_error}), 500
    if not ably_client:
        log.error("Error: Ably client is not available.")
        return flask.jsonify({"error": "Server configuration error", "details": "Ably client not initialized."}), 500

    try:
        # Define token parameters as a dictionary
        # Using parameters from user's script:
        token_params = {
            "clientId": "client@example.com", # User's specified clientId
            "capability": {
                "the_park": ["publish", "subscribe"] # User's specified capabilities
            },
            'ttl': 60 * 20 # User's specified TTL (20 minutes)
        }

        # Generate a token request - MUST use await for the async function
        log.info(f"Requesting token with params: {token_params}")
        token_data = await ably_client.auth.create_token_request(token_params=token_params) # Added await

        # token_data is a TokenRequest object, but jsonify should handle it
        log.info(f"Token request generated successfully for clientId: {token_params['clientId']}")
        log.debug(f"TokenRequest object: {token_data}") # Keep debug log if needed

        # *** FIX: Return the TokenRequest object directly using jsonify ***
        # Flask's jsonify is generally able to serialize dict-like objects.
        return flask.jsonify(token_data)

    except Exception as e:
        # Log the full exception traceback
        log.exception(f"Error generating token request or creating response: {e}")
        # Return a JSON error response
        return flask.jsonify({"error": "Failed to generate token request", "details": str(e)}), 500

# --- Local Testing Setup ---
if __name__ == '__main__':
    print("Flask app defined. To run locally for testing async route:")
    print("1. Ensure 'hypercorn' is installed (`pip install hypercorn`).")
    print("2. Run: `hypercorn api.tokenRequest:app --reload` (assuming file is api/tokenRequest.py)")
    if not apiKey:
         print("\nWARNING: 'apiKey' environment variable not set.")
         print("Token requests will likely fail.\n")
