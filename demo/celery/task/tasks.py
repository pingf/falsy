import json
from time import sleep

from celery import current_task
from celery.task import Task

from demo.celery.task.main import app
# from demo.celery.task.util.context_decorator import log_runtime
from falsy.netboy.curl_loop import CurlLoop
from falsy.netboy.fetch import get_boy
from falsy.netboy.run import run
from falsy.utils.decorator import redirect_exceptions, log_runtime

class ExampleException(Exception):
    pass


def catch(et, ev, es):
    print(et, ev, 'catched')
    return True


@app.task(bind=True, max_retries=3)
@log_runtime(label='hahaha')
@redirect_exceptions(to='demo.celery.task.tasks.catch',exceptions=(Exception))
def crawl(self, urls):
    ress=run(get_boy(urls))
    print(type(ress))
    print(ress)
    for res in ress:
        if type(res) == CurlLoop.Exception:
            print('curl error')
            continue
        if res is None:
            print('res is None')
            continue
        res['data'] = res['data'][:80]
        print(json.dumps(res, indent=2))
    return '>>>'



@app.task(bind=True)
def callback(self, s):
    print(s)
    return None


@app.task
def on_chord_error(request, exc, traceback):
    print('!' * 400)
    # print('Task {0!r} raised error: {1!r}'.format(request.id, exc))
    return True


@app.task(name='super_task.error_callback')
def error_callback(*args, **kwargs):
    print('error_callback')
    # print(args)
    # print(kwargs)
    return None
    # return 'error'

def post_func(payload, resp):
    print('post func called')
    print(resp)
    return resp
