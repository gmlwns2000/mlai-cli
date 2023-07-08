import subprocess
import sys, os
from ..utils.logging import get_log
log = get_log('iostat.watcher')

class IostatWatcherCallbacks:
    def __init__(self, on_updated=None):
        self.on_updated = on_updated
    
    def updated(self, stats):
        if self.on_updated is not None:
            self.on_updated(stats)

class IostatWatcher:
    def __init__(self, callbacks):
        self.callbacks = callbacks # type: IostatWatcherCallbacks
    
    def start(self):
        self.proc = subprocess.Popen(
            ["iostat", "-d", "1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    
    def sample(self, stats):
        if stats[0][0] == 'Linux': return
        stat_dict = {}
        for stat in stats:
            dev, tps, read_speed, write_speed = stat [:4]
            tps, read_speed, write_speed = float(tps), float(read_speed) * 1024, float(write_speed) * 1024
            stat_dict[dev] = {
                'tps': tps,
                'read_speed': read_speed,
                'write_speed': write_speed,
                'bytes_per_transaction': (read_speed + write_speed) / (tps + 1e-8)
            }
        self.callbacks.updated(stat_dict)
    
    def reading(self):
        stats = []
        for line in iter(self.proc.stdout.readline,''):
            if isinstance(line, bytes):
                line = line.decode()
            line = line.strip()
            if len(line) > 0:
                if line.lower().startswith('device'):
                    self.sample(stats)
                    stats = []
                else:
                    stats.append([s.strip() for s in line.split(' ') if len(s) > 0])

    def join(self):
        try:
            self.reading()
        except KeyboardInterrupt as ex:
            self.proc.kill()
            raise ex