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

async def crawl0(prefix: str, url: str = "") -> None:
    url = url or prefix
    print(f"Crawling {url}")
    client = httpx.AsyncClient()
    try:
        res = await client.get(url)
    finally:
        await client.aclose()
    for line in res.text.splitlines():
        if line.startswith(prefix):
            await crawl0(prefix, line)
            
        
            
# asyncio.run(crawl0("https://langa.pl/crawl/"))

addr = "https://langa.pl/crawl/"

async def progress(
    url: str, 
    algo: Callable[..., Coroutine],
    ) -> None:
    # asyncio.create_task(
    #     algo(url),
    #     name=url,
    # )
    # todo.add(url)
    task = asyncio.create_task(algo(url), name=url,)
    todo.add(task)
    start = time.time()
    while len(todo):
        # print(f"{len(todo)}:"+", ".join(sorted(todo))[:])
        # await asyncio.sleep(0.5)
        done, _pending = await asyncio.wait(todo, timeout=0.5)
        todo.difference_update(done)
        urls = [t.get_name() for t in todo]
        print(f"{len(urls)}:"+", ".join(sorted(urls))[:])
    end = time.time()
    print(f"Took {int(end - start)} seconds")
    
todo = set()

async def crawl1(prefix: str, url: str = "") -> None:
    # print(f"crawl1 args {prefix=} {url=}")
    url = url or prefix
    # print(f"crawl1 {url=}")
    client = httpx.AsyncClient()
    try:
        res = await client.get(url)
    finally:
        await client.aclose()
    for line in res.text.splitlines():
        if line.startswith(prefix):
            todo.add(line)
            await crawl1(prefix, line)
    todo.discard(url)
    
# asyncio.run(progress(addr, crawl1))

async def crawl2(prefix: str, url: str = "") -> None:
    url = url or prefix
    client = httpx.AsyncClient()
    try:
        res = await client.get(url)
    finally:
        await client.aclose()
    for line in res.text.splitlines():
        if line.startswith(prefix):
            task = asyncio.create_task(crawl2(prefix, line), name=line,)
            todo.add(task)
            # todo.add(line)
            # asyncio.create_task(crawl2(prefix, line), name=line,)
    # todo.discard(url)
    
# asyncio.run(progress(addr, crawl2))

async def async_main() -> None:
    try:
        await progress(addr, crawl2)
    except asyncio.CancelledError:
        print("Caught cancel")
        for task in todo:
            task.cancel()
    done, pending = await asyncio.wait(todo, timeout=1.0)
    todo.difference_update(done)
    todo.difference_update(pending)
    if todo:
        print("warning: new tasks were added while cancelling")

loop = asyncio.get_event_loop()
task = loop.create_task(async_main())
loop.call_later(4, task.cancel)
loop.run_until_complete(task)


        