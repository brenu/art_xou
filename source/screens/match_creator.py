import pygame
import pygame_textinput
import sys
import re

from source.core.game_consts import GameConsts

game_consts = GameConsts()

class MatchCreator:
    def __init__(self, screen, palette, music_player):
        self.screen = screen
        self.palette = palette    
        self.navigate = None
        self.music_player = music_player
        
        self.words = []
        self.words_delete_rects = []
        self.word_hover = -1

        self.font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 20)
        self.title_font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 36)
        self.selected_input = 0
        
        self.step = 0
        self.hover_on = -1

        match_name_manager = pygame_textinput.TextInputManager(validator = lambda input: len(input) <= 15)
        self.match_name_input = pygame_textinput.TextInputVisualizer(manager=match_name_manager)
        self.match_name_input.font_color = palette["white"]
        self.match_name_input.cursor_color = palette["white"]
        self.match_name_input.font_object = self.font
        self.match_name_input.cursor_width = 2
        self.match_name_rect = pygame.Rect(0, 0, 400, 50)
        self.match_name_rect.center = (1280/2, 720*0.4)

        player_name_manager = pygame_textinput.TextInputManager(validator = lambda input: len(input) <= 15)
        self.player_name_input = pygame_textinput.TextInputVisualizer(manager=player_name_manager)
        self.player_name_input.font_color = palette["white"]
        self.player_name_input.cursor_color = palette["white"]
        self.player_name_input.font_object = self.font
        self.player_name_input.cursor_width = 2
        self.player_name_rect = pygame.Rect(0, 0, 400, 50)
        self.player_name_rect.center = (1280/2, 720*0.55)

        theme_word_manager = pygame_textinput.TextInputManager(validator = lambda input: len(input) <= 15)
        self.theme_word_input = pygame_textinput.TextInputVisualizer(manager=theme_word_manager)
        self.theme_word_input.font_color = palette["white"]
        self.theme_word_input.cursor_color = palette["white"]
        self.theme_word_input.font_object = self.font
        self.theme_word_input.cursor_width = 2
        self.theme_word_rect = pygame.Rect(0, 0, 380, 50)
        self.theme_word_rect.center = (1280/2, 720*0.3)
        self.new_word_button = pygame.Rect(0, 0, 35, 35)
        self.new_word_button.center = (self.theme_word_rect.x+self.theme_word_rect.width-self.new_word_button.width/2 - 10, self.theme_word_rect.centery)

        self.customized_theme_button = pygame.Rect(0, 0, 300, 50)
        self.customized_theme_button.center = (1280/2, 720*0.77)

    def run(self):
        while True:
            self.draw_base_components()
            if self.navigate:
                return

            events = pygame.event.get()
            
            if self.selected_input == 0:
                self.match_name_input.update(events)
                self.match_name_input.value = re.sub(game_consts.inputs_regex, "", self.match_name_input.value)
            elif self.selected_input == 1:
                self.player_name_input.update(events)
                self.player_name_input.value = re.sub(game_consts.inputs_regex, "", self.player_name_input.value)
            elif len(self.words) < 35:
                self.theme_word_input.update(events)
                self.theme_word_input.value = re.sub(game_consts.inputs_regex, "", self.theme_word_input.value)
            else:
                self.theme_word_input.cursor_visible = False

            ( x, y ) = pygame.mouse.get_pos()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.check_input_focus(x, y)
                    self.clicked_customized_theme(x, y)
                    self.check_word_submit(x, y)
                    self.check_words_delete(x, y)
                    self.check_submit(x, y)
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "\x1b":
                        if self.step > 0:
                            self.step = self.step - 1
                        else:
                            self.navigate = "menu"
                    elif event.unicode == "\x0D":
                        if self.step == 0:
                            if self.selected_input == 0:
                                self.selected_input = 1
                                self.match_name_input.cursor_visible = False
                                self.player_name_input.cursor_visible = True
                            else:
                                self.navigate = "game"
                        elif self.step == 1:
                            if self.theme_word_input.value:
                                self.music_player.play_sound_effect("button_click")
                                self.words.append(self.theme_word_input.value)
                                self.theme_word_input.value = ""
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                else:
                    self.check_buttons_hover(x, y)

    def check_words_delete(self, x, y):
        if self.step == 0:
            return
    
        for index, word in enumerate(self.words_delete_rects):
            if word.collidepoint(x, y):
                self.music_player.play_sound_effect("button_click")
                self.words_delete_rects.pop(index)
                self.words.pop(index)
            

    def check_buttons_hover(self, x, y):
        if self.create_button.collidepoint(x, y):
            self.hover_on = 0
        elif self.customized_theme_button.collidepoint(x, y):
            self.hover_on = 1
        elif self.new_word_button.collidepoint(x, y):
            self.hover_on = 2
        else:
            self.hover_on = -1

    def check_input_focus(self, x, y):
        if self.step == 0:
            if self.match_name_rect.collidepoint(x, y):
                self.selected_input = 0
                self.match_name_input.cursor_visible = True
                self.player_name_input.cursor_visible = False
            elif self.player_name_rect.collidepoint(x, y):
                self.selected_input = 1
                self.match_name_input.cursor_visible = False
                self.player_name_input.cursor_visible = True
        else:
            if len(self.words) < 35:
                self.theme_word_input.cursor_visible = True
            else:
                self.theme_word_input.cursor_visible = False

        return


    def check_submit(self, x, y):
        if self.create_button.collidepoint(x, y):
            self.music_player.play_sound_effect("button_click")
            self.navigate = "game"

    def check_word_submit(self, x, y): 
        if len(self.words) >= 35:
            return

        if self.step == 1 and self.new_word_button.collidepoint(x, y):
            self.music_player.play_sound_effect("button_click")
            self.words.append(self.theme_word_input.value)
            self.theme_word_input.value = ""


    def clicked_customized_theme(self, x, y):
        if self.step == 0 and self.customized_theme_button.collidepoint(x, y):
            self.music_player.play_sound_effect("button_click")
            self.selected_input = 2
            self.step = 1

    def draw_base_components(self):
        self.screen.fill(self.palette["blue"])

        if self.step == 0:
            text = self.title_font.render("Criar Partida", True, self.palette["white"])
            self.screen.blit(text, text.get_rect(center=(1280/2, 720/6)))

            text = self.font.render("Nome da partida", True, self.palette["white"])
            pygame.draw.rect(self.screen, self.palette["navy_blue"], self.match_name_rect, 0, 5)
            self.screen.blit(text, text.get_rect(left=self.match_name_rect.left, bottom=self.match_name_rect.top - 10))

            text = self.font.render("Nome de jogador", True, self.palette["white"])
            pygame.draw.rect(self.screen, self.palette["navy_blue"], self.player_name_rect, 0, 5)
            self.screen.blit(text, text.get_rect(left=self.player_name_rect.left, bottom=self.player_name_rect.top - 10))

            self.screen.blit(self.match_name_input.surface, (self.match_name_rect.left+4, self.match_name_rect.top+10))
            self.screen.blit(self.player_name_input.surface, (self.player_name_rect.left+4, self.player_name_rect.top+10))

            self.create_button = pygame.Rect(0, 0, 400, 50)
            self.create_button.center = (1280/2, 720*0.67)
            text = self.font.render("criar partida", True, self.palette["white"])
            pygame.draw.rect(self.screen, 
                             self.palette["navy_blue"] if not self.hover_on == 0 else self.palette["navy_blue_hover"], 
                             self.create_button, 0, 6)
            self.screen.blit(text, text.get_rect(center=self.create_button.center))

            text = self.font.render("tema personalizado", True, self.palette["white"])
            pygame.draw.rect(self.screen, 
                             self.palette["blue_secondary_buttons"] if not self.hover_on == 1 else self.palette["blue_secondary_buttons_hover"], 
                             self.customized_theme_button, 0, 6)
            self.screen.blit(text, text.get_rect(center=self.customized_theme_button.center))
        elif self.step == 1:
            text = self.title_font.render("Tema Personalizado", True, self.palette["white"])
            self.screen.blit(text, text.get_rect(center=(1280/2, 720/8)))


            if len(self.words) < 35:
                text = self.font.render("Adicionar palavras", True, self.palette["white"])
                # Input de adicionar palavra
                pygame.draw.rect(self.screen, self.palette["navy_blue"], self.theme_word_rect, 0, 5)
                self.screen.blit(text, text.get_rect(left=self.theme_word_rect.left, bottom=self.theme_word_rect.top - 10))
                # Botão de adicionar palavra
                pygame.draw.rect(self.screen, self.palette["blue"] if not self.hover_on == 2 else self.palette["navy_blue_hover"], self.new_word_button, 0, 3)
                text = self.font.render("+", True, self.palette["white"])
                self.screen.blit(text, text.get_rect(center=self.new_word_button.center))
            else:
                text = self.font.render("Limite atingido!", True, self.palette["white"])
                # Input de adicionar palavra
                pygame.draw.rect(self.screen, self.palette["red_delete"], self.theme_word_rect, 0, 5)
                self.screen.blit(text, text.get_rect(left=self.theme_word_rect.left, bottom=self.theme_word_rect.top - 10))
                # Botão de adicionar palavra
                pygame.draw.rect(self.screen, self.palette["navy_blue_hover"], self.new_word_button, 0, 3)
                text = self.font.render("+", True, self.palette["white"])
                self.screen.blit(text, text.get_rect(center=self.new_word_button.center))
            

            self.screen.blit(self.theme_word_input.surface, (self.theme_word_rect.left+4, self.theme_word_rect.top+10))

            self.create_button = pygame.Rect(0, 0, 400, 50)
            self.create_button.center = (1280/2, 720*0.90)
            text = self.font.render("criar partida", True, self.palette["white"])
            pygame.draw.rect(self.screen, 
                             self.palette["navy_blue"] if not self.hover_on == 0 else self.palette["navy_blue_hover"], 
                             self.create_button, 0, 6)
            self.screen.blit(text, text.get_rect(center=self.create_button.center))

            self.words_delete_rects = []
            for index, word in enumerate(self.words):
                text = self.font.render(word, True, self.palette["white"])
                text_rect = text.get_rect()

                word_button = pygame.Rect(0, 0, 200, text_rect.height+5)
                word_button.center = self.get_word_center(index)
                text_rect.center = word_button.center

                pygame.draw.rect(self.screen,
                        self.palette["navy_blue"] if not self.word_hover == index else self.palette["navy_blue_hover"],
                        word_button, 0, 3)
                self.screen.blit(text, text_rect)
                
                text = self.font.render("x", True, self.palette["white"])

                delete_button = pygame.Rect(0, 0, 25, 25)
                delete_button.center = (word_button.x+word_button.width, word_button.y)
                self.words_delete_rects.append(delete_button)

                pygame.draw.rect(self.screen,
                        self.palette["red_delete"],
                        delete_button, 0, 13)
                self.screen.blit(text, text.get_rect(center=(delete_button.centerx, delete_button.centery-2)))

        self.draw_screen()

    def get_word_center(self, index):
        if index % 5 == 0:
            return (1280*0.125, 720*0.4+50*int(index/5))
        else:
            return (self.get_word_center(index-1)[0]+200+40, 720*0.4+50*int(index/5))

    def draw_screen(self):
        pygame.display.update()