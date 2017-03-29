from io import BytesIO

import aiohttp
import pycurl
import re

from falsy.loader.func import load
from falsy.netboy.curl_loop import CurlLoop

DEFAULT_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm; Baiduspider/2.0; +http://www.baidu.com/search/spider.html) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80() Safari/537.36'


def setup_curl_for_get(c, p, data_buf, headers=None):
    def header_function(header_line):
        header_line = header_line.decode('iso-8859-1')

        if ':' not in header_line:
            return

        # Break the header line into header name and value.
        name, value = header_line.split(':', 1)

        # Remove whitespace that may be present.
        # Header lines include the trailing newline, and there may be whitespace
        # around the colon.
        name = name.strip()
        value = value.strip()

        # Header names are case insensitive.
        # Lowercase name here.
        name = name.lower()

        # Now we can actually record the header name and value.
        headers[name] = value

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
    cookiefile = p.get('cookiefile')
    if cookiefile:
        c.setopt(c.COOKIEFILE, cookiefile)

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
    header_buf = BytesIO()
    headers = {}
    try:
        setup_curl_for_get(c, payload, data_buf, headers)  # header_buf)

        with aiohttp.Timeout(payload.get('timeout', 10)):
            await CurlLoop.handler_ready(c)
            storage = payload.get('storage')
            # if storage == 'seaweed':
            # header = header_buf.getvalue().decode('utf-8', 'ignore')
            encoding = None
            if 'content-type' in headers:
                content_type = headers['content-type'].lower()
                match = re.search('charset=(\S+)', content_type)
                if match:
                    encoding = match.group(1)
                    print('Decoding using %s' % encoding)
            if encoding is None:
                # Default encoding for HTML is iso-8859-1.
                # Other content types may have different default encoding,
                # or in case of binary data, may have no encoding at all.
                # encoding = 'iso-8859-1'
                encoding = 'utf8'
                print('Assuming encoding is %s' % encoding)

            body = data_buf.getvalue()
            data = body.decode(encoding, 'ignore')
            # Decode using the encoding we figured out.



            # data = data_buf.getvalue().decode('utf-8', 'ignore')

            # if 'content-type' in headers:
            #     content_type = headers['content-type'].lower()
            #     match = re.search('charset=(\S+)', content_type)
            #     if match:
            #         encoding = match.group(1)
            #         print('Decoding using %s' % encoding)

            effective_url = c.getinfo(pycurl.EFFECTIVE_URL)
            primary_port = c.getinfo(pycurl.PRIMARY_PORT)
            local_ip = c.getinfo(pycurl.LOCAL_IP)
            local_port = c.getinfo(pycurl.LOCAL_PORT)
            speed_download = c.getinfo(pycurl.SPEED_DOWNLOAD)
            size_download = c.getinfo(pycurl.SIZE_DOWNLOAD)
            redirect_time = c.getinfo(pycurl.REDIRECT_TIME)
            redirect_count = c.getinfo(pycurl.REDIRECT_COUNT)
            http_code = c.getinfo(pycurl.HTTP_CODE)
            response_code = c.getinfo(pycurl.RESPONSE_CODE)
            total_time = c.getinfo(pycurl.TOTAL_TIME)
            content_type = c.getinfo(pycurl.CONTENT_TYPE)
            namelookup_time = c.getinfo(pycurl.NAMELOOKUP_TIME)
            info_filetime = c.getinfo(pycurl.INFO_FILETIME)

            return {
                'data': data,
                'headers': headers,
                'encoding': encoding,
                'effective_url': effective_url,
                'primary_port': primary_port,
                'local_ip': local_ip,
                'local_port': local_port,
                'speed_download': speed_download,
                'size_download': size_download,
                'redirect_time': redirect_time,
                'redirect_count': redirect_count,
                'http_code': http_code,
                'response_code': response_code,
                'total_time': total_time,
                'content_type': content_type,
                'namelookup_time': namelookup_time,
                'info_filetime': info_filetime,
            }

        print('timeout', url)
        return {
            'timeout': url
        }
    finally:
        c.close()
