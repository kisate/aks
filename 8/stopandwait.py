import random
import socket
from typing import Tuple
from checksum import Checksum

class SocketWrapper:
    def __init__(self, timeout):
        self.checksum = Checksum()
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.settimeout(timeout)
        self.timeout = timeout
        self.header_size = 2
        self.ack_size = 3
        self.packet_size = 1024

    def add_header(self, data: bytes, number: int) -> bytes:
        data = bytes([number]) + data
        cs = self.checksum.compute(data)
        return bytes([cs]) + data

    def build_packet(self, data: bytes, number: int) -> bytes:
        return self.add_header(data, number)

    def build_ack(self, number: int) -> bytes:
        return self.add_header(b"ACK", number)

    def send(self, data: bytes, addr):
        number = 1
        for i in range(0, len(data), self.packet_size):
            number = (number + 1) % 2
            packet = self.build_packet(data[i:i+self.packet_size], number)
            while True:
                self.soc.sendto(packet, addr)
                try:
                    ack, _ = self.soc.recvfrom(self.header_size + self.ack_size)
                    if random.random() < 0.3:
                        raise socket.timeout()
                    if ack == self.build_ack(number):
                        print(f'ACK ({number}) received.')
                        break
                except socket.timeout:
                    print('timed out')
                    continue

    def recv(self, remaining_data) -> bytes:
        next_number = 0
        received = []

        while remaining_data > 0:
            try:
                packet, addr = self.soc.recvfrom(self.header_size + self.packet_size)
                _, new_number, *new_data = packet

                if random.random() < 0.3:
                    raise socket.timeout()

                if new_number == next_number:
                    if not self.checksum.check(packet):
                        print('incorrect checksum')
                        continue
                    next_number = (new_number + 1) % 2
                    received.extend(new_data)
                    remaining_data -= len(new_data)
                    print(f'Packet with ({new_number}) received: {len(new_data)}')

                self.soc.sendto(self.build_ack(new_number), addr)

            except socket.timeout:
                print('timed out')
                continue

        return bytes(received)