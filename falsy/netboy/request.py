from io import BytesIO

import aiohttp
import pycurl
from bs4 import UnicodeDammit
import re

from falsy.loader.func import load
from falsy.netboy.curl_loop import CurlLoop

DEFAULT_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm; Baiduspider/2.0; +http://www.baidu.com/search/spider.html) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80() Safari/537.36'

# curl_easy_perform()
#     |
#     |--NAMELOOKUP
#     |--|--CONNECT
#     |--|--|--APPCONNECT
#     |--|--|--|--PRETRANSFER
#     |--|--|--|--|--STARTTRANSFER
#     |--|--|--|--|--|--TOTAL
#     |--|--|--|--|--|--REDIRECT

def setup_curl_for_get(c, p, data_buf, headers=None):
    def header_function(header_line):
        count = headers['count']
        header_line = header_line.decode('iso-8859-1')

        if ':' not in header_line and not header_line.startswith('HTTP'):
            # print(header_line)
            if '\r\n' in header_line:
                headers['count'] += 1
                headers['content'].append({})
            return

        # Break the header line into header name and value.
        if ':' in header_line:
            name, value = header_line.rstrip('\r\n').split(':', 1)
        else:
            name, value = header_line.rstrip('\r\n').split(' ', 1)

        # Remove whitespace that may be present.
        # Header lines include the trailing newline, and there may be whitespace
        # around the colon.
        name = name.strip()
        value = value.strip()

        # Header names are case insensitive.
        # Lowercase name here.
        name = name.lower()

        # Now we can actually record the header name and value.
        if name in headers['content'][count]:
            headers['content'][count][name].append(value)
        else:
            headers['content'][count][name] = [value]

    def write_function(buf):
        size = data_buf.getbuffer().nbytes
        if size < 4096000:
            data_buf.write(buf)
            return len(buf)
        return 0

    # def debug_function(debug_type, debug_msg):
    #     print("debug(%d): %s" % (debug_type, debug_msg))
    #
    # def progress_function(download_t, download_d, upload_t, upload_d):
    #     print('>'*40)
    #     print("Total to download", download_t)
    #     print("Total downloaded", download_d)
    #     print("Total to upload", upload_t)
    #     print("Total uploaded", upload_d)

    url = p.get('url')
    c.setopt(pycurl.URL, url.encode('utf-8'))
    c.setopt(pycurl.FOLLOWLOCATION, p.get('followlocation', 1))
    c.setopt(pycurl.MAXREDIRS, p.get('maxredirs', 5))
    # c.setopt(pycurl.WRITEHEADER, header_buf)
    headerfunction = p.get('headerfunction')
    if headerfunction is None:
        c.setopt(pycurl.HEADERFUNCTION, header_function)
    else:
        c.setopt(pycurl.HEADERFUNCTION, load(headerfunction))
    writefunction = p.get('writefunction')
    if writefunction is None:
        c.setopt(pycurl.WRITEFUNCTION, write_function)
    else:
        c.setopt(pycurl.WRITEFUNCTION, load(writefunction))
    c.setopt(pycurl.USERAGENT, p.get('useragent', DEFAULT_USER_AGENT))
    c.setopt(pycurl.SSL_VERIFYPEER, p.get('ssl_verifypeer', 0))
    c.setopt(pycurl.SSL_VERIFYHOST, p.get('ssl_verifyhost', 0))
    c.setopt(pycurl.NOSIGNAL, p.get('nosignal', 1))
    c.setopt(pycurl.CONNECTTIMEOUT, p.get('connecttimeout', 7))
    c.setopt(pycurl.TIMEOUT, p.get('timeout', 15))
    c.setopt(pycurl.DNS_CACHE_TIMEOUT, p.get('dns_cache_timeout', 360))
    c.setopt(pycurl.DNS_USE_GLOBAL_CACHE, p.get('dns_use_global_cache', 1))
    c.setopt(pycurl.TCP_NODELAY, p.get('tcp_nodelay', 1))
    c.setopt(pycurl.IPRESOLVE, p.get('ipresolve', pycurl.IPRESOLVE_V4))
    c.setopt(pycurl.ENCODING, p.get('encoding', 'gzip, deflate'))

    c.setopt(pycurl.HTTP_VERSION, p.get('http_version', pycurl.CURL_HTTP_VERSION_1_0))
    c.setopt(pycurl.FORBID_REUSE, p.get('forbid_reuse', 1))
    c.setopt(pycurl.FRESH_CONNECT, p.get('fresh_connect', 1))
    c.setopt(c.AUTOREFERER, p.get('autoreferer', 1))

    httpheader = p.get('httpheader')
    if httpheader:
        c.setopt(pycurl.HEADER, p.get('header', 1))
        c.setopt(c.HTTPHEADER, httpheader)
    referer = p.get('referer')
    if referer:
        c.setopt(c.REFERER, referer)
    cookiejar = p.get('cookiejar')
    if cookiejar:
        print('cookiejar', cookiejar)
        c.setopt(c.COOKIEJAR, cookiejar)
    cookiefile = p.get('cookiefile')
    if cookiefile:
        print('cookiefile', cookiefile)
        c.setopt(c.COOKIEFILE, cookiefile)

    dns_servers = p.get('dns_servers')
    if dns_servers:
        c.setopt(c.DNS_SERVERS, dns_servers)

    debug = p.get('debugfunction')
    if debug:
        c.setopt(pycurl.DEBUGFUNCTION, load(debug))
    c.setopt(pycurl.VERBOSE, p.get('verbose', 0))

    # noprogress = p.get('noprogress', True)
    # if noprogress is False:
    #     c.setopt(c.NOPROGRESS, False)
    #     xferinfo = p.get('XFERINFOFUNCTION')
    #     if xferinfo:
    #         c.setopt(c.XFERINFOFUNCTION, load(xferinfo))

    proxy = p.get('proxy')
    proxyport = p.get('proxyport')
    proxytype = p.get('proxytype')
    proxyuserpwd = p.get('proxyuserpwd')
    if proxy and proxyport and proxytype:
        c.setopt(pycurl.PROXY, proxy)
        c.setopt(pycurl.PROXYPORT, proxyport)
        c.setopt(pycurl.PROXYTYPE, proxytype)
        if proxyuserpwd:
            c.setopt(pycurl.PROXYUSERPWD, proxyuserpwd)
    return c


# Single curl request:
async def request(payload):
    c = pycurl.Curl()
    data_buf = BytesIO()
    # header_buf = BytesIO()
    headers = {'count': 0, 'content': [{}]}
    try:
        setup_curl_for_get(c, payload, data_buf, headers)  # header_buf)

        with aiohttp.Timeout(payload.get('timeout', 10)):
            resp = await CurlLoop.handler_ready(c)
            storage = payload.get('storage')
            # if storage == 'seaweed':
            encoding = None
            if 'content-type' in headers:
                content_type = headers['content-type'].lower()
                match = re.search('charset=(\S+)', content_type)
                if match:
                    encoding = match.group(1)
                    print('Decoding using %s' % encoding)
            body = data_buf.getvalue()

            if encoding is None:
                dammit = UnicodeDammit(body, ["utf-8", "gb2312", "gbk", "big5", "gb18030"], smart_quotes_to="html")
                data = dammit.unicode_markup
                encoding = dammit.original_encoding
            else:
                data = body.decode(encoding, 'ignore')
            # headers.remove({})
            headers['content'] = [h for h in headers['content'] if len(h)>0]
            resp.update({
                'data': data,
                'headers': headers,
                'encoding': encoding,
            })
            return resp



        # return 'haha'
        # print('timeout', url)
        # return {
        #     'timeout': url
        # }
    finally:
        c.close()
