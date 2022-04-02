import ftplib
from ftplib import FTP
import argparse


def help_message():
    return """commands:
    help -- display this message
    ls -- list files in current directory
    upload <src_file_path> <dest_file_path> -- upload to server
    download <src_file_path> <dest_file_path> -- download from server
    quit -- exit program
    """


def command_ls(ftp: FTP):
    ftp.dir()


def command_download(ftp: FTP, src_path: str, dest_path: str):
    with open(dest_path, "wb") as f:
        ftp.retrbinary(f"RETR {src_path}", f.write)


def command_upload(ftp: FTP, src_path: str, dest_path: str):
    with open(src_path, "rb") as f:
        ftp.storbinary(f"STOR {dest_path}", f)


def main(host: str, port: int, user: str, password: str):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login(user, password)

    commands = {
        "ls": command_ls,
        "download": command_download,
        "upload": command_upload,
    }

    print(help_message())

    while True:
        line = input()
        command, *arguments = line.split()
        if command == "help":
            print(help_message())
        elif command == "quit":
            break
        else:
            try:
                if command not in commands:
                    print("Unknown command")
                else:
                    commands[command](ftp, *arguments)
            except ftplib.Error as e:
                print(f"Error: {e}")

    ftp.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str)
    parser.add_argument("port", type=int)
    parser.add_argument("user", type=str)
    parser.add_argument("password", type=str)
    args = parser.parse_args()

    main(args.host, args.port, args.user, args.password)
