A custom made event loop with async and await syntax,
background tasks, and helper functions, along with concurrent synchronization.

The selectors module makes this all possible.

https://docs.python.org/3/library/selectors.html

![Screenshot 2024-06-21 125920](https://github.com/bendeez/async_event_loop/assets/127566471/378260f9-9145-49ff-b910-366f1204171f)

```python
from AsyncLoop import EventLoop, AsyncClient


async def scrape_other_website():
    results = await EventLoop.gather(*[AsyncClient.request("https://www.google.com/") for _ in range(100)])
    return results

async def scrape_website(url):
    first_result = await scrape_other_website()
    print(first_result)
    second_result = await EventLoop.gather(*[AsyncClient.request(url) for _ in range(20)])
    return second_result

async def main():
    url = "https://github.com/"
    task_1 = EventLoop.create_task(scrape_website(url))
    task_2 = EventLoop.create_task(scrape_other_website())
    result = await EventLoop.gather(task_1,task_2)
    print(result)

EventLoop.run(main())