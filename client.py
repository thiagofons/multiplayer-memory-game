import socket
import sys
import os
import json
import time

HOST = "localhost"
PORT = 65432


def limpa_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def imprime_tabuleiro(tabuleiro):
    # Limpa a tela
    limpa_tela()

    # Imprime coordenadas horizontais
    dim = len(tabuleiro)
    sys.stdout.write("     ")
    for i in range(0, dim):
        sys.stdout.write("{0:2d} ".format(i))

    sys.stdout.write("\n")

    # Imprime separador horizontal
    sys.stdout.write("-----")
    for i in range(0, dim):
        sys.stdout.write("---")

    sys.stdout.write("\n")

    for i in range(0, dim):

        # Imprime coordenadas verticais
        sys.stdout.write("{0:2d} | ".format(i))

        # Imprime conteudo da linha 'i'
        for j in range(0, dim):

            # Peca ja foi removida?
            if tabuleiro[i][j] == '-':

                # Sim.
                sys.stdout.write(" - ")

            # Peca esta levantada?
            elif tabuleiro[i][j] >= 0:

                # Sim, imprime valor.
                sys.stdout.write("{0:2d} ".format(tabuleiro[i][j]))
            else:

                # Nao, imprime '?'
                sys.stdout.write(" ? ")

        sys.stdout.write("\n")


def imprime_placar(placar):
    n_jogadores = len(placar)

    print("Placar:")
    print("---------------------")
    for i in range(0, n_jogadores):
        print("Jogador {0}: {1:2d}".format(i + 1, placar[i]))


def imprime_status(tabuleiro, placar, vez):
    imprime_tabuleiro(tabuleiro)
    sys.stdout.write('\n')

    imprime_placar(placar)
    sys.stdout.write('\n')
    sys.stdout.write('\n')

    print("Vez do Jogador {0}.\n".format(vez + 1))


def le_coordenada(dim):
    input_str = input("Especifique uma peca: ")

    try:
        i = int(input_str.split(' ')[0])
        j = int(input_str.split(' ')[1])
    except (ValueError, IndexError):
        print("Coordenadas invalidas! Use o formato \"i j\" (sem aspas),")
        print("onde i e j sao inteiros maiores ou iguais a 0 e menores que {0}".format(dim))
        input("Pressione <enter> para continuar...")
        return False

    if i < 0 or i >= dim:
        print("Coordenada i deve ser maior ou igual a zero e menor que {0}".format(dim))
        input("Pressione <enter> para continuar...")
        return False

    if j < 0 or j >= dim:
        print("Coordenada j deve ser maior ou igual a zero e menor que {0}".format(dim))
        input("Pressione <enter> para continuar...")
        return False

    return i, j


# Tamanho (da lateral) do tabuleiro. NECESSARIAMENTE PAR E MENOR QUE 10!
dim = 4

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT))

mensagens = [
    "Especifique uma peca:",
    "Escolha uma peca ainda fechada!"
]


while True:

    # Escolha das pecas
    while True:
        jogo_json = cliente.recv(1024).decode()
        jogo = json.loads(jogo_json)
        imprime_status(jogo['tabuleiro'], jogo['placar'], jogo['vez'])

        if jogo['msg'] == -1:
            break
        print(mensagens[jogo['msg']])

        while True:

            coordenadas = le_coordenada(dim)
            if coordenadas:
                break

        coordenadas_json = json.dumps(coordenadas)
        cliente.send(coordenadas_json.encode())

    cliente.send("OK".encode())

    pecas_escolhidas = cliente.recv(1024).decode()
    print(pecas_escolhidas)

    resultado_pecas = cliente.recv(1024).decode()
    print(resultado_pecas)

    time.sleep(4)
