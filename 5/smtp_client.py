import argparse
import base64, socket, ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from pathlib import Path

mailserv = "smtp.mail.ru"
mailport = 465
username = "lpoks@internet.ru"
password = ""
mailfrom = "lpoks@internet.ru"

def send_and_check_code(message: bytes, sock: socket.socket, code: int):
    sock.send(message)
    response_code = sock.recv(2048).split()[0]
    
    if int(response_code) != code:
        raise Exception(f"Expected {code} but got {response_code} for {message}")

def build_message(message_file: str, mailrcpt: str):
    message = MIMEMultipart()
    message["Subject"] = "Lab message"
    message["From"] = mailfrom
    message["To"] = mailrcpt

    message_path = Path(message_file)

    if message_path.suffix == ".txt":
        with open(message_path, "r") as f:
            part = MIMEText(f.read(), "plain")
    if message_path.suffix == ".html":
        with open(message_path, "r") as f:
            part = MIMEText(f.read(), "html")
    if message_path.suffix in [".png", ".jpg"]:
        with open(message_path, "rb") as f:
            part = MIMEImage(f.read())

    message.attach(part)

    return message.as_bytes()

def main(mailrcpt: str, message_file: str):
    context = ssl.create_default_context()
    sock = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=mailserv)
    sock.connect((mailserv, mailport))
    sock.recv(2048)

    send_and_check_code('HELO labpoks\r\n'.encode("utf-8"), sock, 250)

    send_and_check_code('AUTH LOGIN\r\n'.encode("utf-8"), sock, 334)
    
    user64 = base64.b64encode(username.encode('utf-8'))
    pass64 = base64.b64encode(password.encode('utf-8'))

    sock.send(user64)
    send_and_check_code("\r\n".encode('utf-8'), sock, 334)

    sock.send(pass64)
    send_and_check_code("\r\n".encode('utf-8'), sock, 235)
    
    msg = f'MAIL FROM: <{mailfrom}>\r\n'
    send_and_check_code(msg.encode('utf-8'), sock, 250)

    msg = f'RCPT TO: <{mailrcpt}>\r\n'
    send_and_check_code(msg.encode('utf-8'), sock, 250)

    msg = 'DATA\r\n'
    send_and_check_code(msg.encode('utf-8'), sock, 354)

    sock.send(build_message(message_file, mailrcpt))

    send_and_check_code('\r\n.\r\n'.encode("utf-8"), sock, 250)

    send_and_check_code('QUIT\r\n'.encode("utf-8"), sock, 221)
    
    sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("recipient", type=str)
    parser.add_argument("message_file", type=str)
    args = parser.parse_args()

    with open("pswd", "r") as f:
        password = f.read()

    main(args.recipient, args.message_file)