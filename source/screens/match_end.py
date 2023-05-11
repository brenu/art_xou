import pygame
import pygame_textinput
import sys

class MatchEnd:
    def __init__(self, screen, client, palette, music_player, is_match_creator, ranking):
        self.screen = screen
        self.palette = palette    
        self.navigate = None
        self.music_player = music_player
        self.client = client
        self.is_match_creator = is_match_creator
        
        self.ranking = ranking
        self.ranking.sort(key=lambda a: a["score"], reverse=True)

        self.font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 20)
        self.title_font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 36)

        self.trophies = [
            pygame.image.load("assets/icons/1st_trophy.png").convert_alpha(),
            pygame.image.load("assets/icons/2nd_trophy.png").convert_alpha(),
            pygame.image.load("assets/icons/3rd_trophy.png").convert_alpha(),
        ]

        for trophy_index, trophy in enumerate(self.trophies):
            self.trophies[trophy_index] = pygame.transform.scale(trophy, (trophy.get_width()*0.2, trophy.get_height()*0.2))

        self.match_reset_button = pygame.Rect(0, 0, 300, 50)
        self.match_reset_button.center = (1280/2, 720-60)

    def run(self):
        self.draw_base_components()
        while True:
            if self.navigate:
                self.client.navigate = None
                return
            if self.client.reset:
                self.navigate = "game"
                return

            events = pygame.event.get()

            ( x, y ) = pygame.mouse.get_pos()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.check_reset_match(x, y)
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "\x1b":
                        self.navigate = "menu"
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def check_reset_match(self, x, y):
        if self.match_reset_button.collidepoint(x, y):
            self.music_player.play_sound_effect("button_click")
            self.navigate = "game"

    def draw_base_components(self):
        self.screen.fill(self.palette["blue"])

        text = self.title_font.render("Vencedores", True, self.palette["white"])
        self.screen.blit(text, text.get_rect(center=(1280/2, 720/12)))

        players_count = len(self.ranking)
        
        first_trophy_rect = self.trophies[0].get_rect(center=(1280/2, 720/2-self.trophies[0].get_height()/2))
        self.screen.blit(self.trophies[0], first_trophy_rect)
        if players_count > 0:
            text = self.title_font.render(self.ranking[0].get("name"), True, self.palette["white"])
            self.screen.blit(text, text.get_rect(center=(first_trophy_rect.centerx, first_trophy_rect.centery+110)))

        
        second_trophy_rect = self.trophies[1].get_rect(center=(1280/2-1.5*self.trophies[1].get_width(), 720/2+0.5*self.trophies[1].get_height()))
        self.screen.blit(self.trophies[1], second_trophy_rect)
        if players_count > 1:
            text = self.title_font.render(self.ranking[1].get("name"), True, self.palette["white"])
            self.screen.blit(text, text.get_rect(center=(second_trophy_rect.centerx, second_trophy_rect.centery+110)))
        
        third_trophy_rect = self.trophies[2].get_rect(center=(1280/2+1.5*self.trophies[2].get_width(), 720/2+0.5*self.trophies[2].get_height()))
        self.screen.blit(self.trophies[2], third_trophy_rect)
        if players_count > 2:
            text = self.title_font.render(self.ranking[2].get("name"), True, self.palette["white"])
            self.screen.blit(text, text.get_rect(center=(third_trophy_rect.centerx, third_trophy_rect.centery+110)))
        
        if self.is_match_creator:
            pygame.draw.rect(self.screen, self.palette["navy_blue"], self.match_reset_button, 0, 5)
            text = self.font.render("reiniciar partida", True, self.palette["white"])
            self.screen.blit(text, text.get_rect(center=(self.match_reset_button.center)))

        self.draw_screen()

    def draw_screen(self):
        pygame.display.update()