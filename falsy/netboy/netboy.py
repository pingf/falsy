import typing

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
                return '!netboy key [' + name + '] does not exist'
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
            if type(v) is not dict:
                obj_ress.append(NetBoy.Dict({'error': str(v)}))
            else:
                obj_ress.append(NetBoy.Dict(v))
        return obj_ress
