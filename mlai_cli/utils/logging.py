def log(*args, caller='?', sep=' '):
    print(f'[MLAI-CLI:{caller}] {sep.join(args)}')