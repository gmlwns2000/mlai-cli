from ..gpustat.gpu_stat import GpuStat
from ..utils.logging import get_log
import argparse
import sys
log = get_log('freegpu')

class FreeGpuApp:
    def __init__(self) -> None:
        self.monitor = GpuStat()
    
    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--fp32', default=0, type=float, help='Limit lower bound of FP32 TFLOPs')
        parser.add_argument('--bf16', default=0, type=float, help='Limit lower bound of BF16 TFLOPs. You can use this to filter out older gpu than Ampere.')
        parser.add_argument('--fp16', default=0, type=float, help='Limit lower bound of FP16 TFLOPs')
        parser.add_argument('--mem', default=0, type=float, help='Limit lower bound of VRAM in GB')
        args = parser.parse_args(sys.argv[2:])
        
        cluster, gpus = self.monitor.query_free_gpus(
            mem_thresh=args.mem,
            fp32_thresh=args.fp32,
            fp16_thresh=args.fp16,
            bf16_thresh=args.bf16,
        )
        
        n_gpus = sum([len(node.instances) for node in cluster])
        gpus = sorted(gpus, key=lambda gpu: gpu.spec.fp16_tflops)
        for gpu in gpus:
            log(gpu)
        log(len(gpus), '/', n_gpus, 'are free')