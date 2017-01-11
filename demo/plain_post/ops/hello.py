def post_it(name):
    return {
        'post': name
    }


def more_than_8(name):
    if len(name) < 8:
        return False, 'less than 8'
    return True
