import json
import threading
import socket
import random
import datetime
import time

PORT = 65432

class Server:
    def __init__(self, game_client):
        temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temporary_socket.connect(("8.8.8.8", 80))
    
        self.host = temporary_socket.getsockname()[0]
        self.match_name = "blablabla"
        self.port = PORT
        self.server_address = (self.host, self.port)
        self.default_string_format = "utf-8"
        self.message_length_header_length = 128
        
        self.possible_words = open("source/core/words.txt", "r", encoding="utf-8").read().splitlines()
        self.clients = []
        self.client_names = []
        self.drawing_player_name = "DonoDaBola"
        self.word_of_the_round = self.possible_words[random.randint(0, len(self.possible_words))]
        self.round_start_time = datetime.datetime.now()
        self.open = True

        self.game_client = game_client
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.server.bind(self.server_address)
            threading.Thread(target=self.handle_connections, args=[]).start()
            threading.Thread(target=self.handle_rounds, args=[]).start()
        except:
            self.game_client.navigate = "menu"
            self.game_client.error = "Não foi possível criar a partida, tente novamente!"


    def handle_rounds(self):
        while True:
            time.sleep(0.1)
            if self.open == False:
                return
            if datetime.datetime.now() >= self.round_start_time + datetime.timedelta(minutes=2):
                self.round_start_time = datetime.datetime.now()
                self.word_of_the_round = self.possible_words[random.randint(0, len(self.possible_words)-1)]
                self.drawing_player_name = self.client_names[random.randint(0, len(self.client_names)-1)]


    def handle_connections(self):
        self.server.listen()

        while True:
            try:
                connection, address = self.server.accept()
                threading.Thread(target=self.handle_new_client, args=(connection, address)).start()
            except:
                return

    def handle_new_client(self, connection: socket.socket, address):
        while True:
            try:
                initial_header = connection.recv(self.message_length_header_length).decode(self.default_string_format)
            
                if initial_header:
                    message_length = int(initial_header)
                    message = connection.recv(message_length).decode(self.default_string_format)

                    object = json.loads(message)

                    if object["type"] == "match_info":
                        object["data"] = {"name": self.match_name}
                    elif object["type"] == "join":
                        if not object["data"]["name"] in self.client_names:
                            self.clients.append(connection)
                            self.client_names.append(object["data"]["name"])
                            object["data"] = {"success": True}
                        else:
                            object["data"] = {"success": False}
                    elif object["type"] == "answer":
                        # Remeber, in the future, to verify if the answer is correct or not
                        object["data"] = f"{object['author']}: {object['data']}"
                        
                    message = json.dumps(object).encode(self.default_string_format)
                    message_length = ("0"*(self.message_length_header_length - len(str(len(message)))) + str(len(message))).encode(self.default_string_format)

                    if object["type"] == "match_info" or object["type"] == "join":
                        connection.sendall(message_length)
                        connection.sendall(message)

                        if object["data"].get("success") == False:
                            connection.shutdown(socket.SHUT_RDWR)
                            connection.close()
                            break
                    elif object["type"] == "answer":
                        for client in self.clients:
                            if client != connection:
                                client.sendall(message_length)
                                client.sendall(message)
                    else:
                        connection_index = self.clients.index(connection)
                        connection_player_name = self.client_names[connection_index]

                        if connection_player_name == self.drawing_player_name:
                            for client in self.clients:
                                client.sendall(message_length)
                                client.sendall(message)
                else:
                    break
            except Exception as e:
                print(e)
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
                break

        if connection in self.clients:
            connection.close()
            connection_index = self.clients.index(connection)
            self.clients.pop(connection_index)
            self.client_names.pop(connection_index)