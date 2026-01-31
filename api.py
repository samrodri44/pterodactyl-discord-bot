import asyncio
import json
import os

import requests
import websockets
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL_PANEL")
SERVER_ID = os.getenv("SERVER")
API_KEY = os.getenv("API_KEY")


class PterodactylWS:
    def __init__(self):
        self.ws_url = None
        self.origin = None
        self.ws = None
        self.queue = asyncio.Queue()
        self.task = None

    def get_jwt(self):
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "Application/vnd.pterodactyl.v1+json",
        }

        response = requests.get(
            f"{BASE_URL}/api/client/servers/{SERVER_ID}/websocket", headers=headers
        )

        print(response)
        data = response.json()["data"]
        socket_url = data["socket"]
        jwt_token = data["token"]

        print(f"Websocket URL: {socket_url}")
        print(f"JWT Token: {jwt_token[:10]}")

        return socket_url, jwt_token

    async def connect(self):
        socket_url, token = self.get_jwt()

        additional_headers = {
            "Authorization": f"Bearer {token}",
            "Origin": f"{BASE_URL}",
        }

        self.ws = await websockets.connect(
            socket_url, additional_headers=additional_headers
        )
        print("Websocket Connection Established.")

    # Authenticate
    async def authenticate(self, token):
        auth_message = {
            "event": "auth",
            "args": [token],
        }
        await self.ws.send(json.dumps(auth_message))

    # Listen for messages
    async def consume(self):
        async for message in self.ws:
            data = json.loads(message)
            # TODO:Handle Output
            print("Received:", data)


# May not be necessary
# if __name__ == "__main__":
#    pterows_instance = PterodactylWS()
