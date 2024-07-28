from AsyncLoop import AsyncClient
from AsyncLoop import Future
import AsyncLoop



def test_async_client_request_return_type(urls):
    async def async_client_request_return_type():
        fut = AsyncClient.request(urls[0])
        assert isinstance(fut, Future)
        assert not fut.finished

    AsyncLoop.run(async_client_request_return_type())

def test_async_client_request(single_request_task):
    async def async_client_request():
        response = await single_request_task
        assert response is not None
        assert isinstance(response, str)

    AsyncLoop.run(async_client_request())
