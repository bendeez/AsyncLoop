import pytest
from AsyncLoop import AsyncClient
import AsyncLoop


@pytest.fixture()
def urls():
    return ["https://google.com","https://github.com"]

@pytest.fixture()
def single_request_task(urls):
    async def _single_request_task():
        response = await AsyncClient.request(urls[0])
        return response
    return _single_request_task()


@pytest.fixture()
def gather_task(urls):
    async def _gather_task():
        response = await AsyncLoop.gather(*[AsyncClient.request(url) for url in urls])
        return response
    return _gather_task()