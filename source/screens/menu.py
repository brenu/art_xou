import sys
import pygame


class Menu():
    def __init__(self, screen, palette, music_player):
        self.screen = screen
        self.palette = palette
        self.server = False
        self.music_player = music_player

        self.screen.fill(self.palette["blue"])
        self.font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 20)

        self.title_font = pygame.font.Font("assets/fonts/CaveatBrush-Regular.ttf", 100)

        self.join_button = pygame.Rect(0, 0, 450, 50)
        self.join_button.center = (1280/2, 720/2 - 70)

        self.icon_picture = pygame.image.load("assets/icons/menu_icon.png").convert_alpha()
        self.icon_picture = pygame.transform.smoothscale(self.icon_picture, (self.icon_picture.get_width()*0.25, self.icon_picture.get_height()*0.25))

        self.create_button = pygame.Rect(0, 0, 450, 50)
        self.create_button.center = (1280/2, 720/2)

        self.mute_button = {
            "False": pygame.image.load("assets/icons/com_som.png").convert_alpha(),
            "True": pygame.image.load("assets/icons/sem_som.png").convert_alpha()
        }
        self.mute_button_center = (1280-35,10)
        
        self.hover_on = -1

        self.navigate = None
        self.draw_base_components()

    def draw_base_components(self):
        self.screen.fill(self.palette["blue"])
        pygame.draw.rect(self.screen, self.palette["navy_blue"] if self.hover_on != 0 else self.palette["navy_blue_hover"], self.join_button, 0, 5)
        pygame.draw.rect(self.screen, self.palette["navy_blue"] if self.hover_on != 1 else self.palette["navy_blue_hover"], self.create_button, 0, 5)
        
        if self.music_player.muted:
            self.screen.blit(self.mute_button["True"], self.mute_button_center)
        else:
            self.screen.blit(self.mute_button["False"], self.mute_button_center)

        create_text = self.title_font.render("Art Xou", True, self.palette["white"])        
        self.screen.blit(create_text, create_text.get_rect(center=(1280/2, 720/8)))

        self.screen.blit(self.icon_picture, self.icon_picture.get_rect(center=(1280/2+create_text.get_rect().width/2+35, 720/8-30)))

        create_text = self.font.render("entrar em partida", True, self.palette["white"])        
        self.screen.blit(create_text, create_text.get_rect(center=self.join_button.center))

        create_text = self.font.render("criar partida", True, self.palette["white"])        
        self.screen.blit(create_text, create_text.get_rect(center=self.create_button.center))

        self.draw_screen()

    def run(self):
        self.screen.fill(self.palette["blue"])
        while True:
            if self.navigate:
                return
            
            self.draw_base_components()
            ( x, y ) = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.has_clicked_create_button(x, y):
                        self.music_player.play_sound_effect("button_click")
                        self.navigate = "match_creator"
                        self.server = True
                    elif self.has_clicked_join_button(x, y):
                        self.music_player.play_sound_effect("button_click")
                        self.navigate = "match_finder"
                    elif self.mute_button["True"].get_rect(center=(self.mute_button_center), width=self.mute_button["True"].get_width()*1.5, height=self.mute_button["True"].get_height()*1.5).collidepoint(x, y):
                        self.music_player.change_playing_state()
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                else:
                    self.check_buttons_hover(x, y)

            
            self.draw_screen()

    def stop(self):
        self.is_running = False

    def check_buttons_hover(self, x, y):
        if self.create_button.collidepoint(x, y):
            self.hover_on = 1
        elif self.join_button.collidepoint(x, y):
            self.hover_on = 0
        else:
            self.hover_on = -1

    def has_clicked_create_button(self, x, y):
        return self.create_button.collidepoint(x, y)
            
    def has_clicked_join_button(self, x, y):
        return self.join_button.collidepoint(x, y)

    def draw_screen(self):
        pygame.display.update()