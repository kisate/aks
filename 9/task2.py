import socket
import argparse

def find_open_ports(min_port: int, max_port: int):
    s = socket.socket
    for port in range(min_port, max_port): 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            res = sock.connect_ex(("localhost", port))
            if res == 0:
                yield port

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('min_port', type=int)
    parser.add_argument('max_port', type=int)
    args = parser.parse_args()

    print(list(find_open_ports(args.min_port, args.max_port)))
