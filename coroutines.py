import sys
import os
import re
import asyncio
from path import Path
from typing import *
import datetime
import inspect

def print_now():
    print(datetime.datetime.now())
    
async def keep_printing(name: str = "") -> None:
    while True:
        print(name, end=" ")
        print_now()
        await asyncio.sleep(0.50)
        
async def async_main1() -> None:
    try:
        myfunc = keep_printing("Hey") # get address of function, does not invoke
        mywaiter = asyncio.wait_for(myfunc, 2) # address of "wait" function
        await mywaiter # schedules and invokes mywaiter
        # waiter # Sample Error
    except asyncio.TimeoutError:
        print("oops, time's up")
        
# asyncio.run(keep_printing())
# asyncio.run(asyncio.wait_for(keep_printing(), 10))        
        
asyncio.run(async_main1())        
        
async def print3times() -> None:
    for _ in range(3):
        print_now()
        await asyncio.sleep(0.1)
        
        
coro1 = print3times()
coro2 = print3times()
print(type(print3times))
print(type(coro1))
print(type(coro2))

# asyncio.run(print3times) # fails because print3times is a function, where print3times() is a coroutines

async def async_function() -> None:
    await keep_printing()
        
coroutine = async_function()
print(type(async_function))
print(type(coroutine))
print(inspect.isawaitable(async_function))
print(inspect.isawaitable(coroutine))

async def async_main2() -> None:
    await keep_printing("First")
    await keep_printing("Second")
    await keep_printing("Third")
    
# asyncio.run(async_main2())    

async def asyncio_main3() -> None:
    try:
        await asyncio.wait_for(asyncio.gather(keep_printing("First"),
            keep_printing("Second"),
            keep_printing("Third")),5)
    except asyncio.TimeoutError:
        print("done with 5 seconds of 3 coroutines")
    
# asyncio.run(asyncio_main3())    

async def keep_printing2(name: str = "") -> None:
    while True:
        print(name, end=" ")
        print_now()
        try:
            await asyncio.sleep(0.50)
        except asyncio.CancelledError:
            print(f"{name} was cancelled")
            break

async def asyncio_main4() -> None:
    try:
        await asyncio.wait_for(asyncio.gather(keep_printing2("First"),
            keep_printing2("Second"),
            keep_printing2("Third")),5)
    except asyncio.TimeoutError:
        print("done with 5 seconds of 3 coroutines")
    
asyncio.run(asyncio_main4())    

