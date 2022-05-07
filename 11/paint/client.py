from common import *
import socket

class ClientCanvas(MyCanvas):
    def __init__(self, host: str = "") -> None:
        super().__init__()
        self.points = []
        self.pressed = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(1)

        self.host = host

    def send_command(self, command: str, *points: List[int]):
        self.socket.sendto(self.make_message(command, points), (self.host, PORT))

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.send_command("quit", [])
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.pressed = True
                x, y = pygame.mouse.get_pos()
                self.points = [x, y]
                self.draw(*self.points)
                self.send_command("draw", *self.points)
 
            elif event.type == pygame.MOUSEBUTTONUP:
                self.points = []
                self.pressed = False
 
            elif event.type == pygame.MOUSEMOTION and self.pressed:
                x, y = pygame.mouse.get_pos()
                self.points = self.points[-2:] + [x, y]
                self.draw(*self.points)
                self.send_command("draw", *self.points)
    

if __name__ == "__main__":
    ClientCanvas().run()