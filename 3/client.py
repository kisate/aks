import chunk
import socket
import argparse

def main(address: str, port: int, filename: str):
    BUFFER_SIZE = 1024

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((address, port))
    conn.sendall(bytes(f"GET /{filename} HTTP/1.1\r\n\r\n", "utf-8"))

    raw_message = []

    conn.settimeout(1)
    conn.setblocking(True)

    while True:
        try:
            chunk = conn.recv(BUFFER_SIZE)
            raw_message.extend(chunk)
            if len(chunk) < BUFFER_SIZE:
                break
        except socket.timeout:
            break
    
    print(bytes(raw_message).decode("utf-8"))
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str)
    parser.add_argument("port", type=int)
    parser.add_argument("filename", type=str)
    args = parser.parse_args()

    main(args.host, args.port, args.filename)