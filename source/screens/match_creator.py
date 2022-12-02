import pygame
import pygame_textinput
import sys

class MatchCreator:
    def __init__(self, screen, palette):
        self.screen = screen
        self.palette = palette    
        self.navigate = None

        self.font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 20)
        self.title_font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 36)
        self.selected_input = 0

        match_name_manager = pygame_textinput.TextInputManager(validator = lambda input: len(input) <= 15)
        self.match_name_input = pygame_textinput.TextInputVisualizer(manager=match_name_manager)
        self.match_name_input.font_color = palette["white"]
        self.match_name_input.cursor_color = palette["white"]
        self.match_name_input.font_object = self.font
        self.match_name_input.cursor_width = 2
        self.match_name_rect = pygame.Rect(0, 0, 300, 50)
        self.match_name_rect.center = (1280/2, 720*0.4)

        player_name_manager = pygame_textinput.TextInputManager(validator = lambda input: len(input) <= 15)
        self.player_name_input = pygame_textinput.TextInputVisualizer(manager=player_name_manager)
        self.player_name_input.font_color = palette["white"]
        self.player_name_input.cursor_color = palette["white"]
        self.player_name_input.font_object = self.font
        self.player_name_input.cursor_width = 2
        self.player_name_rect = pygame.Rect(0, 0, 300, 50)
        self.player_name_rect.center = (1280/2, 720*0.55)

        self.create_button = pygame.Rect(0, 0, 300, 50)
        self.create_button.center = (1280/2, 720*0.67)

    def run(self):
        while True:
            self.draw_base_components()
            if self.navigate:
                return

            events = pygame.event.get()
            
            if self.selected_input == 0:
                self.match_name_input.update(events)
            else:
                self.player_name_input.update(events)

            ( x, y ) = pygame.mouse.get_pos()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.check_input_focus(x, y)
                    self.check_submit(x, y)
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "\x1b":
                        self.navigate = "menu"
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def check_input_focus(self, x, y):
        if self.match_name_rect.collidepoint(x, y):
            self.selected_input = 0
            self.match_name_input.cursor_visible = True
            self.player_name_input.cursor_visible = False
        elif self.player_name_rect.collidepoint(x, y):
            self.selected_input = 1
            self.match_name_input.cursor_visible = False
            self.player_name_input.cursor_visible = True

    def check_submit(self, x, y):
        if self.create_button.collidepoint(x, y):
            self.navigate = "game"

    def draw_base_components(self):
        self.screen.fill(self.palette["blue"])

        text = self.title_font.render("Criar Partida", True, self.palette["white"])
        self.screen.blit(text, text.get_rect(center=(1280/2, 720/6)))

        text = self.font.render("Nome da partida", True, self.palette["white"])
        pygame.draw.rect(self.screen, self.palette["navy_blue"], self.match_name_rect, 0, 0)
        self.screen.blit(text, text.get_rect(left=self.match_name_rect.left, bottom=self.match_name_rect.top - 10))

        text = self.font.render("Nome de jogador", True, self.palette["white"])
        pygame.draw.rect(self.screen, self.palette["navy_blue"], self.player_name_rect, 0, 0)
        self.screen.blit(text, text.get_rect(left=self.player_name_rect.left, bottom=self.player_name_rect.top - 10))

        self.screen.blit(self.match_name_input.surface, (self.match_name_rect.left+4, self.match_name_rect.top+10))
        self.screen.blit(self.player_name_input.surface, (self.player_name_rect.left+4, self.player_name_rect.top+10))

        text = self.font.render("Criar", True, self.palette["white"])
        pygame.draw.rect(self.screen, self.palette["navy_blue"], self.create_button, 0, 6)
        self.screen.blit(text, text.get_rect(center=self.create_button.center))

        self.draw_screen()

    def draw_screen(self):
        pygame.display.update()