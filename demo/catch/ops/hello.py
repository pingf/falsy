from demo.catch.serve import CustomException


def get_it(name):
    raise CustomException('haha')
    return {
        'get': name
    }


def post_it(name):
    return {
        'post': name
    }
