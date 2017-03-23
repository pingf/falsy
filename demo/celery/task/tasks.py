from time import sleep

from celery import current_task
from celery.task import Task

from demo.celery.task.main import app
# from demo.celery.task.util.context_decorator import log_runtime
from falsy.utils.decorator import suppress_exceptions, log_runtime


@app.task(bind=True)  # , soft_time_limit=5)
def test(self, s):
    print(111111111)
    print(self.request.id)
    # sleep(20)
    # raise Exception('test')
    # add.delay('haha')
    return s + '.'


def catch(et, ev, es):
    print(et, ev)
    return True


@app.task(bind=True, max_retries=3)
@log_runtime(label='hahaha')
@suppress_exceptions(on_error='demo.celery.task.tasks.catch')
def test2(self, s):
    print(self.request.id)
    raise Exception('test')
    # try:
    #     raise Exception('test')
    # except Exception as e:
    #     self.retry(countdown=3)
    # add.delay('haha')
    return s + '.'


@app.task(bind=True)
def cht(self, s):
    print(s)
    print('?????????????????????' * 4)
    return None


@app.task
def on_chord_error(request, exc, traceback):
    print('!' * 400)
    # print('Task {0!r} raised error: {1!r}'.format(request.id, exc))
    return None


@app.task(name='super_task.error_callback')
def error_callback(*args, **kwargs):
    print('error_callback')
    # print(args)
    # print(kwargs)
    return None
    # return 'error'
