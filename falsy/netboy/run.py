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
    # print(r)
    # print(r[0])
    print(json.dumps(r[0], indent=2))
    # print(r[0]['primary_port'])
    # print(r[0]['local_ip'])
    # print(r[0]['local_port'])
    # print(r[0]['speed_download'])
    print('>'*50)
    # print(r[1]['header'])
