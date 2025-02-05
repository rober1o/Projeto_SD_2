import socket

HOST = 'localhost'
PORT = 5000

def is_prime_range(number, start, end):
    """Verifica se number é divisível por algum número no intervalo [start, end]"""
    for i in range(start, end):
        if number % i == 0:
            return False
    return True

# Conectar ao servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Receber dados
data = client.recv(1024).decode()
number, start, end = map(int, data.split(','))

# Processar se é primo na faixa designada
if is_prime_range(number, start, end):
    client.sendall("PRIME".encode())
else:
    client.sendall("NOT_PRIME".encode())

client.close()
