import socket  # Biblioteca para comunicação via rede (sockets)
import threading  # Biblioteca para lidar com threads (execução paralela)
import math  # Biblioteca matemática, usada para calcular a raiz quadrada
import time  # Biblioteca para medir tempo de execução
from concurrent.futures import ThreadPoolExecutor  # Gerenciador de threads para tarefas paralelas
# Define o endereço e porta do servidor
HOST = '192.168.206.107'  
PORT = 5000  

# Cria um socket do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET -> IPv4, SOCK_STREAM -> TCP
server.bind((HOST, PORT))  # Associa o socket ao IP e porta
server.listen()  # Coloca o servidor para escutar conexões

print("Servidor aguardando conexões de clientes...")

# Lista para armazenar os clientes conectados
clients = []
clients_lock = threading.Lock()  # Lock para evitar problemas com múltiplas threads acessando a lista
stop_flag = threading.Event()  # Flag para interromper a execução

def accept_clients():
    """Função para aceitar conexões de clientes dinamicamente"""
    while True:
        conn, addr = server.accept()  # Aguarda um cliente conectar
        with clients_lock:  # Garante acesso seguro à lista de clientes
            clients.append((conn, addr))  # Adiciona o cliente à lista
        print(f"Cliente conectado: {addr}")  # Exibe o endereço do cliente conectado

# Inicia uma thread para aceitar clientes continuamente, sem bloquear a execução principal
threading.Thread(target=accept_clients, daemon=True).start()

def is_client_connected(conn):
    """Verifica se o cliente ainda está conectado enviando um PING"""
    try:
        conn.sendall(b"PING")  # Envia uma mensagem de teste
        return True  # Cliente está ativo se não houver erro
    except:
        return False  # Cliente foi desconectado se ocorrer erro

def distribute_task(number):
    """Função para distribuir a verificação de primalidade entre os clientes conectados"""
    
    if number < 2:  # Verifica se o número é válido
        print("O número deve ser maior ou igual a 2.")
        return

    with clients_lock:  # Acessa a lista de clientes de forma segura
        # Remove clientes desconectados antes de distribuir tarefas
        active_clients = [c for c in clients if is_client_connected(c[0])]
    
    if not active_clients:  # Se não houver clientes ativos, cancela a distribuição da tarefa
        print("Nenhum cliente disponível para processar a tarefa.")
        return

    num_clients = len(active_clients)  # Número de clientes disponíveis
    print(f"Distribuindo a tarefa para {num_clients} clientes ativos...")

    is_prime = True  # Assume que o número é primo até encontrar um divisor
    start_time = time.perf_counter()  # Marca o início do tempo de execução

    step = max(1, math.isqrt(number) // num_clients)  # Define o tamanho do intervalo para cada cliente

    with ThreadPoolExecutor(max_workers=num_clients) as executor:  # Cria um pool de threads para gerenciar os clientes
        future_to_conn = {}  # Dicionário para armazenar as tarefas enviadas aos clientes
        
        for i, (conn, addr) in enumerate(active_clients):
            start = 2 + i * step  # Define o início do intervalo para o cliente
            end = min(start + step, math.isqrt(number) + 1)  # Define o fim do intervalo
            
            if start >= end:  # Garante que o intervalo é válido
                continue

            try:
                # Envia a tarefa ao cliente e associa o futuro à conexão correspondente
                future = executor.submit(send_task, conn, number, start, end)
                future_to_conn[future] = conn
            except Exception as e:
                print(f"Erro ao enviar tarefa para o cliente {addr}: {e}")

        for future in future_to_conn:  # Processa as respostas dos clientes
            conn = future_to_conn[future]
            try:
                response = future.result()  # Obtém a resposta do cliente
                
                if response.startswith("NOT_PRIME"):  # Se um cliente encontrou um divisor
                    divisor = response.split(",")[1]  # Extrai o divisor encontrado
                    print(f"Cliente {conn.getpeername()} detectou que {number} NÃO é primo, divisor encontrado: {divisor}")
                    is_prime = False

                    # Enviar um sinal de parada para todos os clientes ativos
                    for c, _ in active_clients:
                        try:
                            c.sendall(b"STOP")  # Envia um sinal para os clientes pararem
                        except Exception as e:
                            print(f"Erro ao encerrar cliente {c.getpeername()}: {e}")
                    
                    break  # Sai do loop após notificar os clientes
                
                elif response == "PRIME":  # Cliente não encontrou divisores
                    print(f"Cliente {conn.getpeername()} não encontrou divisores no intervalo.")
                
                else:  # Caso a resposta seja inválida
                    print(f"Resposta inesperada do cliente {conn.getpeername()}: {response}")
            
            except Exception as e:
                print(f"Erro ao receber resposta do cliente {conn.getpeername()}: {e}")

    print(f"O número {number} é primo!" if is_prime else f"O número {number} NÃO é primo!")

    end_time = time.perf_counter()  # Marca o fim do tempo de execução
    elapsed_time = (end_time - start_time) * 1000  # Calcula o tempo total em milissegundos
    print(f"Tempo total de execução: {elapsed_time:.2f} milissegundos")
    print()
    print()

def send_task(conn, number, start, end):
    """Função auxiliar para enviar a tarefa a um cliente"""
    try:
        # Envia os dados ao cliente no formato "numero,inicio,fim"
        conn.sendall(f"{number},{start},{end}".encode())
        response = conn.recv(1024).decode()  # Recebe a resposta do cliente
        return response
    except Exception:
        # Se o cliente se desconectar, remove-o da lista
        with clients_lock:
            clients.remove((conn, conn.getpeername()))
        return "ERROR"

# Loop principal para receber números do usuário
while True:
    try:
        number = int(input("Digite o número para verificar se é primo (ou 0 para sair): "))  # Solicita um número ao usuário
        if number == 0:  # Se for 0, encerra o servidor
            break
        distribute_task(number)  # Chama a função para distribuir a tarefa
    except ValueError:  # Captura erro caso o usuário não digite um número válido
        print("Entrada inválida. Digite um número inteiro.")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET -> IPv4, SOCK_STREAM -> TCP
server.bind((HOST, PORT))  # Associa o socket ao IP e porta
server.listen()  # Coloca o servidor para escutar conexões

print("Servidor aguardando conexões de clientes...")

# Lista para armazenar os clientes conectados
clients = []
clients_lock = threading.Lock()  # Lock para evitar problemas com múltiplas threads acessando a lista
stop_flag = threading.Event()  # Flag para interromper a execução

def accept_clients():
    """Função para aceitar conexões de clientes dinamicamente"""
    while True:
        conn, addr = server.accept()  # Aguarda um cliente conectar
        with clients_lock:  # Garante acesso seguro à lista de clientes
            clients.append((conn, addr))  # Adiciona o cliente à lista
        print(f"Cliente conectado: {addr}")  # Exibe o endereço do cliente conectado

# Inicia uma thread para aceitar clientes continuamente, sem bloquear a execução principal
threading.Thread(target=accept_clients, daemon=True).start()

def is_client_connected(conn):
    """Verifica se o cliente ainda está conectado enviando um PING"""
    try:
        conn.sendall(b"PING")  # Envia uma mensagem de teste
        return True  # Cliente está ativo se não houver erro
    except:
        return False  # Cliente foi desconectado se ocorrer erro

def distribute_task(number):
    """Função para distribuir a verificação de primalidade entre os clientes conectados"""
    
    if number < 2:
        print("O número deve ser maior ou igual a 2.")
        return

    with clients_lock:
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
            end = min(start + step, math.isqrt(number) + 1)

            if start >= end:
                continue

            try:
                future = executor.submit(send_task, conn, number, start, end)
                future_to_conn[future] = conn
            except Exception as e:
                print(f"Erro ao enviar tarefa para {addr}: {e}")

        for future in future_to_conn:
            conn = future_to_conn[future]
            try:
                response = future.result()
                
                if response.startswith("NOT_PRIME"):
                    divisor = response.split(",")[1]
                    print(f"Cliente {conn.getpeername()} detectou que {number} NÃO é primo, divisor encontrado: {divisor}")
                    is_prime = False

                    # 🚨 **Enviar "STOP" para todos os clientes imediatamente**
                    for c, _ in active_clients:
                        try:
                            c.sendall(b"STOP")
                        except Exception as e:
                            print(f"Erro ao encerrar cliente {c.getpeername()}: {e}")
                    
                    break  # Interrompe a execução

                elif response == "PRIME":
                    print(f"Cliente {conn.getpeername()} não encontrou divisores no intervalo.")
                
                else:
                    print(f"Resposta inesperada do cliente {conn.getpeername()}: {response}")

            except Exception as e:
                print(f"Erro ao receber resposta do cliente {conn.getpeername()}: {e}")

    print(f"O número {number} é primo!" if is_prime else f"O número {number} NÃO é primo!")

    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000
    print(f"Tempo total de execução: {elapsed_time:.2f} milissegundos\n\n")

    print()
    print()

def send_task(conn, number, start, end):
    """Função auxiliar para enviar a tarefa a um cliente"""
    try:
        # Envia os dados ao cliente no formato "numero,inicio,fim"
        conn.sendall(f"{number},{start},{end}".encode())
        response = conn.recv(1024).decode()  # Recebe a resposta do cliente
        return response
    except Exception:
        # Se o cliente se desconectar, remove-o da lista
        with clients_lock:
            clients.remove((conn, conn.getpeername()))
        return "ERROR"

# Loop principal para receber números do usuário
while True:
    try:
        number = int(input("Digite o número para verificar se é primo (ou 0 para sair): "))  # Solicita um número ao usuário
        if number == 0:  # Se for 0, encerra o servidor
            break
        distribute_task(number)  # Chama a função para distribuir a tarefa
    except ValueError:  # Captura erro caso o usuário não digite um número válido
        print("Entrada inválida. Digite um número inteiro.")
