import sys
import os
import re
import asyncio
from path import Path
from typing import *
import datetime
import inspect
import random

async def worker(name: str, q: asyncio.Queue) -> None:
    print(f"{name} Starting")
    for i in range(500000):
        f = random.random()
        l = [f, f+1, f+2]
        await q.put({name:l})
    print(f"{name} Complete")

async def listener(q: asyncio.Queue) -> None:
    print(f"Listener starting")
    d = dict()
    count = 0
    finished_tasks = 0
    while not q.empty():
        try:
            item = await q.get()
            if type(item) == bool:
                finished_tasks += 1
                if finished_tasks == 3:
                    break
            else:
                d.update(item)
                count += 1
        except asyncio.CancelledError as e:
            print('Caught {e}')

    print(f"{count} updates")
    print(d)
    print(f"Listener complete")

async def async_main():  
    q = asyncio.Queue()
    worker_tasks = [asyncio.create_task(worker(f'Worker#{i}', q)) for i in range(3)]
    listener_task = asyncio.create_task(listener(q))
    asyncio.gather(*worker_tasks, listener_task)

asyncio.run(async_main())