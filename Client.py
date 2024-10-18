import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
client_name = client_socket.recv(1024).decode()
print(f"Server says: {client_name}")

while True:
    message = input("Enter message ('exit' to disconnect, 'list' for files, 'get [filename]' to download): ")
    client_socket.send(message.encode())
    while True:
        response = client_socket.recv(1024)
        if response == b"EOF":
            print("File transfer completed.")
            break
        print(f"Server responded: {response.decode()}")
    if message.lower() == "exit":
        print("Disconnecting...")
        break
client_socket.close()
