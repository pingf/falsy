import pycurl
def curl_result(c):
    effective_url = c.getinfo(pycurl.EFFECTIVE_URL)
    primary_ip = c.getinfo(pycurl.PRIMARY_IP)
    primary_port = c.getinfo(pycurl.PRIMARY_PORT)
    local_ip = c.getinfo(pycurl.LOCAL_IP)
    local_port = c.getinfo(pycurl.LOCAL_PORT)
    speed_download = c.getinfo(pycurl.SPEED_DOWNLOAD)
    size_download = c.getinfo(pycurl.SIZE_DOWNLOAD)
    redirect_time = c.getinfo(pycurl.REDIRECT_TIME)
    redirect_count = c.getinfo(pycurl.REDIRECT_COUNT)
    redirect_url = c.getinfo(pycurl.REDIRECT_URL)
    http_code = c.getinfo(pycurl.HTTP_CODE)
    response_code = c.getinfo(pycurl.RESPONSE_CODE)
    total_time = c.getinfo(pycurl.TOTAL_TIME)
    content_type = c.getinfo(pycurl.CONTENT_TYPE)
    namelookup_time = c.getinfo(pycurl.NAMELOOKUP_TIME)
    info_filetime = c.getinfo(pycurl.INFO_FILETIME)
    http_connectcode = c.getinfo(pycurl.HTTP_CONNECTCODE)
    starttransfer_time = c.getinfo(pycurl.STARTTRANSFER_TIME)
    pretransfer_time = c.getinfo(pycurl.PRETRANSFER_TIME)
    header_size = c.getinfo(pycurl.HEADER_SIZE)
    request_size = c.getinfo(pycurl.REQUEST_SIZE)
    ssl_verifyresult = c.getinfo(pycurl.SSL_VERIFYRESULT)
    num_connects = c.getinfo(pycurl.NUM_CONNECTS)

    return {
        'effective_url': effective_url,
        'primary_ip': primary_ip,
        'primary_port': primary_port,
        'local_ip': local_ip,
        'local_port': local_port,
        'speed_download': speed_download,
        'size_download': size_download,
        'redirect_time': redirect_time,
        'redirect_count': redirect_count,
        'redirect_url': redirect_url,
        'http_code': http_code,
        'response_code': response_code,
        'total_time': total_time,
        'content_type': content_type,
        'namelookup_time': namelookup_time,
        'info_filetime': info_filetime,
        'http_connectcode': http_connectcode,
        'starttransfer_time': starttransfer_time,
        'pretransfer_time': pretransfer_time,
        'header_size': header_size,
        'request_size': request_size,
        'ssl_verifyresult': ssl_verifyresult,
        'num_connects': num_connects,
        # 'proxy_ssl_verifyresult': proxy_ssl_verifyresult,
        # 'app_connecttime': app_connecttime,

    }
