import pygame


def play_sound_effect(self, sound_name, effect_volume, shake=False):
    sound_effect = pygame.mixer.Sound(self.sound_effect_pool[sound_name])
    sound_effect.set_volume(effect_volume)
    sound_effect.play()

    if shake is not False:
        self.screen_shake_value += shake
