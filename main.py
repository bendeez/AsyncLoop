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

