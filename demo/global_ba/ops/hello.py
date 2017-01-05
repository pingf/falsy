import json


def before_all(req, resp):
    resp.body = {
        'method': req.method
    }


def after_all(req, resp, response):
    jbody = json.loads(resp.body)
    jbody.update({'keys': [k for k in response.keys()]})
    resp.body = json.dumps(jbody)


def get_it(name):
    return {
        'name': name
    }


def post_it(name):
    return {
        'name': name
    }


def delete_it(name):
    return {
        'name': name
    }


def put_it(name):
    return {
        'name': name
    }


def patch_it(name):
    return {
        'name': name
    }
