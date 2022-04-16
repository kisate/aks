import argparse
import socket

from stopandwait import SocketWrapper

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=9001, type=int)
    parser.add_argument('--timeout', default=1, type=int)
    parser.add_argument("--file_size", default=3084, type=int)
    parser.add_argument('--to_send', action="store_true")
    args = parser.parse_args()
    return args.host, args.port, args.timeout, args.file_size, args.to_send

def send_file(host, port, timeout):
    with open("lorem.txt", "r") as f:
        contents = f.read()
    data = contents.encode("utf-8")

    print(f"Sending {len(data)} bytes.")

    soc = SocketWrapper(timeout)
    soc.send(data, (host, port))

def recv_file(host, port, timeout, file_size):
    soc = SocketWrapper(timeout)
    soc.soc.bind((host, port))
    data = soc.recv(file_size)

    with open("received.txt", "w") as f:
        f.write(data.decode("utf-8"))


if __name__ == '__main__':
    host, port, timeout, file_size, to_send = parse_arguments()

    if to_send:
        send_file(host, port, timeout)
    else:
        recv_file(host, port, timeout, file_size)
