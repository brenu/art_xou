import threading
import pygame
from source.screens.client import Client
from source.screens.match_finder import MatchFinder
from source.screens.menu import Menu
from source.screens.match_creator import MatchCreator
import gc

def main():
    pygame.mixer.init()
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Art Xou")

    palette = {
        "blue": (30,129,176),
        "white": (255,255,255),
        "black": (10,10,10),
        "red": (255, 85, 85),
        "cyano": (68, 187, 187),
        "green": (96, 210, 5),
        "purple": (136, 58, 234),
        "pink": (252, 123, 255),
        "yellow": (253, 227, 137),
        "orange": (254, 171, 95), 
        "navy_blue": (29, 89, 132),
        "gray_border": (231, 228, 228)
    }
    mode = "menu"
    ran = False

    client = None
    menu = None
    match_finder = None
    match_creator = None

    while True:
        if not ran:
            ran = True
            if mode == "menu":
                menu = Menu(screen, palette)
                menu.run()
            elif mode == "game":

                client = Client(
                    screen,
                    palette, 
                    match_creator.player_name_input.value if match_creator else match_finder.player_name_input.value,
                    match_finder.selected_match["address"].split(":") if match_finder else ("localhost", 65432),
                    menu.server,
                    match_creator.match_name_input.value if match_creator else "",
                )

                match_creator = None
                match_finder = None

                client.run()
            elif mode == "match_finder":
                match_creator = None
                match_finder = MatchFinder(screen, palette)
                match_finder.run()
            elif mode == "match_creator":
                match_finder = None
                match_creator = MatchCreator(screen, palette)
                match_creator.run()
        else:
            if mode == "menu" and menu.navigate:
                ran = False
                mode = menu.navigate
            elif mode == "game" and client.navigate:
                ran = False
                mode = client.navigate
                client = None
            elif mode == "match_finder" and match_finder.navigate:
                ran = False
                mode = match_finder.navigate
            elif mode == "match_creator" and match_creator.navigate:
                ran = False
                mode = match_creator.navigate


if __name__ == "__main__":
    main()