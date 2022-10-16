from numpy import empty
import pygame
from pygame import gfxdraw

class Ranking:
    def __init__(self, width, height, client, palette):
        self.padding = 14
        self.width = width
        self.height = height

        self.palette = palette
        self.ranking_rect = pygame.Rect(self.padding*2+client.board.width, self.padding, width, height)
        self.subsurface = client.screen.subsurface(self.ranking_rect)
        self.clear()

    def clear(self):
        self.subsurface.fill(self.palette["blue"])
        self.background_rect = pygame.Rect(0,0,self.width,self.height)
        pygame.draw.rect(self.subsurface, self.palette["navy_blue"], self.background_rect,0,5)

        

