

class Future:
    def __init__(self):
        self.result = None
        self.finished = False
        self.unblocking_task = None
        self.callbacks: list[tuple[callable, tuple, dict]] = []

    def set_result(self, result):
        self.result = result
        self.finished = True
        self.run_callbacks()

    def add_done_callback(self, func, *args, **kwargs):
        self.callbacks.append((func, args, kwargs))

    def run_callbacks(self):
        for callback in self.callbacks:
            func, args, kwargs = callback
            func(*args, **kwargs)

    def __await__(self):
        if not self.finished:
            yield self
        return self.result