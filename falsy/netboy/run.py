import asyncio as aio
import json
from contextlib import suppress

import uvloop

from falsy.netboy.curl_loop import curl_loop



def exception_handler(context):
    print('context:', context)

def run(coro):
    async def main_task():
        pycurl_task = aio.ensure_future(curl_loop())
        try:
            r = await coro
        finally:
            pycurl_task.cancel()
            with suppress(aio.CancelledError):
                await pycurl_task
        return r, pycurl_task

    loop = uvloop.new_event_loop()
    # loop = aio.get_event_loop()
    aio.set_event_loop(loop)
    loop.set_exception_handler(exception_handler)
    r, _ = loop.run_until_complete(main_task())
    return r
