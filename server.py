import socket
import zlib  # Usado para calcular o checksum

BUFFER_SIZE = 1024
simulation_mode = 0  # 0 = Normal, 1 = Perder pacotes, 2 = Corromper pacotes

def set_simulation_mode():
    """Define o modo de simulação para o servidor."""
    global simulation_mode
    while True:
        try:
            mode = int(input("Escolha o modo de simulação:\n0 = Normal\n1 = Perder pacotes\n2 = Corromper pacotes\n-> "))
            if mode in [0, 1, 2]:
                simulation_mode = mode
                break
            else:
                print("Modo inválido. Por favor, escolha 0, 1 ou 2.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")

def simulate_network(packet):
    """Simula a perda e corrupção de pacotes baseado no modo de simulação."""
    if simulation_mode == 1:
        print("Pacote perdido.")
        return None  # Simula perda de pacote
    elif simulation_mode == 2:
        print("Pacote corrompido.")
        return packet + "corrupt"  # Simula corrupção de pacote
    return packet  # Pacote recebido corretamente

def verify_checksum(data, received_checksum):
    """Verifica se o checksum calculado corresponde ao checksum recebido."""
    calculated_checksum = zlib.crc32(data.encode())
    return calculated_checksum == received_checksum

def main():
    """Configura o servidor para receber dados de jogo e enviar ACKs."""
    global simulation_mode
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 4444))  # Escuta em todas as interfaces de rede
    print("Servidor esperando por dados de jogo...")

    set_simulation_mode()

    print(f"Modo de simulação definido como: {simulation_mode}")

    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        if not data:
            continue  # Ignora pacotes vazios

        # Envia a configuração de simulação para o cliente
        server_socket.sendto(f"START:{simulation_mode}".encode(), addr)

        data = simulate_network(data.decode())

        if data is None:
            print("Pacote perdido, esperando o próximo pacote...")
            continue  # Ignora o pacote perdido

        if "corrupt" in data:
            print("Pacote corrompido")
            server_socket.sendto("RETRY".encode(), addr)  # Solicita reenvio do pacote
            continue  # Ignora o pacote corrompido

        # Extrai dados e checksum do pacote
        try:
            game_data, received_checksum = data.rsplit(":", 1)
            received_checksum = int(received_checksum)

            if verify_checksum(game_data, received_checksum):
                print(f"Dados de jogo recebidos com sucesso: {game_data} de {addr}")
                server_socket.sendto("ACK".encode(), addr)  # Confirma o recebimento do pacote
            else:
                print("Checksum inválido. Pacote corrompido.")
                server_socket.sendto("RETRY".encode(), addr)  # Solicita reenvio do pacote

        except ValueError:
            print("Erro ao processar o pacote. Pacote corrompido ou mal formado.")
            server_socket.sendto("RETRY".encode(), addr)  # Solicita reenvio do pacote

if __name__ == "__main__":
    main()
