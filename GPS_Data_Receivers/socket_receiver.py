import socket as socket_lib
from os import getenv

from dotenv import load_dotenv

from exceptions import SocketDataError

load_dotenv()

HOST_IP = getenv("SOCKET_HOST_IP")
if not HOST_IP:
    raise ValueError(f"Environment variable SOCKET_HOST_IP must be provided when using socket_receiver.")
HOST_PORT = getenv("SOCKET_HOST_PORT")
if not HOST_PORT:
    raise ValueError(f"Environment variable SOCKET_HOST_PORT must be provided when using socket_receiver.")

socket = socket_lib.socket()
socket.setsockopt(socket_lib.SOL_SOCKET, socket_lib.SO_REUSEADDR, 1)
socket.bind((HOST_IP,int(HOST_PORT)))
socket.listen(1)
connection, client_address = socket.accept()

def get_raw_location_data() -> str:
    contents = connection.recv(2048).decode("ascii").split("%")
    for content in contents:
        if content != "{}":
            return content

    raise SocketDataError(socket_data=contents)
