from dataclasses import dataclass, field
import getpass
import socket
import re
import collections
from typing import List

from ..utils.logging import get_log
from ..secrets.cluster_def import CLUSTER
log = get_log('survey')

try:
    import paramiko
    PARAKIMO_IMPORTED = True
except:
    PARAKIMO_IMPORTED = False

@dataclass
class SurveyResult:
    succ: bool = False
    gpus: List[str] = field(default_factory=list)
    gpu_summary: str = ""

class SurveyApp:
    def __init__(self):
        self.timeout = 10
    
    def survey(self, addr: str):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                addr, 
                username=self.username, 
                password=self.password,
                timeout=self.timeout,
            )
        except:
            return SurveyResult(succ=False)
        
        result = SurveyResult(succ=False)
        
        # stdin, stdout, stderr = ssh.exec_command(r"""sudo dmidecode | grep -A10 '^System Information'""", timeout=self.timeout, get_pty=True)
        # stdin.write(self.password + '\n')
        # stdin.flush()
        # log(stderr.read().decode())
        # log(stdout.read().decode())
        
        try:
            _, stdout, _ = ssh.exec_command(r"""nvidia-smi -L""", timeout=self.timeout)
            decoded = stdout.read().decode()
        except paramiko.SSHException:
            return result
        
        self.decode_gpu_list(result, decoded)
        
        result.succ = True
        return result
    
    def decode_gpu_list(self, result:SurveyResult, decoded:str):
        gpu_names = list(map(lambda x: x.lower().strip(), re.findall(r'GPU \d+: ([^\(]+)', decoded)))
        result.gpus = gpu_names
        counter = collections.Counter(gpu_names)
        log(counter)
        result.gpu_summary = "\n".join([f'{item[0].capitalize()} * {item[1]}' for item in counter.most_common()])
    
    def check_libraries(self):
        assert PARAKIMO_IMPORTED, 'pip install parakimo'
    
    def main(self):
        log('SurveyApp')
        
        self.username = input('user >>> ')
        self.password = getpass.getpass('password >>> ')
        
        results = {}
        
        for cluster in CLUSTER:
            log('survey', cluster)
            result = self.survey(cluster.address)
            if result.succ:
                results[cluster.name] = result
        
        print(*[f'{item[0]},{item[1].gpu_summary}' for item in results.items()], sep='\n')