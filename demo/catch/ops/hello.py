import json

import falcon

from demo.catch.serve import CustomException


def get_it(name):
    raise CustomException('haha')
    return {
        'get': name
    }


def post_it(name):
    raise CustomException('haha')
    return {
        'post': name
    }


def post_excp(req, resp, error):
    if type(error) == CustomException:
        resp.body = json.dumps({
            'error': 'hahah'
        })
        resp.status = falcon.HTTP_500
        # raise error
