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

        self.join_button = pygame.Rect(0, 0, 300, 50)
        self.join_button.center = (1280/2, 720/2 - 70)

        self.create_button = pygame.Rect(0, 0, 300, 50)
        self.create_button.center = (1280/2, 720/2)

        self.navigate = None
        self.draw_base_components()

    def draw_base_components(self):
        pygame.draw.rect(self.screen, self.palette["navy_blue"], self.join_button, 0, 5)
        pygame.draw.rect(self.screen, self.palette["navy_blue"], self.create_button, 0, 5)

        create_text = self.font.render("entrar em partida", True, self.palette["white"])        
        self.screen.blit(create_text, create_text.get_rect(center=self.join_button.center))

        create_text = self.font.render("criar partida", True, self.palette["white"])        
        self.screen.blit(create_text, create_text.get_rect(center=self.create_button.center))

        self.draw_screen()

    def run(self):
        self.screen.fill(self.palette["blue"])
        self.draw_base_components()
        while True:
            if self.navigate:
                return
            
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
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            
            self.draw_screen()

    def stop(self):
        self.is_running = False

    def has_clicked_create_button(self, x, y):
        return self.create_button.collidepoint(x, y)
            
    def has_clicked_join_button(self, x, y):
        return self.join_button.collidepoint(x, y)

    def draw_screen(self):
        pygame.display.update()