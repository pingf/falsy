from falsy.jlog.jlog import JLog
from falsy.loader import func, task

log = JLog().bind()

def post_it(name):
    log.debug('post it')
    payload = {
        'type': 'normal',
        'tasks': [
            {"args": "haha", "ids": ["demo.celery.task.tasks.test2"], "on_error": "demo.celery.task.tasks.on_chord_error"},
            {"args": "haha", "ids": ["demo.celery.task.tasks.test"], "on_error": "demo.celery.task.tasks.on_chord_error"},
        ],
        'callback': "demo.celery.task.tasks.cht"
    }
    res = task.loads(payload).delay()
    return {
        'post': name
    }



