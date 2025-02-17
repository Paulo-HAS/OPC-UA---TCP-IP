# OPC-UA---TCP-IP
Sistema distribuído de controle industrial com interfaceamento entre redes OPC UA e TCP/IP

Neste projeto, se propõe a criação de um software em Python de interface entre a
rede de controle de um sistema simulado de três tanques, que se comunica por uma rede
OPC UA (com servidor simulado pelo programa Prosys OPC UA Simulation Server), com
um sistema supervisório que opera por conexão TCP/IP.

Intruções:

Instalar O "Prosys OPC UA Simulation Server"

Criar os nodes "h1ref, h2ref, h3ref, h1pv, h2pv, h3pv" como no tipo BaseDataType e com a opção de identificação por nome ativada.

Executar na ordem:

tanques.py> CLP.py> MES.py> cliente_tcp.py
