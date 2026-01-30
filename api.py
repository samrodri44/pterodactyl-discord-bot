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


def get_jwt():
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
    print(f"JWT Token: {jwt_token}")

    return socket_url, jwt_token


async def connect_websocket():
    socket_url, token = get_jwt()

    additional_headers = {
        "Authorization": f"Bearer {token}",
        "Origin": f"{BASE_URL}",
    }

    async with websockets.connect(
        socket_url, additional_headers=additional_headers
    ) as websocket:
        print("Websocket Connection Established.")

        # Authenticate
        auth_message = {
            "event": "auth",
            "args": [token],
        }
        await websocket.send(json.dumps(auth_message))

        # Listen for messages
        async for message in websocket:
            data = json.loads(message)
            print("Received:", data)


asyncio.run(connect_websocket())

connect_websocket()
