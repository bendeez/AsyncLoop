import socket
import ssl
from urllib.parse import urlparse
from .future import Future
from typing import Optional

class Connection:

    def __init__(self, host, port, path):
        self.buffer = b""
        self.fut: Optional[Future] = None
        self.client: Optional[socket.socket] = None
        self.host = host
        self.port = port
        self.path = path
        self.connection_callback = self.initialize_connection
        self.write_callback = self.send_request
        self.read_callback = self.get_response
        """
            None values will be set
            when scheduled on the event loop
        
            callback attributes allow
            for consistent names for the event
            loop to call whenever they're scheduling
            or being notified by the selectors module
            aka semantics
        """

    def initialize_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.port == 443:
            context = ssl.create_default_context()
            self.client = context.wrap_socket(s, server_hostname=self.host)
            self.client.setblocking(False)
        else:
            self.client = s
            self.client.setblocking(False)
        self.client.connect_ex((self.host, self.port))

    def send_request(self, loop):
        try:
            self.client.sendall(f"GET {self.path} HTTP/1.1\r\nHost: {self.host}\r\nConnection: close\r\n\r\n".encode())
            loop.modify_event(self, "r")
        except ssl.SSLError:
            pass
        except BlockingIOError:
            pass

    def get_response(self, loop):
        try:
            data = self.client.recv(1024)
            if not data:
                self.fut.set_result(self.buffer.decode())
                if self.fut.unblocking_task is not None:
                    task = self.fut.unblocking_task
                    task.update_progress(self.fut,self.buffer.decode())
                loop.remove_connection(self)
            self.buffer += data
        except ssl.SSLError:
            pass
        except BlockingIOError:
            pass

    @classmethod
    def create_connection(cls,url):
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
