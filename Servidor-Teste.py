import socket
import selectors
import types

# selector
sel = selectors.DefaultSelector()

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

lsock.bind((HOST, PORT))
lsock.listen()

print(f"Listening on {HOST, PORT}")

# configure the socket in non-blocking mode
lsock.setblocking(False)

# registers the socket to be monitored by
sel.register(lsock, selectors.EVENT_READ, data=None)



def accept_wrapper(sock):
    connection, address = sock.accept()
    print(f"Accepted connection from {address}")

    connection.setblocking(False)

    data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    sel.register(connection, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        received_data = sock.recv(1024)

        if received_data:
            data.outb += received_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

# event loop
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting...")
finally:
    sel.close()



