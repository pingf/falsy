import asyncio as aio
import atexit
import pycurl

from falsy.netboy.curl_result import curl_result


class CurlLoop:
    class Error(Exception):
        pass

    _multi = pycurl.CurlMulti()
    atexit.register(_multi.close)
    _futures = {}

    @classmethod
    async def handler_ready(cls, c):
        cls._futures[c] = aio.Future()
        cls._multi.add_handle(c)
        try:
            try:
                curl_ret = await cls._futures[c]
            except Exception as e:
                print('exception', e)
                raise e
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
                    cc = cls._futures.pop(c)
                    cc.set_result(curl_result(c))

                for c, err_num, err_msg in fail:
                    print('error:', err_num, err_msg, c.getinfo(pycurl.EFFECTIVE_URL))
                    cls._futures.pop(c).set_exception(CurlLoop.Error('curl error:' + str(err_num) + ' ' + err_msg))
                if num_ready == 0:
                    break

async def curl_loop():
    while True:
        await aio.sleep(0)
        CurlLoop.perform()
