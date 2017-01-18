import tornado.web
import tornado.wsgi


class TornadoHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("<h1 style='color:blue'>Hello Tornado!</h1>")
PRE_TORNADO = 'tornado'


def pre_tornado(route):
    return '/' + PRE_TORNADO + '/' + route.lstrip('/')

application = tornado.web.Application([
    (pre_tornado('test'), TornadoHandler),
])
tornado_app = tornado.wsgi.WSGIAdapter(application)
