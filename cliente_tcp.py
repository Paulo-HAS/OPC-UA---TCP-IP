import socket
import time
import inputimeout
import os


# Configurações do cliente TCP/IP
SERVER_IP = "127.0.0.1"  # Endereço do servidor
SERVER_PORT = 8080        # Porta do servidor
BUFFER_SIZE = 1024        # Tamanho do buffer para recebimento de dados

# Nome do arquivo de registro
HISTORIADOR_FILE = "historiador.txt"

class TCPClient:
    def __init__(self):
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.socket.connect((SERVER_IP, SERVER_PORT))
            print(f"Conectado ao servidor TCP em {SERVER_IP}:{SERVER_PORT}")
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")
            self.running = False

    def send_data(self, values):   # método de envio de setpoint
        try:
            message = f"{values[0]} | {values[1]} | {values[2]}"
            self.socket.send(message.encode())
        except Exception as e:
            print(f"Erro ao enviar dados: {e}")

    def receive_data(self):     # método de recebimento dos PV's
        try:
            print('jooj')
            return self.socket.recv(BUFFER_SIZE).decode().strip()
        
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            return None

    def close(self):
        self.socket.close()

    def log_to_file(self, message):
        with open(HISTORIADOR_FILE, "a") as file:
            file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

    def run(self):
        self.connect()
        if not self.running:
            return

        try:
            while self.running:
                # Receber dados do servidor
                
                leitura = self.receive_data()
                os.system('cls') #limpar a tela do terminal
                print("Variáveis medidas:")
                print(leitura)
                self.log_to_file(leitura)
                print("Menu:")
                print("Escolha um dos comandos a seguir:")
                print("1 ) alterar setpoint \n2 ) ")
                print("0 ) Sair\n")
                try:
                    command = inputimeout.inputimeout(prompt='-->', timeout=0.9)
                    if command == '0':
                        print("Fechando Interface...")
                        self.running = False
                        break
                    elif command == '1':
                        v = [0, 0, 0]
                        print('Insira os novos valores de setpoint:')
                        v[0] = input('altura do tanque 1:')
                        v[1] = input('altura do tanque 2:')
                        v[2] = input('altura do tanque 3:')
                        self.send_data(v)
                        self.log_to_file(f"Setpoint alterado: {v}")
                    else:
                        pass
                except Exception as e:
                    print(e)
                    
    
            self.close()

        except KeyboardInterrupt:
            print("Cliente encerrado manualmente.")

        finally:
            self.close()
            print("Conexão encerrada.")

if __name__ == "__main__":
    print("Iniciando cliente TCP/IP.")
    client = TCPClient()
    client.run()
    print("Cliente finalizado.")
