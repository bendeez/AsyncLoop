from future import Future

class Task(Future):

    gather_reference = []
    def __init__(self, loop, coro=None):
        super().__init__()
        self.loop = loop
        self.coro = coro
        self.fut_result = {}
        self.results = []
        self.futures = []

    async def start_gather_connections(self,*connections):
        futures = []
        for connection in connections:
            fut = self.loop.add_connection(connection)
            futures.append(fut)
        Task.gather_reference.append(connections[-1].fut) # last gather connection
        responses = [await fut for fut in futures]
        self.set_result(responses)

    async def start_gather_tasks(self,*tasks):
        responses = []
        for task in tasks:
            response = await task
            responses.append(response)
        self.set_result(responses)

    def start(self):
        if self.coro:
            try:
                while True:
                    fut = self.coro.send(None)
                    fut.unblocking_task = self
                    self.futures.append(fut)
                    if fut in Task.gather_reference:
                        Task.gather_reference.remove(fut)
                        break
            except StopIteration as e:
                for fut in e.value:
                    if isinstance(fut,Future):
                        self.results.append(self.fut_result[fut])
                    else:
                        self.results.append(fut) # already has a value
                self.set_result(self.results)
    def update_progress(self,fut,result):
        self.futures.remove(fut)
        self.fut_result[fut] = result
        if len(self.futures) == 0:
            self.start()