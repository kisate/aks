import random
import socket
import time

server_address_port   = ("", 9001)
buffer_size          = 1024

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
try:
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
except Exception as e:
    print(e)


sock.bind(server_address_port)

while True:
    msg, addr = sock.recvfrom(buffer_size)
    msg = msg.decode("utf-8").upper()
    if random.random() > 0.2:
        time.sleep(random.random())
        sock.sendto(msg.encode("utf-8"), addr)
