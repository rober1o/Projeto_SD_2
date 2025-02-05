import socket  # Biblioteca para comunicação entre cliente e servidor

# Função do cliente
def cliente():
    ip_servidor = "127.0.0.1"  # Endereço do servidor (localhost)
    porta_servidor = 5555  # Porta usada pelo servidor

    conexao_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP/IP
    conexao_servidor.connect((ip_servidor, porta_servidor))  # Conecta ao servidor

    while True:
        numero = input("Digite um número (ou 'sair' para encerrar): ")  # Solicita um número ao usuário
        if numero.lower() == "sair":
            break  # Encerra o cliente se o usuário digitar "sair"

        conexao_servidor.send(numero.encode())  # Envia o número ao servidor
        resposta = conexao_servidor.recv(1024).decode()  # Recebe a resposta do servidor
        print(f"Servidor: {resposta}")  # Exibe a resposta

    conexao_servidor.close()  # Fecha a conexão ao final

# Executar o cliente
if __name__ == "__main__":
    cliente()
