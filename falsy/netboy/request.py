from io import BytesIO

import aiohttp
import pycurl

from falsy.netboy.curl_loop import CurlLoop


def setup_curl(c, p, data, header):
    def write_function(buf):
        size = data.getbuffer().nbytes
        if size < 4096000:
            data.write(buf)
            return len(buf)
        return 0

    url = p.get('url')
    c.setopt(pycurl.URL, url.encode('utf-8'))
    c.setopt(pycurl.FOLLOWLOCATION, p.get('followlocation', 1))
    c.setopt(pycurl.MAXREDIRS, p.get('maxredirs', 5))
    c.setopt(pycurl.WRITEHEADER, header)
    c.setopt(pycurl.WRITEFUNCTION, write_function)
    return c


# Single curl request:
async def request(payload):
    c = pycurl.Curl()
    data_buf = BytesIO()
    header_buf = BytesIO()
    try:
        setup_curl(c, payload, data_buf, header_buf)

        with aiohttp.Timeout(payload.get('timeout', 10)):
            await CurlLoop.handler_ready(c)
            storage = payload.get('storage')
            # if storage == 'seaweed':
            data = data_buf.getvalue().decode('utf-8', 'ignore')
            header = header_buf.getvalue().decode('utf-8', 'ignore')
            return {
                'header': header,
                'data': data,
            }

        print('timeout', url)
        return {
            'timeout': url
        }
    finally:
        print('final close')
        c.close()
