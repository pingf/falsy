import datetime
import json
import socket
import traceback
from concurrent import futures
from logging import Logger
from time import sleep
import html

import pycurl
from urllib.parse import urlparse

import uvloop
import websocket
import sys

from bs4 import UnicodeDammit

from falsy.loader import func
from falsy.netboy.netboy import NetBoy
from falsy.netboy.one import get_it


class ChromeShortException(Exception):
    pass


class ChromeEmptyException(Exception):
    pass


class ChromeECMAScriptException(Exception):
    pass


import asyncio as aio


class ChromeTargetException(Exception):
    pass


class ChromeBoy:
    def __init__(self, **kwargs):
        self._host = kwargs.get('host', 'localhost')
        self._port = kwargs.get('port', 9222)
        self._url = '%s:%d' % (self._host, self._port)
        self._socket_timeout = kwargs.get('sockettimeout', 20)
        self._browser_url = 'ws://' + self._url + '/devtools/browser'
        self._id = 0
        self._user_agent = kwargs.get('useragent')
        self._http_header = kwargs.get('httpheader')
        self._cookies = kwargs.get('cookies')
        self._load_timeout = kwargs.get('loadtimeout', 15)

    def run1_core(self, payload, browser, begin_time):
        page = None
        target_id = None

        retry = payload.get('retried', False)
        try:
            socket_timeout = payload.get('sockettimeout') or self._socket_timeout
            target_id = self.new_blank_target(browser)
            page_url = 'ws://' + self._url + '/devtools/page/' + str(target_id)
            page = websocket.create_connection(page_url, timeout=socket_timeout)
            url = payload.get('url')
            load_timeout = payload.get('loadtimeout') or self._load_timeout
            user_agent = payload.get('useragent') or self._user_agent
            http_header = payload.get('httpheader') or self._http_header
            cookies = payload.get('cookies') or self._cookies
            self.json_endp()
            self.enable_network(page)
            self.enable_page(page)
            self.set_user_agent(page, user_agent)
            self.set_http_header(page, http_header)
            self.set_cookies(page, cookies)
            self.navigate_to_url(page, url, load_timeout)
            result = self.eval_result(page)
            data = self.load_data(page, result, payload)

            self.auto_id(0)
            # if data.get('state') != 'normal':
            #     return data
            # else:
            #     data['state'] = 'normal'
            return self.crawl_info(data, payload, begin_time)
        except ChromeECMAScriptException as e:
            if retry:
                error_data = {
                    'state': 'error',
                    'error_code': -1,
                    'error_desc': 'es error'
                }
                ret = self.crawl_info(error_data, payload, begin_time)
                return ret
            else:
                sleep(payload.get('retry_sleep', 3))
                payload['sockettimeout'] = int(payload.get('sockettimeout') or self._socket_timeout) + payload.get(
                    'retry_extra', 10)
                payload['loadtimeout'] = int(payload.get('loadtimeout') or self._socket_timeout) + payload.get('retry_extra',
                                                                                                               10)
                payload['retried'] = True
                return self.run1_core(payload, browser=browser, begin_time=begin_time)
        except ChromeEmptyException as e:
            if retry:
                error_data = {
                    'state': 'error',
                    'error_code': -2,
                    'error_desc': 'data empty'
                }
                ret = self.crawl_info(error_data, payload, begin_time)
                return ret
            else:
                sleep(payload.get('retry_sleep', 3))
                payload['sockettimeout'] = int(payload.get('sockettimeout') or self._socket_timeout) + payload.get(
                    'retry_extra', 10)
                payload['loadtimeout'] = int(payload.get('loadtimeout') or self._socket_timeout) + payload.get('retry_extra',
                                                                                                               10)
                payload['retried'] = True
                return self.run1_core(payload, browser=browser, begin_time=begin_time)

        except ChromeShortException as e:
            if retry:
                error_data = {
                    'state': 'error',
                    'error_code': -3,
                    'error_desc': 'content too short'
                }
                ret = self.crawl_info(error_data, payload, begin_time)
                return ret
            else:
                sleep(payload.get('retry_sleep', 3))
                payload['sockettimeout'] = int(payload.get('sockettimeout') or self._socket_timeout) + payload.get(
                    'retry_extra', 10)
                payload['loadtimeout'] = int(payload.get('loadtimeout') or self._socket_timeout) + payload.get('retry_extra',
                                                                                                               10)
                payload['retried'] = True
                return self.run1_core(payload, browser=browser, begin_time=begin_time)
        except ChromeTargetException as e:
            if retry:
                error_data = {
                    'state': 'critical',
                    'error_code': -4,
                    'error_desc': 'target not created'
                }
                ret = self.crawl_info(error_data, payload, begin_time)
                return ret
            else:
                sleep(payload.get('retry_sleep', 3))
                payload['sockettimeout'] = int(payload.get('sockettimeout') or self._socket_timeout) + payload.get(
                    'retry_extra', 10)
                payload['loadtimeout'] = int(payload.get('loadtimeout') or self._socket_timeout) + payload.get('retry_extra',
                                                                                                               10)
                payload['retried'] = True
                return self.run1_core(payload, browser=browser, begin_time=begin_time)
        except websocket.WebSocketTimeoutException as e:
            if retry:
                error_data = {
                    'state': 'critical',
                    'error_code': -5,
                    'error_desc': str(type(e)) + ': ' + str(e)
                }
                ret = self.crawl_info(error_data, payload, begin_time)
                return ret
            else:
                sleep(payload.get('retry_sleep', 3))
                payload['sockettimeout'] = int(payload.get('sockettimeout') or self._socket_timeout) + payload.get(
                    'retry_extra', 10)
                payload['loadtimeout'] = int(payload.get('loadtimeout') or self._socket_timeout) + payload.get('retry_extra',
                                                                                                               10)
                payload['retried'] = True
                return self.run1_core(payload, browser=browser, begin_time=begin_time)
                # return self.rerun1(payload, data)
        except Exception as e:
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
            error_data = {
                'state': 'critical',
                'error_code': -7,
                'error_desc': str(type(e)) + ': ' + str(e)
            }
            ret = self.crawl_info(error_data, payload, begin_time)
            return ret

        finally:
            if page is not None:
                page.close()
            self.close_target(browser, target_id)

    def run1(self, payload):
        data = None
        browser = None
        begin_time = datetime.datetime.now()
        retry = payload.get('retried', False)
        try:
            socket_timeout = payload.get('sockettimeout') or self._socket_timeout
            browser = websocket.create_connection(self._browser_url, timeout=socket_timeout)
            data = self.run1_core(payload, browser, begin_time)
            return data
        except websocket.WebSocketTimeoutException as e:
            if retry:
                error_data = {
                    'state': 'critical',
                    'error_code': -6,
                    'error_desc': str(type(e)) + ': ' + str(e)
                }
                ret = self.crawl_info(error_data, payload, begin_time)
                return ret
            else:
                sleep(payload.get('retry_sleep', 3))
                payload['sockettimeout'] = int(payload.get('sockettimeout') or self._socket_timeout) + payload.get(
                    'retry_extra', 10)
                payload['loadtimeout'] = int(payload.get('loadtimeout') or self._socket_timeout) + payload.get('retry_extra',
                                                                                                               10)
                payload['retried'] = True
                return self.run1_core(payload, browser=browser, begin_time=begin_time)
        except Exception as e:
            error_data = {
                'state': 'critical',
                'error_code': -7,
                'error_desc': str(type(e)) + ': ' + str(e)
            }
            ret = self.crawl_info(error_data, payload, begin_time)
            return ret

        finally:
            if browser is not None:
                browser.close()

    def json_endp(self):
        payload = {
            'url': self._url + '/json',
            'httpheader': ["Content-Type: application/json; charset=utf-8"],
            'http_version': pycurl.CURL_HTTP_VERSION_1_1,
            'useragent': 'curl/7.53.1'
        }
        resp = get_it(payload)
        return resp

    def auto_id(self, value=None):
        id = self._id
        if value is None:
            self._id = id + 1
        else:
            self._id = value
        return self._id

    def enable_network(self, ws):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Network.enable'
        ws.send(json.dumps(req))
        ress = ws.recv()
        return ress

    def enable_page(self, ws):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Page.enable'
        ws.send(json.dumps(req))
        ress = ws.recv()
        return ress

    def recv4result(self, ws, raise_exception=False):
        packet = None
        try:
            while 1:
                s = ws.recv()
                packet = json.loads(s)
                if packet.get('result') is not None or packet.get('error') is not None:
                    return packet
        except Exception as e:
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
            if raise_exception:
                raise e
            else:
                sleep(3)
                return packet

    def new_target(self, ws, url):
        req = {}
        req['id'] = self._id
        req['method'] = 'Target.createTarget'
        req['params'] = {"url": url, "browserContextId": 1, "width": 1280}  # , "height": 1696}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        return resp

    def new_blank_target(self, ws):
        resp = self.new_target(ws, "about:blank")
        if resp is None or resp.get('error') or resp.get('result') is None or resp.get('result').get(
                'targetId') is None:
            raise ChromeTargetException('chrome target not created!')
        return resp.get('result').get('targetId')

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if type(value) is dict:
            self._url = '%s:%d' % (value.get('host', 'localhost'), value.get('port', 9222))
        elif type(value) is tuple:
            self._url = '%s:%d' % (value[0], value[1])
        elif type(value) is str:
            self._url = value

    def set_user_agent(self, ws, user_agent):
        if user_agent is None:
            return
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Network.setUserAgentOverride'
        req['params'] = {"userAgent": user_agent}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        return resp

    def set_http_header(self, ws, headers):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Network.setExtraHTTPHeaders'
        req['params'] = {"headers": headers}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        return resp

    def set_cookies(self, ws, cookies):
        if cookies:
            for cookie in cookies:
                self.set_cookie(ws, cookie['url'], cookie['name'], cookie['value'])

    def set_cookie(self, ws, url, name, value):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Network.setCookie'
        req['params'] = {"url": url, "name": name, "value": value}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        return resp

    def navigate_to_url(self, ws, url, timeout):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Page.navigate'
        req['params'] = {"url": url}
        ws.send(json.dumps(req))
        resp = self.recv4load(ws, timeout)
        return resp

    def recv4load(self, ws, timeout=10):
        try:
            a = datetime.datetime.now()
            ret = None
            i = 0
            while 1:
                s = ws.recv()
                packet = json.loads(s)
                if packet.get('result') is not None:
                    ret = packet
                if packet.get('error') is not None:
                    return packet
                if packet.get('method') == 'Page.loadEventFired':
                    sleep(1)
                    return ret
                i += 1
                if i % 100 == 0:
                    b = datetime.datetime.now()
                    seconds = (b - a).total_seconds()
                    if seconds > timeout:
                        return ret

        except Exception as e:
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
            raise e

    def eval_result(self, ws):
        result = self.eval_result_full(ws)
        if result is None or result.get('result') is None or \
                        result['result'].get('result') is None or \
                        result['result']['result'].get('subtype') == 'error':
            result = self.eval_result_easy(ws)
            if result is None or result.get('result') is None or \
                            result['result'].get('result') is None or \
                            result['result']['result'].get('subtype') == 'error':
                raise ChromeECMAScriptException('es error')
        return result

    def eval_result_full(self, ws):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Runtime.evaluate'
        eval_func = '''
        function links(){
          var arr = [], l = document.links;
          for(var i=0; i<l.length; i++) {
            if(!l[i].href.startsWith('javascript:')){
              arr.push(l[i].href);
            }
          }
          return arr;
        }
        var req = new XMLHttpRequest();
        req.open('GET', document.location, false);
        req.send(null);
        var headers = req.getAllResponseHeaders().toLowerCase();
        JSON.stringify({
            "title": document.title,
            "location": document.location,
            "metas": Array.prototype.map
            .call(document.getElementsByTagName("meta"), function(meta){
              prop = meta.getAttribute("property")
              if (prop) {
                return {"property":prop, "content":meta.content}
              }
              return {"name":meta.name, "content":meta.content}
            }).filter(function(meta){return meta.content != ''}),
            "links": Array.prototype.map.call(document.links,function(link){return link.href}),
            "links2": Array.prototype.map.call(document.querySelectorAll("link"),function(link){return link.href})
            .filter(function(text){ return !text.startsWith('javascript');}),
            "scripts": Array.prototype.map.call(document.scripts,function(script){return script.src})
            .filter(function(text){ return !text.startsWith('javascript');}),
            "headers": headers.split("\\r\\n"),
            "images": Array.prototype.map.call(document.images,function(img){return img.src})
            .filter(function(text){ return !text.startsWith('javascript');}),
            "location": {
                "href": window.location.href,
                "origin": window.location.origin,
                "host": window.location.host,
                "hostname": window.location.hostname,
                "pathname": window.location.pathname,
                "port": window.location.port,
                "protocol": window.location.protocol,
                "search": window.location.search,
            },
            "body": document.body.outerHTML,
            "head": document.head.outerHTML,
            "charset": document.charset,
            "text": document.body.innerText,
        });
        '''
        req['params'] = {"expression": eval_func}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        return resp

    def eval_result_easy(self, ws):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Runtime.evaluate'

        eval_func = '''
        var req = new XMLHttpRequest();
        req.open('GET', document.location, false);
        req.send(null);
        var headers = req.getAllResponseHeaders().toLowerCase();
        JSON.stringify({
            "title": document.title,
            "location": document.location,
            "location": {
                "href": window.location.href,
            },
            "body": document.body.outerHTML,
            "head": document.head.outerHTML,
            "charset": document.charset,
            "text": document.body.innerText,
        });
        '''
        req['params'] = {"expression": eval_func}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        return resp

    def crawl_info(self, data, payload, begin_time):
        end_time = datetime.datetime.now()
        elapsed = (end_time - begin_time).total_seconds()
        tid = payload.get('id')
        url = payload.get('url')
        if type(data) == dict:
            data['time'] = elapsed
            if tid:
                data['id'] = tid
            data['spider'] = 'chrome'
            data['url'] = url
            data['payload'] = payload
            # data['chrome_id'] = payload.get('chrome_id')
        else:
            data = {
                'time': elapsed,
                'spider': 'chrome',
                'url': url,
            }

        post_func = payload.get('post_func')
        if type(post_func) == str:
            post_func = func.load(post_func)
        if post_func:
            data2 = post_func(payload, data)
            if type(data2) is dict and len(data2) >= len(data):
                data = data2
        return data

    def load_data(self, ws, result, payload):
        data = json.loads(result['result']['result']['value'])
        if data is None:
            raise ChromeEmptyException('data is null')
        charset = data['charset']
        data['body'] = self.beautify(html.unescape(data['body']), charset)
        data['head'] = self.beautify(data['head'], charset)
        data['text'] = self.beautify(data['text'], charset)
        effect = self.effect_url(data)
        hostname = urlparse(effect).hostname if effect else None
        data['ip'] = socket.gethostbyname(hostname) if hostname else None
        if len(data['body']) <= len('<body></body>'):
            raise ChromeShortException('too short in retry')
        if payload.get('need_screenshot', True):
            screen = self.screenshot(ws, payload.get('shot_quality', 40), payload.get('shot_format', 'jpeg'))
        else:
            screen = None
        data['screenshot'] = screen
        current_cookies = self.get_cookies(ws)
        data['cookies'] = current_cookies
        data['state']='normal'
        return data

    def effect_url(self, data):

        if data is None or type(data) is not dict \
                or data.get('location') is None or data.get('location').get('href') is None:
            return None
        effect = data['location']['href']
        return effect

    def get_body(self, ws, node_id):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'DOM.querySelector'
        req['params'] = {"selector": "body", "nodeId": node_id}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        body_id = resp['result']['nodeId']
        return body_id

    def get_size(self, ws, node_id):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'DOM.getBoxModel'
        req['params'] = {"nodeId": node_id}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        box = resp['result']['model']
        return box['width'], box['height']

    def get_document(self, ws):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'DOM.getDocument'
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        node_id = resp['result']['root']['nodeId']
        return node_id

    def update_size(self, ws, width, height):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Emulation.setVisibleSize'
        req['params'] = {"width": width, "height": height}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Emulation.forceViewport'
        req['params'] = {"x": 0, "y": 0, "scale": 1}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)

    def screenshot(self, ws, quality=40, shot_format='jpeg'):
        doc_id = self.get_document(ws)
        body_id = self.get_body(ws, doc_id)
        w, h = self.get_size(ws, body_id)

        self.update_size(ws, w, h)
        if h > 2000:
            sleep((h // 1000) * 0.05)

        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Page.captureScreenshot'
        req['params'] = {"format": shot_format, "quality": quality, "fromSurface": False}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws, False)
        if resp is None or resp.get('result') is None:
            return None
        data = resp['result']['data']
        return data

    def get_cookies(self, ws):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Network.getCookies'
        # req['params'] = {"url": url, "name": name, "value": value}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        return resp['result']['cookies']

    def close_target(self, ws, tid):
        req = {}
        req['id'] = self.auto_id()
        req['method'] = 'Target.closeTarget'
        req['params'] = {"targetId": tid}
        ws.send(json.dumps(req))
        resp = self.recv4result(ws)
        return resp

    def beautify(self, data, charset):
        dammit = UnicodeDammit(data, [charset, "utf-8", "gb2312", "gbk", "big5", "gb18030"], smart_quotes_to="html")
        data = dammit.unicode_markup
        return data

    def run(self, data, max=4):
        results = []
        with futures.ThreadPoolExecutor(max_workers=max) as executor:
            future_to_url = {}
            for i, payload in enumerate(data):
                payload['chrome_id'] = i
                future_to_url[executor.submit(self.run1, payload)] = payload
                # future_to_url[executor.submit(self.run1_core, payload, browser, begin_time)] = payload
            for future in futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                else:
                    data['chrome_id'] = url['chrome_id']
                    results.append(data)

        sorted_results = sorted(results, key=lambda tup: tup['chrome_id'])
        return sorted_results


if __name__ == '__main__':
    a = ChromeBoy()
    payload = [
        # {'url': 'http://www.bing.com'},
        {'url': 'http://www.baidu.com'},
        {'url': 'http://www.douban.com'},
        {'url': "http://job.xyxww.com.cn"},
        # {'url': "http://wx.pdsxww.com"},
        # {'url': "http://fang.xiangcheng.org"},
        # {'url': "http://kj.hnciq.org.cn"},
        # {'url': "http://pub.dzdj.com.cn"},
        ]
    resp = a.run(payload)
    for r in resp:
        print(r['chrome_id'])
        print(r.get('url'))
        print(r.get('title'))
        print(r.get('text'))
        print(r['state'])
        # resp = a.run1({
        #     'url': 'http://www.douban.com'
        # })
        # for r in resp:
        #     print(r['chrome_id'])
        #     print(r['title'])
        # print(json.dumps(resp, indent=2))
