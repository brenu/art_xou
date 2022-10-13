import json
import threading
import socket
import os

class Server:
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 65432
        self.server_address = (self.host, self.port)
        self.default_string_format = "utf-8"
        self.message_length_header_length = 128
        self.clients = []

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.server_address)

        threading.Thread(target=self.handle_connections, args=[]).start()


    def handle_connections(self):
        self.server.listen()

        while True:
            connection, address = self.server.accept()
            threading.Thread(target=self.handle_new_client, args=(connection, address)).start()
            print(f"New connection, yay! Say hello to {address}!")

    def handle_new_client(self, connection: socket.socket, address):
        self.clients.append(connection)

        while True:
            initial_header = connection.recv(self.message_length_header_length).decode(self.default_string_format)
            
            if initial_header:
                message_length = int(initial_header)
                message = connection.recv(message_length).decode(self.default_string_format)

                object = json.loads(message)

                if object["type"] == "answer":
                    message = f"{object['author']}: {object['data']}".encode(self.default_string_format)
                    message_length = ("0"*(self.message_length_header_length - len(str(len(message)))) + str(len(message))).encode(self.default_string_format)
                    
                    for client in self.clients:
                        if client != connection:
                            client.sendall(message_length)
                            client.sendall(message)
                
                
            else:
                break

        self.clients.remove(connection)