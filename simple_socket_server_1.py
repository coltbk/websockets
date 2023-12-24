#!/usr/bin/env python

import asyncio
import websockets
import json
from time import sleep


async def handler(websocket):
    # req = await websocket.recv()
    # for i in range(10):
    #     await websocket.send(str(i))
    #     await asyncio.sleep(0.5)
    async for message in websocket:
        event = json.loads(message)
        print(event)
    
async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())