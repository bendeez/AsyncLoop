A custom made event loop with async and await syntax,
background tasks, and custom functions.

The selectors module makes this all possible.

https://docs.python.org/3/library/selectors.html

![Screenshot 2024-06-21 125920](https://github.com/bendeez/async_event_loop/assets/127566471/378260f9-9145-49ff-b910-366f1204171f)

```python
from event_loop import EventLoop
from connection import Connection



loop = EventLoop(max_connections=15)

async def scrape_other_website():
    results = await loop.gather(Connection("https://www.google.com/"))
    return results

async def scrape_website(url):
    first_result = await scrape_other_website()
    print(first_result)
    second_result = await loop.gather(*[Connection(url) for _ in range(10)])
    return second_result

async def main(loop):
    url = "https://github.com/"
    task_1 = loop.create_task(scrape_website(url))
    result = await loop.gather(task_1)
    print(result)

loop.run(main(loop))

