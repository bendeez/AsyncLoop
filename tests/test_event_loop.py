from AsyncLoop import EventLoop
from AsyncLoop import AsyncClient
from AsyncLoop import Future
import AsyncLoop

def test_add_client(urls):
    async def add_client():
        client = AsyncClient.create_client(urls[0])
        loop = EventLoop.running_loop
        fut = loop.add_client(client=client)
        assert isinstance(fut, Future)
        assert client.fut == fut
    AsyncLoop.run(add_client())
