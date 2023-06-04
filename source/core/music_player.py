import pygame

class MusicPlayer:
    def __init__(self):
        self.tracks = {
            "main_theme": 'assets/sfx/audio_hero_Yellow-Cafe_SIPML_C-0361.ogg',
            "match_end": 'assets/sfx/audio_hero_Jet-Stream_SIPML_C-0711_1.ogg',
        }

        self.sound_effects = {
            "button_click": pygame.mixer.Sound("assets/sfx/zapsplat_multimedia_button_click_bright_003_92100.ogg"),
            "waterdrop": pygame.mixer.Sound('assets/sfx/zapsplat_household_baby_lotion_movement_sudden_in_bottle_1.ogg'),
            "success": pygame.mixer.Sound('assets/sfx/freesound_success.ogg'),
            "next_word": pygame.mixer.Sound('assets/sfx/freesound_next_word.ogg')
        }

        self.muted = False

    def play_track(self, name: str):
        if not self.muted:
            pygame.mixer.music.load(self.tracks[name])
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)

    def play_sound_effect(self, name:str):
        pygame.mixer.Sound.play(self.sound_effects[name])

    def change_playing_state(self):
        self.muted = not self.muted

        if self.muted:
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.load(self.tracks["main_theme"])
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)