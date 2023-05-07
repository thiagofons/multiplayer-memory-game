import socket
import random
import json

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


# Tamanho (da lateral) do tabuleiro. NECESSARIAMENTE PAR E MENOR QUE 10!
dim = 4

# Numero de jogadores
nJogadores = 2

# Numero total de pares de pecas
totalDePares = dim ** 2 / 2

# Partida continua enquanto ainda ha pares de pecas a
# casar.
paresEncontrados = 0

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))

servidor.listen()
cliente, endereco = servidor.accept()

while True:

    # Cria um tabuleiro para a partida
    tabuleiro = novo_tabuleiro(dim)

    # Cria um placar zerado
    placar = novo_placar(nJogadores)

    vez = 0

    jogo = {
        'tabuleiro': tabuleiro,
        'placar': placar,
        'vez': vez,
        'msg': 0
    }

    while paresEncontrados < totalDePares:
        coord_pecas = []
        jogo['msg'] = 0

        # Escolha de pecas
        while len(coord_pecas) < 4:

            jogo_json = json.dumps(jogo)
            print("sending")
            cliente.send(jogo_json.encode())

            coordenadas_json = cliente.recv(1024).decode()
            coordenadas = json.loads(coordenadas_json)
            peca_fechada = abre_peca(tabuleiro, coordenadas[0], coordenadas[1])

            if not peca_fechada:
                jogo['msg'] = 1
                continue
            else:
                coord_pecas.extend(coordenadas)
                jogo['msg'] = 0 if len(coord_pecas) < 4 else -1

        jogo['vez'] = -jogo['vez']
        jogo_json = json.dumps(jogo)
        print("extra")
        cliente.send(jogo_json.encode())

        i1, j1, i2, j2 = coord_pecas
        cliente.send(str.encode("Pecas escolhidas --> ({0}, {1}) e ({2}, {3})\n".format(i1, j1, i2, j2)))

        # Pecas escolhidas sao iguais?
        # if jogo['tabuleiro'][i1][j1] == jogo['tabuleiro'][i2][j2]:
        #
        #     cliente.send(str.encode("Pecas casam! Ponto para o jogador {0}.".format(vez + 1)))
        #
        #     incrementa_placar(jogo['placar'], jogo['vez'])
        #     paresEncontrados = paresEncontrados + 1
        #     remove_peca(jogo['tabuleiro'], i1, j1)
        #     remove_peca(jogo['tabuleiro'], i2, j2)
        # else:
        #
        #     cliente.send(str.encode("Pecas nao casam!"))
        #
        #     fecha_peca(jogo['tabuleiro'], i1, j1)
        #     fecha_peca(jogo['tabuleiro'], i2, j2)
        #     vez = (vez + 1) % nJogadores
