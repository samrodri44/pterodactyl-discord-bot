import os

import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL_PANEL")
SERVER_ID = os.getenv("SERVER")
API_KEY = os.getenv("API_KEY")
jwt_token = None
socket_url = None


def GetJWT():
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


GetJWT()
