# ------- Autor - Gabriel Ferreira - 16.1.8213
import time
import datetime
import socket
#import nmap3 #Library para encontrar os hosts na rede

# Define os Id's dos computadores na rede
computers_available = ['192.168.1.9','192.168.1.10','192.168.1.11']

# SOCKT PORT
PORT = 1997

# Define o id deste computador pelo ip
computer_id = '192.168.1.13' #socket.gethostbyname(socket.gethostname())
print(' ************** Computer ID: %s ***********' % computer_id)
#define o master inicial
computers_master = '192.168.1.13'

def main():
    #getComputersId()
    
    while True:
        #Verifica se o computador é o servidor
        if computers_master == computer_id: #Implementar temporizador para pedir uma atualização a cada 10s
            sendMasterIdToClients(computers_available)
            clientTimers = getClientTime() # solicitará o relógio dos clientes
            newTimer = calcTimer(clientTimers) # Calcula o novo timer do grupo
            sendTimerToClients(newTimer)
            time.sleep(10)
            
        # Caso o servidor seja o cliente
        elif master_is_alive(computers_master):
            print('********* CLIENTE ********** \n')
            # Define o Socket e abre a porta especificada
            skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
            client_address = (computer_id, PORT)   # IP do servidor e porta de comunicação
            print(f'>>>> Escutando em IP do Clinte: {client_address[0]}, Porta: {client_address[1]}')
            skt.bind(client_address)

            try:
                print('Aguardando requisições ...')
                skt.settimeout(15)   #Aguarda a requisição por 15s
                data, address = skt.recvfrom(1460)
                data.decode().split(' ')

                if data == 'getClock':
                    skt.sendto(getClock(), address)
                    print('------ Relogio Enviado ------')
                elif data == 'setMaster':
                    print('------ Master atualizado =>>> %s ------' % data)
            except:
                print('------ Nenhum pacote recebido! ------')
                
        else:
            askElection() # Pede uma nova eleição caso o servidor não esteja ativo - Bully


# -------------- Utils --------------------
#def getComputersId():
    #nm = nmap3.NmapScanTechniques()
    #results = nm.nmap_tcp_scan('192.168.1.0/24')
    #print(results)


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

def sendMasterIdToClients(clientsToSend):
    print('---- Enviando Master ID para os clientes ----')
    #CRIAR METRICA DE ENVIO DE DAS MSG DE ATUALIZAÇÃO DO MASTER
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
    master_address = (computers_master, PORT)   # IP do servidor e porta de comunicação
    for ip in clientsToSend:
        msg = 'setMaster %s:%s' % master_address
        print(msg)
        skt.sendto(msg.encode(), (ip, PORT))
        print('Enviando Master ID => %s' % ip)

    #print(f'>>>> Escutando em IP do Servidor: {master_address[0]}, Porta: {master_address[1]}')
    #skt.bind(master_address)


# --------- Client -------------
######################## Verifica se o master está ativo
def master_is_alive(master):
    print(' -------- Metodo: master_is_alive ----------')
    timeout = 0 #Timeout inicial; Sem timeout
    print('1 - Enviar uma msg de confirmação para o servidor e espera pela resposta dado um setTimeout')
    if timeout:
        return False
    else:
        return True

################## Solicita a eleição
def askElection(): # Implementação do algoritmo Bully
    print(' -------- Metodo: askElection ----------')
    reponseIds = []

    # receber um lista com a respota dos IDs maiores
    reponseIds = print('1 - Envia mensagem de eleição para todos os processos com id maior. *É necessário congelar a eleição dos ids menores, pois podem perceber o que o servidor caiu*')

    if not reponseIds: #caso ninguem responda, o cliente tornará o master
        setMaster(computer_id)

###################### Define o master
def setMaster(computer_id):
    global computers_master
    computers_master = computer_id
    print('------------- Novo Master: %s -------------' % computer_id)

#################### Recebe a definição do relógio do master
def setClock():
    print(' ------- Metodo: setClock ----------')

################# Envia o relógio do
def getClock():
    print(' -------- Metodo: getClock ----------')
    return datetime.datetime.now().time()
# ---------- Inicial do programa ----------
if __name__ == "__main__":
    main()