import socket
import threading
from datetime import datetime
import time

port   = 9001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

try:
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
except Exception as e:
    print(e)


print("UDP server up and listening")

 
try:
    while True:
        sock.sendto(datetime.now().strftime("%H:%M:%S").encode("utf-8"), ("255.255.255.255", port))
        time.sleep(1)
        
except KeyboardInterrupt as e:
    print("Stopping")

sock.close()