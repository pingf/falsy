import time

from falsy.netboy.request import request
import asyncio as aio


async def fetch(urls):
    targets = []
    for payload in urls:
        targets.append(request(payload))
    begin = time.time()
    res = await aio.gather(
        *targets, return_exceptions=True
    )
    end = time.time()
    print('time:', end - begin)
    return res
