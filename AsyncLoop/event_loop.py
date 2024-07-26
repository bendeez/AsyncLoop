import selectors
from queue import Queue
from .future import Future


class EventLoop:
    running_loop = None

    def __init__(self, max_clients=100):
        EventLoop.running_loop = self
        self.select_clients = []
        self.select = selectors.DefaultSelector()
        self.max_clients = max_clients
        self.client_queue = Queue()
        self.task_queue = Queue()

    def call_soon(self, coro):
        self.task_queue.put(coro)

    def run_coro(self, coro):
        # main coro
        try:
            while True:
                coro.send(None)
                self.run_until_complete()
        except StopIteration:
            pass

    def run_until_complete(self):
        """
            synchronizes event loop
        :return: 
        """""
        while True:
            self.check_queue_clients()
            if len(self.select_clients) == 0:
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

def run(coro, max_clients=100):
    loop = EventLoop(max_clients=max_clients)
    loop.run_coro(coro)
