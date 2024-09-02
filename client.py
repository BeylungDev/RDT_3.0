import socket
import pyautogui
import zlib
import time
import os

# Função não utilizada, era para ficar limpando o terminal mas decidi não utilizar no final
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Calcula o cheksum
def checksum(data):
    return zlib.crc32(data.encode())

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('127.0.0.1', 3333)
    client_socket.settimeout(2)  # Define o timeout para 2 segundos
    
    ack_number = 0  # ACK inicial

    while True:
        # Escolha dos modos
        print("|------------------------------------------------------------------------------------------|\n")
        client_choice = input("Escolha o modo para ENVIAR suas mensagens:\n1 - Normal\n2 - Corromper\n3 - Perder\nEscolha: ")
        if client_choice == '1':
            client_mode = "normal"
        elif client_choice == '2':
            client_mode = "corromper"
        elif client_choice == '3':
            client_mode = "perder"
        else:
            print("Escolha inválida. Tente novamente.")
            continue

        server_choice = input("\nEscolha o modo para RECEBER as mensagens do servidor:\n1 - Normal\n2 - Corromper\n3 - Perder\nEscolha: ")
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
        print(f"\nModos escolhidos: ENVIAR - '{client_mode}', RECEBER - '{server_mode}'.")

        try:
            # Recebe confirmação do servidor
            ack, _ = client_socket.recvfrom(1024)
            if ack.decode() == "ACK":
                print("Sincronizado com o servidor. Pronto para enviar dados...\n")
            else:
                print("Erro na sincronização com o servidor.")
                continue
        
        except socket.timeout:
            print("Tempo de espera excedido. Tentando novamente...\n")
            continue

        # Captura a posição do mouse
        x, y = pyautogui.position()
        data = f'{x},{y}'
        data_checksum = checksum(data)
        packet = f'{data}, {data_checksum}, {ack_number}'
        
        if client_mode == 'corromper':  # Corromper
            data_checksum += 1  # Corrompe o checksum
            packet = f'{data}, {data_checksum}, {ack_number}'
            print("Pacote será corrompido antes do envio.")
        elif client_mode == 'perder':  # Perder
            print("Simulando perda de pacote...")
            time.sleep(2)  # Simula o tempo de perda
            print("Tempo de espera excedido. Pacote considerado como perdido.\n")
            continue  # Retorna ao início do loop para nova escolha

        # Envia o pacote para o servidor
        client_socket.sendto(packet.encode(), server_address)
        print(f"Pacote enviado: {packet}")
        
        try:
            # Recebe a resposta do servidor
            response, _ = client_socket.recvfrom(1024)
            response = response.decode()
            if client_mode != 'perder':
                print(f"Resposta do servidor recebida.")
            
            # Verifica o checksum da resposta e o ACK
            response_data, response_checksum, received_ack = response.rsplit(',', 2)
            response_checksum = int(response_checksum)
            received_ack = int(received_ack)
            calculated_checksum = checksum(response_data)
            
            if calculated_checksum == response_checksum:
                if received_ack == ack_number:
                    print(f"Resposta recebida corretamente com ACK {received_ack}: {response_data} / Checksum da resposta: {response_checksum}, Checksum esperado da resposta: {calculated_checksum}.\n")
                    ack_number = 1 - ack_number  # Alterna o ACK para a próxima mensagem
                else:
                    print("ACK incorreto.\n")
            else:
                print(f"Resposta corrompida / Checksum da resposta: {response_checksum}, Checksum esperado da resposta: {calculated_checksum}.\n")
        
        except socket.timeout:
            ack_number = 1 - ack_number
            print("Tempo de espera excedido. Resposta não recebida.\n")

if __name__ == '__main__':
    main()
