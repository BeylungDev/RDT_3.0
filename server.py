import socket
import zlib
import time

def checksum(data):
    return zlib.crc32(data.encode())

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 12345))
    
    print("Servidor: Aguardando as escolhas do cliente...")

    while True:
        try:
            print("|------------------------------------------------------------------------------------------|\n")
            # Recebe os modos do cliente
            modes, client_address = server_socket.recvfrom(1024)
            client_mode, server_mode = modes.decode().split(',')
            print(f"Servidor: Modos recebidos - ENVIAR (cliente): '{client_mode}', RECEBER (servidor): '{server_mode}'.")
            
            # Envia confirmação ao cliente
            server_socket.sendto("ACK".encode(), client_address)
            print("Servidor: Sincronizado com o cliente. Pronto para receber dados...\n")
        
            while True:
                try:
                    # Recebe o pacote do cliente
                    packet, client_address = server_socket.recvfrom(1024)
                    packet = packet.decode()
                    print(f"Servidor: Pacote recebido: {packet}")

                    # Tenta separar o pacote e calcular o checksum
                    try:
                        data, received_checksum_str = packet.rsplit(',', 1)
                        received_checksum = int(received_checksum_str.strip())
                        calculated_checksum = checksum(data)
                    except ValueError as e:
                        print(f"Servidor: Erro ao processar o pacote - {e}")
                        break

                    # Verifica se o checksum recebido coincide com o calculado
                    if calculated_checksum == received_checksum:
                        if client_mode == 'perder':
                            response_data = "Pacote perdido."
                        else:
                            response_data = "Pacote recebido corretamente"
                    else:
                        response_data = "Pacote corrompido"
                    
                    response_checksum = checksum(response_data)

                    if server_mode == 'corromper':  # Corromper
                        response_checksum += 1  # Corrompe o checksum
                        print("Servidor: Resposta será corrompida antes do envio.")
                    elif server_mode == 'perder':  # Perder
                        print("Servidor: Simulando perda de resposta...")
                        time.sleep(2)  # Simula o tempo de perda
                        print("Servidor: Tempo de resposta excedido. Resposta não enviada.\n")
                        break  # Volta ao início para nova espera

                    response_packet = f'{response_data},{response_checksum}'
                    server_socket.sendto(response_packet.encode(), client_address)
                    print(f"Servidor: Resposta enviada: {response_packet}\n")
                    break

                except socket.timeout:
                    print("Servidor: Tempo de espera excedido. Nenhum pacote recebido.\n")
                    break
        
        except Exception as e:
            print(f"Servidor: Erro inesperado: {e}\n")

if __name__ == '__main__':
    main()
