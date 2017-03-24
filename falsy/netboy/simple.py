from contextlib import suppress
from io import BytesIO
import asyncio as aio
import aiohttp
import pycurl
import atexit

import time
import uvloop


# Curl event loop:
class CurlLoop:
    class Error(Exception): pass

    _multi = pycurl.CurlMulti()
    atexit.register(_multi.close)
    _futures = {}

    @classmethod
    async def handler_ready(cls, c):
        cls._futures[c] = aio.Future()
        cls._multi.add_handle(c)
        try:
            # try:
            curl_ret = await cls._futures[c]
                # print(curl_ret, '>>>>')
            # except Exception as e:
            #     raise e
            #     print('exception', e)
                # return
            return curl_ret
        finally:
            cls._multi.remove_handle(c)

    @classmethod
    def perform(cls):
        if cls._futures:
            while True:
                status, num_active = cls._multi.perform()
                if status != pycurl.E_CALL_MULTI_PERFORM:
                    break
            while True:
                num_ready, success, fail = cls._multi.info_read()
                for c in success:
                    cls._futures.pop(c).set_result('')
                for c, err_num, err_msg in fail:
                    print(err_num)
                    cls._futures.pop(c).set_exception(CurlLoop.Error('curl error:' +str(err_num)+' '+err_msg))
                if num_ready == 0:
                    break

# Single curl request:
async def request(url, timeout=5):
    c = pycurl.Curl()
    try:
        c.setopt(pycurl.URL, url.encode('utf-8'))
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)

        raw_text_buf = BytesIO()
        c.setopt(pycurl.WRITEFUNCTION, raw_text_buf.write)

        with aiohttp.Timeout(timeout):
            await CurlLoop.handler_ready(c)
            return raw_text_buf.getvalue().decode('utf-8', 'ignore')
        print('timeout',url)
        return 'timeout'
    finally:
        c.close()


def exception_handler(context):
    print(context, '????')
# Asyncio event loop + CurlLoop:
def run_until_complete(coro):
    async def main_task():
        pycurl_task = aio.ensure_future(_pycurl_loop())
        try:
            await coro
        finally:
            pycurl_task.cancel()
            with suppress(aio.CancelledError):
                await pycurl_task
    # Run asyncio event loop:
    # aio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # loop = uvloop.new_event_loop()
    # aio.set_event_loop(loop)

    loop = aio.get_event_loop()
    loop.set_exception_handler(exception_handler)
    loop.run_until_complete(main_task())


async def _pycurl_loop():
    while True:
        await aio.sleep(0)
        CurlLoop.perform()

# Test it:
async def main():
    url = 'http://httpbin.org/delay/3'
    url1 = 'http://www.baidu.com'
    url2 = 'http://www.douban.com'
    url3 = 'http://www.sina.com'
    url4 = 'http://www.bing.com'
    url5 = 'http://www.taobao.com'
    url6 = 'http://www.csdn.net'
    begin = time.time()
    urls = [request(url1), request(url2),
            request(url3), request(url4),
            request(url5), request(url6),
            ]
    urls =[request(url1)]
    res = await aio.gather(
        *urls,return_exceptions=True
    )
    end = time.time()
    print(end-begin)
    # print(res[0][400:440],0)  # to see result
    # print(res[3][400:440],3)  # to see result
    # print(res[5],type(res[5]))
    # print(res[5][400:440],5)  # to see result
    # print(res[7][400:440])  # to see result
    # print(res[9][400:440])  # to see result


if __name__ == "__main__":
    # try:
    run_until_complete(main())
    # except Exception as e:
    #     print(e, '>>>>>>1234')