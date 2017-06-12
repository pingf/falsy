import asyncio as aio
import atexit
import pycurl

from falsy.loader.func import load
from falsy.netboy.curl_result import curl_result


class CurlLoop:
    class CurlException(Exception):
        def __init__(self, code, desc, data):
            self.code = code
            self.desc = desc
            self.data = data

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
                print('exception', e, type(e))
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
                    result = curl_result(c)
                    result['url'] = c._raw_url
                    result['id'] = c._raw_id
                    result['state'] = 'normal'
                    result['spider'] = 'pycurl'
                    result['payload'] = payload = c._raw_payload

                    # post_func = payload.get('post_func')
                    # if type(post_func) == str:
                    #     post_func = load(post_func)
                    # if post_func:
                    #     result = post_func(payload, result)

                    cc.set_result(result)
                for c, err_num, err_msg in fail:
                    print('error:', err_num, err_msg, c.getinfo(pycurl.EFFECTIVE_URL))
                    result = curl_result(c)
                    result['url'] = c._raw_url
                    result['id'] = c._raw_id
                    result['state'] = 'error'
                    result['spider'] = 'pycurl'
                    result['error_code'] = err_num
                    result['error_desc'] = err_msg

                    result['payload'] = payload = c._raw_payload

                    post_func = payload.get('post_func')
                    if type(post_func) == str:
                        post_func = load(post_func)
                    if post_func:
                        result2 = post_func(payload, result)
                        if type(result2) is dict and len(result2) >= len(result):
                            result=result2
                    cls._futures.pop(c).set_exception(CurlLoop.CurlException(code=err_num, desc=err_msg, data=result))
                if num_ready == 0:
                    break


async def curl_loop():
    while True:
        await aio.sleep(0)
        CurlLoop.perform()
