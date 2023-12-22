#!/usr/bin/env python

import asyncio
import websockets
from time import sleep


async def producer_1(websocket):
    # req = await websocket.recv()
    for i in range(10):
        await websocket.send(str(i))
        await asyncio.sleep(0.5)
    
async def main():
    async with websockets.serve(producer_1, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())