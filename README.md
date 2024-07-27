A custom made event loop with async and await syntax,
background tasks, and helper functions, along with concurrent synchronization.

The selectors module makes this all possible.

https://docs.python.org/3/library/selectors.html

![Screenshot 2024-06-21 125920](https://github.com/bendeez/async_event_loop/assets/127566471/378260f9-9145-49ff-b910-366f1204171f)

```python
import AsyncLoop
from AsyncLoop import AsyncClient


async def scrape_other_website():
    results = await AsyncLoop.gather(*[AsyncClient.request("https://youtube.com") for _ in range(10)])
    return results

async def scrape_website(url):
    first_result = await scrape_other_website()
    print(first_result)
    second_result = await AsyncLoop.gather(*[AsyncClient.request(url) for _ in range(20)])
    return second_result

async def main():
    url = "https://github.com/"
    task_1 = AsyncLoop.create_task(scrape_website(url))
    print(task_1)
    task_2 = AsyncLoop.create_task(scrape_other_website())
    print(task_2)
    result = await AsyncLoop.gather(task_1,task_2)
    print(result)

AsyncLoop.run(main(), max_clients=100)
