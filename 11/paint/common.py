import pygame
from typing import List

WIDTH = 600
HEIGHT = 400
THICKNESS = 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

PORT = 9003


class MyCanvas:
    def __init__(self) -> None:
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Remote Paint')
        self.window.fill(WHITE)
        pygame.display.update()

        self.running = False

    def draw(self, *points: List[int]):
        if points:
            if len(points) == 2:
                x, y = points
                pygame.draw.circle(self.window, BLACK, (x, y), THICKNESS)
            else:
                x1, y1, x2, y2 = points
                pygame.draw.line(self.window, BLACK, (x1, y1), (x2, y2), THICKNESS + 1)


    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break

    def run(self):
        self.running = True
        while self.running:
            self.update()
            pygame.display.update()
        pygame.quit()

    @staticmethod
    def parse_message(msg: bytes):
        msg = msg.decode("utf-8")
        cmd, *parts = msg.split()
        parts = [int(x) for x in parts]
        return cmd, *parts

    @staticmethod
    def make_message(command: str, points: List[int]) -> bytes:
        msg = " ".join(str(x) for x in points)
        msg = f"{command} {msg}"
        return msg.encode("utf-8")