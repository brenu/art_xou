import json
import os
import sys
import threading
import pygame
import socket

from source.screens.client_partials.board import Board
from source.screens.client_partials.chat import Chat
from source.screens.client_partials.ranking import Ranking
from source.screens.client_partials.word_container import WordContainer
from source.screens.client_partials.hints import Hints
from source.core.server import Server
from source.core.protocol_parsing import ProtocolParsing

from source.core.game_consts import GameConsts
game_consts = GameConsts()

class Client:
    def __init__(self, screen, palette, name, game_address, music_player, server=False, match_name=""):
        self.screen = screen
        self.navigate = None
        self.name = name
        self.music_player = music_player
        self.reset = False

        self.default_padding = 14
        self.palette = palette

        self.screen.fill(self.palette["blue"])
        self.font = pygame.font.SysFont("arial", 24)
        self.is_board_pressed = False
        self.pen_radius = 3
        self.pen_color = "black"
        self.pen_previous_color = "black"
        self.mode = "paint"

        self.previous_points = 0
        self.initial_board = []
        self.initial_ranking = []
        self.initial_hint = ""

        self.word_to_draw = None
               
        self.board = Board(600, 400, self, self.palette)
        pygame.display.update()

        self.ranking = Ranking(188, 400, self, self.palette)
        self.chat = Chat(435, 696, self, self.palette)
        self.word_container = WordContainer(600,225, self, self.palette)
        self.hints = Hints(188, 50, self, self.palette)

        self.server = Server(self, match_name) if server == True else None
        
        self.connected_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            if server:
                self.connected_client.connect((self.server.host, self.server.port))
            else:
                self.connected_client.connect((game_address[0], 65432))
            
            self.initial_ranking = self.join_match()
            threading.Thread(target=self.handle_incoming_data).start()
        except Exception as e:
            print(e)
            self.navigate = "menu"
            self.error = "Não foi possível se conectar ao servidor"

    def match_reset(self):
        if not self.server:
            return False

        self.connected_client.sendall(ProtocolParsing.parse({
            "type": "match_reset",
            "data": {}
        }))

        while not self.reset:
            continue

        return True

    def match_reset_ui(self):
        self.screen.fill(self.palette["blue"])
        self.is_board_pressed = False
        self.pen_radius = 3
        self.pen_color = "black"
        self.pen_previous_color = "black"
        self.mode = "paint"

        self.previous_points = 0
        self.initial_board = []
        self.initial_ranking = []
        self.initial_hint = ""

        self.word_to_draw = None
               
        self.board = Board(600, 400, self, self.palette)
        pygame.display.update()

        self.ranking = Ranking(188, 400, self, self.palette)
        self.chat = Chat(435, 696, self, self.palette)
        self.word_container = WordContainer(600,225, self, self.palette)
        self.hints = Hints(188, 50, self, self.palette)

        self.reset = False
        self.navigate = False

        self.run()

    def handle_incoming_data(self):
        while True:
            try:
                initial_packet = self.connected_client.recv(game_consts.MESSAGE_LENGTH_HEADER_LENGTH).decode(game_consts.DEFAULT_STRING_FORMAT)

                if initial_packet:
                    incoming_message_length = int(initial_packet)

                    message = self.connected_client.recv(incoming_message_length).decode(game_consts.DEFAULT_STRING_FORMAT)
                    object = json.loads(message)
                    
                    if object["type"] == "answer":
                        self.chat.update_messages_list(object["data"])
                    elif object["type"] == "board_update":
                        pygame.draw.circle(self.screen, object["data"]["color"], ( object["data"]["x"], object["data"]["y"] ), object["data"]["radius"] )
                    elif object["type"] == "new_round":
                        self.music_player.play_sound_effect("next_word")
                        self.word_container.clear()
                        self.initial_hint = ""
                        if object["data"].get("word"):
                            self.board.clear(True)
                            self.hints.clear(True)
                            self.word_to_draw = object["data"].get("word")
                            self.word_container.update(self.word_to_draw)
                        else:
                            self.board.clear(False)
                            self.hints.clear(False)
                    elif object["type"] == "ranking_update":
                        player = list(filter(lambda x: x["name"] == self.name, object["data"]))[0]

                        if player["score"] > self.previous_points:
                            self.music_player.play_sound_effect("success")

                        self.previous_points = player["score"]

                        self.ranking.clear()
                        self.ranking.update(object["data"])
                    elif object["type"] == "hint":
                        self.word_container.update(object["data"])
                    elif object["type"] == "match_end":
                        self.ranking = object["data"].get("ranking")
                        self.navigate = "match_end"
                    elif object["type"] == "match_reset":
                        self.navigate = "game"
                        self.reset = True
                        
            except Exception as e:
                print(e)
                self.navigate = "menu"
                self.error = "Houve um problema de conexão com a partida!"
                return
                

    def pen(self, screen, x, y):
        pygame.draw.circle( screen, self.palette[self.pen_color], ( x, y ), self.pen_radius )

    def draw_base_components(self):
        self.ranking.clear()
        self.chat.clear()
        self.board.clear(False)
        self.word_container.clear()
        self.hints.clear(False)

        self.word_container.update(self.initial_hint)

        if self.server and self.server.drawing_player_name == self.name:
            self.board.clear(True)
            self.hints.clear(True)
            self.word_container.update(self.server.word_of_the_round)
            self.ranking.update(self.server.ranking)

    def close_server_sockets(self):
        self.connected_client.shutdown(socket.SHUT_RDWR)
        self.connected_client.close()
        if self.server:
            for client in self.server.clients:
                try:
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
                except:
                    continue

            try:
                self.server.server.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.server.server.close()
            self.server.open = False

    def run(self):
        self.screen.fill(self.palette["blue"])
        self.draw_base_components()
        self.ranking.update(self.initial_ranking)

        if self.initial_board:
            for dot in self.initial_board:
                    pygame.draw.circle(self.screen, dot["color"], ( dot["x"], dot["y"] ), dot["radius"] )

        self.is_running = True
        while True: 
            if self.navigate:
                if self.navigate != "match_end" and self.navigate != "game":
                    self.close_server_sockets()
                return

            ( x, y ) = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.board.is_painting_inside_board(x, y, self.pen_radius):
                        self.is_board_pressed = True
                    else:
                        possible_new_color = self.board.is_color_being_changed(x, y)

                        if possible_new_color and self.mode == "paint":
                            self.music_player.play_sound_effect("waterdrop")
                            self.pen_color = possible_new_color
                        elif self.board.is_brush_clicked(x, y):
                            self.mode = "paint"
                            self.pen_color = self.pen_previous_color
                        elif self.board.is_eraser_clicked(x, y):
                            self.music_player.play_sound_effect("waterdrop")
                            self.mode = "erase"
                            self.pen_previous_color = self.pen_color if self.pen_color != "white" else self.pen_previous_color
                            self.pen_color = "white"
                        elif self.hints.is_hint_clicked(x, y):
                            self.music_player.play_sound_effect("button_click")
                            self.hints.give_hint()

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_board_pressed = False

                elif event.type == pygame.MOUSEMOTION and self.is_board_pressed == True and self.board.is_painting_inside_board(x, y, self.pen_radius):
                    if self.mode == "paint":
                        self.pen_radius = 3
                        self.send_board_update(self.palette[self.pen_color], self.pen_radius, x, y)
                    elif self.mode == "erase":
                        self.pen_radius = 10
                        self.send_board_update(self.palette[self.pen_color], self.pen_radius, x, y)
                    pygame.display.update()

                elif event.type == pygame.QUIT:
                    self.close_server_sockets()
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "\x1b":
                        self.navigate = "menu"
                    self.chat.update([event])
            
            self.draw_screen()
            self.chat.update([])
    
    def stop(self):
        self.is_running = False

    def draw_screen(self):
        pygame.display.update()

    def send_board_update(self, color, radius, x, y):
        self.connected_client.sendall(ProtocolParsing.parse({
            "type": "board_update",
            "data": {
                "color": color,
                "radius": radius,
                "x": x,
                "y": y
            }
        }))

    def join_match(self):
        self.connected_client.sendall(ProtocolParsing.parse({
            "type": "join",
            "data": {
                "name": self.name
            }
        }))

        initial_packet = self.connected_client.recv(game_consts.MESSAGE_LENGTH_HEADER_LENGTH).decode(game_consts.DEFAULT_STRING_FORMAT)

        if initial_packet:
            incoming_message_length = int(initial_packet)

            message = self.connected_client.recv(incoming_message_length).decode(game_consts.DEFAULT_STRING_FORMAT)
            object = json.loads(message)

            if not object["data"].get("success"):
                self.navigate = "menu"
                self.error = "Oops!"
            
            self.initial_board = object["data"].get("board")
            self.initial_hint = object["data"].get("hint")

        initial_packet = self.connected_client.recv(game_consts.MESSAGE_LENGTH_HEADER_LENGTH).decode(game_consts.DEFAULT_STRING_FORMAT)

        if initial_packet:
            incoming_message_length = int(initial_packet)

            message = self.connected_client.recv(incoming_message_length).decode(game_consts.DEFAULT_STRING_FORMAT)
            object = json.loads(message)

            if object["type"] == "ranking_update":
                return object["data"]