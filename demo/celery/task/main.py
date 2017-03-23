from celery import Celery


app = Celery('ymon', include=['demo.celery.task.tasks'])
app.config_from_object('demo.celery.task.celeryconfig')


if __name__ == '__main__':
    app.start()