import threading

class Buffer:
    def __init__(self, max_size):
        self.max_size = max_size
        self.items = []
        self.lock = threading.Lock()
    
    def is_full(self):
        return len(self.items) == self.max_size
    
    def add_event(self, event):
        with self.lock:
            if not self.is_full():
                self.items.append(event)
                return True
            return False
        
    def process(self):
        with self.lock:
            data = self.items.copy()
            self.items.clear()
        return data