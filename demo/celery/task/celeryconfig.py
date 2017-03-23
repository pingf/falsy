import os
import socket

ENV_IP = os.environ.get('ENV_IP', '127.0.0.1')
ip = ENV_IP
if '.' not in ip:
    ip = [(s.connect(('223.5.5.5', 53)), s.getsockname()[0], s.close()) for s in
          [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

broker_pwd = result_pwd = 'xxxxx'
broker_url = os.environ.get('CELERY_BROKER_URL', 'amqp://dameng:' + broker_pwd + '@' + ip + '/ymon')
result_backend = os.environ.get('CELERY_RESULT_URL', 'redis://:' + result_pwd + '@' + ip + ':6379/2')

task_serializer = 'msgpack'
result_serializer = 'json'
accept_content = ['json', 'msgpack']
timezone = 'UTC'
enable_utc = True
