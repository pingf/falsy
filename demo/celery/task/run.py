from time import sleep

from celery import group, chain, chord
from celery.result import AsyncResult

# from ymon.loader.task import loads
from .main import app

from falsy.loader import func, task
from .tasks import add, on_chord_error



if __name__ == '__main__':
    payload = {
        'tasks': [
            {"args": "haha", "ids": ["demo.celery.task.tasks.test2"], "on_error": "demo.celery.task.tasks.on_chord_error"},
        ],
        'callback': "demo.celery.task.tasks.callback"
    }
    res = task.loads(payload).delay()
    sleep(3)
    print(res.result, res.state)
    print(res, type(res), dir(res))
    print(res.id)
