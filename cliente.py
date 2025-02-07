import socket
import time
import math

HOST = '192.168.1.158'
PORT = 5000


def connect_to_server():
    """Tenta conectar ao servidor e retorna o socket conectado"""
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((HOST, PORT))
            print("Conectado ao servidor!")
            return client_socket
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")
            print("Tentando reconectar em 5 segundos...")
            time.sleep(5)


def check_prime(number, start, end):
    """Verifica se há algum divisor do número no intervalo especificado"""
    for i in range(start, end):
        if number % i == 0:
            return f"NOT_PRIME,{i}"
    return "PRIME"


while True:
    client_socket = connect_to_server()

    try:
        while True:
            data = client_socket.recv(1024).decode()

            if not data:
                print("Conexão fechada pelo servidor.")
                break

            if data == "PING":
                # client_socket.sendall(b"ALIVE")
                continue

            try:
                # Verifica se o formato recebido é válido
                number, start, end = map(int, data.split(','))
                print(f"Processando intervalo {start} - {end} para o número {number}")
                result = check_prime(number, start, end)
                client_socket.sendall(result.encode())
            except ValueError:
                print("Recebido um dado inválido do servidor.")
                continue

    except Exception as e:
        print(f"Erro na comunicação com o servidor: {e}")

    print("Reconectando...")
    time.sleep(5)
