from os import getenv
from dotenv import load_dotenv

load_dotenv()

_ALLOWED_RECEIVER_FUNCS = ("file", "socket")
RECEIVER_FUNC = getenv("RECEIVER_FUNC", "file")
if RECEIVER_FUNC not in _ALLOWED_RECEIVER_FUNCS:
    raise ValueError(f"Environment variable RECEIVER_FUNC must be one of {_ALLOWED_RECEIVER_FUNCS}")

if RECEIVER_FUNC == _ALLOWED_RECEIVER_FUNCS[0]:
    from file_receiver import get_location
elif RECEIVER_FUNC == _ALLOWED_RECEIVER_FUNCS[1]:
    from socket_receiver import get_location

def main():
    print(get_location())


if __name__ == "__main__":
    while True:
        main()
