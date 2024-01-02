import json
import requests
from urllib import parse
import time

from ..utils.logging import get_log
log = get_log('gpu_stat')
from ..secrets.cluster_def import CLUSTER, NodeDef, GRAFANA_NODE_ADDR

class GpuSpec:
    def __init__(self, fp32_tflops, fp16_tflops, bf16_tflops, mem_gb):
        self.fp32_tflops = fp32_tflops
        self.fp16_tflops = fp16_tflops
        self.bf16_tflops = bf16_tflops
        self.mem_gb = mem_gb
    
    def __repr__(self):
        return "GpuSpec(fp32={}, fp16={}, bf16={}, vram={})".format(self.fp32_tflops, self.fp16_tflops, self.bf16_tflops, self.mem_gb)

GPU_SPECS = {
    'RTX4090': GpuSpec(
        fp32_tflops=82.6,
        fp16_tflops=256,
        bf16_tflops=256,
        mem_gb=24
    ),
    'RTXA5000': GpuSpec(
        fp32_tflops=27.7,
        fp16_tflops=111.0,
        bf16_tflops=111.0,
        mem_gb=24
    ),
    'RTXA4000': GpuSpec(
        fp32_tflops=19.2,
        fp16_tflops=76.0,
        bf16_tflops=76.0,
        mem_gb=16
    ),
    'RTX3090': GpuSpec(
        fp32_tflops=35.7,
        fp16_tflops=142,
        bf16_tflops=142,
        mem_gb=24
    ),
    'RTX3080': GpuSpec(
        fp32_tflops=34.1,
        fp16_tflops=119,
        bf16_tflops=119,
        mem_gb=10
    ),
    'RTX8000': GpuSpec(
        fp32_tflops=16.3,
        fp16_tflops=65,
        bf16_tflops=0,
        mem_gb=48
    ),
    'TITANRTX': GpuSpec(
        fp32_tflops=16.3,
        fp16_tflops=65,
        bf16_tflops=0,
        mem_gb=24
    ),
    '2080Ti': GpuSpec(
        fp32_tflops=13.6,
        fp16_tflops=57,
        bf16_tflops=0,
        mem_gb=11
    ),
    '1080Ti': GpuSpec(
        fp32_tflops=11.5,
        fp16_tflops=11.5,
        bf16_tflops=0,
        mem_gb=11
    ),
    'NVIDIA TITAN X (Pascal)': GpuSpec(
        fp32_tflops=10.97 ,
        fp16_tflops=10.97 ,
        bf16_tflops=0,
        mem_gb=12
    ),
    'TITANXp': GpuSpec(
        fp32_tflops=12.15,
        fp16_tflops=12.15,
        bf16_tflops=0,
        mem_gb=12
    ),
    'TITANX': GpuSpec(
        fp32_tflops=6.691,
        fp16_tflops=6.691,
        bf16_tflops=0,
        mem_gb=12
    ),
}

class GpuNode:
    def __init__(
        self, 
        node_def, #type: NodeDef
    ):
        self.desc = node_def
        self.instances = []
    
    def __repr__(self):
        return "GpuNode({}, n_gpus={})".format(self.desc.name, len(self.instances))
    
    def update(self):
        self.instances = []
        query_str = \
            """label_replace( 100*(nvidia_gpu_memory_used_bytes{{instance="{node_name}:9445"}} / nvidia_gpu_memory_total_bytes{{instance="{node_name}:9445"}}) , "name", "$2$3", "name", "(.+) (\\\\w+) (\\\\w+)$")"""
        query_str = query_str.format(node_name=self.desc.grafana_name)
        query_str = parse.quote(query_str)
        query_url = \
            """/api/datasources/proxy/1/api/v1/query_range?"""\
            """query={query_str}&"""\
            """start={start_time}&"""\
            """end={end_time}&"""\
            """step=5"""
        current_time = int(time.time())
        query_url = query_url.format(query_str=query_str, end_time=current_time, start_time=current_time-0)
        query_url = 'http://{}:3000'.format(GRAFANA_NODE_ADDR) + query_url
        # log(query_url)
        
        res = requests.get(query_url)
        data_mem_usage = res.json()["data"]["result"]
        # log(json.dumps(data_mem_usage, indent=2))
        
        num_gpus = len(data_mem_usage)
        gpus = []
        for i in range(num_gpus):
            # {
            #     "metric": {
            #     "instance": "ai21:9445",
            #     "job": "gpu",
            #     "minor_number": "2",
            #     "name": "RTXA5000",
            #     "uuid": "GPU-45ffec0d-eb4c-23e8-b161-055b11fa3304"
            #     },
            #     "values": [
            #     [
            #         1688804093,
            #         "1.311879172773164"
            #     ]
            #     ]
            # }
            data = data_mem_usage[i]
            gpu = GpuInstance(
                self,
                name=data['metric']['name'],
                mem_util=float(data['values'][0][-1]),
                compute_util=0.0,
                index=int(data['metric']['minor_number']),
            )
            gpus.append(gpu)
        
        self.instances = gpus

class GpuInstance:
    node = None # type: GpuNode
    name = "H100"
    mem_util = 100.0
    compute_util = 0.0
    index = 0
    spec = None # type: GpuSpec
    
    def __init__(self, node, name, mem_util, compute_util, index):
        self.node = node # type: GpuNode
        self.name = name
        self.mem_util = mem_util
        self.compute_util = compute_util
        self.index = index
        self.spec = GPU_SPECS.get(self.name, None)
    
    def __repr__(self):
        return "GpuInstance(node={}, index={}, name={}, mem={:.1f}%, compute={:.1f}%, spec={})".format(
            self.node,
            self.index,
            self.name,
            self.mem_util,
            self.compute_util,
            self.spec
        )

class GpuStat:
    def __init__(self):
        pass
    
    def query(self):
        clusters = []
        for c in CLUSTER:
            clusters.append(GpuNode(c))
        for c in clusters:
            c.update()
        return clusters

    def query_free_gpus(
        self, 
        mem_util_thresh=5, 
        comput_util_thresh=80,
        fp32_thresh=0,
        fp16_thresh=0,
        bf16_thresh=0,
        mem_thresh=0,
    ):
        cluster = self.query()
        gpus = []
        for node in cluster:
            for gpu in node.instances:
                gpu = gpu #type: GpuInstance
                if gpu.compute_util <= comput_util_thresh and \
                    gpu.mem_util <= mem_util_thresh and \
                    gpu.spec.fp16_tflops >= fp16_thresh and \
                    gpu.spec.fp32_tflops >= fp32_thresh and \
                    gpu.spec.bf16_tflops >= bf16_thresh and \
                    gpu.spec.mem_gb >= mem_thresh:
                    gpus.append(gpu)
        return cluster, gpus

if __name__ == '__main__':
    monitor = GpuStat()
    
    log('# test query')
    n_gpus = 0
    cluster = monitor.query()
    for node in cluster:
        log(node)
        for gpu in node.instances:
            log(" -", gpu)
            n_gpus += 1
        if len(node.instances) == 0:
            log(" - No gpus")
    
    log('# test query free gpus')
    _, gpus = monitor.query_free_gpus(fp16_thresh=13, mem_thresh=11)
    for gpu in gpus:
        log(gpu)
    log('{}/{} gpus are free'.format(len(gpus), n_gpus))