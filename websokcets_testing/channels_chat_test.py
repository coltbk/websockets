#!/usr/bin/env python

import asyncio
import websockets
import json

async def hello():
    uri = "ws://localhost:8000/ws/chat/TestRoom/"
    # uri = "https://localhost:8000/chat/TestRoom"
    async with websockets.connect(uri) as websocket:
        message = json.dumps('shia hulud')

        await websocket.send(message)
        print(f">>> {message}")

        greeting = await websocket.recv()
        print(f"<<< {greeting}")

if __name__ == "__main__":
    asyncio.run(hello())