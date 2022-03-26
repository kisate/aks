
import socket

serverAddressPort   = ("127.0.0.1", 9001)
bufferSize          = 1024


UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPClientSocket.sendto("Hello UDP Server".encode("utf-8"), serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)

while True:
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Current time: {}".format(msgFromServer[0].decode("utf-8"))
    print(msg, end="\r")