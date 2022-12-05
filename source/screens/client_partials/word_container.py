import pygame
import pygame_textinput
import json

from source.core.game_consts import GameConsts
game_consts = GameConsts()

class WordContainer:
    def __init__(self, width, height, client, palette):
        self.padding = 14
        self.width = width
        self.height = height
        self.client = client

        self.font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 50)

        self.palette = palette

        self.container_rect = pygame.Rect(self.padding, self.padding*3+client.board.height+42, width, height)
        self.subsurface = client.screen.subsurface(self.container_rect)
        self.clear()

    def clear(self):
        self.subsurface.fill(self.palette["blue"])
        self.background_rect = pygame.Rect(0,0,self.width,self.height)
        pygame.draw.rect(self.subsurface, self.palette["navy_blue"], self.background_rect,0,5)

    def update(self, word):
        self.clear()

        text = self.font.render(word, True, self.palette["white"])

        text_rectangle = text.get_rect()
        text_rectangle.center = self.background_rect.center

        self.subsurface.blit(text, text_rectangle)