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
                raise NetBoy.Exception('netboy key error: ' + name)
            except Exception:
                raise NetBoy.Exception('netboy exception: ' + name)

        def __setattr__(self, name, value):
            # type: (str, Any) -> None
            self[name] = value

    def __init__(self, payload):
        self.payload = payload

    def run(self, payload=None):
        if payload:
            ress = run(net_boy(self.payload + payload))
        else:
            ress = run(net_boy(self.payload))
        obj_ress = []
        for v in ress:
            obj_ress.append(NetBoy.Dict(v))
        return obj_ress
