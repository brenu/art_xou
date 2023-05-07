import pygame
from pygame import gfxdraw
import json
from source.core.game_consts import GameConsts

game_consts = GameConsts()

class Hints:
    def __init__(self, width, height, client, palette):
        self.padding = 14
        self.width = width
        self.height = height
        self.palette = palette
        self.client = client
        self.hint_rect = pygame.Rect(self.padding+614, self.padding+414, width, height)
        self.subsurface = client.screen.subsurface(self.hint_rect)
        self.subsurface.fill(palette["blue"])

        self.bulb_icon = pygame.image.load("assets/icons/bulb.svg")
        self.font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 22)

        self.gaven_hints = 0

    def clear(self, is_drawing_player):
        self.subsurface.fill(self.palette["blue"])
        if is_drawing_player:
            self.background_rect = pygame.Rect(0,0,self.width,self.height)
            pygame.draw.rect(self.subsurface, self.palette["navy_blue"], self.background_rect,0,5)

            text = self.font.render("dica", True, self.palette["white"])

            text_rectangle = text.get_rect()
            text_rectangle.center = self.background_rect.center

            self.subsurface.blit(text, text_rectangle)
            self.subsurface.blit(self.bulb_icon, (10,text_rectangle.centery-self.bulb_icon.get_height()/2))
            self.subsurface.blit(self.bulb_icon, (self.background_rect.width-self.bulb_icon.get_width()-10, text_rectangle.centery-self.bulb_icon.get_height()/2))

    def give_hint(self):
        try:
            hint = json.dumps({
                "type": "hint",
                "data": {}
            }).encode(game_consts.DEFAULT_STRING_FORMAT)
            hint_length = ("0"*(game_consts.MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(hint)))) + str(len(hint))).encode(game_consts.DEFAULT_STRING_FORMAT)

            self.client.connected_client.sendall(hint_length)
            self.client.connected_client.sendall(hint)
        except:
            pass
    
    def is_hint_clicked(self, x, y):
        return self.hint_rect.collidepoint(x,y)
