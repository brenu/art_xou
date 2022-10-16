import json
import threading
import socket
import os

PORT = 65432

class Server:
    def __init__(self, game_client):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = PORT
        self.server_address = (self.host, self.port)
        self.default_string_format = "utf-8"
        self.message_length_header_length = 128
        self.clients = []
        self.game_client = game_client

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.server.bind(self.server_address)
            threading.Thread(target=self.handle_connections, args=[]).start()
        except:
            self.game_client.navigate = "menu"
            self.game_client.error = "Não foi possível criar a partida, tente novamente!"



    def handle_connections(self):
        self.server.listen()

        while True:
            try:
                connection, address = self.server.accept()
                threading.Thread(target=self.handle_new_client, args=(connection, address)).start()
                print(f"New connection, yay! Say hello to {address}!")
            except:
                return

    def handle_new_client(self, connection: socket.socket, address):
        self.clients.append(connection)

        while True:
            try:
                initial_header = connection.recv(self.message_length_header_length).decode(self.default_string_format)
            
                if initial_header:
                    message_length = int(initial_header)
                    message = connection.recv(message_length).decode(self.default_string_format)

                    object = json.loads(message)

                    if object["type"] == "answer":
                        # Remeber, in the future, to verify if the answer is correct or not
                        object["data"] = f"{object['author']}: {object['data']}"
                        
                    message = json.dumps(object).encode(self.default_string_format)
                    message_length = ("0"*(self.message_length_header_length - len(str(len(message)))) + str(len(message))).encode(self.default_string_format)
                    
                    for client in self.clients:
                        if client != connection:
                            client.sendall(message_length)
                            client.sendall(message)
                    
                    
                else:
                    break
            except:
                return

        self.clients.remove(connection)