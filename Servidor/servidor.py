import socket
import threading
import math
import time
from concurrent.futures import ThreadPoolExecutor

HOST = 'localhost'
PORT = 5000

# Criando o socket do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Servidor aguardando conexões de clientes...")

clients = []

def accept_clients():
    """Função para aceitar conexões de clientes dinamicamente"""
    while True:
        conn, addr = server.accept()
        clients.append((conn, addr))
        print(f"Cliente conectado: {addr}")

# Inicia uma thread para aceitar clientes em paralelo
threading.Thread(target=accept_clients, daemon=True).start()

def distribute_task(number):
    """Função para distribuir a tarefa entre os clientes conectados"""
    if not clients:
        print("Aguardando pelo menos um cliente conectar...")
        while not clients:  # Espera até ter pelo menos um cliente
            pass

    num_clients = len(clients)  # Conta quantos clientes estão ativos
    print(f"Distribuindo a tarefa para {num_clients} clientes ativos...")

    is_prime = True
    start_time = time.perf_counter()  # Inicia o cronômetro

    # Divide o intervalo de 2 até sqrt(number) entre os clientes disponíveis
    step = max(1, math.isqrt(number) // num_clients)

    # Usando ThreadPoolExecutor para gerenciar as threads de clientes
    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        # Envia a tarefa para os clientes
        future_to_conn = {}
        for i, (conn, addr) in enumerate(clients):
            start = 2 + i * step
            end = start + step if i < num_clients - 1 else math.isqrt(number) + 1
            try:
                future = executor.submit(send_task, conn, number, start, end)  # Envia a tarefa de forma assíncrona
                future_to_conn[future] = conn
            except Exception as e:
                print(f"Erro ao enviar tarefa para o cliente {addr}: {e}")

        # Espera pelas respostas de todos os clientes
        for future in future_to_conn:
            conn = future_to_conn[future]
            try:
                response = future.result()  # Aguarda o resultado da tarefa
                if response.startswith("NOT_PRIME"):
                    divisor = response.split(",")[1]
                    print(f"Cliente {conn.getpeername()} detectou que {number} NÃO é primo, divisor encontrado: {divisor}")
                    is_prime = False
                else:
                    print(f"Cliente {conn.getpeername()} não encontrou divisores no intervalo!")
            except Exception as e:
                print(f"Erro ao receber resposta do cliente {conn.getpeername()}: {e}")

    # Exibe o resultado final
    if is_prime:
        print(f"O número {number} é primo!")
    else:
        print(f"O número {number} NÃO é primo!")

    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000  # Converte para milissegundos
    print(f"Tempo total de execução: {elapsed_time:.2f} milissegundos")

def send_task(conn, number, start, end):
    """Função auxiliar para enviar a tarefa a um cliente"""
    try:
        conn.sendall(f"{number},{start},{end}".encode())  # Envia a tarefa para o cliente
        response = conn.recv(1024).decode()  # Recebe a resposta do cliente
        return response
    except Exception as e:
        return f"Erro ao comunicar com o cliente: {e}"

# O usuário digita o número para verificação quando quiser
while True:
    number = int(input("Digite o número para verificar se é primo (ou 0 para sair): "))
    if number == 0:
        break  # Sai do programa
    distribute_task(number)
