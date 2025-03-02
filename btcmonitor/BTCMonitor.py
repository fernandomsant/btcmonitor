import threading
from queue import Queue
from btcmonitor import Buffer
import time

class BTCMonitor:
    def __init__(self, buffer_size, storage):
        self.buffer_size = buffer_size
        self.buffer_queue = Queue()
        self.current_buffer = Buffer(buffer_size)
        self.lock = threading.Lock()
        self.storage = storage
        self.storage.connect_to_storage()
        self.is_started = False

    def add_event_to_buffer(self, event):
        if not self.current_buffer.add_event(event):
            self.buffer_queue.put(self.current_buffer)
            self.current_buffer = Buffer(self.buffer_size)
            self.current_buffer.add_event(event)
    
    def process_buffer_queue(self):
        while True:
            if not self.buffer_queue.empty():
                while not self.buffer_queue.empty():
                    buffer = self.buffer_queue.get()
                    self.process_buffer(buffer)
            else:
                time.sleep(0.5)
    
    def process_buffer(self, buffer):
        for item in buffer.items:
            self.storage.push(item)
    
    def add_event(self, event):
        if self.is_started:
            self.add_event_to_buffer(event)
        else:
            raise Exception("BTCMonitor is not started")
    
    def start(self):
        self.is_started = True
        threading.Thread(target=self.process_buffer_queue, daemon=True).start()