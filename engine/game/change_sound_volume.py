from pygame.mixer import music


def change_sound_volume(self):
    self.master_volume = float(self.config["USER"]["master_volume"])

    self.music_volume = float(self.config["USER"]["music_volume"])
    self.play_music_volume = self.master_volume * self.music_volume / 10000
    self.effect_volume = float(self.config["USER"]["effect_volume"])
    self.play_effect_volume = self.master_volume * self.effect_volume / 10000
    self.voice_volume = float(self.config["USER"]["voice_volume"])
    self.play_voice_volume = self.master_volume * self.voice_volume / 10000

    music.set_volume(self.play_music_volume)  # set new music player volume

    self.battle.master_volume = self.master_volume
    self.battle.play_music_volume = self.play_music_volume
    self.battle.play_effect_volume = self.play_effect_volume
    self.battle.play_voice_volume = self.play_voice_volume

    volume_stat = {"master": self.master_volume, "music": self.music_volume,
                   "effect": self.effect_volume, "voice": self.voice_volume}

    for key, value in self.option_menu_sliders.items():  # re-update volume slider
        value.player_input(self.value_boxes[key], forced_value=volume_stat[key])
        self.battle.esc_slider_menu[key].player_input(self.battle.esc_value_boxes[key], forced_value=volume_stat[key])
