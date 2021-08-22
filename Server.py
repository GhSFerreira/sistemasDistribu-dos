# ------- Autor - Gabriel Ferreira - 16.1.8213 ------- Servidor ----------
import time
import datetime
import socket


# Define o id deste computador pelo ip
computers_master = socket.gethostbyname(socket.gethostname())

# -------------- Server -------------------
#################### Solicita o time dos clientes
def getClientTime():
    print(' -------- Metodo: getClientTime ----------')
    return datetime.datetime.now().time()
    #print('1 - selecionar os computadores clientes')
    #print('2 - pedir o timer para cada cliente e inserir em um vetor')
    #print('3 - retornar uma tupla com o id cliente e a hora')

#################### Calcula o novo relógio
def calcTimer(clientTimers):
    print(' -------- Metodo: calcTimer ----------')
    #print('1 - tratar a tupla com os ids clientes e os relógios')
    #print('2 - calcular a media dos RTT e relógios')
    #print('3 - retornar o novo relogio')

def sendTimerToClients(newTimer):
    print(' -------- Metodo: sendTimerToClients ----------')
    #print('1 - Pega os computadores clientes')
    #print('2 - envia o relogio para cada cliente')

def sendMasterIdToClients():
    print('---- Enviando Master ID para os clientes ----')
    #CRIAR METRICA DE ENVIO DE DAS MSG DE ATUALIZAÇÃO DO MASTER
