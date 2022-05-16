import socket
import datetime

import PySimpleGUI as sg

PACKET_SIZE = 1024
host, port = '127.0.0.1', 9013

def create_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    return s

sock = create_socket(host, port)

layout = [
    [sg.Text('IP', size=(40, 1)), sg.InputText(host)],
    [sg.Text('Port', size=(40, 1)), sg.InputText(str(port))],
    [sg.Text('Packets arrived:', size=(40, 1)), sg.Text(key='messages')],
    [sg.Text('Speed:', size=(40, 1)), sg.Text(key='speed')],
    [sg.Button('Receive packets')],
]

window = sg.Window('UDP Receiver', layout)

total = 0
counter = 0
first_time = None
last_time = 1

while True:
    event, values = window.read(100)

    if event in (None, 'Exit'):
        break

    if event == 'Receive packets':
        counter = 0
        first_time = None

        try:
            sock.settimeout(None)
            total = int(sock.recv(PACKET_SIZE).decode())
            sock.settimeout(0.1)
            for i in range(total):
                try:
                    msg = sock.recv(PACKET_SIZE)
                    msg_time, _ = msg.decode("ascii").split()
                    counter += 1
                    if first_time is None:
                        first_time = int(msg_time)
                except socket.timeout:
                    pass
            last_time = round(datetime.datetime.now().timestamp() * 1000)
        except Exception as e:
            print(f'Receiving failed: {e}')
        finally:
            sock.close()

    try:
        new_host, new_port = values[0], int(values[1])
        # if new_host != host or new_port != port:
        host, port = new_host, new_port
        sock.close()
        sock = create_socket(host, port)
    except:
        pass
    if first_time is not None:
        total_time = last_time - first_time
        if total_time > 0:
            speed = round(PACKET_SIZE * counter / total_time)
        window['speed'].Update(f'{speed} KB/s')
        window['messages'].Update(f'{counter}/{total}')

sock.close()