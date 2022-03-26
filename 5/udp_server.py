import socket
import threading
from datetime import datetime
import time

localIP     = "127.0.0.1"
localPort   = 9001
bufferSize  = 1024

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

running = True

try:
    UDPServerSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
except Exception as e:
    print(e)

UDPServerSocket.bind((localIP, localPort))


print("UDP server up and listening")

 
clients = []

# Listen for incoming datagrams

def send_time():
    for client in clients:
        message = datetime.now().strftime("%H:%M:%S")
        UDPServerSocket.sendto(message.encode("utf-8"), client)

def main_cycle():
    while running:
        threading.Thread(target=send_time).start()
        time.sleep(1)
    

broadcast_thread = threading.Thread(target=main_cycle)
broadcast_thread.start()

try:
    while running:

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message.decode("utf-8"))
        clientIP  = "Client IP Address:{}".format(address)
        
        print(clientMsg)
        print(clientIP)

        clients.append(address)

        UDPServerSocket.sendto("Wellcome to the time broadcast".encode("utf-8"), address)
except KeyboardInterrupt as e:
    print("Stopping")
    running = False
    
broadcast_thread.join()