import threading
import pygame
from source.screens.client import Client
from source.screens.match_finder import MatchFinder
from source.screens.menu import Menu
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

    while True:
        if not ran:
            ran = True
            if mode == "menu":
                menu = Menu(screen, palette)
                menu.run()
            elif mode == "game":
                client = Client(
                    screen,
                    palette, "DonoDaBola" if menu.server else "Fulano",
                    match_finder.selected_match["address"].split(":") if match_finder else ("localhost", 65432),
                    menu.server
                )
                client.run()
            elif mode == "match_finder":
                match_finder = MatchFinder(screen, palette)
                match_finder.run()
        else:
            if mode == "menu" and menu.navigate:
                ran = False
                mode = menu.navigate
            elif mode == "game" and client.navigate:
                ran = False
                mode = client.navigate
            elif mode == "match_finder" and match_finder.navigate:
                ran = False
                mode = match_finder.navigate


if __name__ == "__main__":
    main()