from falsy.jlog.jlog import JLog
from falsy.loader import func, task

log = JLog().bind()


def post_it(name):
    log.debug('post it')
    payload = {
        'type': 'normal',
        'tasks': [
            {
                "args": [
                    {
                        'url': 'http://www.baidu.com',
                        'dns_servers': '114.114.114.114',
                        'post_func': 'demo.celery.task.tasks.post_func'
                    },
                    {
                        'url': 'http://www.douban.com',
                        'dns_servers': '114.114.114.114'
                    },
                ],
                "ids": ["demo.celery.task.tasks.crawl"],
            },
            {
                "args": [
                    {
                        'url': 'http://www.google.com',
                    },
                ],
                "ids": ["demo.celery.task.tasks.crawl"],
            },
        ],
        'callback': "demo.celery.task.tasks.callback"
    }
    res = task.loads(payload).delay()
    return {
        'post': name
    }
