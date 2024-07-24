from .future import Future
from .connection import Connection

class Task(Future):

    def __init__(self, loop, coro=None):
        super().__init__()
        self.loop = loop
        self.coro = coro # some tasks run coros and some tasks gather tasks

    async def gather_tasks(self,*tasks):
        """
            gather connections and tasks
            This task could be inside another task
        """
        futures = []
        print(tasks)
        for task in tasks:
            if isinstance(task,Task):
                futures.append(task)
            elif isinstance(task,Connection):
                fut = self.loop.add_connection(task)
                futures.append(fut)
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