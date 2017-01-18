from flask import Flask

PRE_FLASK = 'flask'

def pre_flask(route):
    return '/' + PRE_FLASK + '/' + route.lstrip('/')

flask_app = Flask(__name__)
@flask_app.route(pre_flask('/test'))
def hello_flask():
    return "<h1 style='color:blue'>Hello Flask!</h1>"
