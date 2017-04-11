import time

from falsy.netboy.request import get_request, post_request
import asyncio as aio


async def get_boy(payload):
    targets = []
    for payload in payload:
        targets.append(get_request(payload))
    begin = time.time()
    res = await aio.gather(
        *targets, return_exceptions=True
    )
    end = time.time()
    print('time:', end - begin)
    # return [t.result() for t in targets]
    return res

async def post_boy(payload):
    targets = []
    for payload in payload:
        targets.append(post_request(payload))
    begin = time.time()
    res = await aio.gather(
        *targets, return_exceptions=True
    )
    end = time.time()
    print('time:', end - begin)
    # return [t.result() for t in targets]
    return res

async def net_boy(payload):
    targets = []
    for payload in payload:
        if payload.get('postfields'):
            targets.append(post_request(payload))
        else:
            targets.append(get_request(payload))
    begin = time.time()
    res = await aio.gather(
        *targets, return_exceptions=True
    )
    end = time.time()
    print('time:', end - begin)
    # return [t.result() for t in targets]
    return res
