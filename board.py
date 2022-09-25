import pygame
from pygame import gfxdraw

class Board:
    def __init__(self, width, height, screen, palette):
        self.padding = 10
        self.width = width
        self.height = height

        self.palette = palette
        self.board_rect = pygame.Rect(self.padding, self.padding, width, height)
        self.subsurface = screen.subsurface(self.board_rect)
        self.subsurface.fill(palette["white"])

        self.options_container_rect = pygame.Rect(self.padding, self.padding*2+height, width, 42)
        self.options_container = screen.subsurface(self.options_container_rect)
        
        self.possible_colors = ["black", "red", "cyano", "green", "purple", "pink", "yellow", "white", "orange", "navy_blue"]
        self.color_btn_diameter = 30

        for index, color in enumerate(self.possible_colors):
            border_color = "white"
            # if color == "white":
            #     border_color = "gray_border"

            gfxdraw.aacircle(self.options_container, 22 + index*(13+30), 21, 15, palette[border_color])
            gfxdraw.filled_circle(self.options_container, 22 + index*(13+30), 21, 15, palette[border_color])

            gfxdraw.aacircle(self.options_container, 22 + index*(13+30), 21, 12, palette[color])
            gfxdraw.filled_circle(self.options_container, 22 + index*(13+30), 21, 12, palette[color])

    
    def is_painting_inside_board(self, x, y, radius) -> bool:
        return x - self.padding*0.5 > self.padding and x + radius < self.padding + self.width \
            and y - self.padding*0.5 > self.padding and y + radius < self.padding + self.height

    def is_color_being_changed(self, x, y):
        if not self.options_container_rect.collidepoint(x,y):
            return None

        color_found = None

        for color in self.possible_colors:
            if self.options_container.get_parent().get_at((x,y))[:3] == self.palette[color]:
                color_found = color

        return color_found
