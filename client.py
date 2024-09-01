import socket
import pyautogui
import zlib
import time
import os

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def checksum(data):
    return zlib.crc32(data.encode())

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 12345)
    client_socket.settimeout(2)  # Define o timeout para 2 segundos
    
    while True:
        # Escolha dos modos
        print("|------------------------------------------------------------------------------------------|\n")
        client_choice = input("Cliente: Escolha o modo para ENVIAR suas mensagens:\n1 - Normal\n2 - Corromper\n3 - Perder\nEscolha: ")
        if client_choice == '1':
            client_mode = "normal"
        elif client_choice == '2':
            client_mode = "corromper"
        elif client_choice == '3':
            client_mode = "perder"
        else:
            print("Escolha inválida. Tente novamente.")
            continue

        server_choice = input("\nCliente: Escolha o modo para RECEBER as mensagens do servidor:\n1 - Normal\n2 - Corromper\n3 - Perder\nEscolha: ")
        if server_choice == '1':
            server_mode = "normal"
        elif server_choice == '2':
            server_mode = "corromper"
        elif server_choice == '3':
            server_mode = "perder"
        else:
            print("Escolha inválida. Tente novamente.")
            continue
        
        # Envia os modos para o servidor
        modes = f"{client_mode},{server_mode}"
        client_socket.sendto(modes.encode(), server_address)
        print(f"\nCliente: Modos escolhidos: ENVIAR - '{client_mode}', RECEBER - '{server_mode}'.")

        try:
            # Recebe confirmação do servidor
            ack, _ = client_socket.recvfrom(1024)
            if ack.decode() == "ACK":
                print("Cliente: Sincronizado com o servidor. Pronto para enviar dados...\n")
            else:
                print("Erro na sincronização com o servidor.")
                continue
        
        except socket.timeout:
            print("Cliente: Tempo de espera excedido. Tentando novamente...\n")
            continue

        # Captura a posição do mouse
        x, y = pyautogui.position()
        data = f'{x},{y}'
        data_checksum = checksum(data)
        packet = f'{data}, {data_checksum}'
        
        if client_mode == 'corromper':  # Corromper
            data_checksum += 1  # Corrompe o checksum
            packet = f'{data}, {data_checksum}'
            print("Cliente: Pacote será corrompido antes do envio.")
        elif client_mode == 'perder':  # Perder
            print("Cliente: Simulando perda de pacote...")
            time.sleep(2)  # Simula o tempo de perda
            print("Cliente: Tempo de espera excedido. Pacote considerado como perdido.\n")
            #continue  # Retorna ao início do loop para nova escolha

        # Envia o pacote para o servidor
        client_socket.sendto(packet.encode(), server_address)
        print(f"Cliente: Pacote enviado: {packet}")
        
        try:
            # Recebe a resposta do servidor
            response, _ = client_socket.recvfrom(1024)
            response = response.decode()
            print(f"Cliente: Resposta do servidor recebida.")
            
            # Verifica o checksum da resposta
            response_data, response_checksum = response.rsplit(',', 1)
            response_checksum = int(response_checksum)
            calculated_checksum = checksum(response_data)
            
            if calculated_checksum == response_checksum:
                print(f"Cliente: Resposta recebida corretamente: {response}\n")
            else:
                print("Cliente: Resposta corrompida.\n")
        
        except socket.timeout:
            print("Cliente: Tempo de espera excedido. Resposta não recebida.\n")

if __name__ == '__main__':
    main()
