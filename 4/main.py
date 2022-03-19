from functools import cache
from http.client import HTTP_PORT
from cache import Cache
import socket

from numpy import byte

import logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename='app.log', filemode='w')
PORT = 9001

server_cache = Cache()

def change_destination(msg: str):
    parts = msg.split("\r\n")

    first_header = parts[0].split(" ")
    
    request_type = first_header[0]
    query = first_header[1][1:]

    address, *query_parts = query.split("/")
    
    if address == "favicon.ico":
        address = "www.google.com"
        query_parts = ["favicon.ico"]

    first_header[1] = "/" + "/".join(query_parts)
    parts[0] = " ".join(first_header)

    added_host = False

    for i, part in enumerate(parts):
        if part.startswith("Host:"):
            parts[i] = f"Host: {address}"
            added_host = True
            break

    if not added_host:
       parts.insert(1, f"Host: {address}")

    return "\r\n".join(parts), address, query, request_type

def build_error_message(code, message):
    return bytes(f"HTTP/1.1 {code} {message}\r\n\r\n", "utf-8")

def add_to_journal(msg, query):
    code = msg.decode("ISO-8859-1").split("\n")[0].strip().split(" ")[1]
    logging.info((query, code))

def make_refresh_request(msg, query):
    parts = msg.split("\r\n")

    _, last_modied, etag = server_cache.get_data(query) 

    parts.insert(1, f"Last-Modified: {last_modied}")
    parts.insert(1, f"If-None-Match: {etag}")

    return "\r\n".join(parts)
    

def add_to_cache(msg: str, query):
    last_modified = None
    etag = None

    found_modified = False
    found_etag = False

    parts = msg.split("\r\n")
    for part in parts:
        if part.startswith("Last-Modified:"):
            last_modified = part.replace("Last-Modified: ")
            found_modified = True
        if part.startswith("ETag:"):
            etag = part.replace("ETag: ")
            found_etag = True

        if found_etag and found_modified:
            break

    if server_cache.is_in_cache(query):
        last_val = server_cache.get_data(query)
        if last_val[0] != last_modified:
            server_cache.add_to_cache(query, last_modified, etag, msg)
    else:
        server_cache.add_to_cache(query, last_modified, etag, msg)

    

    




def process_connection(conn: socket.socket, addr):
    
    try:
        msg = get_message(conn).decode("utf-8")
        msg, address, query, request_type = change_destination(msg)

        print(request_type)

        if request_type == "GET":
            if server_cache.is_in_cache(query):
                new_msg = make_refresh_request(msg)


        new_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_conn.connect((address, HTTP_PORT))

        new_conn.sendall(bytes(msg, "utf-8"))

        msg = get_message(new_conn)

        if request_type == "GET":
            

        print(msg.decode("utf-8"))

        add_to_journal(msg, query)

    except Exception as e:
        msg = build_error_message(500, "Internal Server Error")
        raise e
        print(e)

    print(msg)

    conn.sendall(msg)
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