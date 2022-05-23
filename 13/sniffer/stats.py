from collections import defaultdict

PROT_VERSION = {
    "0x800" : "IPv4",
    "0x86dd": "IPv6"
}

PROT_TYPE = {
    6: "TCP",
    17: "UDP"
}

class Packet:
    def __init__(self, version, ttl, src, dst, prot, src_port, dest_port, size) -> None:
        self.version = version
        self.ttl = ttl
        self.src = src
        self.dst = dst
        self.prot = prot
        self.src_port = src_port
        self.dest_port = dest_port
        self.size = size

    def __str__(self) -> str:
        return f"{self.src} -> {self.dest_port} {self.size}"

    def pretty_str(self):
        return "\n".join([
            f"{self.src} > {self.dst}",
            PROT_VERSION[self.version],
            f"Size: {self.size}",
            f"TTL: {self.ttl}",
            f"Protocol: {PROT_TYPE[self.prot]}",
            f"Source port: {self.src_port}",
            f"Destination port: {self.dest_port}"
        ])

class Stats:
    def __init__(self, ip) -> None:
        self.ip = ip

        self.packets = []
        self.total_in = 0
        self.total_out = 0
        self.total_port_in = defaultdict(lambda: 0)
        self.total_port_out = defaultdict(lambda: 0)

    def add_packet(self, packet: Packet):
        self.packets.append(packet)
        if packet.src == self.ip:
            self.total_out += packet.size
            self.total_port_out[packet.src_port] += packet.size
        else:
            self.total_port_in[packet.dest_port] += packet.size
            self.total_in += packet.size

        
