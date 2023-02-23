import pygame


def play_sound_effect(self, sound, effect_volume, shake=False):
    sound_effect = pygame.mixer.Sound(sound)
    sound_effect.set_volume(effect_volume)
    sound_effect.play()
    if shake:
        self.screen_shake_value += shake
