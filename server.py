import socket
import random
import json
import sys
import _thread
import time

HOST = "127.0.0.1"
PORT = 65432


def novo_tabuleiro(dim):
    # Cria um tabuleiro vazio.
    tabuleiro = []
    for i in range(0, dim):

        linha = []
        for j in range(0, dim):
            linha.append(0)

        tabuleiro.append(linha)

    # Cria uma lista de todas as posicoes do tabuleiro. Util para
    # sortearmos posicoes aleatoriamente para as pecas.
    posicoes_disponiveis = []
    for i in range(0, dim):

        for j in range(0, dim):
            posicoes_disponiveis.append((i, j))

    # Varre todas as pecas que serao colocadas no
    # tabuleiro e posiciona cada par de pecas iguais
    # em posicoes aleatorias.
    for j in range(0, dim // 2):
        for i in range(1, dim + 1):
            # Sorteio da posicao da segunda peca com valor 'i'
            maximo = len(posicoes_disponiveis)
            indice_aleatorio = random.randint(0, maximo - 1)
            r_i, r_j = posicoes_disponiveis.pop(indice_aleatorio)

            tabuleiro[r_i][r_j] = -i

            # Sorteio da posicao da segunda peca com valor 'i'
            maximo = len(posicoes_disponiveis)
            indice_aleatorio = random.randint(0, maximo - 1)
            r_i, r_j = posicoes_disponiveis.pop(indice_aleatorio)

            tabuleiro[r_i][r_j] = -i

    return tabuleiro


def abre_peca(tabuleiro, i, j):
    if tabuleiro[i][j] == '-':
        return False
    elif tabuleiro[i][j] < 0:
        tabuleiro[i][j] = -tabuleiro[i][j]
        return True

    return False


def fecha_peca(tabuleiro, i, j):
    if tabuleiro[i][j] == '-':
        return False
    elif tabuleiro[i][j] > 0:
        tabuleiro[i][j] = -tabuleiro[i][j]
        return True

    return False


def remove_peca(tabuleiro, i, j):
    if tabuleiro[i][j] == '-':
        return False
    else:
        tabuleiro[i][j] = "-"
        return True


def novo_placar(nJogadores):
    return [0] * nJogadores


def incrementa_placar(placar, jogador):
    placar[jogador] = placar[jogador] + 1


def create_thread(message, servidor, clientes, nJogadores):
    servidor.listen()
    cliente, endereco = servidor.accept()
    clientes.append(cliente)

    if len(clientes) < nJogadores:
        _thread.start_new_thread(create_thread, (message, servidor, clientes, nJogadores))

# Tamanho (da lateral) do tabuleiro. NECESSARIAMENTE PAR E MENOR QUE 10!
dim = 4

# Numero de jogadores
nJogadores = 2

# Numero total de pares de pecas
totalDePares = dim ** 2 / 2

# Partida continua enquanto ainda ha pares de pecas a
# casar.
paresEncontrados = 0

# Array com todos os clientes conectados
clientes = []

message = []

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
_thread.start_new_thread(create_thread, (message, servidor, clientes, nJogadores))

while(len(clientes) < nJogadores):
    pass

def inicia_jogo(clientes, nJogadores, dim):
    # Cria um tabuleiro para a partida
    tabuleiro = novo_tabuleiro(dim)

    # Cria um placar zerado
    placar = novo_placar(nJogadores)

    jogo = {
        'tabuleiro': tabuleiro,
        'placar': placar,
        'vez': 0,
        'msg': 0
    }

    paresEncontrados = 0
    totalDePares = dim ** 2 / 2

    id = 0
    for cliente in clientes:
        jogo_json = json.dumps((jogo, id))
        cliente.send(jogo_json.encode())
        id += 1

    while paresEncontrados < totalDePares:
        coord_pecas = []
        jogo['msg'] = 0

        # Escolha de pecas
        while len(coord_pecas) < 4:
            print(clientes[jogo['vez']])

           
            print("sending...")

            # Pega e repassa primeia coordenada
            coordenadas_json1 = clientes[jogo['vez']].recv(1024).decode()
            coordenadas1 = json.loads(coordenadas_json1)

            count_vez1 = 0
            for cliente in clientes:
                if count_vez1 != jogo['vez']:
                    cliente.send(coordenadas_json1)
                count_vez1 += 1
            peca_fechada = abre_peca(tabuleiro, coordenadas1[0], coordenadas1[1])

            if not peca_fechada:
                jogo['msg'] = 1
                continue
            else:
                coord_pecas.extend(coordenadas1)
                jogo['msg'] = 0 if len(coord_pecas) < 4 else -1
            time.sleep(1)

            # Pega e repassa segunda coordenada
            coordenadas_json2 = cliente[jogo['vez']].recv(1024).decode()
            coordenadas2 = json.loads(coordenadas_json2)

            count_vez2 = 0
            for cliente in clientes:
                if count_vez2 != jogo['vez']:
                    cliente.send(coordenadas_json2)
                count_vez2 += 1

            peca_fechada = abre_peca(tabuleiro, coordenadas2[0], coordenadas2[1])
            time.sleep(1)

            if not peca_fechada:
                jogo['msg'] = 1
                continue
            else:
                coord_pecas.extend(coordenadas2)
                jogo['msg'] = 0 if len(coord_pecas) < 4 else -1

        jogo['vez'] = (jogo['vez'] + 1) % nJogadores
        jogo_json = json.dumps(jogo)
        print("extra")
        clientes[jogo['vez']].send(jogo_json.encode())

        while True:
            confirmacao = clientes[jogo['vez']].recv(1024).decode()
            if confirmacao == "OK":
                break

        i1, j1, i2, j2 = coord_pecas
        clientes[jogo['vez']].send(str.encode("Pecas escolhidas --> ({0}, {1}) e ({2}, {3})\n".format(i1, j1, i2, j2)))

        # Pecas escolhidas sao iguais?
        if jogo['tabuleiro'][i1][j1] == jogo['tabuleiro'][i2][j2]:

            clientes[jogo['vez']].send(str.encode("Pecas casam! Ponto para o jogador {0}.".format(vez + 1)))

            incrementa_placar(jogo['placar'], jogo['vez'])
            paresEncontrados = paresEncontrados + 1
            remove_peca(jogo['tabuleiro'], i1, j1)
            remove_peca(jogo['tabuleiro'], i2, j2)
        else:

            clientes[jogo['vez']].send(str.encode("Pecas nao casam!"))

            fecha_peca(jogo['tabuleiro'], i1, j1)
            fecha_peca(jogo['tabuleiro'], i2, j2)
            jogo['vez'] = (jogo['vez'] + 1) % nJogadores
    # Verificar o vencedor e imprimir
    pontuacao_maxima = max(placar)
    vencedores = []
    for i in range(0, nJogadores):

        if placar[i] == pontuacao_maxima:
            vencedores.append(i)

    if len(vencedores) > 1:

        print("Houve empate entre os jogadores ", end="")
        for i in vencedores:
            sys.stdout.write(str(i + 1) + ' ')

        sys.stdout.write("\n")

    else:
        print("Jogador {0} foi o vencedor!".format(vencedores[0] + 1))

inicia_jogo(clientes, nJogadores, dim)
