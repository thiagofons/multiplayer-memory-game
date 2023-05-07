import socket
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

numero_jogador = input("Insira o numero do jogador: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    while True:
        card = input(f"J{numero_jogador}- Digite o numero do card: ")

        s.sendall(bytes(card, "utf-8"))
        data = s.recv(1024)
        time.sleep(.5)


        print(f"Received {data!r}")
        