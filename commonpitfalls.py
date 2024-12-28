import sys
import os
import re
import asyncio
from path import Path
from typing import *
import datetime
import inspect
import httpx
import time

for v in ['PYTHONASYNCIODEBUG', 'PYTHONTRACEMALLOC']:
    print(f"{v}={os.getenv(v)=}")

def indent(count: int) -> str:
    return " " * (6-count*3)

async def example(count: int) -> str:
    await asyncio.sleep(0)
    if count == 0:
        return "result"
    for i in range(count):
        await asyncio.sleep(i)
    return await example(count-1)

print(f"{len(sys.argv)=}")
r = asyncio.run(example(0))
print(r)
