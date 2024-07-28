import socket
import ssl
from urllib.parse import urlparse
from .future import Future
from .event_loop import EventLoop
from typing import Optional

class AsyncClient:

    def __init__(self, host, port, path):
        self.buffer = b""
        self.fut: Optional[Future] = None
        self.sock: Optional[socket.socket] = None
        self.host = host
        self.port = port
        self.path = path
        self.initialize_connection()

    def initialize_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.port == 443:
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(s, server_hostname=self.host)
            self.sock.setblocking(False)
        else:
            self.sock = s
            self.sock.setblocking(False)
        self.sock.connect_ex((self.host, self.port))

    def write_callback(self, loop):
        try:
            self.sock.sendall(f"GET {self.path} HTTP/1.1\r\nHost: {self.host}\r\nConnection: close\r\n\r\n".encode())
            loop.modify_event(self, "r")
        except ssl.SSLError:
            pass
        except BlockingIOError:
            pass

    def read_callback(self, loop):
        try:
            data = self.sock.recv(1024)
            if not data:
                loop.remove_client(self)
                self.fut.set_result(self.buffer.decode())
            self.buffer += data
        except ssl.SSLError:
            pass
        except BlockingIOError:
            pass

    @classmethod
    def create_client(cls,url):
        parsed_url = urlparse(url)
        if parsed_url.hostname.startswith("www."):
            host = parsed_url.hostname[4:]
        else:
            host = parsed_url.hostname
        if parsed_url.scheme == 'http':
            port = 80
        elif parsed_url.scheme == 'https':
            port = 443
        else:
            port = None
        if parsed_url.path == "":
            path = "/"
        else:
            path = parsed_url.path
        return cls(host=host,port=port,path=path)

    @staticmethod
    def request(url):
        client = AsyncClient.create_client(url)
        loop = EventLoop.running_loop
        if loop is not None:
            fut = loop.add_client(client)
            return fut
        else:
            raise RuntimeError("No event loop is running")


