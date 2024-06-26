from AsyncLoop import EventLoop
from AsyncLoop import Connection



loop = EventLoop(max_connections=15)

async def scrape_other_website():
    results = await loop.gather(Connection.create_connection("https://www.google.com/"))
    return results

async def scrape_website(url):
    first_result = await scrape_other_website()
    print(first_result)
    second_result = await loop.gather(*[Connection.create_connection(url) for _ in range(10)])
    return second_result

async def main(loop):
    url = "https://github.com/"
    task_1 = loop.create_task(scrape_website(url))
    result = await loop.gather(task_1)
    print(result)

loop.run(main(loop))

