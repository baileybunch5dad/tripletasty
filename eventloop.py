import sys
import os
import re
import asyncio
from path import Path
from typing import *
import datetime

# from Tutorial
# import asyncio: Learn Python's AsyncIO #2

loop = asyncio.get_event_loop() # asyncio.get_event_loop()
                                # loop = _

loop.run_until_complete(asyncio.sleep(5))
# loop.run_forever()

def print_now():
    print(datetime.datetime.now())
    
loop.call_soon(print_now)
loop.call_soon(print_now)
loop.run_until_complete(asyncio.sleep(5))

def trampoline(name: str = "") -> None:
    print(name, end=" ")
    print_now()
    print_now()
    loop.call_later(0.5, trampoline, name)

loop.call_soon(trampoline)
loop.call_later(8, loop.stop)
loop.run_forever()

loop.call_soon(trampoline, "First")
loop.call_soon(trampoline, "Second")
loop.call_soon(trampoline, "Third")
loop.call_later(8, loop.stop)
loop.run_forever()

def hog():
    print("hog")
    sum = 0
    for i in range(100_000):
        for j in range(10_000):
            sum += j
    return sum

loop.call_later(15, hog)
loop.call_later(20, loop.stop)
loop.run_forever()

loop.set_debug(True)
loop.call_later(15, hog)
loop.call_later(20, loop.stop)
loop.run_forever()

