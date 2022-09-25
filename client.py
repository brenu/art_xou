import os
import pygame

from board import Board

class Client:
    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Art Xou")

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
        self.pen_radius = 5
        self.pen_color = "black"
               
        self.board = Board(600, 400, self.screen, self.palette)
        pygame.display.update()

    def pen(self, screen, x, y):
        pygame.draw.circle( screen, self.palette[self.pen_color], ( x, y ), self.pen_radius )

    def run(self):
        while True: 
            ( x, y ) = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.board.is_painting_inside_board(x, y, self.pen_radius):
                        self.is_board_pressed = True
                    else:
                        possible_new_color = self.board.is_color_being_changed(x, y)

                        if possible_new_color:
                            pygame.mixer.Sound.play(self.sfx["waterdrop"])
                            self.pen_color = possible_new_color

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_board_pressed = False

                elif event.type == pygame.MOUSEMOTION and self.is_board_pressed == True and self.board.is_painting_inside_board(x, y, self.pen_radius):
                    self.pen(self.screen, x, y)
                    pygame.display.update()

                elif event.type == pygame.QUIT:
                    pygame.quit()
            
            self.drawScreen()

    def drawScreen(self):
        pygame.display.update()