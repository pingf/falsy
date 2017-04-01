#run woker

```
python -m demo.celery.task.main worker -l info -n w1
```


#trigger

```
gunicorn -b 0.0.0.0:8005 demo.celery.serve:api  -w 1 --reload
``