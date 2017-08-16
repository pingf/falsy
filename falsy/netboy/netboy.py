import typing

from falsy.netboy.curl_loop import CurlLoop
from falsy.netboy.fetch import net_boy
from falsy.netboy.run import run
import pycurl


class NetBoy:
    class Exception(Exception):
        pass

    class Dict(typing.Dict[str, typing.Any]):
        def __getattr__(self, name):
            # type: (str) -> Any
            try:
                return self[name]
            except KeyError:
                # raise NetBoy.Exception('netboy key error: ' + name)
                return None  # '!netboy key [' + name + '] does not exist'
            except Exception:
                raise NetBoy.Exception('netboy exception: ' + name)

        def __setattr__(self, name, value):
            # type: (str, Any) -> None
            self[name] = value

    def __init__(self, payload=None, share=None):
        self.payload = payload
        if share:
            s = pycurl.CurlShare()
            s.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_COOKIE)
            s.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_DNS)
            s.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_SSL_SESSION)
            self.share = s
        else:
            self.share = None

    def run(self, payload=None, loop=None):
        real_payload = payload
        if self.payload is None:
            real_payload = payload
        elif payload is None:
            real_payload = self.payload
        else:
            real_payload = self.payload + payload
        ress = run(net_boy(real_payload, self.share), loop=loop)
        obj_ress = []
        for v in ress:
            if type(v) == CurlLoop.CurlException:
                boy = NetBoy.Dict(v.data)
                # boy['payload'] = real_payload
                obj_ress.append(boy)
            elif type(v) == dict:
                boy = NetBoy.Dict(v)
                obj_ress.append(boy)
                # else:
                #     boy = NetBoy.Dict({
                #         'state': 'critical',
                #         'spider': 'pycurl',
                #         'error_code': -1,
                #         'error_desc': "{} - {}".format(type(v), str(v)),
                #         'payload': real_payload
                #     })
                #     obj_ress.append(boy)
        return obj_ress
