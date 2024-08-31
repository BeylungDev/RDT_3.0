import subprocess
import sys
import socket
import time
import json
import pyautogui
import zlib  # Usado para calcular o checksum

BUFFER_SIZE = 1024
TIMEOUT = 1.0  # Tempo de espera antes de considerar um pacote perdido
RETRY_LIMIT = 5  # Número máximo de tentativas para reenviar um pacote
network_status = 0  # Inicializado como normal

def install_package(package_name):
    """Instala um pacote usando pip."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar o pacote {package_name}: {e}")
        sys.exit(1)

# Verifica se o pyautogui está instalado, se não estiver, instala
try:
    import pyautogui
except ImportError:
    print("pyautogui não encontrado. Instalando...")
    install_package('pyautogui')
    import pyautogui

def clear_screen():
    """Limpa o terminal, adaptando para Windows ou Unix/Linux/Mac."""
    import os
    import platform

    sistema = platform.system()

    if sistema == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def calculate_checksum(data):
    """Calcula o checksum usando zlib."""
    return zlib.crc32(data.encode())

def generate_game_data(player_id, coordinates):
    """Gera dados de jogo no formato JSON."""
    data = json.dumps({
        "player_id": player_id,
        "coordinates": coordinates
    })
    checksum = calculate_checksum(data)
    return f"{data}:{checksum}"

def simulate_network(packet):
    """Simula a perda e corrupção de pacotes com base na configuração global."""
    global network_status
    if network_status == 1:
        return None  # Simula perda de pacote
    if network_status == 2:
        return packet + "corrupt"  # Simula corrupção de pacote
    return packet  # Pacote recebido corretamente

def main():
    """Configura o cliente para enviar dados de jogo e aguardar ACKs."""
    global network_status

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('127.0.0.1', 4444)  # IP do servidor

    player_id = 1

    # Espera pela configuração de simulação do servidor
    while True:
        try:
            client_socket.settimeout(TIMEOUT)
            client_socket.sendto(b"CONNECT", server_address)  # Envia um pedido de conexão
            response, _ = client_socket.recvfrom(BUFFER_SIZE)
            response = response.decode()
            
            if response.startswith("START"):
                _, mode = response.split(":")
                network_status = int(mode)
                print(f"Conexão estabelecida com o servidor. Modo de simulação: {network_status}. Iniciando envio de pacotes.")
                break
            else:
                print("Recebido do servidor:", response)
                print("Esperando confirmação do servidor...")
        except socket.timeout:
            print("Tempo esgotado ao esperar confirmação do servidor.")

    while True:
        # Captura a posição atual do ponteiro do mouse
        x, y = pyautogui.position()
        coordinates = [x, y]
        game_data = generate_game_data(player_id, coordinates)

        retry_count = 0
        ack_received = False

        while not ack_received and retry_count < RETRY_LIMIT:
            # Adiciona número de sequência ao pacote
            packet = game_data
            packet = simulate_network(packet)
            if packet is None:
                print("Pacote perdido, reenviando...")
                retry_count += 1
                continue

            if "corrupt" in packet:
                print("Pacote corrompido, reenviando...")
                retry_count += 1
                continue

            clear_screen()
            print(f"Enviando dados de jogo: {packet}")
            client_socket.sendto(packet.encode(), server_address)

            try:
                client_socket.settimeout(TIMEOUT)
                response, _ = client_socket.recvfrom(BUFFER_SIZE)
                response = response.decode()
                
                if response == "ACK":
                    ack_received = True
                    print("ACK recebido, pacote enviado com sucesso")
                elif response == "RETRY":
                    print("Servidor solicitou reenvio do pacote.")
                else:
                    print("Resposta inválida recebida do servidor.")
            except socket.timeout:
                print("Tempo esgotado, reenviando pacote...")
                retry_count += 1

        if retry_count >= RETRY_LIMIT:
            print("Número máximo de tentativas alcançado, falha na transmissão.")

        time.sleep(2)  # Intervalo entre envios de pacotes

if __name__ == "__main__":
    main()
