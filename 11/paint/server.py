from common import *
import socket


class ServerCanvas(MyCanvas):
    def __init__(self, host: str = "") -> None:
        super().__init__()
        self.host = host

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(0.01)
        self.socket.bind((self.host, PORT))

    def recieve(self):
        msg, _ = self.socket.recvfrom(1024)
        return self.parse_message(msg)

    def update(self):
        super().update()

        try:
            cmd, *points = self.recieve()
        except socket.timeout:
            return

        if cmd == 'quit':
            self.running = False
        elif cmd == 'draw':
            self.draw(*points)


if __name__ == "__main__":
    ServerCanvas().run()