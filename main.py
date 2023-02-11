import socket as socket_lib

HOST_IP = "192.168.43.70"
HOST_PORT = 12345
socket = socket_lib.socket()

socket.setsockopt(socket_lib.SOL_SOCKET, socket_lib.SO_REUSEADDR, 1)
socket.bind((HOST_IP,HOST_PORT))
socket.listen(1)
connection, client_address = socket.accept()


def main():
    print(connection.recv(2048).decode("ascii"))


if __name__ == "__main__":
    while True:
        main()
