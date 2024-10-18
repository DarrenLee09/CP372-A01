import socket
import threading
import os
from datetime import datetime


SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
MAX_CLIENTS = 3
FILE_REPOSITORY = './repository'  


clients = {}
client_count = 0


def handle_client(client_socket, client_address, client_name):
    print(f"{client_name} connected from {client_address}")

    connection_start_time = datetime.now()
    clients[client_name] = {
        'address': client_address,
        'start_time': connection_start_time,
        'end_time': None
    }
    

    client_socket.send(f"Your name is {client_name}".encode())

    while True:

        data = client_socket.recv(1024).decode()
        if not data:
            break

        print(f"Received from {client_name}: {data}")
        

        if data.lower() == "status":
            status_message = "Connected clients:\n"
            for name, info in clients.items():
                start_time_str = info['start_time'].strftime('%Y-%m-%d %H:%M:%S')
                end_time_str = info['end_time'].strftime('%Y-%m-%d %H:%M:%S') if info['end_time'] else "Still connected"
                status_message += f"{name}: connected at {start_time_str}, ended at {end_time_str}\n"
            client_socket.send(status_message.encode())
        

        elif data.lower() == "exit":
            print(f"{client_name} is disconnecting")
            clients[client_name]['end_time'] = datetime.now()  
            break

        elif data.lower() == "list":
            try:
                files = os.listdir(FILE_REPOSITORY)
                file_list = "\n".join(files)
                client_socket.send(f"Available files:\n{file_list}".encode())
            except Exception as e:
                client_socket.send(f"Error listing files: {str(e)}".encode())
        

        elif data.startswith("get"):
            filename = data.split(" ", 1)[1]
            file_path = os.path.join(FILE_REPOSITORY, filename)
            
            if os.path.isfile(file_path):
                client_socket.send(f"Streaming file: {filename}".encode())
                with open(file_path, 'rb') as file:
                    while chunk := file.read(1024):  
                        client_socket.send(chunk)
                client_socket.send(b"EOF") 
            else:
                client_socket.send(f"File {filename} not found.".encode())
        
        else:
            client_socket.send(f"ACK: {data}".encode())

    client_socket.close()
    print(f"{client_name} disconnected")

def start_server():
    global client_count
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(MAX_CLIENTS)
    
    print(f"Server started on {SERVER_IP}:{SERVER_PORT}. Waiting for clients...")

    while True:
        if client_count < MAX_CLIENTS:
            client_socket, client_address = server_socket.accept()
            client_count += 1
            client_name = f"Client{client_count:02d}"
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, client_name))
            client_thread.start()
        else:
            print("Max clients reached. Waiting for a client to disconnect...")

if __name__ == "__main__":
    start_server()
