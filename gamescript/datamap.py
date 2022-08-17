import csv
import os

import pygame
from gamescript import weather, battleui, lorebook, menu, uniteditor, datastat, popup, battlemap
from gamescript.common import utility, animation

stat_convert = utility.stat_convert
load_image = utility.load_image
load_images = utility.load_images
csv_read = utility.csv_read


class BattleMapData:
    def __init__(self, main_dir, screen_scale):
        self.feature_list = []
        with open(os.path.join(main_dir, "data", "map", "terrain_effect.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                self.feature_list.append(row[1])  # get terrain feature combination name for folder
        edit_file.close()
        self.feature_list = self.feature_list[1:]

        empty_image = load_image(main_dir, (1, 1), "empty.png", "map/texture")  # empty texture image
        map_texture = []
        texture_folder = [item for item in self.feature_list if item != ""]  # For now remove terrain with no planned name/folder yet
        for index, folder in enumerate(texture_folder):
            images = load_images(main_dir, (1, 1), ["map", "texture", folder], load_order=False)
            map_texture.append(list(images.values()))

        # read terrain feature mode
        self.feature_mod = {}
        with open(os.path.join(main_dir, "data", "map", "terrain_effect.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            mod_column = ("Infantry Speed/Charge Effect", "Infantry Combat Effect", "Infantry Defense Effect",
                          "Cavalry Speed/Charge Effect", "Cavalry Combat Effect", "Cavalry Defense Effect")
            int_column = ("ID", "Range Defense Bonus", "Hide Bonus", "Discipline Bonus",
                          "Day Temperature", "Night Temperature", "Dust")  # value int only
            tuple_column = ("Status",)
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, mod_column=mod_column, tuple_column=tuple_column,
                                       int_column=int_column)
                self.feature_mod[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}

                # Add twilight temperature
                self.feature_mod[row[0]]["Twilight Temperature"] = \
                    int((self.feature_mod[row[0]]["Day Temperature"] +
                         self.feature_mod[row[0]]["Night Temperature"]) / 2)

        edit_file.close()

        self.day_effect_images = load_images(main_dir, screen_scale, ["map", "day"], load_order=False)

        # set up default
        battlemap.FeatureMap.feature_mod = self.feature_mod

        battlemap.BeautifulMap.texture_images = map_texture
        battlemap.BeautifulMap.load_texture_list = texture_folder
        battlemap.BeautifulMap.empty_texture = empty_image

        self.weather_data = {}
        with open(os.path.join(main_dir, "data","map", "weather", "weather.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", )  # value int only
            tuple_column = ("Element", "Status", "Spell", "Ruleset")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column)
                self.weather_data[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()
        weather_list = [item["Name"] for item in self.weather_data.values()]
        strength_list = ["Light ", "Normal ", "Strong "]
        self.weather_list = []
        for item in weather_list:  # list of weather with different strength
            for strength in strength_list:
                self.weather_list.append(strength + item)

        self.weather_matter_images = []
        for weather_sprite in weather_list:  # Load weather matter sprite image
            try:
                images = load_images(main_dir, screen_scale, ["map", "weather", "matter", weather_sprite],
                                     load_order=False)
                self.weather_matter_images.append(list(images.values()))
            except FileNotFoundError:
                self.weather_matter_images.append([])

        self.weather_effect_images = []
        for weather_effect in weather_list:  # Load weather effect sprite image
            try:
                images = load_images(main_dir, screen_scale, ["map", "weather", "effect", weather_effect],
                                     load_order=False)
                self.weather_effect_images.append(list(images.values()))
            except FileNotFoundError:
                self.weather_effect_images.append([])

        weather_icon_list = load_images(main_dir, screen_scale, ["map", "weather", "icon"],
                                        load_order=False)  # Load weather icon
        new_weather_icon = []
        for weather_icon in weather_list:
            for strength in range(0, 3):
                new_name = weather_icon + "_" + str(strength)
                for item in weather_icon_list:
                    if new_name == item:
                        new_weather_icon.append(weather_icon_list[item])
                        break

        weather.Weather.icons = new_weather_icon
