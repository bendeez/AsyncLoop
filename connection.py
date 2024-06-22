import socket
import ssl
from urllib.parse import urlparse

class Connection:

    def __init__(self, url):
        self.buffer = b""
        self.url = url
        self.fut = None
        self.host = None
        self.path = None
        self.port = None
        self.client = None

    def initialize_connection(self):
        self.get_url_details()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.port == 443:
            self.client = ssl.create_default_context().wrap_socket(s, server_hostname=self.host)
            self.client.setblocking(False)
        else:
            self.client = s
            self.client.setblocking(False)
        self.client.connect_ex((self.host, self.port))

    def get_url_details(self):
        parsed_url = urlparse(self.url)
        if parsed_url.hostname.startswith("www."):
            self.host = parsed_url.hostname[4:]
        else:
            self.host = parsed_url.hostname
        if parsed_url.path == "":
            self.path = "/"
        else:
            self.path = parsed_url.path
        if parsed_url.scheme == 'http':
            self.port = 80
        elif parsed_url.scheme == 'https':
            self.port = 443

    def send_request(self, client, mask, loop):
        try:
            self.client.sendall(f"GET {self.path} HTTP/1.1\r\nHost: {self.host}\r\nConnection: close\r\n\r\n".encode())
            loop.modify_event(self, "r")
        except ssl.SSLError:
            pass
        except BlockingIOError:
            pass

    def get_response(self, client, mask, loop):
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