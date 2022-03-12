import socket
import argparse

from pathlib import Path

from threadpool import ThreadPool



PORT = 9009

def make_error_response() -> bytes:
    return b"HTTP/1.1 404 Not Found\r\n\r\n"

def make_response(filename: Path) -> bytes:
    if not filename.exists() or filename.is_dir():
        return make_error_response()

    with open(filename, "r") as f:
        contents = f.read()

    response_string = f"HTTP/1.1 200 OK\r\nContent-Length: {len(contents)}\r\n\r\n{contents}"

    return bytes(response_string, "utf-8")


def get_query(request: str) -> str:
    headers = request.split("\n")
    parts = headers[0].strip().split(" ")
    return parts[1][1:]

def process_new_client(conn: socket.socket, addr): 
    msg = conn.recv(4096)
    query = get_query(msg.decode("utf-8"))
    
    filename = Path(query)

    conn.sendall(make_response(filename))

    conn.close()

def main(max_threads: int):
    pool = ThreadPool(max_threads, process_new_client)
    pool.start()

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
            pool.task_queue.put((conn, addr))
        except KeyboardInterrupt:
            print("Shutting down")
            break        

    pool.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_threads", type=int, default=2)
    args = parser.parse_args()
    main(args.max_threads)