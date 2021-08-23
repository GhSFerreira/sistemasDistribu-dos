# ------- Autor - Gabriel Ferreira - 16.1.8213
import time
import datetime
import socket


##################### VARIABLES #################
# SOCKT PORT
PORT = 1997

# Define o id deste computador pelo ip
computer_id = '192.168.2.23' #socket.gethostbyname(socket.gethostname())

#define o master inicial
computers_master = '192.168.2.23'

# Define os Id's dos computadores na rede
computers_available = ['192.168.2.28', '192.168.2.23', '192.168.2.30', '192.168.2.27']

# Remove o ID do computador que executa o programa dá lista de compuptadores disponiveis
computers_toSend = computers_available[:]
computers_toSend.remove(computer_id)

###################################################

def main():
    print(' ************** Computer ID: %s ***********' % computer_id)
    
    while True:
        #Verifica se o computador é o servidor
        if computers_master == computer_id: 
            clientTimers = getClientTimers(computers_toSend)
            #clientTimers = getClientTime() # solicitará o relógio dos clientes
            newTimer = calcTimer(clientTimers) # Calcula o novo timer do grupo
            sendTimerToClients(newTimer)
            print(' \n -------- Tempo de Espera 10 Segundos ---------')
            time.sleep(10)
            
        # Caso o servidor seja o cliente
        else:
            print('********* CLIENTE ********** \n')
            # Define o Socket e abre a porta especificada
            skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
            client_address = (computer_id, PORT)   # IP do servidor e porta de comunicação
            print(f'>>>> Escutando em IP do Clinte: {client_address[0]}, Porta: {client_address[1]}')
            skt.bind(client_address)

            try:
                print('Aguardando requisições ...')
                skt.settimeout(45)   #Aguarda a requisição por 15s
                data, address = skt.recvfrom(1460)

                info = data.decode().split()
                print(info)

                if info[0] == 'setMaster':
                    skt.sendto(getClock().encode(), address)
                    print('------ Relogio Enviado ------- ')
                    setMaster(info[1].split(':')[0])
                elif info[0] == 'setClock':
                    setClock(info[1])
                elif info[0] == 'election':
                    skt.sendto('OK'.encode(), address)
                    print('======= Votação Iniciada por IP: %s' % info[1])

            except socket.timeout:
                #Caso o tempo da repsosta demore, significa que o servidor caiu
                askElection() # Pede uma nova eleição caso o servidor não esteja ativo - Bully



# -------------- Utils --------------------

# -------------- Server -------------------
#################### Calcula o novo relógio
def calcTimer(clientTimers):
    print(' =========  Calcula o Timer Médio  =========')
    sumTimers = 0
    if not clientTimers:
        timer = datetime.datetime.now().strftime('%H:%M:%S')
        print('Nenhum relogio recebido! Atualizado com o horario do servidor: %s \n' % timer)
        return timer
    else:
        for time in clientTimers:
            pt = time.split(':')
            total_seconds = int(pt[2]) + int(pt[1])*60 + int(pt[0])*3600
            sumTimers += total_seconds
            print('Time in seconds: %s' % total_seconds)
        average = sumTimers / len(clientTimers)
        time_str = str(datetime.timedelta(seconds= average))
        print('Average Time: %s' % time_str)

        return time_str

def sendTimerToClients(newTimer):
    print('========== Enviando relógio para os clientes ============')
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
    client_address = (computers_master, PORT)   # IP do servidor e porta de comunicação    
    skt.bind(client_address)

    for ip in computers_toSend:
        print(' -------- ID: %s ----------' % ip)
        skt.sendto(('setClock ' + getClock()).encode(), (ip,PORT))
    

def getClientTimers(clientsToSend):
    print('========== Enviando Master ID para os clientes ============')

    clientTimers = []
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
    master_address = (computers_master, PORT)   # IP do servidor e porta de comunicação
    skt.bind(master_address)
    for ip in clientsToSend:
        msg = 'setMaster %s:%s' % master_address
        #print(msg)
        skt.sendto(msg.encode('utf-8'), (ip, PORT))
        print('Enviando Master ID => %s' % ip)
        try:
            print('\nAguardando resposta...')
            skt.settimeout(2)   #Aguarda a requisição por 15s
            data, address = skt.recvfrom(1460)
            data_str = str(data.decode())
            print(data_str)
            clientTimers.append(data_str)
        except socket.timeout:
            print('------- Nenhum pacote recebido para atualizar o Master ID --------')  
    
    return clientTimers

# --------- Client -------------
################## Solicita a eleição
def askElection(): # Implementação do algoritmo Bully
    print(' ---------- Iniciando Eleição ----------')
    reponseIds = []

    # receber um lista com a respota dos IDs maiores
    #print('1 - Envia mensagem de eleição para todos os processos com id maior. *É necessário congelar a eleição dos ids menores, pois podem perceber o que o servidor caiu*')
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
    client_address = (computer_id, PORT)   # IP do servidor e porta de comunicação
    skt.bind(client_address)

    for ip in computers_toSend:
        msg = 'election %s:%s' % client_address
        #print(msg)
        skt.sendto(msg.encode('utf-8'), (ip, PORT))
        print('------ Enviando Mensagem de Eleição enviada para o ID => %s -----------' % ip)
        try:
            print('Aguardando resposta da eleição...')
            skt.settimeout(2)   #Aguarda a requisição por 15s
            data, address = skt.recvfrom(1460)
            data_str = str(data.decode())
           
            if data_str == 'OK':
                print('Recebido resposta de => %s' % address)
                reponseIds.append(data_str)

        except socket.timeout:
            print('------ Nenhum pacote recebido! === getClientTime------')    

    if not reponseIds: #caso ninguem responda, o cliente tornará o master
        setMaster(computer_id)
    else:
        print(reponseIds)

###################### Define o master
def setMaster(computer_id):
    global computers_master
    computers_master = computer_id
    print('------------- Master Atualizado: %s -------------' % computer_id)

#################### Recebe a definição do relógio do master
def setClock(clock):
    print(' ------- Relógio Atualizado %s ----------' % clock)


################# Envia o relógio do
def getClock():
    return datetime.datetime.now().strftime('%H:%M:%S')
# ---------- Inicial do programa ----------
if __name__ == "__main__":
    main()