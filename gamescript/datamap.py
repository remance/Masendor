import csv
import os

import pygame
from gamescript import weather, battleui, lorebook, menu, uniteditor, datastat, popup, map
from gamescript.common import utility, animation
from gamescript.common.subunit import common_subunit_setup

make_sprite = common_subunit_setup.make_sprite
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
            run = 0  # for skipping the first row
            rd = [row for row in rd]
            header = rd[0]
            for row in rd:
                for n, i in enumerate(row):
                    if run != 0:
                        if header[n] == "Status":  # effect list is at column 12
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                            elif i.isdigit():
                                row[n] = [int(i)]

                        elif "Effect" in header[n]:  # other modifier column
                            if i != "":
                                row[n] = float(i) / 100
                            else:  # empty row assign default 1.0
                                row[n] = 1.0

                        elif i.isdigit() or "-" in i:  # modifier bonus (including negative) in other column
                            row[n] = int(i)

                run += 1
                self.feature_mod[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # set up default
        map.FeatureMap.feature_mod = self.feature_mod

        map.BeautifulMap.texture_images = map_texture
        map.BeautifulMap.load_texture_list = texture_folder
        map.BeautifulMap.empty_image = empty_image

        self.weather_data = csv_read(main_dir, "weather.csv", ["data", "map", "weather"], header_key=True)
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
                new_name = weather_icon + "_" + str(strength) + ".png"
                for item in weather_icon_list:
                    if new_name == item:
                        new_weather_icon.append(weather_icon_list[item])
                        break

        weather.Weather.icons = new_weather_icon
