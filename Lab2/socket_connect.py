import websockets
import json


async def receiver(url: str):
    async with websockets.connect(url) as websocket:
        while True:
            try:
                data = await websocket.recv()
                print(f"Received message: {data}")
            except websockets.exceptions.ConnectionClosedError:
                print("Connection closed")
                break


async def sender(url: str):
    async with websockets.connect(url) as websocket:
        while True:
            try:
                message = input("Enter message: ")
                await websocket.send(json.dumps({"command": "send", "message": message}))
            except websockets.exceptions.ConnectionClosedError:
                print("Connection closed")
                break


async def main():
    url = "ws://localhost:8001/chat/ws"
    mode = input("Enter mode: ")
    if mode == "send":
        await sender(url)
    else:
        await receiver(url)


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")


