import os
import socket

ENV_IP = os.environ.get('ENV_IP', '127.0.0.1')
ip = [(s.connect(('223.5.5.5', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
# if ENV == 'SOC':
#     ip = '192.168.199.221'
if ENV_IP != '127.0.0.1':
    ip = ENV_IP
