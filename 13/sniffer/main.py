import socket
import struct
import PySimpleGUI as sg
import netifaces as ni
from stats import Stats, Packet, PROT_TYPE

from threading import Thread

INTERFACE = "wlo1"

ip = ni.ifaddresses(INTERFACE)[ni.AF_INET][0]['addr']
traffic_stats = Stats(ip)

running = True
incoming_total = 0
outgoing_total = 0

radio_column = [
    [sg.Radio('All traffic', "RADIO1", default=True, key="MODE0")],
    [sg.Radio('By dest port', "RADIO1", default=False, key="MODE1")],
    [sg.Radio('By src port', "RADIO1", default=False, key="MODE2")]
]

layout = [
    [sg.Text('Incmoing:'), sg.Text(key='incoming')],
    [sg.Text('Outgoing:'), sg.Text(key='outgoing')],
    [sg.Listbox([], size=(100, 40), key='-LISTBOX-')],
    [sg.Text("Packet info:", size=(40, 1))],
    [sg.Text(key="packet", size=(40, 10)), sg.Column(radio_column)]
]
window = sg.Window('Title', layout, finalize=True)

def ipv4(addr):
    return '.'.join(map(str, addr))

def process_packet(data):
    ipv, ttl, prot_num, checksum, src, dst, src_port, dest_port = struct.unpack("!HBB2s4s4sHH", data[12:14] + data[22:38])
    packet = Packet(hex(ipv), ttl, ipv4(src), ipv4(dst), prot_num, src_port, dest_port, len(data))
    if prot_num in PROT_TYPE:
        traffic_stats.add_packet(packet)
    # print()

def reading_thead(sock):
    while running:
        try:
            raw_data, addr = sock.recvfrom(65536)
            if not running:
                break
            process_packet(raw_data)
        except socket.timeout:
            pass

def main():
    global running
    s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    s.bind((INTERFACE, 0))
    s.settimeout(1)

    th = Thread(target=reading_thead, args=(s, ))
    th.start()

    while True:
        event, values = window.read(200)
        if event == sg.WINDOW_CLOSED:
            break

        if values["MODE0"]:
            if len(values['-LISTBOX-']) > 0:
                packet = values['-LISTBOX-'][0]
                window["packet"].Update(packet.pretty_str())
            window['-LISTBOX-'].Update(values=traffic_stats.packets)
        if values["MODE1"]:
            window['-LISTBOX-'].Update(values=[f"{v}: {k}" for v, k in traffic_stats.total_port_in.items()])
        if values["MODE2"]:
            window['-LISTBOX-'].Update(values=[f"{v}: {k}" for v, k in traffic_stats.total_port_out.items()])

        
        window['incoming'].Update(traffic_stats.total_in)
        window['outgoing'].Update(traffic_stats.total_out)
        
    running = False
    th.join()
    window.close()

if __name__ == "__main__":
    main()