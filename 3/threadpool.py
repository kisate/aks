from threading import Thread
import queue

class ThreadPool:
    def __init__(self, max_threads: int, task_callable) -> None:
        self.max_threads = max_threads
        self.task_queue = queue.Queue()
        self.threads = [Thread(target=self._thread_callable) for _ in range(self.max_threads)]
        self.running = False
        self.task_callable = task_callable 

    def start(self):
        self.running = True
        for thread in self.threads:
            thread.start()

    def stop(self):
        self.running = False
        for thread in self.threads:
            thread.join()

    def _thread_callable(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=0.1)
                self.task_callable(*task)
            except queue.Empty:
                pass