"""CoLa-A query helper for the standalone collector's settings snapshot."""

import socket


def cola(ip, cmd, timeout=3.0):
    with socket.create_connection((ip, 2111), timeout) as connection:
        connection.settimeout(timeout)
        connection.sendall(b"\x02" + cmd.encode() + b"\x03")
        try:
            reply = connection.recv(4096)
        except OSError as error:
            reply = repr(error).encode()
    return reply.replace(b"\x02", b"").replace(b"\x03", b"").decode("latin1")
