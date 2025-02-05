import socket  # Biblioteca para comunicação entre cliente e servidor
import threading  # Para permitir múltiplos clientes simultaneamente
import math  # Para cálculos matemáticos (usado na verificação de primos)

# Função para verificar se um número é primo
def eh_primo(numero):
    if numero < 2:
        return False  # Números menores que 2 não são primos
    if numero in (2, 3):
        return True  # 2 e 3 são primos
    if numero % 2 == 0 or numero % 3 == 0:
        return False  # Números pares e múltiplos de 3 não são primos

    divisor = 5
    while divisor * divisor <= numero:  # Testa até a raiz quadrada do número
        if numero % divisor == 0 or numero % (divisor + 2) == 0:
            return False  # Se for divisível, não é primo
        divisor += 6  # Testa apenas números na forma 6k ± 1

    return True  # Se passou por todos os testes, é primo

# Função para lidar com cada cliente
def atender_cliente(conexao_cliente, endereco):
    print(f"[+] Nova conexão de {endereco}")  # Mensagem informando uma nova conexão

    while True:
        try:
            dados = conexao_cliente.recv(1024).decode()  # Recebe dados do cliente
            if not dados:
                break  # Encerra a conexão se não houver mais dados

            numero = int(dados)  # Converte a entrada do cliente para um número inteiro
            resultado = eh_primo(numero)  # Chama a função que verifica se é primo

            # Responde ao cliente se o número é primo ou não
            resposta = f"{numero} é primo" if resultado else f"{numero} não é primo"
            conexao_cliente.send(resposta.encode())  # Envia a resposta para o cliente

        except Exception as erro:
            print(f"Erro: {erro}")  # Exibe erros (se houver)
            break  # Encerra a conexão em caso de erro

    conexao_cliente.close()  # Fecha a conexão do cliente
    print(f"[-] Conexão encerrada com {endereco}")

# Função principal do servidor
def iniciar_servidor(ip="0.0.0.0", porta=5555):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket do servidor
    servidor.bind((ip, porta))  # Liga o servidor ao IP e porta
    servidor.listen(5)  # Permite até 5 conexões simultâneas na fila
    print(f"[*] Servidor rodando em {ip}:{porta}")

    while True:
        conexao_cliente, endereco = servidor.accept()  # Aceita uma nova conexão de cliente
        thread = threading.Thread(target=atender_cliente, args=(conexao_cliente, endereco))
        thread.start()  # Inicia uma nova thread para cada cliente

# Executar o servidor
if __name__ == "__main__":
    iniciar_servidor()
