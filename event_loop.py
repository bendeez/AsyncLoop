import selectors
from queue import Queue
from task import Task
from future import Future


class EventLoop:

    def __init__(self, max_connections=100):
        self.select_connections = []
        self.select = selectors.DefaultSelector()
        self.max_connections = max_connections
        self.connection_queue = Queue()

    def run(self, coro):
        try:
            coro.send(None)
            self.run_until_complete(coro)
        except StopIteration:
            pass

    def run_until_complete(self, coro):
        while True:
            self.check_queue_connections()
            if len(self.select_connections) == 0:
                self.run(coro)
                break
            events = self.select.select()
            for key, mask in events:
                connection = key.data
                client = key.fileobj
                if mask & selectors.EVENT_READ:
                    connection.get_response(client, mask, self)
                if mask & selectors.EVENT_WRITE:
                    connection.send_request(client, mask, self)

    def check_queue_connections(self):
        if len(self.select_connections) < self.max_connections:
            if not self.connection_queue.empty():
                connection = self.connection_queue.get()
                if connection.fut:
                    self.add_connection(connection,connection.fut)
                else:
                    self.add_connection(connection)

    async def gather(self, *args):
        task = Task(loop=self)
        await task.gather_tasks(*args)
        responses = await task
        return responses

    def create_task(self, coro):
        task = Task(self,coro)
        task.start()
        return task

    def add_connection(self, connection, fut=None,in_gather=False):
        """
            in gather=False makes it so we know to set the
            task's fut reference to synchronize the task
            in between print statements

            in_gather=True means that the setting
            the task's fut reference will be set
            in the task's gather function because only
            the last future/connection of the gather function
            needs to be set to the task's fut reference
        """
        if fut is None:
            fut = Future()
            connection.fut = fut
        if not in_gather:
            Task.fut_reference.append(fut)
        connection.initialize_connection()
        if len(self.select_connections) < self.max_connections:
            self.select_connections.append(connection)
            self.select.register(connection.client, selectors.EVENT_READ | selectors.EVENT_WRITE,
                                 data=connection)
        else:
            self.connection_queue.put(connection)
        return fut

    def remove_connection(self, connection):
        self.select_connections.remove(connection)
        self.select.unregister(connection.client)

    def modify_event(self, connection, method):
        if method == "r":
            event = selectors.EVENT_READ
        elif method == "w":
            event = selectors.EVENT_WRITE
        else:
            return
        self.select.modify(connection.client, event, data=connection)
