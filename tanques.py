from opcua import Client
from opcua.ua import AttributeIds
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import atexit

plt.rcParams['figure.figsize'] = (8,4)

running = True
sem = threading.Semaphore()


##################
# cria o client
client = Client("opc.tcp://localhost:53530/OPCUA/SimulationServer")

client.connect()

# Obtém uma lista de servidores disponíveis na rede
servers = client.find_servers()
for server in servers:
	print("Server URI:", server.ApplicationUri)
	print("Server ProductURI:", server.ProductUri)
	print("Discovery URLs:", server.DiscoveryUrls)
	print("\n")

node1 = client.get_node("ns=3;s=h1ref") #obtenção dos nodes das referências para o pcrocesso
node2 = client.get_node("ns=3;s=h2ref")
node3 = client.get_node("ns=3;s=h3ref")
ref1 = node1.get_value()
ref2 = node2.get_value()
ref3 = node3.get_value()

leitura1 = client.get_node("ns=3;s=h1pv")   #obtenção dos nodes que transmitem as PV's 
leitura2 = client.get_node("ns=3;s=h2pv")
leitura3 = client.get_node("ns=3;s=h3pv")



###Parametros dos tanques
H1, H2, H3 = 10, 10, 10 #altura máxima
r1, r2, r3 = 1, 1, 1  #raio inferior
R1, R2, R3 = 3, 3, 3  #raio superior
gamma = [0.4, 0.4, 0.4]  #coef de vazão nas saídas
pi = np.pi
hyst = [[], [], []]
q_in =[0, 0, 0]
q_out = [0, 0, 0]
###Condições iniciais
h0 = 3
h = [h0, 4, 5]

def exit_function():
    global running
    running = False
    print("Shutdown!")


class tanques(threading.Thread):  #classe da thread "tanques"
    def __init__(self):
        super(tanques, self).__init__()
        self.T = 5  #Período
        self.running = True

    def run(self):
        while self.running:
            for i in range(len(q_out)):
                q_out[i] = gamma[i] * np.sqrt(h[i])

            dh1_dt = (q_in[0] - q_out[0] - q_in[1]) / (pi * (r1 + ((R1 - r1) / H1) * h[0])**2)  # equações da dinâmica
            dh2_dt = (q_in[1] - q_out[1] - q_in[2]) / (pi * (r2 + ((R2 - r2) / H2) * h[1])**2)
            dh3_dt = (q_in[2] - q_out[2]) / (pi * (r3 + ((R3 - r3) / H3) * h[2])**2)  
            h[0]+=dh1_dt
            h[1]+=dh2_dt
            h[2]+=dh3_dt

            hyst[0].append(h[0])    # atualização dos valores no servidor OPC
            hyst[1].append(h[1])
            hyst[2].append(h[2])
            leitura1.set_value(h[0])
            leitura2.set_value(h[1])
            leitura3.set_value(h[2])

            time.sleep(self.T)
            if(not running): self.running = False
            


class controle(threading.Thread): #classe da thread "controle"
    def __init__ (self):
        super(controle, self).__init__()
        self.T = 1 #Período
        self.kp = [10, 10, 10]
        self.ki = [0.1, 0.1, 0.1]
        self.running = True
    
    def run(self):
        c_error = []
        i_term = [0, 0, 0]
        while self.running:
            try:
                c_in = [ref1, ref2, ref3]
                
                #receber valores de href do servidor pelo cliente
                c_error = [c_in[i] - h[i] for i in range(3)]
            except:
                continue
            # implementação do controlador PI
            for i in range(len(c_error)):
                # Termo integral
                i_term[i] += c_error[i] * self.ki[i] * self.T

                # Sinal de controle
                q_in[i] = self.kp[i] * c_error[i] + i_term[i]
            time.sleep(self.T)
            if(not running): self.running = False


if __name__ == "__main__":
    atexit.register(exit_function, )
    th1 = tanques()
    th1.start()
    th2 = controle()
    th2.start()
    plt.ion()
    plt.figure(1)
    while(th1.running & th2.running):
        # Gerando gráfico da simulação
        
        plt.clf()
        plt.plot(hyst[0][-50:], label='h1',marker='o')
        plt.plot(hyst[1][-50:], label='h2',marker='o')
        plt.plot(hyst[2][-50:], label='h3',marker='o')
        plt.title('Processo')
        plt.ylim([-1., 13.])
        plt.show()
        plt.pause(1.0)

    plt.ioff()
    th1.join()
    th2.join()
    print("Simulação encerrada.")
    client.disconnect()