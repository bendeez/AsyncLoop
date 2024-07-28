import AsyncLoop
from AsyncLoop import AsyncClient
from AsyncLoop import Task
import inspect


def test_create_task_return_type(urls):
    async def create_task():
        task = AsyncLoop.create_task(AsyncClient.request(urls[0]))
        assert isinstance(task, Task)
        assert not task.finished
    AsyncLoop.run(create_task())

def test_gather_in_create_task(urls, gather_task):
    async def gather_in_create_task():
        task = AsyncLoop.create_task(gather_task)
        response = await task
        assert len(response) == len(urls)
        assert len(set(response)) == len(urls) # check if responses are unique
        assert task.finished
        assert all(r is not None for r in response)
    AsyncLoop.run(gather_in_create_task())


def test_gather_tasks_in_create_task(urls, single_request_task, gather_task):
    async def gather_tasks_in_create_task():
        task = AsyncLoop.create_task(AsyncLoop.gather(AsyncLoop.create_task(gather_task),
                                          AsyncLoop.create_task(single_request_task)))
        response = await task
        assert task.finished
        assert len(response) == 2
        assert isinstance(response[0], list)
        assert len(response[0]) == len(urls)
        assert len(set(response[0])) == len(urls) # check if responses are unique
        assert isinstance(response[1], str)

    AsyncLoop.run(gather_tasks_in_create_task())

def test_gather_tasks(urls, single_request_task, gather_task):
    async def gather_tasks():
        response = await AsyncLoop.gather(AsyncLoop.create_task(gather_task),AsyncLoop.create_task(single_request_task))
        assert len(response) == 2
        assert isinstance(response[0],list)
        assert len(response[0]) == len(urls)
        assert len(set(response[0])) == len(urls)  # check if responses are unique
        assert all(r is not None for r in response[0])
        assert isinstance(response[1],str)

    AsyncLoop.run(gather_tasks())

def test_gather_return_type(single_request_task, gather_task):
    async def gather_return_type():
        response = AsyncLoop.gather(AsyncLoop.create_task(gather_task),
                                    AsyncLoop.create_task(single_request_task))
        assert inspect.iscoroutine(response)

    AsyncLoop.run(gather_return_type())



