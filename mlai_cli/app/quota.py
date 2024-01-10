import functools
import getpass
import subprocess
import os
import sys

from ..utils.logging import log
from ..secrets.cluster_def import STORAGE_CLUSTER

log = functools.partial(log, caller='quota.main')

class QuotaApp:
    def __init__(self):
        pass
    
    def main(self):
        if len(sys.argv) >= 3:
            username = sys.argv[2]
        else:
            username = os.getlogin()
        password = getpass.getpass(f'Password of {username}: ')
        
        for storage_node in STORAGE_CLUSTER:
            log('Try to log in', storage_node)
            ssh = subprocess.Popen(
                ['ssh', '-tt', f'{username}@{storage_node.address}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            ssh.stdin.write(f'{password}\n\n'.encode())
            ssh.stdin.flush()
            log(f'Logged in {username}@{storage_node.address}')
            ssh.wait()