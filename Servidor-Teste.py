import socket
import sys
import select

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

dim = int(sys.argv[1])
njog = int(sys.argv[2])


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(njog)
    sockets_list = [server]

    while True:
        read_sockets, _, _ = select.select(sockets_list, [], [])

        for sock in read_sockets:
        # se o socket for o servidor, aceita uma nova conexão
            if sock == server:
                client_socket, client_address = server.accept()
                sockets_list.append(client_socket)
                print(f'Nova conexão de {client_address}')
            # se o socket for um cliente, recebe dados
            else:
                while True:
                    data = sock.recv(1024)
                    print(data)
                    if not data:
                        sock.close()
                        sockets_list.remove(sock)
                        break
                    
                    print(f'Recebido de {sock.getpeername()}: {data.decode()}')
   
#    sockets_list.append(conn)
    
#     with conn:
#         print(f"Connected by {addr}")
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             conn.sendall(data)