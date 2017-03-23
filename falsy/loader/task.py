from falsy.loader import func

try:
    from celery import chain, chord, group
except Exception as e:
    raise Exception('celery import failed')


def load(id, args, error_handler=None):
    if args and error_handler:
        return func.load(id).s(args).on_error(func.load(error_handler).s())
    if args and not error_handler:
        return func.load(id).s(args)
    if not args and error_handler:
        return func.load(id).s().on_error(func.load(error_handler).s())
    return func.load(id).s()


def loads(payload):
    if payload.get('type') != 'normal':
        raise Exception('celery task loader only support normal mode')
    tasks = payload.get('tasks', [])
    cts = []
    for task in tasks:
        ops = [load(id, task.get('args'), task.get('on_error')) if i == 0 else load(id, None, task.get('on_error')) for
               i, id in enumerate(task['ids'])]
        cts.append(chain(ops))
    callback = payload.get('callback')
    if callback:
        return chord(header=group(cts), body=func.load(callback).s())
    return group(cts)
