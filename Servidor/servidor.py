import socket
import threading
import math
import time
from concurrent.futures import ThreadPoolExecutor

HOST = '192.168.1.158'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Servidor aguardando conexões de clientes...")

clients = []
clients_lock = threading.Lock()  # Para evitar problemas de concorrência


def accept_clients():
    """Função para aceitar conexões de clientes dinamicamente"""
    while True:
        conn, addr = server.accept()
        with clients_lock:
            clients.append((conn, addr))
        print(f"Cliente conectado: {addr}")


# Inicia uma thread para aceitar clientes em paralelo
threading.Thread(target=accept_clients, daemon=True).start()


def is_client_connected(conn):
    """Verifica se o cliente ainda está conectado enviando um PING"""
    try:
        conn.sendall(b"PING")
        return True
    except:
        return False


def distribute_task(number):
    """Função para distribuir a tarefa entre os clientes conectados"""
    with clients_lock:
        # Remove clientes desconectados antes de distribuir tarefas
        active_clients = [c for c in clients if is_client_connected(c[0])]
    
    if not active_clients:
        print("Nenhum cliente disponível para processar a tarefa.")
        return

    num_clients = len(active_clients)
    print(f"Distribuindo a tarefa para {num_clients} clientes ativos...")

    is_prime = True
    start_time = time.perf_counter()

    step = max(1, math.isqrt(number) // num_clients)

    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        future_to_conn = {}
        for i, (conn, addr) in enumerate(active_clients):
            start = 2 + i * step
            end = start + step if i < num_clients - 1 else math.isqrt(number) + 1
            try:
                future = executor.submit(send_task, conn, number, start, end)
                future_to_conn[future] = conn
            except Exception as e:
                print(f"Erro ao enviar tarefa para o cliente {addr}: {e}")

        for future in future_to_conn:
            conn = future_to_conn[future]
            try:
                response = future.result()
                if response.startswith("NOT_PRIME"):
                    divisor = response.split(",")[1]
                    print(f"Cliente {conn.getpeername()} detectou que {number} NÃO é primo, divisor encontrado: {divisor}")
                    is_prime = False
                    break
                else:
                    print(f"Cliente {conn.getpeername()} não encontrou divisores no intervalo.")
            except Exception as e:
                print(f"Erro ao receber resposta do cliente {conn.getpeername()}: {e}")

    print(f"O número {number} é primo!" if is_prime else f"O número {number} NÃO é primo!")

    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000
    print(f"Tempo total de execução: {elapsed_time:.2f} milissegundos")


def send_task(conn, number, start, end):
    """Função auxiliar para enviar a tarefa a um cliente"""
    try:
        conn.sendall(f"{number},{start},{end}".encode())
        response = conn.recv(1024).decode()
        return response
    except Exception:
        with clients_lock:
            clients.remove((conn, conn.getpeername()))
        return "ERROR"


while True:
    try:
        number = int(input("Digite o número para verificar se é primo (ou 0 para sair): "))
        if number == 0:
            break
        distribute_task(number)
    except ValueError:
        print("Entrada inválida. Digite um número inteiro.")
