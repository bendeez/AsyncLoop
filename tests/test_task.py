import AsyncLoop
from AsyncLoop import AsyncClient
from AsyncLoop import Task


def test_create_task_return_type():
    async def create_task():
        task = AsyncLoop.create_task(AsyncClient.request("https://google.com"))
        assert isinstance(task, Task)
    AsyncLoop.run(create_task())

def test_gather_in_create_task():
    async def gather_in_create_task():
        response = await AsyncLoop.create_task(AsyncLoop.gather(*[AsyncClient.request("https://google.com") for _
                                                                  in range(10)]))
        assert len(response) == 10
        assert all(r is not None for r in response)
    AsyncLoop.run(gather_in_create_task())