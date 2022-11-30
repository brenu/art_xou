import pygame
import pygame_textinput
import json

from source.core.game_consts import GameConsts
game_consts = GameConsts()

class Chat:
    def __init__(self, width, height, client, palette):
        self.padding = 14
        self.width = width
        self.height = height
        self.client = client
        
        chat_manager = pygame_textinput.TextInputManager(validator = lambda input: len(input) <= 15)
        self.chat_input = pygame_textinput.TextInputVisualizer(manager=chat_manager)
        self.chat_input.font_color = palette["black"]
        self.chat_input.cursor_color = palette["black"]
        self.chat_input.font_object = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 20)
        self.chat_input.cursor_width = 2

        self.messages = []

        self.palette = palette
        self.chat_rect = pygame.Rect(self.padding*3+client.board.width+client.ranking.width, self.padding, width, height)
        self.subsurface = client.screen.subsurface(self.chat_rect)
        self.clear()

    def clear(self):
        self.subsurface.fill(self.palette["blue"])
        self.background_rect = pygame.Rect(0,0,self.width,self.height)
        pygame.draw.rect(self.subsurface, self.palette["navy_blue"], self.background_rect,0,5)
        self.chat_input_rect = pygame.Rect(self.padding, self.height - self.padding - 40, self.width - self.padding*2, 40)
        pygame.draw.rect(self.subsurface, self.palette["white"], self.chat_input_rect,0,3)

    def update(self, event):
        self.clear()
        self.chat_input.update(event)

        for item in event:
            if item.unicode == "\r":
                self.send_answer(self.chat_input.value)
                self.chat_input.value = ""

        for index, message in enumerate(self.messages):
            font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 16)
            text = font.render(message, True, self.palette["white"])
            
            text_rectangle = text.get_rect()
            text_rectangle.x = 20
            text_rectangle.y = 600 - (index*30)

            self.subsurface.blit(text, text_rectangle)

        self.subsurface.blit(self.chat_input.surface, (20, 650))

    def update_messages_list(self, new_message):
        self.messages.insert(0, new_message)

        if len(self.messages) > 21:
            self.messages.pop()

    def send_answer(self, answer):
        self.update_messages_list(f"You: {answer}")
        
        answer = json.dumps({
            "type": "answer",
            "data": answer
        }).encode(game_consts.DEFAULT_STRING_FORMAT)
        answer_length = ("0"*(game_consts.MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(answer)))) + str(len(answer))).encode(game_consts.DEFAULT_STRING_FORMAT)

        self.client.connected_client.sendall(answer_length)
        self.client.connected_client.sendall(answer)

