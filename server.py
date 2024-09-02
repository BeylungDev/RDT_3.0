import socket
import zlib
import time

# Função para calcular o checksum:
def checksum(data):
    return zlib.crc32(data.encode())

def main():
    # Conecta-se ao cliente
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 3333)) 
    server_socket.settimeout(2)
    
    print("Aguardando as escolhas do cliente...")

    while True:
        try:
            # Recebe os modos do cliente
            modes, client_address = server_socket.recvfrom(1024)
            client_mode, server_mode = modes.decode().split(',')
            print("|------------------------------------------------------------------------------------------|\n")
            print(f"Modos recebidos - ENVIAR (cliente): '{client_mode}', RECEBER (servidor): '{server_mode}'.")
            
            # Envia confirmação ao cliente
            server_socket.sendto("ACK".encode(), client_address)
            print("Sincronizado com o cliente. Pronto para receber dados...\n")
        
            while True:
                try:
                    # Recebe o pacote do cliente
                    packet, client_address = server_socket.recvfrom(1024)
                    packet = packet.decode()
                    if client_mode != 'perder':
                        print(f"Pacote recebido: {packet}")

                    # Tenta separar o pacote e calcular o checksum
                    try:
                        data, received_checksum_str, received_ack = packet.rsplit(',', 2)
                        received_checksum = int(received_checksum_str.strip())
                        received_ack = int(received_ack.strip())
                        calculated_checksum = checksum(data)
                    except ValueError as e:
                        print(f"Erro ao processar o pacote - {e}")
                        break

                    # Verifica se o checksum recebido coincide com o calculado
                    if calculated_checksum == received_checksum:
                        print(f"ACK {received_ack} recebido corretamente.")
                        response_data = f"ACK {received_ack}. Pacote recebido corretamente, Checksum recebido: {received_checksum}, Checksum esperado: {calculated_checksum}"
                    # Caso o checksum seja diferente, significa que está corrompido e então envia uma resposta ao cliente
                    else:
                        print(f"Checksum incorreto. Esperado: {calculated_checksum}. Recebido: {received_checksum}.")
                        response_data = f'Pacote corrompido, Checksum recebido: {received_checksum}, Checksum esperado: {calculated_checksum}'
                    
                    # Calcula o checksum da resposta
                    response_checksum = checksum(response_data)

                    if server_mode == 'corromper':  # Corromper o envio do servidor para o cliente
                        response_checksum += 1  # Corrompe o checksum adicionando +1 ao seu valor
                        print("Resposta será corrompida antes do envio.")
                    elif server_mode == 'perder':  # Perder os dados
                        print("Simulando perda de resposta...")
                        time.sleep(2)
                        print("Tempo de resposta excedido. Resposta não enviada.\n")
                        break

                    response_packet = f'{response_data},{response_checksum},{received_ack}'  # Envia de volta o ACK recebido
                    server_socket.sendto(response_packet.encode(), client_address)
                    if client_mode != 'perder':
                        print(f"Resposta enviada com ACK {received_ack}: {response_packet}\n")
                    break

                except socket.timeout:
                    print("Tempo de espera excedido. Nenhum pacote recebido.\n")
                    break
        
        except Exception as e:
            continue

if __name__ == '__main__':
    main()
