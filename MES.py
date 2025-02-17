from opcua import Client
from opcua.ua import AttributeIds
import time


MES_FILE = "mes.txt"

#################
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

leitura1 = client.get_node("ns=3;s=h1pv")   #obtenção dos nodes que transmitem as PV's 
leitura2 = client.get_node("ns=3;s=h2pv")
leitura3 = client.get_node("ns=3;s=h3pv")

if __name__ == "__main__":
	while True:
		with open(MES_FILE, "a") as file:
			message = f"Altura Tanque 1 : {float("{:.2f}".format(leitura1.get_value()))} | Altura Tanque 2: {float("{:.2f}".format(leitura2.get_value()))} | Altura Tanque 3: {float("{:.2f}".format(leitura3.get_value()))}\n"
			file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
			time.sleep(1)