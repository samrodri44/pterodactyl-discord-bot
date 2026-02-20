import asyncio
import json
import os
from datetime import datetime

import requests
import websockets
from dotenv import load_dotenv

from snapshot import Snapshot

load_dotenv()
BASE_URL = os.getenv("BASE_URL_PANEL")
SERVER_ID = os.getenv("SERVER")
API_KEY = os.getenv("API_KEY")


class PterodactylWS:
    def __init__(self):
        self.ws = None
        self.queue = asyncio.Queue()
        # self.task = None
        self.snapshot = Snapshot()

    # Run the daemon
    async def run(self):
        while True:
            try:
                await self.connect()

                consumer = asyncio.create_task(self.consume())
                producer = asyncio.create_task(self.produce())

                done, pending = await asyncio.wait(
                    [consumer, producer],
                    return_when=asyncio.FIRST_EXCEPTION,
                )

                for task in pending:
                    task.cancel()

            except Exception as e:
                print("WS Error: ", e)
                self.snapshot.ws_connected = False
                await asyncio.sleep(5)

    # Get JWT token and WSS url from the panel
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
        if jwt_token:
            print("JWT Token received")
        else:
            print("There's been an error, the jwt token was not retrieved")

        return socket_url, jwt_token

    # Connect to the websocket
    async def connect(self):
        socket_url, token = self.get_jwt()

        additional_headers = {
            "Authorization": f"Bearer {token}",
            "Origin": f"{BASE_URL}",
        }

        self.ws = await websockets.connect(
            socket_url, additional_headers=additional_headers
        )

        await self.authenticate(token)

        self.snapshot.ws_connected = True
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
            event = data["event"]

            # Handle jwt related messages
            if (
                event == "token expiring"
                or event == "jwt error"
                or event == "token expired"
            ):  # If token expires, refresh
                print()
                print("YO LOOK OVER HERE")
                print()
                _, token = await self.get_jwt()
                await self.authenticate(token)

            # Handle each type of mesage
            try:
                if event == "stats":
                    args = json.loads(data["args"][0])
                    self.snapshot.status = args["state"]
                    self.snapshot.uptime = args["uptime"]
                    print(
                        "Stats: ",
                        f"CPU: {round(args['cpu_absolute'], 2)}% ",
                        f"Disk: {round(args['disk_bytes'] / 1000000, 2)}Mib ",
                        f"RAM: {round(args['memory_bytes'] / 1000000, 2)}Mib ",
                        # f"RAM_Limit: {
                        #    round(args['memory_limit_bytes'] / 1000000, 2)
                        # }MiB ",
                        f"Receive: {round(args['network']['rx_bytes'] / 1000, 2)}KiB ",
                        f"Transmit: {round(args['network']['tx_bytes'] / 1000, 2)}KiB ",
                        f"State: {args['state']} ",
                        f"Uptime: {round(args['uptime'] / 1000)}s",
                    )
                elif event == "console output":
                    args = data["args"][0]

                    # TODO:Handle output
                    # Player connected:
                    # Player disconnected:
                    # There are xx/xx players online:
                    if len(args) >= 30:
                        if args[25:30] == "INFO]":
                            if "Player Spawned:" in args:
                                print("Player connected")
                                await self.list_players()
                            elif "Player disconnected:" in args:
                                print("Player disconnected:")
                                await self.list_players()
                            elif "There are " in args and "players online:" in args:
                                content, _ = args[41:46].split(" ")
                                players, max_players = content.split("/")
                                self.snapshot.player_count = int(players)
                                print(
                                    f"{self.snapshot.player_count} players online. Max {
                                        int(max_players)
                                    }."
                                )
                            else:
                                print()

                    print(args)
                elif event == "status":
                    args = data["args"][0]
                    self.snapshot.status = args
                    if args == "offline":
                        self.snapshot.player_count = 0
                        self.snapshot.uptime = 0
                    elif args == "running":
                        await self.list_players()
                    print("Server is now", args)
                else:
                    args = data["args"][0]
                    print(f"Received: Event: {event} Args: {args}")

                self.snapshot.last_update = datetime.now()
            except Exception as e:
                if (
                    event == "token expiring"
                    or event == "jwt error"
                    or event == "token expired"
                    or event == "auth success"
                ):
                    print("Received: Event: ", event)
                else:
                    print(f"Received: Event: {event} Args: No {e}")
                self.snapshot.last_update = datetime.now()

    # Send messages
    async def produce(self):
        while True:
            message = await self.queue.get()
            print(f"Sending message with event: {message['event']}.")
            await self.ws.send(json.dumps(message))

    # Start the server
    async def start(self):
        start = {
            "event": "set state",
            "args": ["start"],
        }
        await self.queue.put(start)
        print("Sending start command...")

    # Stop the server
    async def stop(self):
        if self.snapshot.player_count != 0:
            return False

        stop = {
            "event": "set state",
            "args": ["stop"],
        }
        await self.queue.put(stop)

        return True

    async def list_players(self):
        command = {
            "event": "send command",
            "args": ["list"],
        }
        print("Queueing list command")
        await self.queue.put(command)


# For testing
if __name__ == "__main__":
    pterows_instance = PterodactylWS()
    asyncio.run(pterows_instance.run())
