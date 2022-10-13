import json
import os
import sys
import threading
import pygame
import socket

from board import Board
from chat import Chat
from ranking import Ranking
from server import Server

PORT = 65432
DEFAULT_STRING_FORMAT = "utf-8"
MESSAGE_LENGTH_HEADER_LENGTH = 128

class Client:
    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Art Xou")
        self.name = "Fulano"

        self.default_padding = 14
        self.palette = {
            "blue": (30,129,176),
            "white": (255,255,255),
            "black": (10,10,10),
            "red": (255, 85, 85),
            "cyano": (68, 187, 187),
            "green": (96, 210, 5),
            "purple": (136, 58, 234),
            "pink": (252, 123, 255),
            "yellow": (253, 227, 137),
            "orange": (254, 171, 95),
            "navy_blue": (29, 89, 132),
            "gray_border": (231, 228, 228)
        }

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

        self.server = Server() if sys.argv[1] == "server" else None
        
        self.connected_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_client.connect((socket.gethostbyname(socket.gethostname()), PORT))

        threading.Thread(target=self.handle_incoming_data).start()

    def handle_incoming_data(self):
        while True:
            initial_packet = self.connected_client.recv(MESSAGE_LENGTH_HEADER_LENGTH).decode(DEFAULT_STRING_FORMAT)

            if initial_packet:
                incoming_message_length = int(initial_packet)

                message = self.connected_client.recv(incoming_message_length).decode(DEFAULT_STRING_FORMAT)
                object = json.loads(message)

                if object["type"] == "answer":
                    self.chat.update_messages_list(object["data"])
                elif object["type"] == "board_update":
                    pygame.draw.circle(self.screen, object["data"]["color"], ( object["data"]["x"], object["data"]["y"] ), object["data"]["radius"] )
                

    def pen(self, screen, x, y):
        pygame.draw.circle( screen, self.palette[self.pen_color], ( x, y ), self.pen_radius )
        self.send_board_update(self.palette[self.pen_color], self.pen_radius, x, y)

    def run(self):
        while True: 
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
                    pygame.quit()

                elif event.type == pygame.KEYDOWN:
                    self.chat.update([event])
            
            self.drawScreen()
            self.chat.update([])

    def drawScreen(self):
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