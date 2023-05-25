import pygame
from source.screens.client import Client
from source.screens.match_finder import MatchFinder
from source.screens.menu import Menu
from source.screens.match_creator import MatchCreator
from source.core.music_player import MusicPlayer
from source.screens.match_end import MatchEnd

def main():
    pygame.mixer.init()
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Art Xou")

    music_player = MusicPlayer()
    music_player.play_track("main_theme")

    palette = {
        "blue": (30,129,176),
        "white": (255,255,255),
        "black": (10,10,10),
        "red": (255, 85, 85),
        "red_delete": (229, 85, 85),
        "cyano": (68, 187, 187),
        "green": (96, 210, 5),
        "purple": (136, 58, 234),
        "pink": (252, 123, 255),
        "yellow": (253, 227, 137),
        "orange": (254, 171, 95), 
        "navy_blue": (29, 89, 132),
        "navy_blue_hover": (19, 79, 122),
        "gray_border": (231, 228, 228),
        "blue_secondary_buttons": (40, 111, 162),
        "blue_secondary_buttons_hover": (30, 101, 152),
    }
    mode = "menu"
    ran = False

    client = None
    menu = None
    match_finder = None
    match_creator = None
    match_end = None

    while True:
        if not ran:
            ran = True
            if client and client.reset:
                client.reset = False
                music_player.play_track("main_theme")
                client.match_reset_ui()
            elif mode == "menu":
                menu = Menu(screen, palette, music_player)
                menu.run()
            elif mode == "game":

                if not match_end:
                    client = Client(
                        screen,
                        palette, 
                        match_creator.player_name_input.value if match_creator else match_finder.player_name_input.value,
                        match_finder.selected_match["address"].split(":") if match_finder else ("localhost", 65432),
                        music_player,
                        menu.server,
                        match_creator.match_name_input.value if match_creator else "",
                        words=[*match_creator.words] if menu.server else []
                    )

                    match_creator = None
                    match_finder = None

                    client.run()
                else:
                    if client.server:
                        client.match_reset()

                    match_end = None
                    client.navigate = None
                
            elif mode == "match_finder":
                match_creator = None
                match_finder = MatchFinder(screen, palette, music_player)
                match_finder.run()
            elif mode == "match_creator":
                match_finder = None
                match_creator = MatchCreator(screen, palette, music_player)
                match_creator.run()
            elif mode == "match_end":
                match_end = MatchEnd(screen, client, palette, music_player, True if client.server else False, client.ranking)
                match_end.run()
        else:
            if mode == "menu" and menu.navigate:
                ran = False
                mode = menu.navigate
            elif mode == "game" and client.navigate:
                ran = False
                mode = client.navigate
                if mode != "match_end" and mode != "game":
                    client = None
            elif mode == "game" and client.reset:
                ran = False
            elif mode == "match_finder" and match_finder.navigate:
                ran = False
                mode = match_finder.navigate
            elif mode == "match_creator" and match_creator.navigate:
                ran = False
                mode = match_creator.navigate
            elif mode == "match_end" and match_end.navigate:
                ran = False
                mode = match_end.navigate

if __name__ == "__main__":
    main()