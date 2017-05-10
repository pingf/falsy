
from falsy.netboy.request import get_request, post_request
import asyncio as aio


async def get_boy(payload):
    targets = []
    for payload in payload:
        targets.append(get_request(payload))
    res = await aio.gather(
        *targets, return_exceptions=True
    )
    return res

async def post_boy(payload):
    targets = []
    for payload in payload:
        targets.append(post_request(payload))
    res = await aio.gather(
        *targets, return_exceptions=True
    )
    return res

async def net_boy(payload):
    targets = []
    for payload in payload:
        if payload.get('postfields'):
            targets.append(post_request(payload))
        else:
            targets.append(get_request(payload))
    res = await aio.gather(
        *targets, return_exceptions=True
    )
    return res
