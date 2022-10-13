import pygame
from pygame import gfxdraw

class Board:
    def __init__(self, width, height, client, palette):
        self.padding = 14
        self.width = width
        self.height = height

        self.palette = palette
        self.board_rect = pygame.Rect(self.padding, self.padding, width, height)
        self.subsurface = client.screen.subsurface(self.board_rect)
        self.subsurface.fill(palette["white"])

        self.options_container_rect = pygame.Rect(self.padding, self.padding*2+height, width, 42)
        self.options_container = client.screen.subsurface(self.options_container_rect)
        
        self.button_icons = {
            "brush": pygame.image.load("assets/icons/brush.png").convert_alpha(),
            "eraser": pygame.image.load("assets/icons/eraser.png").convert_alpha(),
            "square": pygame.image.load("assets/icons/square.png").convert_alpha(),
            "circle": pygame.image.load("assets/icons/circle.png").convert_alpha(),
        }

        self.possible_colors = ["black", "red", "cyano", "green", "purple", "pink", "yellow", "white", "orange", "navy_blue"]
        self.color_btn_diameter = 30

        for index, color in enumerate(self.possible_colors):
            border_color = "white"
            # if color == "white":
            #     border_color = "gray_border"

            gfxdraw.aacircle(self.options_container, 18 + index*(13+30), 21, 15, palette[border_color])
            gfxdraw.filled_circle(self.options_container, 18 + index*(13+30), 21, 15, palette[border_color])

            gfxdraw.aacircle(self.options_container, 18 + index*(13+30), 21, 12, palette[color])
            gfxdraw.filled_circle(self.options_container, 18 + index*(13+30), 21, 12, palette[color])

        pygame.draw.rect(self.options_container, self.palette["white"], pygame.Rect(18 + (len(self.possible_colors)-1)*(13+30)+25,1,4,38), 0, 5)

        for key, icon in enumerate(self.button_icons.keys()):
            self.options_container.blit(self.button_icons[icon],((len(self.possible_colors)+key)*(13+30)+14,8))
    
    def is_brush_clicked(self, x, y):
        brush_index = list(self.button_icons.keys()).index("brush")
        brush_width = self.button_icons["brush"].get_rect().width
        brush_position = (len(self.possible_colors)+brush_index)*(13+30)+14

        return self.options_container_rect.collidepoint(x,y) and x >= brush_position + self.padding and x <= brush_position + brush_width + self.padding


    def is_eraser_clicked(self, x, y):
        eraser_index = list(self.button_icons.keys()).index("eraser")
        eraser_width = self.button_icons["eraser"].get_rect().width
        eraser_position = (len(self.possible_colors)+eraser_index)*(13+30)+14

        return self.options_container_rect.collidepoint(x,y) and x >= eraser_position + self.padding and x <= eraser_position + eraser_width + self.padding

    def is_painting_inside_board(self, x, y, radius) -> bool:
        return x - self.padding*0.5 > self.padding and x + radius < self.padding + self.width \
            and y - self.padding*0.5 > self.padding and y + radius < self.padding + self.height

    def is_color_being_changed(self, x, y):
        if not self.options_container_rect.collidepoint(x,y) or x > 435:
            return None

        color_found = None

        for color in self.possible_colors:
            if self.options_container.get_parent().get_at((x,y))[:3] == self.palette[color]:
                color_found = color

        return color_found

    def send_board_update():
        pass
