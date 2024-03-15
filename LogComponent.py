import os
import threading
import datetime
from queue import Queue, Empty

class AsyncLogWriter(threading.Thread):
    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.running = True
        self.current_day = datetime.datetime.now().day
        self.log_file = self._get_log_file()
        self.daemon = True

    def run(self):
        while self.running or not self.queue.empty():
            try:
                log_entry = self.queue.get(timeout=0.1)
                if log_entry is None:  # Stop signal received
                    break
                if self._should_rollover():
                    self.log_file.close()
                    self.log_file = self._get_log_file()
                self.log_file.write(log_entry + '\n')
                self.log_file.flush()
            except Empty:
                continue
            except Exception as e:
                print(f"Error writing to log file: {e}")
        if self.log_file:
            self.log_file.close()

    def write(self, message):
        if self._should_rollover():
            self.log_file.close()
            self.log_file = self._get_log_file()
        self.queue.put(message)

    def stop(self, wait=True):
        self.running = False
        if not wait:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except Empty:
                    break
        else:
            self.queue.put(None)  # Send stop signal to the thread
        if wait:
            self.join()

    def _get_log_file(self):
        filename = datetime.datetime.now().strftime("logs/%Y-%m-%d_%H-%M-%S.log")
        self.current_day = datetime.datetime.now().day
        return open(filename, 'a')

    def _should_rollover(self):
        return datetime.datetime.now().day != self.current_day

# ILog interface
class ILog:
    def __init__(self):
        self.writer = AsyncLogWriter()
        self.writer.start()

    def write(self, message):
        self.writer.write(message)

    def stop(self, wait=True):
        self.writer.stop(wait)