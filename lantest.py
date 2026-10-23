import argparse
import random
import socket
from queue import Queue
from threading import Event, Thread

from sqids import Sqids

PORT_UDP_BROADCAST = 20002
PORT_TCP_SOCKET = 20003

host_id: str = Sqids().encode(
    [
        random.randint(0, 9),
        random.randint(0, 9),
        random.randint(0, 9),
        random.randint(0, 9),
    ]
)


def start_host() -> None:
    stop_broadcast = Event()
    broadcast_errors: Queue[OSError] = Queue()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", PORT_TCP_SOCKET))
        server_socket.listen(1)
        server_socket.settimeout(0.2)

        broadcaster = Thread(
            target=start_broadcast,
            args=(stop_broadcast, broadcast_errors),
            name="lan-broadcast",
        )
        print(f"Hosting {host_id}; waiting for a connection.")
        broadcaster.start()
        try:
            while not stop_broadcast.is_set():
                try:
                    client_socket, address = server_socket.accept()
                except TimeoutError:
                    continue

                with client_socket:
                    stop_broadcast.set()
                    broadcaster.join()
                    if not broadcast_errors.empty():
                        raise broadcast_errors.get_nowait()
                    print(f"Connected to {address[0]}; broadcasting stopped.")
                    msg = b""
                    while len(msg) < 10:
                        chunk = client_socket.recv(10 - len(msg))
                        if not chunk:
                            raise ConnectionError(
                                "Client disconnected before sending the full message."
                            )
                        msg += chunk
                    print(msg)
                return

            raise broadcast_errors.get_nowait()
        finally:
            stop_broadcast.set()
            broadcaster.join()


def start_client() -> None:
    host_ip = start_broadcatch()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        print(f"Connecting to {host_ip}:{PORT_TCP_SOCKET}.")
        client_socket.connect((host_ip, PORT_TCP_SOCKET))
        client_socket.sendall(b"A" * 10)
        print("Message sent.")


def start_broadcast(stop: Event, errors: Queue[OSError]) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as bc_socket:
            bc_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            bc_socket.settimeout(1.0)
            msg = f"c2k {host_id}".encode()

            while not stop.is_set():
                bc_socket.sendto(msg, ("255.255.255.255", PORT_UDP_BROADCAST))
                if stop.wait(3):
                    break
    except OSError as error:
        errors.put(error)
        stop.set()


def start_broadcatch() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as bc_socket:
        bc_socket.bind(("0.0.0.0", PORT_UDP_BROADCAST))
        print("Waiting for a host announcement.")
        while True:
            msg, address = bc_socket.recvfrom(65535)
            prefix, separator, identifier = msg.partition(b" ")
            if prefix == b"c2k" and separator and identifier and identifier.isalnum():
                print(f"Discovered {identifier.decode('ascii')} at {address[0]}.")
                return address[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        action="store_true",
        help="Start a host connection",
    )
    args = parser.parse_args()

    try:
        if args.host:
            start_host()
        else:
            start_client()
    except KeyboardInterrupt:
        parser.exit(130, "\nStopped.\n")
    except OSError as error:
        parser.exit(1, f"Network error: {error}\n")


if __name__ == "__main__":
    main()
