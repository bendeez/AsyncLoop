import AsyncLoop
from AsyncLoop import Task


def test_create_task_return_value(run,coro):
    async def create_task():
        task = AsyncLoop.create_task(coro)
        assert isinstance(task,Task)
    run(create_task())