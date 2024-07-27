from .future import Future

class Task(Future):

    def __init__(self, awaitable=None):
        super().__init__()
        self.awaitable = awaitable

    def start(self):
        try:
            if isinstance(self.awaitable, Future):
                fut = self.awaitable
            else:
                fut = self.awaitable.send(None)
            fut.add_done_callback(self.start)
        except StopIteration as e:
            self.set_result(e.value)

async def gather(*futures):
    """
        gather futures and tasks
        This task could be inside another task
    """
    task = Task()
    responses = [await fut for fut in futures]
    task.set_result(responses)
    response = await task
    return response

def create_task(awaitable):
    """
        runs task without blocking
    """
    task = Task(awaitable=awaitable)
    try:
        if isinstance(awaitable, Future):
            fut = awaitable
        else:
            fut = awaitable.send(None)
        fut.add_done_callback(task.start)
        return task
    except StopIteration as e:
        task.set_result(e.value)

