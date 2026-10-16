from glob import glob
from os import listdir
from os.path import split, join

from pygame.mixer import Sound

from engine.data.datastat import GameData
from engine.utils.data_loading import filename_convert_readable as fcv


class SoundData(GameData):
    def __init__(self):
        GameData.__init__(self)

        # load sound effect
        self.sound_effect_pool = {}
        dir_path = join(self.data_dir, "sound", "effect")
        for file in listdir(dir_path):
            if file.endswith(".ogg"):  # read ogg file only
                file_name = file.split(".")[0]
                if file_name[-1].isdigit() and "_" in file_name and file_name.rfind("_") <= len(file_name) - 2 and \
                        file_name[file_name.rfind("_") + 1].isdigit():  # variation for same sound effect
                    file_name = file_name[:file_name.rfind("_")]

                file_name = fcv(file_name)

                if file_name not in self.sound_effect_pool:
                    self.sound_effect_pool[file_name] = [join(dir_path, file)]
                else:
                    self.sound_effect_pool[file_name].append(join(dir_path, file))

        for file_name in self.sound_effect_pool:  # convert to tuple with pygame Sound object inside
            self.sound_effect_pool[file_name] = tuple([Sound(item) for item in self.sound_effect_pool[file_name]])

        # load music
        self.music_pool = glob(join(self.data_dir, "sound", "music", "*.ogg"))
        self.music_pool = {fcv(split(item)[-1].replace(".ogg", "")): item for
                           item in self.music_pool}

        # load ambient
        self.ambient_pool = glob(join(self.data_dir, "sound", "ambient", "*.ogg"))
        self.ambient_pool = {fcv(split(item)[-1].replace(".ogg", "")): item for
                             item in self.ambient_pool}

        # load weather ambient
        self.weather_ambient_pool = glob(join(self.data_dir, "sound", "weather", "*.ogg"))
        self.weather_ambient_pool = {fcv(split(item)[-1].replace(".ogg", "")): item for
                                     item in self.weather_ambient_pool}
