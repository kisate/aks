import socket
import subprocess

PORT = 9001

def process_connection(conn: socket.socket, addr):
    msg = get_message(conn).decode("utf-8")
    return_code = subprocess.call(msg, shell=True)
    conn.send(f"Call returned: {return_code}".encode("utf-8"))
    conn.close()


def get_message(conn: socket.socket) -> bytes:
    BUFFER_SIZE = 1024

    raw_message = bytes()

    while True:
        try:
            chunk = conn.recv(BUFFER_SIZE)
            raw_message += chunk
            if len(chunk) < BUFFER_SIZE:
                break
        except socket.timeout:
            break
    
    return raw_message


def main():
    global blacklist
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        main_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    except Exception as e:
        print(e)

    main_socket.bind(("", PORT))
    main_socket.listen()

    while True:
        try:
            conn, addr = main_socket.accept()
            process_connection(conn, addr)
        except KeyboardInterrupt:
            print("Shutting down")
            break        

if __name__ == "__main__":
    main()