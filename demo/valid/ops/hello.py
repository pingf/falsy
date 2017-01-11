import json

import falcon


def validate_post_name_starts_with_john(payload):
    name = payload['name']
    if not name.startswith('john'):
        return False, 'not starts with john'
    return True


def validate_post_name_more_than_8(payload):
    name = payload['name']
    if len(name) < 8:
        return False, 'less than 8'
    return True


def validate_get_more_than_6(name):
    if len(name) < 6:
        return False, 'less than 6'
    return True


def validate_get_required(name):
    if name is None:
        return False
    return True


def get_it_required(name):
    return {
        'get': name
    }


def get_it(name):
    return {
        'get': name
    }


def before_get_it2(req, resp, name, id):
    if len(name) < 6:
        raise falcon.HTTPInvalidParam('invalid param', name + ':' + 'name less than 6')
    if int(id) < 10:
        raise falcon.HTTPInvalidParam('invalid param', name + ':' + 'id less than 10')


def get_it2(name, id):
    return {
        'hello1': name,
        'hello2': id
    }


def post_it(payload):
    return {
        'post': payload
    }


def delete_it(name):
    return {
        'delete': name
    }


def put_it(name):
    return {
        'put': name
    }


def patch_it(name):
    return {
        'patch': name
    }
