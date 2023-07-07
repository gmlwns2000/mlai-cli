import functools

def log(*args, **kwargs):
    caller=kwargs.get('caller', '?')
    sep=kwargs.get('sep', ' ')
    args = [str(a) for a in args]
    print('[MLAI-CLI:{}] {}'.format(caller, sep.join(args)))
    
def get_log(caller):
    return functools.partial(log, caller=caller)