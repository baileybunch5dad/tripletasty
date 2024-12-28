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

# https://www.youtube.com/watch?v=1LTHbmed3D4

# fut = asyncio.Future()
# fut.done()
# fut.cancelled()
# fut.result()

# fut.set_result("a result is set here")
# fut.done()
# fut.cancelled()
# fut.result()


# indent = lambda spaces : ' ' * spaces

# async def example(count: int) -> str:
#     print(indent(count), "Before the first await")
#     await asyncio.sleep(0)
#     print(indent(count), "After the first await")
#     if count == 0:
#         print(indent(count), "Returning result")
#         return "result"
#     for i in range(count):
#         print(indent(count), "Before await inside loop iteration ", i)
#         await asyncio.sleep(i)
#         print(indent(count), "Before await inside loop iteration ", i)
#     print(indent(count), f"Before await on example({count - 1})")
#     return await example(count - 1)

# class TraceStep(asyncio.tasks._PyTask):
#     def _task__(self, exc=None):
#         print(f"<step name={self.get_name()} done={self.done()}>")
#         result = super()._task__step(exc=exc)
#         print(f"</step name={self.get_name()} done={self.done()}>")        


# def mytaskfactory(loop, coro) -> Callable:
#     task = asyncio.Task(coro, loop=loop)
#     task.set_name(f"CustomTask-{task.get_name()}")
#     return task


# print("Starting")
# loop = asyncio.get_event_loop()
# loop.set_task_factory(mytaskfactory(loop, coro))
# loop.run_until_complete()
# print("Done")

async def get_result(awaitable: Awaitable) -> str:
    try:
        result = await awaitable
    except Exception as e:
        print(f"Caught {e}")
        return "no result"
    else:
        return result

f = asyncio.Future()
loop = asyncio.get_event_loop()
loop.call_later(5, f.set_result, "this is my result")
r = loop.run_until_complete(get_result(f))
print(r)
f = asyncio.Future()
loop.call_later(10, f.set_result, "another result")
r = loop.run_until_complete(get_result(get_result(get_result(f))))
print(r)

f = asyncio.Future()
loop.call_later(5, f.set_exception, ValueError('bad value 53'))
r = loop.run_until_complete(get_result(f))
print(r)

# f = asyncio.Future()
# loop.call_later(5, f.cancel)
# loop.run_until_complete(get_result(f))

f = asyncio.Future()
loop.call_later(10, f.set_result, "final result")
r = loop.run_until_complete(asyncio.gather(get_result(f), get_result(f), get_result(f)))
print(r)

def callback(fut: asyncio.Future) -> None:
    print(f"called by {fut}")
    
f = asyncio.Future()
f.add_done_callback(callback)
f.add_done_callback(lambda f: loop.stop())
f.set_result("yupo")
loop.run_forever()

