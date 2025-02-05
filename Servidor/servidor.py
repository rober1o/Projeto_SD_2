import socket
import threading
import random

# Configurações do servidor
HOST = 'localhost'
PORT = 5000
NUM_CLIENTS = 3  # Número de clientes esperados

# Gera um número grande
BIG_NUMBER = random.getrandbits(50)  # Número aleatório de 50 bits
print(f"Servidor gerou o número: {BIG_NUMBER}")

# Lista para armazenar conexões
clients = []

def handle_client(conn, addr, start, end):
    """Função que delega um intervalo de verificação para um cliente"""
    try:
        conn.sendall(f"{BIG_NUMBER},{start},{end}".encode())  # Envia os dados
        response = conn.recv(1024).decode()  # Aguarda resposta
        if response == "NOT_PRIME":
            print(f"Cliente {addr} detectou que {BIG_NUMBER} NÃO é primo!")
            global is_prime
            is_prime = False
    finally:
        conn.close()

# Cria o socket do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(NUM_CLIENTS)

# Divide o intervalo de 2 até sqrt(BIG_NUMBER) entre os clientes
import math
is_prime = True
step = math.isqrt(BIG_NUMBER) // NUM_CLIENTS

for i in range(NUM_CLIENTS):
    conn, addr = server.accept()
    clients.append(conn)
    start = 2 + i * step
    end = start + step
    threading.Thread(target=handle_client, args=(conn, addr, start, end)).start()

# Aguarda todos os clientes finalizarem
server.close()

if is_prime:
    print(f"O número {BIG_NUMBER} é primo!")
else:
    print(f"O número {BIG_NUMBER} NÃO é primo!")
