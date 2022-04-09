import socket
import datetime
from stats import Stats

port   = 9001
host = "127.0.0.1"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.settimeout(1)

times = {}

st = Stats()

for i in range(1, 11):

    times[i] = datetime.datetime.now()

    sock.sendto(f"Ping {i} {times[i]}".encode("utf-8"), (host, port))
    
    try: 
        msg, _ = sock.recvfrom(1024)
        msg = msg.decode("utf-8")

        idx = int(msg.split()[1])
        time_now = datetime.datetime.now()
        print(msg)
    
        rtt_ms = (time_now - times[idx]).total_seconds() * 1000

        st.add_recived(rtt_ms)

    except socket.timeout:
        print("Request timed out")
        st.add_missed()

    rtt_min, rtt_max, rtt_mean, rtt_missed = st.stats()

    print(f'''
    --- {host} ping statistics ---
        {st.total_count} packets transmitted, {st.recieved} recieved, {round(rtt_missed*100, 5)}% packet loss
        rtt min/max/avg = {round(rtt_min, 5)}/{round(rtt_max, 5)}/{round(rtt_mean, 5)} ms
    ''')