import argparse
from audioop import add
from datetime import datetime
from re import A
import socket
import time
from threading import RLock
from threading import Thread
import os

class Storage:
    def __init__(self, port: int, message_interval: float, timeout: int) -> None:
        self.others = {}
        self.message_interval = message_interval
        self.timeout = timeout
        self.lock = RLock()

        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.bind(("", port))

        self.running = True

    def update(self, msg: str, addr):
        self.lock.acquire()
        now = time.time()

        if msg == "closed":
            del self.others[addr]
        else:
            if addr in self.others:
                self.others[addr] = now
            elif msg == "started":
                self.others[addr] = now

            if msg == "alive":
                self.others[addr] = now
            elif msg == "started":
                self.others[addr] = now
                self.send_alive(addr)

        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_others()

        self.lock.release()
            

    def send_alive(self, addr):
        self.sock.sendto("alive".encode("utf-8"), addr)


    def send_started(self):
        for port in range(1000, 65536):
            self.sock.sendto("started".encode("utf-8"), ("255.255.255.255", port))

    def close(self):
        self.lock.acquire()
        for addr in self.others:
            self.sock.sendto("closed".encode("utf-8"), addr)
        self.lock.release()
        self.sock.close()
        self.running = False

    def listen(self):
        msg, addr = self.sock.recvfrom(1024)
        self.update(msg, addr)

    def send(self):
        while self.running:
            self.lock.acquire()
            for addr in self.others:
                self.send_alive(addr)

            now = time.time()
            for addr, last_seen in list(self.others.items()):
                if now - last_seen > self.timeout * self.message_interval:
                    del self.others[addr]
            self.lock.release()
            time.sleep(self.message_interval)

    def print_others(self):
        for addr, port in self.others:
            print(f"{addr}:{port}")




def send_alive(sock: socket, addr):
    sock.sendto("alive".encode("utf-8"), addr)

def main(port: int):

    storage = Storage(port, 0.5, 3)
    storage.send_started()

    send_thread = Thread(target=storage.send)
    send_thread.start()

    try:
        while True:
            msg, addr = storage.sock.recvfrom(1024)
            storage.update(msg.decode("utf-8"), addr)
    except KeyboardInterrupt:
        print("shutting down")

    storage.close()
    send_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    main(args.port)
