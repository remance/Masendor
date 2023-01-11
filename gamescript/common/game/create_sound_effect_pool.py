import os
import pygame


def create_sound_effect_pool(self):
    sound_effect_pool = {}
    dir_path = os.path.join(self.main_dir, "data", "sound", "effect")
    for file in os.listdir(dir_path):
        if file.endswith(".ogg"):  # read ogg file only
            sound_effect_pool[file.split(".")[0]] = os.path.join(dir_path, file)
    return sound_effect_pool
