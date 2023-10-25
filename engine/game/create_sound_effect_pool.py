import os

from engine.utils.data_loading import filename_convert_readable as fcv


def create_sound_effect_pool(self):
    sound_effect_pool = {}
    dir_path = os.path.join(self.module_dir, "sound", "effect")
    for file in os.listdir(dir_path):
        if file.endswith(".ogg"):  # read ogg file only
            file_name = file.split(".")[0]
            if file_name[-1].isdigit() and file_name[-2] == "_":  # variation for same sound effect
                file_name = file_name[:-2]

            file_name = fcv(file_name)

            if file_name not in sound_effect_pool:
                sound_effect_pool[file_name] = [os.path.join(dir_path, file)]
            else:
                sound_effect_pool[file_name].append(os.path.join(dir_path, file))

    for file_name in sound_effect_pool:  # convert to tuple
        sound_effect_pool[file_name] = tuple(sound_effect_pool[file_name])

    return sound_effect_pool
