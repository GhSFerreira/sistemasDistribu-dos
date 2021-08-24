# Implementação do algoritmo de Berkeley juntamente com o Algoritmo de Eleição (Bully)
#---------- Autor - Gabriel Ferreira - 16.1.8213 -----------


import time
import datetime
import socket


##################### VARIABLES #################
# SOCKT PORT
PORT = 1997

# Define o id deste computador pelo ip
computer_id = '192.168.2.23'

#define o master inicial
computers_master = ''

# Define os Id's dos computadores na rede
computers_available = ['192.168.2.28', '192.168.2.23', '192.168.2.30', '192.168.2.27']

# Remove o ID do computador que executa o programa dá lista de compuptadores disponiveis
computers_toSend = computers_available[:]
computers_toSend.remove(computer_id)

###################################################

def main():
    print(' ************** Computer ID: %s ***********' % computer_id)
    
    while True:
        #Verifica se o endereço do computador é o mesmo do master
        if computers_master == computer_id:
            print('********* MASTER ********** \n') 
            clientTimers = getClientTimers(computers_toSend)
            newTimer = calcTimer(clientTimers) # Calcula o novo timer do grupo com base na média de todos os relógios
            sendTimerToClients(newTimer)
            print(' \n -------- Tempo de Espera 10 Segundos ---------')
            time.sleep(10)
            
        # Se o IP do Master e o computador executante são siferente
        else:
            print('********* CLIENTE ********** \n')
            # Define o Socket e abre a porta especificada
            skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
            client_address = (computer_id, PORT)   # IP do servidor e porta de comunicação
            print(f'>>>> Escutando em IP do Clinte: {client_address[0]}, Porta: {client_address[1]}')
            skt.bind(client_address)

            try:
                #Inicia a escuta das chamadas vindas pelo master
                print('Aguardando requisições ...')
                skt.settimeout(15)   #Caso não receba uma solicitação em 15s, lança um timeout, sinalizando que o master caiu
                data, address = skt.recvfrom(1460)

                info = data.decode().split()
                print(info)

                if info[0] == 'setMaster': # Recebe uma msg de definição do Master
                    setMaster(info[1])
                elif info[0] == 'getClock': # Recebe uma msg para informar o relógio do sistema
                    print('------ Relogio Enviado ------- ')
                    skt.sendto(getClock().encode(), address)
                elif info[0] == 'setClock':  # Recebe uma msg para ajustar o relógio do sistema
                    setClock(info[1])
                elif info[0] == 'election':  # Solicita uma nova eleição
                    time.sleep(2)
                    skt.sendto(b'OK', address)  # Responde que concorda com a eleição
                    print('======= Votação Iniciada por IP: %s' % info[1])
                skt.close()
            except socket.timeout:
                #Com o timeout significa que o servidor caiu
                skt.close()

                askElection() # Pede uma nova eleição - Bully


# =================== Server =====================
# ----- Calcula o relógio a ser enviado com base na média dos relógios
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

# ----- Envia o relogio calculado e passado por parametro, à todos os clientes
def sendTimerToClients(newTimer):
    print('========== Enviando relógio para os clientes ============')
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
    client_address = (computers_master, PORT)   # IP do servidor e porta de comunicação    
    skt.bind(client_address)

    for ip in computers_toSend:
        print(' -------- ID: %s ----------' % ip)
        skt.sendto(('setClock ' + getClock()).encode(), (ip,PORT))
    skt.close()

# ------ Solicita o relógio de todos os computadores clientes
def getClientTimers(clientsToSend):
    print('========== Pedindo relogio para os clientes ============')

    clientTimers = []
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
    master_address = (computers_master, PORT)   # IP do servidor e porta de comunicação
    skt.bind(master_address)
    for ip in clientsToSend:
        msg = 'getClock'
        #print(msg)
        skt.sendto(msg.encode('utf-8'), (ip, PORT))
        print('Pedir relogio => %s' % ip)
        try:
            print('\nAguardando resposta...')
            skt.settimeout(2)   #Aguarda a requisição por 15s
            data, address = skt.recvfrom(1460)
            data_str = str(data.decode())
            print(data_str)
            clientTimers.append(data_str)
        except socket.timeout:
            print('------- Nenhum pacote recebido sobre o relogio --------')  
    skt.close()
    return clientTimers

# ------ Envia o endereço do Master para todos os clientes
def sendMasterToClients(clientsToSend, master):
    print('========== Enviando Master ID para os clientes ============')

    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
    ip_address = (computer_id, PORT)   # IP do servidor e porta de comunicação
    skt.bind(ip_address)
    for ip in clientsToSend:
        msg = 'setMaster %s' % master
        #print(msg)
        skt.sendto(msg.encode('utf-8'), (ip, PORT))
        print('Enviando Master ID => %s' % ip)
      
    skt.close()



# =================== Client =====================
#--------- Solicita a eleição
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
        skt.settimeout(3)   #Aguarda a requisição por 15s
        while True:
            print('Aguardando resposta da eleição...')
            data, address = skt.recvfrom(1460)
            data_str = str(data.decode())
           
            if data_str == 'OK':
                print('Recebido resposta de => ' + address[0])
                reponseIds.append(str(address[0]))
            else:
                break
    except socket.timeout:
        print('------ Nenhum pacote recebido! === getClientTime------')    

    skt.close()
    if not reponseIds: #caso ninguem responda, o cliente tornará o master
        setMaster(computer_id)
    else:
        #Seleciona o maior ip
        reponseIds.append(computer_id)
        ipList = []
        print(reponseIds)
        temp = ''
        for i in reponseIds:
            ipList.append(str(i).replace('.', ''))
        print(ipList)
        positionMaiorIp = ipList.index(max(ipList, key=int))
        maiorIp = reponseIds[positionMaiorIp]
        print(maiorIp)
        setMaster(maiorIp)

        #Envia o master para os clientes
        reponseIds.remove(computer_id)
        sendMasterToClients(reponseIds, maiorIp)

#--------- Define o endereço do Master no Cliente
def setMaster(computer_id):
    global computers_master
    computers_master = computer_id
    print('------------- Master Atualizado: %s -------------' % computer_id)

#--------- Atualiza o relógio
def setClock(clock):
    print(' ------- Relógio Atualizado %s ----------' % clock)

# --------- Retorna o relógio do sistema
def getClock():
    return datetime.datetime.now().strftime('%H:%M:%S')



# =================== Início =====================
if __name__ == "__main__":
    main()