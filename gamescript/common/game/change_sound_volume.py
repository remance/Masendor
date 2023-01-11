import pygame


def change_sound_volume(self):
    self.master_volume = float(self.config["USER"]["effect_volume"])

    self.music_volume = float(self.config["USER"]["music_volume"])
    self.play_music_volume = self.master_volume * self.music_volume / 10000
    self.effect_volume = float(self.config["USER"]["effect_volume"])
    self.play_effect_volume = self.master_volume * self.effect_volume / 10000
    self.voice_volume = float(self.config["USER"]["voice_volume"])
    self.play_voice_volume = self.master_volume * self.voice_volume / 10000

    pygame.mixer.music.set_volume(self.play_music_volume)  # set new music player volume

    self.battle_game.master_volume = self.master_volume
    self.battle_game.play_music_volume = self.play_music_volume
    self.battle_game.play_effect_volume = self.play_effect_volume
    self.battle_game.play_voice_volume = self.play_voice_volume
