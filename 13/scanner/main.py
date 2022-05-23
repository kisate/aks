import socket
import PySimpleGUI as sg
import scapy.all as scapy
import netifaces as ni
from uuid import getnode as get_mac

INTERFACE = "wlo1"
HOME_IP = ni.ifaddresses(INTERFACE)[ni.AF_INET][0]['addr']
NETWORK_IP = '192.168.0.0'
HOME_MAC = '-'.join(("%012X" % get_mac())[i:i+2] for i in range(0, 12, 2))
HOME_HOST_NAME = socket.gethostbyaddr(HOME_IP)[0]
MASK = [255, 255, 255, 0]


clients = [
    { 'ip': x[1].psrc, 'mac': x[1].hwsrc }
    for x in scapy.srp(
        scapy.Ether(dst='ff:ff:ff:ff:ff:ff') / scapy.ARP(pdst=f'{NETWORK_IP}/24'),
        timeout = 1,
        verbose = False)[0]    
]

layout = [
    [sg.Output(size=(100, 20), font=('Consolas', 10))],
    [sg.Submit('Start')],
    [sg.ProgressBar(len(clients), orientation='h', size=(54, 20), key='progress_bar')]
]
window = sg.Window('LAN scanner', layout)

first_output = True

while True:
    event, values = window.read(timeout=100)

    if event in (None, 'Exit'):
        break

    if event == 'Start':
        if first_output:
            print(f'{"IP":30}{"MAC":30}{"Hostname":30}')
            print('This pc:')
            print(f'{HOME_IP:30}{HOME_MAC:30}{HOME_HOST_NAME:30}')
            print('LAN:')
            first_output = False

        progress_bar = window['progress_bar']
        for i, host in enumerate(clients):
            ip, mac_address = host['ip'], host['mac']
            if ip == HOME_IP:
                continue
            try:
                host_name = socket.gethostbyaddr(ip)[0]
            except Exception:
                host_name = 'Hostname not found'
            print(f'{str(ip):30}{str(mac_address):30}{str(host_name):30}')
            progress_bar.UpdateBar(i + 1)

window.close()