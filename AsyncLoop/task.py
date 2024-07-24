from .future import Future

class Task(Future):

    def __init__(self, loop, coro=None):
        super().__init__()
        self.loop = loop
        self.coro = coro

    async def gather_futures(self,*futures):
        """
            gather futures and tasks
            This task could be inside another task
        """
        responses = [await fut for fut in futures]
        self.set_result(responses)

    def start(self):
        """
            runs task without blocking
        """
        if self.coro:
            try:
                fut = self.coro.send(None)
                fut.add_done_callback(self.start)
            except StopIteration as e:
                self.set_result(e.value)