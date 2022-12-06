from numpy import empty
import pygame
from pygame import gfxdraw

class Ranking:
    def __init__(self, width, height, client, palette):
        self.padding = 14
        self.width = width
        self.height = height

        self.font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 12)
        self.font.bold = True

        self.palette = palette
        self.ranking_rect = pygame.Rect(self.padding*2+client.board.width, self.padding, width, height)
        self.subsurface = client.screen.subsurface(self.ranking_rect)
        self.clear()

    def clear(self):
        self.subsurface.fill(self.palette["blue"])
        self.background_rect = pygame.Rect(0,0,self.width,self.height)
        pygame.draw.rect(self.subsurface, self.palette["navy_blue"], self.background_rect,0,5)

    def update(self, data):
        data = list(data)
        data.sort(key=lambda a: a["score"], reverse=True)

        for index, player in enumerate(data):
            text = self.font.render(f"{index+1}º{player['name']}:{player['score']}", True, self.palette["white"])
            
            text_rectangle = text.get_rect()
            text_rectangle.x = 10
            text_rectangle.y = self.padding + index*30

            self.subsurface.blit(text, text_rectangle)

        

