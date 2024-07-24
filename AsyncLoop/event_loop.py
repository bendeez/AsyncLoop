import selectors
from queue import Queue
from .task import Task
from .future import Future


class EventLoop:
    running_loop = None

    def __init__(self, max_clients=100):
        EventLoop.running_loop = self
        self.select_clients = []
        self.select = selectors.DefaultSelector()
        self.max_clients = max_clients
        self.client_queue = Queue()

    def run_coro(self, coro):
        # main coro
        try:
            coro.send(None)
            self.run_until_complete(coro)
        except StopIteration:
            pass

    def run_until_complete(self, coro):
        # main coro
        while True:
            self.check_queue_clients()
            if len(self.select_clients) == 0:
                self.run_coro(coro)
                break
            events = self.select.select()
            for key, mask in events:
                client = key.data
                if mask & selectors.EVENT_READ:
                    client.read_callback(loop=self)
                if mask & selectors.EVENT_WRITE:
                    client.write_callback(loop=self)

    def check_queue_clients(self):
        """
            checks for waiting requests/clients when
            the max client level isn't reach
            after a client has been removed from
            select clients
        """
        if len(self.select_clients) < self.max_clients:
            if not self.client_queue.empty():
                client = self.client_queue.get()
                self.select_clients.append(client)
                self.select.register(client.sock, selectors.EVENT_READ | selectors.EVENT_WRITE,
                                     data=client)

    def add_client(self,client):
        fut = Future()
        client.fut = fut
        if len(self.select_clients) < self.max_clients:
            self.select_clients.append(client)
            self.select.register(client.sock, selectors.EVENT_READ | selectors.EVENT_WRITE,
                                 data=client)
        else:
           """
           limits the amount of concurrent clients
           """
           self.client_queue.put(client)
        return fut

    def remove_client(self, client):
        self.select_clients.remove(client)
        self.select.unregister(client.sock)

    def modify_event(self, client, method):
        if method == "r":
            event = selectors.EVENT_READ
        elif method == "w":
            event = selectors.EVENT_WRITE
        else:
            return
        self.select.modify(client.sock, event, data=client)

    @classmethod
    def run(cls, coro, max_clients=100):
        loop = cls(max_clients=max_clients)
        loop.run_coro(coro)

    @staticmethod
    async def gather(*args):
        loop = EventLoop.running_loop
        if loop is not None:
            task = Task(loop=loop)
            await task.gather_futures(*args)
            responses = await task
            return responses
        else:
            raise RuntimeError("No event loop is running")

    @staticmethod
    def create_task(coro):
        loop = EventLoop.running_loop
        if loop is not None:
            task = Task(loop,coro)
            task.start()
            return task
        else:
            raise RuntimeError("No event loop is running")
