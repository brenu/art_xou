import json
import threading
import socket
import random
import datetime
import time
from source.core.game_consts import GameConsts
from source.core.protocol_parsing import ProtocolParsing
from source.core.utils import Utils

game_consts = GameConsts()

class Server:
    def __init__(self, game_client, match_name, words=[]):
        temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temporary_socket.connect(("8.8.8.8", 80)) # The whole idea here is to just create a socket and get our local IP. It doesn't really have to connect
    
        self.host = temporary_socket.getsockname()[0]
        self.match_name = match_name
        self.port = game_consts.DEFAULT_PORT
        self.server_address = (self.host, self.port)
        
        self.possible_words = open("assets/words.txt", "r", encoding="utf-8").read().splitlines() if not words else words
        self.clients = []
        self.client_names = []
        self.ranking = []
        self.drawing_player_name = game_client.name
        self.word_of_the_round = self.possible_words[random.randint(0, len(self.possible_words))]
        self.round_start_time = datetime.datetime.now()
        self.correct_answers = []
        self.board_until_now = []
        self.gaven_hints = 0
        self.present_hint = ""
        self.open = True
        self.exit = False
        self.reset = False

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
            if self.exit == True:
                return
            if self.open == False:
                continue
            if (datetime.datetime.now() >= self.round_start_time + datetime.timedelta(minutes=3)) or (len(self.clients) > 1 and len(self.correct_answers) == len(self.clients)-1) or self.reset:
                self.round_start_time = datetime.datetime.now()
                self.word_of_the_round = self.possible_words[random.randint(0, len(self.possible_words)-1)]
                self.drawing_player_name = self.client_names[random.randint(0, len(self.client_names)-1)]
                self.correct_answers = []
                self.board_until_now = []
                self.gaven_hints = 0
                self.present_hint = ""

                if self.reset:
                    self.reset = False
                    for index, _ in enumerate(self.ranking):
                        self.ranking[index]["score"] = 0

                    object = {
                        "type": "ranking_update",
                        "data": self.ranking,
                    }
                    parsed_object = ProtocolParsing.parse(object)

                    for client in self.clients:
                            client.sendall(parsed_object)

                    new_round_message = {
                        "type": "new_round",
                        "data": {}
                    }

                    message = json.dumps(new_round_message).encode(game_consts.DEFAULT_STRING_FORMAT)
                    message_length = ("0"*(game_consts.MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(message)))) + str(len(message))).encode(game_consts.DEFAULT_STRING_FORMAT)

                    new_round_message["data"]["word"] = self.word_of_the_round


                    special_message = json.dumps(new_round_message).encode(game_consts.DEFAULT_STRING_FORMAT)
                    special_message_length = ("0"*(game_consts.MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(special_message)))) + str(len(special_message))).encode(game_consts.DEFAULT_STRING_FORMAT)

                    for index, connection in enumerate(self.clients):
                        if self.client_names[index] == self.drawing_player_name:
                            connection.sendall(special_message_length)
                            connection.sendall(special_message)
                        else:
                            connection.sendall(message_length)
                            connection.sendall(message)

                elif self.ranking[0]["score"] < 120:
                    new_round_message = {
                        "type": "new_round",
                        "data": {}
                    }

                    message = json.dumps(new_round_message).encode(game_consts.DEFAULT_STRING_FORMAT)
                    message_length = ("0"*(game_consts.MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(message)))) + str(len(message))).encode(game_consts.DEFAULT_STRING_FORMAT)

                    new_round_message["data"]["word"] = self.word_of_the_round


                    special_message = json.dumps(new_round_message).encode(game_consts.DEFAULT_STRING_FORMAT)
                    special_message_length = ("0"*(game_consts.MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(special_message)))) + str(len(special_message))).encode(game_consts.DEFAULT_STRING_FORMAT)

                    for index, connection in enumerate(self.clients):
                        if self.client_names[index] == self.drawing_player_name:
                            connection.sendall(special_message_length)
                            connection.sendall(special_message)
                        else:
                            connection.sendall(message_length)
                            connection.sendall(message)
                else:
                    message_data = {
                        "type": "match_end",
                        "data": {
                            "ranking": self.ranking
                        }
                    }

                    message = json.dumps(message_data).encode(game_consts.DEFAULT_STRING_FORMAT)
                    message_length = ("0"*(game_consts.MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(message)))) + str(len(message))).encode(game_consts.DEFAULT_STRING_FORMAT)

                    for index, connection in enumerate(self.clients):
                        connection.sendall(message_length)
                        connection.sendall(message)

                    self.open = False

    def handle_connections(self):
        self.server.listen()

        while True:
            try:
                connection, address = self.server.accept()
                threading.Thread(target=self.handle_new_client, args=(connection, address)).start()
            except:
                return
            
    def handle_new_hint(self):
        hint = ""
        
        if self.gaven_hints == 0:
            hint = " ".join(["_" for _ in range(len(self.word_of_the_round))])
        else:
            hint = ["_" for _ in range(len(self.word_of_the_round))]

            random_index = random.randint(0, len(self.word_of_the_round))
            hint[random_index] = self.word_of_the_round[random_index]

            hint = " ".join(hint)
            self.present_hint = hint

        return hint

    def handle_new_client(self, connection: socket.socket, address):
        while True:
            try:
                initial_header = connection.recv(game_consts.MESSAGE_LENGTH_HEADER_LENGTH).decode(game_consts.DEFAULT_STRING_FORMAT)
            
                if initial_header:
                    message_length = int(initial_header)
                    message = connection.recv(message_length).decode(game_consts.DEFAULT_STRING_FORMAT)

                    object = json.loads(message)

                    if object["type"] == "match_info":
                        object["data"] = {"name": self.match_name}

                    elif object["type"] == "join":
                        if not object["data"]["name"] in self.client_names:
                            self.clients.append(connection)
                            self.client_names.append(object["data"]["name"])
                            self.ranking.append({ "name": object["data"]["name"], "score": 0})
                            object["data"] = {"success": True, "board": self.board_until_now, "hint": self.present_hint}
                        else:
                            object["data"] = {"success": False}

                    elif object["type"] == "answer":
                        connection_index = self.clients.index(connection)
                        author = self.client_names[connection_index]
                        drawing_player_index = self.client_names.index(self.drawing_player_name)

                        if author == self.drawing_player_name:
                            continue
                        if connection in self.correct_answers:
                            continue
                        
                        if object["data"] == self.word_of_the_round:
                            correct_answers_length = len(self.correct_answers)
                            if correct_answers_length + self.gaven_hints < 10:
                                self.ranking[connection_index]["score"] += 10 - correct_answers_length - self.gaven_hints
                            else:
                                self.ranking[connection_index]["score"] += 1

                            if correct_answers_length == 0:
                                self.ranking[drawing_player_index]["score"] += 11 - self.gaven_hints
                            else:
                                self.ranking[drawing_player_index]["score"] += 2

                            self.correct_answers.append(connection)
                            object["type"] = "ranking_update"
                            object["data"] = self.ranking
                        else:
                            object["data"] = f"{author}: {object['data']}"

                    elif object["type"] == "hint":
                        if self.gaven_hints == 2:
                            continue

                        connection_index = self.clients.index(connection)
                        author = self.client_names[connection_index]

                        if author != self.drawing_player_name:
                            continue

                        object["data"] = self.handle_new_hint()


                    if object["type"] == "match_info" or object["type"] == "join":
                        connection.sendall(ProtocolParsing.parse(object))
                        
                        if object["type"] == "match_info":
                            break
                        if object["data"].get("success") == False:
                            break
                        elif object["type"] == "join":
                            for client in self.clients:
                                client.sendall(ProtocolParsing.parse({
                                    "type": "ranking_update",
                                    "data": self.ranking
                                }))
                    elif object["type"] == "answer":
                        for client in self.clients:
                            if client != connection:
                                client.sendall(ProtocolParsing.parse(object))
                    elif object["type"] == "ranking_update":
                        for client in self.clients:
                            client.sendall(ProtocolParsing.parse(object))
                    elif object["type"] == "hint":
                        self.gaven_hints += 1

                        for client in self.clients:
                            if client != connection:
                                client.sendall(ProtocolParsing.parse(object))
                    elif object["type"] == "match_reset":
                        if self.clients.index(connection) == 0:
                            for client in self.clients:
                                client.sendall(ProtocolParsing.parse(object))

                        self.open = True
                        self.reset = True
                    else:
                        if object["type"] == "board_update":
                            self.board_until_now.append(object["data"])

                        connection_index = self.clients.index(connection)
                        connection_player_name = self.client_names[connection_index]

                        if connection_player_name == self.drawing_player_name:
                            for client in self.clients:
                                client.sendall(ProtocolParsing.parse(object))
                else:
                    break
            except:
                break

        try:
            Utils.close_connection(connection)
        except:
            pass

        if connection in self.clients:
            connection_index = self.clients.index(connection)
            self.clients.pop(connection_index)
            self.client_names.pop(connection_index)