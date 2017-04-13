import typing

from falsy.netboy.curl_loop import CurlLoop
from falsy.netboy.fetch import net_boy
from falsy.netboy.run import run


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
                return None#'!netboy key [' + name + '] does not exist'
            except Exception:
                raise NetBoy.Exception('netboy exception: ' + name)

        def __setattr__(self, name, value):
            # type: (str, Any) -> None
            self[name] = value

    def __init__(self, payload=None):
        self.payload = payload

    def run(self, payload=None):
        real_payload = payload
        if self.payload is None:
            real_payload = payload
        elif payload is None:
            real_payload = self.payload
        else:
            real_payload = self.payload+payload
        ress = run(net_boy(real_payload))
        obj_ress = []
        for v in ress:
            if type(v) == CurlLoop.CurlException:
                boy = NetBoy.Dict(v.data)
                boy['error_code'] = v.code
                boy['error_desc'] = v.desc
                boy['state'] = 'error'
                obj_ress.append(boy)
            elif type(v) == dict:
                boy = NetBoy.Dict(v)
                boy['state'] = 'normal'
                obj_ress.append(boy)
            else:
                print('!!!error!!!')
                obj_ress.append(str(v))
        return obj_ress
