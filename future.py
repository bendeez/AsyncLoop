

class Future:
    def __init__(self):
        self.result = None
        self.finished = False
        self.unblocking_task = None

    def set_result(self, result):
        self.result = result
        self.finished = True

    def __await__(self):
        if not self.finished:
            yield self
        if not self.finished:
            return self
        return self.result