def log(*args, **kwargs):
    caller=kwargs.get('caller', '?')
    sep=kwargs.get('sep', ' ')
    print('[MLAI-CLI:{}] {}'.format(caller, sep.join(args)))