import json
import socket
import sys
import pygame
import threading
import netifaces

from source.core.game_consts import GameConsts
game_consts = GameConsts()

class MatchFinder:
    def __init__(self, screen, palette):
        self.navigate = None
        self.screen = screen
        self.palette = palette

        self.screen.fill(self.palette["blue"])
        self.font = pygame.font.Font("assets/fonts/IBMPlexMono-Regular.ttf", 20)
        
        self.test_button = pygame.Rect(0, 0, 300, 50)
        self.test_button.center = (1280/2, 720/2 - 70)
        self.matches = []
        self.selected_match = None

        self.draw_base_components()

    def draw_base_components(self):
        create_text = self.font.render("Partidas Encontradas", True, self.palette["white"])
        create_text_rect = create_text.get_rect()
        create_text_rect.center = (1280/2, 200)

        self.screen.blit(create_text, create_text_rect)

        self.draw_screen()

    def run(self):      
        self.screen.fill(self.palette["blue"])
        self.draw_base_components()
        self.get_available_matches()
        while True:
            if self.navigate:
                return

            ( x, y ) = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.has_clicked_on_match(x, y):
                        self.navigate = "game"
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "\x1b":
                        self.navigate = "menu"
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def has_clicked_on_match(self, x, y):
        for index, match in enumerate(self.matches):
            if match["button"].collidepoint(x, y):
                self.selected_match = self.matches[index]
                return True

    def get_available_matches(self):
        default_gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
        splitted_network_address = default_gateway.split(".")[:3]
        

        for i in range(2, 255):
            possible_device_address = f"{'.'.join(splitted_network_address)}.{i}"
            try:
                threading.Thread(target=self.get_available_match, args=[possible_device_address]).start()
            except:
                continue

    def get_available_match(self, address):
        match_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        match_socket.settimeout(0.05)
        try:
            match_socket.connect((address, 65432))

            self.handle_match_info(match_socket)
            match_socket.shutdown(socket.SHUT_RDWR)
            match_socket.close()
        except:
            match_socket.close()
            return

    def draw_available_matches(self):
        for index, match in enumerate(self.matches):
            create_text = self.font.render(match.get("name"), True, self.palette["white"])
            create_text_rect = create_text.get_rect()
            create_text_rect.center = (1280/2, 250+(index*50))

            match_button = pygame.Rect(0, 0, 450, 50)
            match_button.center = (1280/2, 250+(index*50))

            self.matches[index]["button"] = match_button

            pygame.draw.rect(self.screen, self.palette["navy_blue"], match_button, 0, 10)
            self.screen.blit(create_text, create_text_rect)
            self.draw_screen()

    def handle_match_info(self, connection: socket.socket):
        connection.settimeout(None)
        match_info_request = json.dumps({
            "type": "match_info"
        }).encode(game_consts.DEFAULT_STRING_FORMAT)
        match_info_request_length = ("0"*(game_consts.MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(match_info_request)))) + str(len(match_info_request))).encode(game_consts.DEFAULT_STRING_FORMAT)

        connection.sendall(match_info_request_length)
        connection.sendall(match_info_request)
        initial_packet = connection.recv(game_consts.MESSAGE_LENGTH_HEADER_LENGTH).decode(game_consts.DEFAULT_STRING_FORMAT)

        if initial_packet:
            incoming_message_length = int(initial_packet)

            message = connection.recv(incoming_message_length).decode(game_consts.DEFAULT_STRING_FORMAT)
            object = json.loads(message)

            if object.get("data",{}).get("name"):
                address = f"{connection.getsockname()[0]}:{connection.getsockname()[1]}"

                self.matches.append({
                    "address": address,
                    "name": object.get("data",{}).get("name")
                })

                self.draw_available_matches()

    def stop(self):
        pass

    def draw_screen(self):
        pygame.display.update()