import socket
import argparse

def main(address: str, port: int, command: str):

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((address, port))
    conn.sendall(bytes(command, "utf-8"))
    
    print(bytes(conn.recv(2048)).decode("utf-8"))
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str)
    parser.add_argument("port", type=int)
    parser.add_argument("command", type=str)
    args = parser.parse_args()

    main(args.host, args.port, args.command)