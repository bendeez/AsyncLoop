import pytest
import AsyncLoop


@pytest.fixture()
def run():
    def _run(coro):
        AsyncLoop.run(coro)
    return _run

@pytest.fixture()
async def coro():
    return "coro"



