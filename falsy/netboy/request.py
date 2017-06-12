import uuid
from io import BytesIO
from urllib.parse import urlencode

import aiohttp
import pycurl
from bs4 import UnicodeDammit, BeautifulSoup
import re
import json

from falsy.loader.func import load
from falsy.netboy.curl_loop import CurlLoop
from falsy.netboy.utils import get_links, get_metas, get_images, get_scripts, get_text, setup_curl_for_get, \
    setup_curl_for_post
from falsy.netboy.utils import get_title, get_links2



# curl_easy_perform()
#     |
#     |--NAMELOOKUP
#     |--|--CONNECT
#     |--|--|--APPCONNECT
#     |--|--|--|--PRETRANSFER
#     |--|--|--|--|--STARTTRANSFER
#     |--|--|--|--|--|--TOTAL
#     |--|--|--|--|--|--REDIRECT



# def debug_function(debug_type, debug_msg):
#     print("debug(%d): %s" % (debug_type, debug_msg))
#
# def progress_function(download_t, download_d, upload_t, upload_d):
#     print('>'*40)
#     print("Total to download", download_t)
#     print("Total downloaded", download_d)
#     print("Total to upload", upload_t)
#     print("Total uploaded", upload_d)
# noprogress = p.get('noprogress', True)
# if noprogress is False:
#     c.setopt(c.NOPROGRESS, False)
#     xferinfo = p.get('XFERINFOFUNCTION')
#     if xferinfo:
#         c.setopt(c.XFERINFOFUNCTION, load(xferinfo))

# Single curl request:
async def get_request(payload):
    c = pycurl.Curl()
    data_buf = BytesIO()
    # header_buf = BytesIO()
    headers = {'count': 0, 'content': [{}]}
    try:
        setup_curl_for_get(c, payload, data_buf, headers)  # header_buf)

        with aiohttp.Timeout(payload.get('aiohttp_timeout', 60)):
            resp = await CurlLoop.handler_ready(c)
            charset = None
            if 'content-type' in headers:
                content_type = headers['content-type'].lower()
                match = re.search('charset=(\S+)', content_type)
                if match:
                    charset = match.group(1)
                    print('Decoding using %s' % charset)
            body = data_buf.getvalue()
            if len(body) == 0:
                data = ''
                charset = 'utf-8'
            else:
                if charset is None:
                    dammit = UnicodeDammit(body, ["utf-8", "gb2312", "gbk", "big5", "gb18030"], smart_quotes_to="html")
                    data = dammit.unicode_markup
                    charset = dammit.original_encoding
                else:
                    data = body.decode(charset, 'ignore')
            # headers.remove({})
            headers['content'] = [h for h in headers['content'] if len(h) > 0]
            soup_lxml = BeautifulSoup(data, 'lxml')
            soup_html = BeautifulSoup(data, 'html.parser')
            resp.update({
                'url': payload.get('url'),
                # 'soup': soup,
                'title': get_title(soup_lxml),
                'links': get_links(soup_lxml),
                'links2': get_links2(soup_lxml),
                'metas': get_metas(soup_lxml),
                'images': get_images(soup_lxml),
                'scripts': get_scripts(soup_lxml),
                'text': get_text(soup_html),
                'data': data,
                'headers': headers,
                'charset': charset,
                'spider': 'pycurl',
                'payload': payload,
            })
            post_func = payload.get('post_func')
            if post_func:
                post_func = load(post_func)
                resp = post_func(payload, resp)
            return resp
    finally:
        c.close()


async def post_request(payload):
    c = pycurl.Curl()
    data_buf = BytesIO()
    # header_buf = BytesIO()
    headers = {'count': 0, 'content': [{}]}
    try:
        setup_curl_for_post(c, payload, data_buf, headers)  # header_buf)

        with aiohttp.Timeout(payload.get('aiohttp_timeout', 60)):
            resp = await CurlLoop.handler_ready(c)
            # encoding = None
            # if 'content-type' in headers:
            #     content_type = headers['content-type'].lower()
            #     match = re.search('charset=(\S+)', content_type)
            #     if match:
            #         encoding = match.group(1)
            #         print('Decoding using %s' % encoding)
            body = data_buf.getvalue()
            encoding = 'utf-8'
            data = body.decode(encoding, 'ignore') if len(body) > 0 else ''

            # if encoding is None:
            #     dammit = UnicodeDammit(body, ["utf-8", "gb2312", "gbk", "big5", "gb18030"], smart_quotes_to="html")
            #     data = dammit.unicode_markup
            #     encoding = dammit.original_encoding
            # else:
            #     data = body.decode(encoding, 'ignore')
            # headers.remove({})
            headers['content'] = [h for h in headers['content'] if len(h) > 0]

            resp.update({
                # 'url': payload.get('url'),
                'data': data,
                'headers': headers,
                'encoding': encoding,
            })
            post_func = payload.get('post_func')
            if type(post_func) == str:
                post_func = load(post_func)
            if post_func:
                resp = post_func(payload, resp)
            # post_func = payload.get('post_func')
            # if post_func:
            #     post_func = load(post_func)
            #     resp = post_func(payload, resp)
            return resp
    finally:
        c.close()
