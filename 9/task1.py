import socket
import psutil

def get_ip_addresses(family):
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == family:
                yield (interface, snic.address, snic.netmask)

ipv4s = list(get_ip_addresses(socket.AF_INET))

print(ipv4s)