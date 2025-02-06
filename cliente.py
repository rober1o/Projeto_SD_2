import socket
import math

HOST = 'localhost'
PORT = 5000

def is_prime_range(number, start, end):
    """Verifica se number é divisível por algum número no intervalo [start, end]"""
    for i in range(start, end):
        if number % i == 0:
            return i  # Retorna o divisor encontrado
    return None  # Retorna None se não encontrar div3isores, ou seja, é primo

# Conectar ao servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print("Cliente conectado e aguardando tarefas...")

while True:
    try:
        # Receber dados do servidor
        data = client.recv(1024).decode()
        
        if not data:  # Se não houver dados, significa que o servidor desconectou
            print("Servidor desconectado. Finalizando cliente...")
            break

        # Parse dos dados recebidos (número, start e end)
        try:
            number, start, end = map(int, data.split(','))
        except ValueError:
            print("Formato inválido de dados recebidos. Ignorando...")
            continue  # Pular iteração em caso de erro de formatação

        # Processar se o número é primo na faixa designada e encontrar divisor, se houver
        divisor = is_prime_range(number, start, end)

        if divisor:
            # Envia que não é primo e o divisor encontrado, com a informação do intervalo
            client.sendall(f"NOT_PRIME,{divisor}".encode())
        else:
            # Envia que é primo, com a informação do intervalo
            client.sendall("PRIME".encode())

        # Aguarde pela próxima tarefa
        print(f"Cliente completou a tarefa para o número {number}. Aguardando nova tarefa...")

    except Exception as e:
        print(f"Erro na comunicação com o servidor: {e}")
        break

# Fechar a conexão após o processamento
client.close()
