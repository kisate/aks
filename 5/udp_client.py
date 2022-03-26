
import socket

server_address_port   = ("", 9001)
buffer_size          = 1024

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
try:
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
except Exception as e:
    print(e)


sock.bind(server_address_port)

while True:
    msgFromServer = sock.recvfrom(buffer_size)
    msg = "Current time: {}".format(msgFromServer[0].decode("utf-8"))
    print(msg, end="\r")