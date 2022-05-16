import random
import socket
import datetime
import PySimpleGUI as sg

PACKET_SIZE = 1024

def build_message():
    now = datetime.datetime.now()
    message = f'{int(now.timestamp() * 1000)} '

    payload = ''.join(
        chr(random.randint(ord("!"), ord("z")))
        for _ in range(PACKET_SIZE - len(message))
    )

    return message + payload

layout = [
    [sg.Text('IP', size=(40, 1)), sg.InputText('127.0.0.1', key='host')],
    [sg.Text('Port', size=(40, 1)), sg.InputText('9013', key='port')],
    [sg.Text('Packets to send', size=(40, 1)), sg.InputText('5', key='messages')],
    [sg.Button('Send packets')],
]

window = sg.Window('UDP Sender', layout)

while True:
    event, values = window.read()

    if event in (None, 'Exit'):
        break

    if event == 'Send packets':
        try:
            host, port = values['host'], int(values['port'])
            total = int(values['messages'])
        except Exception as e:
            print(f'Parsing failed: {e}')

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((host, port))
            sock.sendto(str(total).encode("ascii"), (host, port))
            for i in range(total):
                message = build_message()
                sock.sendto(message.encode("ascii"), (host, port))
        except Exception as e:
            print(f'Sending failed: {e}')
        finally:
            sock.close()