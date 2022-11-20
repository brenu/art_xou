import json
import os
import sys
import threading
import pygame
import socket

from source.screens.client_partials.board import Board
from source.screens.client_partials.chat import Chat
from source.screens.client_partials.ranking import Ranking
from source.core.server import Server

DEFAULT_STRING_FORMAT = "utf-8"
MESSAGE_LENGTH_HEADER_LENGTH = 128

class Client:
    def __init__(self, screen, palette, name, game_address, server=False):
        self.screen = screen
        self.navigate = None
        self.name = name

        self.default_padding = 14
        self.palette = palette

        self.sfx = {
            "waterdrop": pygame.mixer.Sound('assets/sfx/waterdrop.ogg')
        }

        self.screen.fill(self.palette["blue"])
        self.font = pygame.font.SysFont("arial", 24)
        self.is_board_pressed = False
        self.pen_radius = 3
        self.pen_color = "black"
        self.pen_previous_color = "black"
        self.mode = "paint"
               
        self.board = Board(600, 400, self, self.palette)
        pygame.display.update()

        self.ranking = Ranking(188, 400, self, self.palette)
        self.chat = Chat(435, 696, self, self.palette)

        self.server = Server(self) if server == True else None
        
        self.connected_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            if server:
                self.connected_client.connect((self.server.host, self.server.port))
            else:
                self.connected_client.connect((game_address[0], 65432))
            
            threading.Thread(target=self.handle_incoming_data).start()
        except Exception as e:
            print(e)
            self.navigate = "menu"
            self.error = "Não foi possível se conectar ao servidor"


    def handle_incoming_data(self):
        self.join_match()
        while True:
            try:
                initial_packet = self.connected_client.recv(MESSAGE_LENGTH_HEADER_LENGTH).decode(DEFAULT_STRING_FORMAT)

                if initial_packet:
                    incoming_message_length = int(initial_packet)

                    message = self.connected_client.recv(incoming_message_length).decode(DEFAULT_STRING_FORMAT)
                    object = json.loads(message)
                    
                    if object["type"] == "answer":
                        self.chat.update_messages_list(object["data"])
                    elif object["type"] == "board_update":
                        pygame.draw.circle(self.screen, object["data"]["color"], ( object["data"]["x"], object["data"]["y"] ), object["data"]["radius"] )
            except:
                return
                

    def pen(self, screen, x, y):
        pygame.draw.circle( screen, self.palette[self.pen_color], ( x, y ), self.pen_radius )
        self.send_board_update(self.palette[self.pen_color], self.pen_radius, x, y)

    def draw_base_components(self):
        self.ranking.clear()
        self.chat.clear()
        self.board.clear()

    def close_server_sockets(self):
        self.connected_client.shutdown(socket.SHUT_RDWR)
        self.connected_client.close()
        if self.server:
            for client in self.server.clients:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
            
            self.server.server.shutdown(socket.SHUT_RDWR)
            self.server.server.close()

    def run(self):
        self.screen.fill(self.palette["blue"])
        self.draw_base_components()
        self.is_running = True
        while True: 
            if self.navigate:
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
                            pygame.mixer.Sound.play(self.sfx["waterdrop"])
                            self.pen_color = possible_new_color
                        elif self.board.is_brush_clicked(x, y):
                            self.mode = "paint"
                            self.pen_color = self.pen_previous_color
                        elif self.board.is_eraser_clicked(x, y):
                            pygame.mixer.Sound.play(self.sfx["waterdrop"])
                            self.mode = "erase"
                            self.pen_previous_color = self.pen_color if self.pen_color != "white" else self.pen_previous_color
                            self.pen_color = "white"

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_board_pressed = False

                elif event.type == pygame.MOUSEMOTION and self.is_board_pressed == True and self.board.is_painting_inside_board(x, y, self.pen_radius):
                    if self.mode == "paint":
                        self.pen_radius = 3
                        self.pen(self.screen, x, y)
                    elif self.mode == "erase":
                        self.pen_radius = 10
                        self.pen(self.screen, x, y)
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
        update = json.dumps({
            "type": "board_update",
            "author": self.name,
            "data": {
                "color": color,
                "radius": radius,
                "x": x,
                "y": y
            }
        }).encode(DEFAULT_STRING_FORMAT)
        update_length = ("0"*(MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(update)))) + str(len(update))).encode(DEFAULT_STRING_FORMAT)

        self.connected_client.sendall(update_length)
        self.connected_client.sendall(update)

    def join_match(self):
        request_body = json.dumps({
            "type": "join",
            "data": {
                "name": self.name
            }
        }).encode(DEFAULT_STRING_FORMAT)
        request_length = ("0"*(MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(request_body)))) + str(len(request_body))).encode(DEFAULT_STRING_FORMAT)

        self.connected_client.sendall(request_length)
        self.connected_client.sendall(request_body)

        initial_packet = self.connected_client.recv(MESSAGE_LENGTH_HEADER_LENGTH).decode(DEFAULT_STRING_FORMAT)

        if initial_packet:
            incoming_message_length = int(initial_packet)

            message = self.connected_client.recv(incoming_message_length).decode(DEFAULT_STRING_FORMAT)
            object = json.loads(message)

            if not object["data"].get("success"):
                self.navigate = "menu"
                self.error = "Oops!"