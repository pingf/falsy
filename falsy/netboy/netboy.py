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
        if self.payload is None:
            ress = run(net_boy(payload))
        elif payload is None:
            ress = run(net_boy(self.payload))
        else:
            ress = run(net_boy(self.payload + payload))
        obj_ress = []
        for v in ress:
            if type(v) == CurlLoop.CurlException:
                code = v.code
                desc = v.desc
                data = v.data
                boy = NetBoy.Dict(data)
                boy['error_code'] = code
                boy['error_desc'] = desc
                boy['state'] = 'error'
                obj_ress.append(boy)
            else:
                boy = NetBoy.Dict(v)
                boy['state'] = 'normal'
                obj_ress.append(boy)
        return obj_ress
