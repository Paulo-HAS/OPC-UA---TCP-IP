import threading
import socket
import re
import asyncio
from opcua import Client
import time
import atexit

running = True
lock = threading.Lock()

# Configurações do cliente OPC
OPC_SERVER_URL = "opc.tcp://localhost:53530/OPCUA/SimulationServer"  # Endereço do servidor OPC

# Configurações do servidor TCP/IP
TCP_ADDRESS = "127.0.0.1"  # Escuta em todas as interfaces de rede
TCP_PORT = 8080       # Porta do servidor TCP
BUFFER_SIZE = 1024

##Var de tunneling
comm_href = [7, 8, 6] #valores iniciais (para teste)
h = [0, 0, 0]



def exit_function():
    global running
    running = True
    print("Shutdown!")


class OPCClientThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.client = Client(OPC_SERVER_URL)
        self.running = True
        self.href = [self.client.get_node("ns=3;s=h1ref"), #nodes do sinal de referência
                        self.client.get_node("ns=3;s=h2ref"), 
                        self.client.get_node("ns=3;s=h3ref")]
        self.pv = [self.client.get_node("ns=3;s=h1pv"),     #nodes da leitura dos PV's
                    self.client.get_node("ns=3;s=h2pv"), 
                    self.client.get_node("ns=3;s=h3pv")]

    def run(self):
        try:
            self.client.connect()
            print(f"Conectado ao servidor OPC em {OPC_SERVER_URL}")

            while self.running:
                try:
                    global h
                    h = [float("{:.2f}".format(self.pv[0].get_value())), float("{:.2f}".format(self.pv[1].get_value())), float("{:.2f}".format(self.pv[2].get_value()))] #valores lidos nos sensores
                    print(f"Altura do tanque 1: {h[0]}")
                    print(f"Altura do tanque 2: {h[1]}")
                    print(f"Altura do tanque 3: {h[2]}")
                    
                    time.sleep(1)
                    if(not running): self.running = False
                except Exception as e:
                    print(f"Erro na comunicação OPC: {e}")
        finally:
            self.client.disconnect()
            print("Cliente OPC desconectado.")

    # método para mudança de referência
    def mudar_ref(self, href):
        try:
            for i in range(len(href)):
                self.href[i].set_value(href[i])
        except:
            pass



class TCPServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        
        self.socket.bind((TCP_ADDRESS, TCP_PORT))
        self.socket.listen(5)
        print(f"Servidor TCP ouvindo em {TCP_ADDRESS}:{TCP_PORT}")

        
        try:
            conn, addr = self.socket.accept()
            print(f"Conexão aceita de {addr}")
            while self.running:
                self.handle_client(conn)
                if(not running): self.running = False
        except Exception as e:
            print(f"Erro no servidor TCP: {e}")

        self.socket.close()

    # Processamento do cliente TCP
    def handle_client(self, conn):
        global h
        with conn:
            
            # criação da thread de recebimento
            receive_thread = threading.Thread(target=self.command, args=(conn,))
            receive_thread.start()
            while True:
                try:
                    #enviando leitura ao cliente
                    data_to_send = f"Altura Tanque 1: {h[0]} | Altura Tanque 2: {h[1]} | Altura Tanque 3: {h[2]}\n"
                    print(data_to_send)
                    with lock:
                        conn.send(data_to_send.encode())
                    time.sleep(1)
                    

                except Exception as e:
                    print(f"Erro ao tratar cliente TCP: {e}")
                    break
            receive_thread.join()
    
    def command(self, conn):
        data = None
        while True:
            try:
                with lock:
                    data = self.socket.recv(BUFFER_SIZE).decode().strip()
                    print(f"Novo setpoint recebido: {data}")
                    novo_sp = list(map(float, re.findall(r'\d+\.\d+', data)))
                    OPCClientThread.mudar_ref(novo_sp)
                time.sleep(1)
            except Exception as e:
                print(f'Recebimento de mensagem falhou: {data}|||{e}')
                time.sleep(10)




if __name__ == "__main__":
    atexit.register(exit_function, )
    try:
        # Inicializar threads
        opc_thread = OPCClientThread()
        tcp_thread = TCPServerThread()

        opc_thread.start()
        tcp_thread.start()
        opc_thread.mudar_ref(comm_href)
        print("CLP em execução. Pressione Ctrl+C para encerrar.")

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando CLP...")
        opc_thread.running = False
        tcp_thread.running = False
        opc_thread.join()
        tcp_thread.join()
        print("CLP encerrado por interrupção.")
