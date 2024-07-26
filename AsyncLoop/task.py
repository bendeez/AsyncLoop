from .future import Future

class Task(Future):

    def __init__(self, coro=None):
        super().__init__()
        self.coro = coro

    def start(self):
        try:
            fut = self.coro.send(None)
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

def create_task(coro):
    """
        runs task without blocking
    """
    task = Task(coro=coro)
    try:
        fut = task.coro.send(None)
        fut.add_done_callback(task.start)
        return task
    except StopIteration as e:
        task.set_result(e.value)

