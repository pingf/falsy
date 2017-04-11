import time

from falsy.netboy.request import get_request, post_request
import asyncio as aio


async def get_boy(urls):
    targets = []
    for payload in urls:
        targets.append(get_request(payload))
    begin = time.time()
    res = await aio.gather(
        *targets, return_exceptions=True
    )
    end = time.time()
    print('time:', end - begin)
    # return [t.result() for t in targets]
    return res

async def post_boy(urls):
    targets = []
    for payload in urls:
        targets.append(post_request(payload))
    begin = time.time()
    res = await aio.gather(
        *targets, return_exceptions=True
    )
    end = time.time()
    print('time:', end - begin)
    # return [t.result() for t in targets]
    return res
