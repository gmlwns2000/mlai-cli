import functools
from ...utils.logging import log
log = functools.partial(log, caller='iostat.main')
from ...utils import human_readable
from ...iostat.watcher import IostatWatcher, IostatWatcherCallbacks

class RunningAverage:
    def __init__(self, count=100):
        self.count = count
        self.buffers = {}
    
    def get(self, name='default'):
        buf = self.buffers.get(name, [])
        return sum(buf) / (len(buf) + 1e-8)
    
    def update(self, sample, name='default'):
        buffer = self.buffers.get(name, [])
        buffer.append(sample)
        if len(buffer) > self.count: buffer.pop(0)
        self.buffers[name] = buffer
        return self.get(name=name)

class IostatWatcherApp:
    def __init__(self):
        callbacks = IostatWatcherCallbacks(
            on_updated=self.on_updated
        )
        self.watcher = IostatWatcher(callbacks=callbacks)
        self.filter = RunningAverage()
    
    def on_updated(self, stats):
        device_activities = [(k, v['read_speed'] + v['write_speed']) for k, v in stats.items()]
        most_active_device = sorted(device_activities, key = lambda it: it[1], reverse=True)[0][0]
        stat = stats[most_active_device]
        log(
            most_active_device, 
            'per_transaction:', human_readable(self.filter.update(stat['bytes_per_transaction'], 'bpt'), unit='B/T'),
            'read:', human_readable(self.filter.update(stat['read_speed'], 'r'), unit='B/S'),
            'write:', human_readable(self.filter.update(stat['write_speed'], 'w'), unit='B/S'),
        )
    
    def main(self):
        self.watcher.start()
        self.watcher.join()