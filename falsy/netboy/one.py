# Single curl request:
import pycurl
from io import BytesIO

import re

from bs4 import UnicodeDammit, BeautifulSoup

from falsy.netboy.curl_result import curl_result
from falsy.netboy.utils import setup_curl_for_get, get_title, get_links, get_links2, get_metas, get_images, \
    get_scripts, get_text, setup_curl_for_post


def post_it(payload):
    if type(payload) is list:
        payload = payload[0]
    c = pycurl.Curl()
    data_buf = BytesIO()
    # header_buf = BytesIO()
    headers = {'count': 0, 'content': [{}]}
    try:
        setup_curl_for_post(c, payload, data_buf, headers)  # header_buf)
        c.perform()

        resp = curl_result(c)
        resp['url'] = payload.get('url')
        resp['id'] = payload.get('id')
        resp['state'] = 'normal'
        resp['spider'] = 'pycurl'
        resp['payload'] = payload

        pycurl_get_resp(data_buf, headers, payload, resp)
        return resp
    except pycurl.error as e:
        resp = curl_result(c)
        resp['url'] = payload.get('url')
        resp['id'] = payload.get('id')
        resp['state'] = 'error'
        resp['spider'] = 'pycurl'
        resp['error_code'] = code = e.args[0]
        resp['error_desc'] = desc = e.args[1]
        if code in [18, 47]:
            resp['state'] = 'abnormal'
            pycurl_get_resp(data_buf, headers, payload, resp)
        return resp
    except Exception as e:
        resp = curl_result(c)
        resp['url'] = payload.get('url')
        resp['id'] = payload.get('id')
        resp['state'] = 'critical'
        resp['spider'] = 'pycurl'
        resp['error_code'] = '-1'
        resp['error_desc'] = 'pycurl re-one exception leaked: ' + str(e) + ' ' + str(type(e))
        return resp
    finally:
        c.close()


def get_it(payload):
    if type(payload) is list:
        payload = payload[0]
    c = pycurl.Curl()
    data_buf = BytesIO()
    # header_buf = BytesIO()
    headers = {'count': 0, 'content': [{}]}
    try:
        setup_curl_for_get(c, payload, data_buf, headers)  # header_buf)
        c.perform()

        resp = curl_result(c)
        resp['url'] = payload.get('url')
        resp['id'] = payload.get('id')
        resp['state'] = 'normal'
        resp['spider'] = 'pycurl'
        resp['payload'] = payload

        pycurl_get_resp(data_buf, headers, payload, resp)
        return resp
    except pycurl.error as e:
        resp = curl_result(c)
        resp['url'] = payload.get('url')
        resp['id'] = payload.get('id')
        resp['state'] = 'error'
        resp['spider'] = 'pycurl'
        resp['error_code'] = code = e.args[0]
        resp['error_desc'] = desc = e.args[1]
        if code in [18, 47]:
            resp['state'] = 'abnormal'
            pycurl_get_resp(data_buf, headers, payload, resp)
        return resp
    except Exception as e:
        resp = curl_result(c)
        resp['url'] = payload.get('url')
        resp['id'] = payload.get('id')
        resp['state'] = 'critical'
        resp['spider'] = 'pycurl'
        resp['error_code'] = '-1'
        resp['error_desc'] = 'pycurl re-one exception leaked: ' + str(e) + ' ' + str(type(e))
        return resp
    finally:
        c.close()


def pycurl_post_resp(data_buf, headers, payload, resp):
    body = data_buf.getvalue()
    encoding = 'utf-8'
    data = body.decode(encoding, 'ignore') if len(body) > 0 else ''

    headers['content'] = [h for h in headers['content'] if len(h) > 0]

    resp.update({
        'data': data,
        'headers': headers,
        'encoding': encoding,
    })

    headers['content'] = [h for h in headers['content'] if len(h) > 0]
    resp.update({
        'url': payload.get('url'),
        'data': data,
        'headers': headers,
        'spider': 'pycurl',
        'payload': payload,
    })


def pycurl_get_resp(data_buf, headers, payload, resp):
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


import json

if __name__ == '__main__':
    # p = {
    #     'url': 'http://www.douban.com',
    #     'dns_servers': '114.114.114.114'
    # }
    # resp = get_it(p)
    # print(json.dumps(resp, indent=2))
    p = {
        "url": "http://127.0.0.1:8006/v1/progress",
        "postfields": ["94679fb6-5245-11e7-9766-1c872c710a48"]
    }
    resp = post_it(p)
    print(json.dumps(resp, indent=2))
