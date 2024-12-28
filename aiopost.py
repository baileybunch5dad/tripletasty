import aiohttp
import asyncio

# https://scrapeops.io/python-web-scraping-playbook/python-aiohttp-post-requests/

# import aiohttp
# import asyncio

# async def post_request():
#     async with aiohttp.ClientSession() as session:
#         response = await session.post(url="https://httpbin.org/post",
#                                       data={"key": "value"},
#                                       headers={"Content-Type": "application/json"})
#         print(await response.json())

# asyncio.run(post_request())

# my modified version

async def post_request() -> str:
    async with aiohttp.ClientSession() as session:
        response = await session.post(url="https://httpbin.org/post",
                                      data={"key": "value"},
                                      headers={"Content-Type": "application/json"})
        s = await response.json()
        return s

r = asyncio.run(post_request())
print(r)