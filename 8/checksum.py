class Checksum:

    def __init__(self, base = 8):
        self.base = base
        self.k = base // 8

    def sum(self, data: bytes) -> int:
        result = 0
        for i in range(0, len(data), self.k):
            result = (result + int.from_bytes(data[i:i + self.k], 'big')) % 2 ** self.base

        return result

    def check(self, data: bytes) -> bool:
        result = self.sum(data)
        return result == 2 ** self.base - 1

    def compute(self, data: bytes) -> int:
        result = self.sum(data)
        return 2 ** self.base - 1 - result