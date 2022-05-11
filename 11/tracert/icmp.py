import struct
import sys
import time
import os
import socket
import select

from checksum import calculate_checksum

ICMP_ECHOREPLY = 0 # Echo reply (per RFC792)
ICMP_ECHO = 8 # Echo request (per RFC792)

ICMP_MAX_RECV = 2048

MAX_SLEEP = 1000

if sys.platform.startswith("win32"):
	# On Windows, the best timer is time.clock()
	default_timer = time.clock
else:
	# On most other platforms the best timer is time.time()
	default_timer = time.time


class Response(object):
	def __init__(self):
		self.max_rtt = None
		self.min_rtt = None
		self.avg_rtt = None
		self.packet_lost = None
		self.ret_code = None
		self.ttl = None
		self.output = []

		self.packet_size = None
		self.timeout = None
		self.destination = None
		self.destination_ip = None

class Ping(object):
    def __init__(self, destination, timeout=1000, packet_size=55, n_packets=3):
        self.destination = destination
        self.timeout = timeout
        self.packet_size = packet_size
        self.n_packets = n_packets

        self.own_id = os.getpid() & 0xFFFF

        self.seq_number = 0
        self.send_count = 0
        self.receive_count = 0
        self.min_time = 999999999
        self.max_time = 0.0
        self.total_time = 0.0


    def print_start(self):
        msg = "\nPYTHON-PING %s (%s): %d data bytes" % (self.destination, self.dest_ip, self.packet_size)
        print(msg)

    def print_success(self, delay, ip, packet_size, ip_header, icmp_header):
        if ip == self.destination:
            from_info = ip
        else:
            from_info = "%s (%s)" % (self.destination, ip)

        msg = "%d bytes from %s: icmp_seq=%d ttl=%d time=%.1f ms" % (packet_size, from_info, icmp_header["seq_number"], ip_header["ttl"], delay)

        
        print(msg)
        #print("IP header: %r" % ip_header)
        #print("ICMP header: %r" % icmp_header)

    def print_failed(self):
        msg = "Request timed out."

        print(msg)

    def print_exit(self):
        msg = "\n----%s PYTHON PING Statistics----" % (self.destination)

        print(msg)

        lost_count = self.send_count - self.receive_count
        #print("%i packets lost" % lost_count)
        lost_rate = float(lost_count) / self.send_count * 100.0

        msg = "%d packets transmitted, %d packets received, %0.1f%% packet loss" % (self.send_count, self.receive_count, lost_rate)

        print(msg)

        if self.receive_count > 0:
            msg = "round-trip (ms)  min/avg/max = %0.3f/%0.3f/%0.3f" % (self.min_time, self.total_time / self.receive_count, self.max_time)
            
            print(msg)

        print('')



    def header2dict(self, names, struct_format, data):
        """ unpack the raw received IP and ICMP header informations to a dict """
        unpacked_data = struct.unpack(struct_format, data)
        return dict(zip(names, unpacked_data))

    #--------------------------------------------------------------------------

    def run(self, count=None, deadline=None):
        """
        send and receive pings in a loop. Stop if count or until deadline.
        """

        ttl = 1

        while True:
            self.send_count = 0
            self.receive_count = 0
            self.min_time = 999999999
            self.max_time = 0.0
            self.total_time = 0.0
            ip, headers = None, None
            for _ in range(self.n_packets):
                _ip, _headers = self.do(ttl)
                if _ip:
                    ip = _ip
                    headers = _headers
                self.seq_number += 1

            if ip:
                try:
                    name, _, _ = socket.gethostbyaddr(ip)
                except socket.error:
                    name = "unknown"
                print(f"{ttl}. {ip} ({name}) : {self.total_time / max(1, self.receive_count)} {self.max_time} {self.min_time}, lost: {1 - self.receive_count / self.send_count}")

                if headers["type"] == 0:
                    break
            else:
                print(f"{ttl}. unreachable ")

            ttl += 1
            
    def do(self, ttl):
        """
        Send one ICMP ECHO_REQUEST and receive the response until self.timeout
        """
        current_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        current_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)


        send_time = self.send_one_ping(current_socket)
        if send_time == None:
            return
        self.send_count += 1

        receive_time, ip, headers = self.receive_one_ping(current_socket)
        current_socket.close()

        if receive_time:
            self.receive_count += 1
            self.ttl = headers["ttl"]
            delay = (receive_time - send_time) * 1000.0
            self.total_time += delay
            if self.min_time > delay:
                self.min_time = delay
            if self.max_time < delay:
                self.max_time = delay

            # self.print_success(delay, ip, packet_size, ip_header, icmp_header)
            return ip, headers
        
        return None, None

    def send_one_ping(self, current_socket):
        """
        Send one ICMP ECHO_REQUEST
        """
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        checksum = 0

        # Make a dummy header with a 0 checksum.
        header = struct.pack(
            "!BBHHH", ICMP_ECHO, 0, checksum, self.own_id, self.seq_number
        )

        padBytes = []
        startVal = 0x42
        for i in range(startVal, startVal + (self.packet_size)):
            padBytes += [(i & 0xff)]  # Keep chars in the 0-255 range
        data = bytes(padBytes)

        # Calculate the checksum on the data and the dummy header.
        checksum = calculate_checksum(header + data) # Checksum is in network order

        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        header = struct.pack(
            "!BBHHH", ICMP_ECHO, 0, checksum, self.own_id, self.seq_number
        )

        packet = header + data

        send_time = default_timer()

        try:
            current_socket.sendto(packet, (self.destination, 1)) # Port number is irrelevant for ICMP
        except socket.error as e:
            self.response.output.append("General failure (%s)" % (e.args[1]))
            current_socket.close()
            return

        return send_time

    def receive_one_ping(self, current_socket):
        """
        Receive the ping from the socket. timeout = in ms
        """
        timeout = self.timeout / 1000.0

        while True: # Loop while waiting for packet or timeout
            select_start = default_timer()
            inputready, outputready, exceptready = select.select([current_socket], [], [], timeout)
            select_duration = (default_timer() - select_start)
            if inputready == []: # timeout
                return None, 0, 0

            receive_time = default_timer()

            packet_data, address = current_socket.recvfrom(ICMP_MAX_RECV)

            headers = self.header2dict(
                names=[
                    "version", "type", "length",
                    "id", "flags", "ttl", "protocol",
                    "checksum", "src_ip", "dest_ip",
                    "type", "code", "checksum",
                    "packet_id", "seq_number"
                ],
                struct_format="!BBHHHBBHIIBBHHH",
                data=packet_data[:28]
            )
            # print(headers)

            if headers["packet_id"] == self.own_id or headers["type"] == 11: # Our packet
                ip = socket.inet_ntoa(struct.pack("!I", headers["src_ip"]))
                # XXX: Why not ip = address[0] ???
                return receive_time, ip, headers

            timeout = timeout - select_duration
            if timeout <= 0:
                return None, 0, 0