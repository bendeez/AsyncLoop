from event_loop import EventLoop
from connection import Connection



loop = EventLoop(max_connections=15)


async def task():
    responses = await loop.gather(*[Connection("https://github.com") for _ in range(10)])
    print(responses)
    return responses

async def main(loop):
    task_1 = loop.create_task(task())
    await task_1


loop.run(main(loop))

