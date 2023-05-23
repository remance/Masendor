import ast
import csv
import os

from pathlib import Path


from engine.weather import weather
from engine.utility import stat_convert, load_images, csv_read, filename_convert_readable as fcv

from engine.data.datastat import GameData


class BattleMapData(GameData):
    terrain_list = None
    terrain_colour = None
    feature_colour = None
    feature_list = None
    feature_mod = None
    battle_map_colour = None

    def __init__(self):
        """
        For keeping all data related to battle map.
        """
        GameData.__init__(self)
        BattleMapData.terrain_colour = {}
        with open(os.path.join(self.module_dir, "map", "terrain.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                        elif "," in i:
                            row[n] = ast.literal_eval(i)
                    BattleMapData.terrain_colour[row[0]] = row[1:]
        BattleMapData.terrain_list = tuple(BattleMapData.terrain_colour.keys())
        BattleMapData.terrain_colour = tuple([value[0] for value in BattleMapData.terrain_colour.values()])

        BattleMapData.feature_colour = {}
        with open(os.path.join(self.module_dir, "map", "feature.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                        elif "," in i:
                            row[n] = ast.literal_eval(i)
                    BattleMapData.feature_colour[row[0]] = row[1:]

        BattleMapData.feature_list = tuple(BattleMapData.feature_colour.keys())
        BattleMapData.feature_colour = tuple([value[0] for value in BattleMapData.feature_colour.values()])

        # read terrain feature mode
        BattleMapData.feature_mod = {}
        with open(os.path.join(self.module_dir, "map", "terrain_effect.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            mod_column = ("Infantry Speed Modifier", "Infantry Melee Modifier",
                          "Cavalry Speed Modifier", "Cavalry Melee Modifier")
            int_column = ("ID", "Range Defence Bonus", "Hide Bonus", "Discipline Bonus",
                          "Day Temperature", "Night Temperature", "Dust")  # value int only
            tuple_column = ("Status",)
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, mod_column=mod_column, tuple_column=tuple_column,
                                       int_column=int_column)
                BattleMapData.feature_mod[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}

                # Add twilight temperature
                BattleMapData.feature_mod[row[0]]["Twilight Temperature"] = \
                    int((BattleMapData.feature_mod[row[0]]["Day Temperature"] +
                         BattleMapData.feature_mod[row[0]]["Night Temperature"]) / 2)
        edit_file.close()

        self.feature_mod_lore = self.localisation.create_lore_data("terrain_effect")

        BattleMapData.battle_map_colour = {}
        with open(os.path.join(self.module_dir, "map", "map_colour.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                        elif "," in i:
                            row[n] = ast.literal_eval(i)
                    BattleMapData.battle_map_colour[row[0]] = row[1:]

        self.weather_data = {}
        with open(os.path.join(self.module_dir, "map", "weather", "weather.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID",)  # value int only
            tuple_column = ("Element", "Status", "Spell")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column)
                self.weather_data[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        weather_list = [item["Name"] for item in self.weather_data.values()]
        strength_list = ("Light ", "Normal ", "Strong ")
        self.weather_list = []
        for item in weather_list:  # list of weather with different strength
            for strength in strength_list:
                self.weather_list.append(strength + item)
        self.weather_list = tuple(self.weather_list)
        edit_file.close()

        self.weather_lore = self.localisation.create_lore_data("weather")

        self.weather_matter_images = {}
        for this_weather in weather_list:  # Load weather matter sprite image
            try:
                images = load_images(self.module_dir, screen_scale=self.screen_scale,
                                     subfolder=("map", "weather", "matter", fcv(this_weather, revert=True)))
                self.weather_matter_images[this_weather] = tuple(images.values())
            except FileNotFoundError:
                self.weather_matter_images[this_weather] = ()

        self.weather_effect_images = {}
        for this_weather in weather_list:  # Load weather effect sprite image
            try:
                images = load_images(self.module_dir, screen_scale=self.screen_scale,
                                     subfolder=("map", "weather", "effect", fcv(this_weather, revert=True)))
                self.weather_effect_images[this_weather] = tuple(images.values())
            except FileNotFoundError:
                self.weather_effect_images[this_weather] = ()

        weather_icon_list = load_images(self.module_dir, screen_scale=self.screen_scale,
                                        subfolder=("map", "weather", "icon"))  # Load weather icon
        new_weather_icon = {}
        for weather_icon in weather_list:
            for strength in range(0, 3):
                new_name = weather_icon + "_" + str(strength)
                for item in weather_icon_list:
                    if new_name == fcv(item):
                        new_weather_icon[new_name] = weather_icon_list[item]
                        break

        weather.Weather.weather_icons = new_weather_icon

        read_folder = Path(os.path.join(self.module_dir, "map", "preset"))
        sub1_directories = [x for x in read_folder.iterdir() if x.is_dir()]

        self.preset_map_list = []  # map name list for map selection list
        self.preset_map_folder = []  # folder for reading later
        self.battle_campaign = {}
        self.preset_map_data = {}

        for file_campaign in sub1_directories:
            read_folder = Path(os.path.join(self.module_dir, "map", "preset", file_campaign))
            campaign_file_name = os.sep.join(os.path.normpath(file_campaign).split(os.sep)[-1:])
            sub2_directories = [x for x in read_folder.iterdir() if x.is_dir()]
            for file_map in sub2_directories:
                map_file_name = os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:])
                self.preset_map_folder.append(map_file_name)
                map_name = self.localisation.grab_text(key=("preset_map", campaign_file_name,
                                                            "info", map_file_name, "Name"))
                self.preset_map_list.append(map_name)
                self.battle_campaign[map_file_name] = campaign_file_name
                self.preset_map_data[map_file_name] = {"source": csv_read(file_map, "source.csv", header_key=True)}

                read_folder = Path(os.path.join(self.module_dir, "map", "preset", file_campaign, file_map))
                sub3_directories = [x for x in read_folder.iterdir() if x.is_dir()]
                for file_source in sub3_directories:
                    source_file_name = os.sep.join(os.path.normpath(file_source).split(os.sep)[-1:])
                    weather_data = csv_read(file_source, "weather.csv", output_type="list")[1:]
                    if not weather:  # no weather data, make random
                        weather_data = [[1, "09:00:00", 0, 0], ]
                    self.preset_map_data[map_file_name][int(source_file_name)] = \
                        {"unit": self.load_map_unit_data(campaign_file_name, map_file_name, source_file_name),
                         "map_event": csv_read(file_source, "map_event.csv", header_key=True),
                         "weather": weather_data,  # weather in list
                         "eventlog": csv_read(file_source, "eventlog.csv", header_key=True)}

        # Load custom map list
        read_folder = Path(os.path.join(self.module_dir, "map", "custom"))
        sub1_directories = [x for x in read_folder.iterdir() if x.is_dir()]

        self.battle_map_list = self.preset_map_list.copy() + ["Random"]
        self.battle_map_folder = self.preset_map_folder.copy() + ["Random"]

        for file_map in sub1_directories:
            self.battle_map_folder.append(os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:]))

            map_name = self.localisation.grab_text(key=("custom_map",
                                                        os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:]),
                                                        "Name"))
            self.battle_map_list.append(map_name)

    def load_map_unit_data(self, campaign_id, map_id, map_source):
        try:
            with open(os.path.join(self.module_dir, "map", "preset", campaign_id, map_id, map_source,
                                   "unit_pos.csv"), encoding="utf-8", mode="r") as unit_file:
                rd = list(csv.reader(unit_file, quoting=csv.QUOTE_ALL))
                header = rd[0]
                int_column = ("ID", "Faction", "Team", "Leader")  # value int only
                list_column = ("POS",)  # value in list only
                float_column = ("Angle", "Start Health", "Start Stamina")  # value in float
                dict_column = ("Troop",)
                int_column = [index for index, item in enumerate(header) if item in int_column]
                list_column = [index for index, item in enumerate(header) if item in list_column]
                float_column = [index for index, item in enumerate(header) if item in float_column]
                dict_column = [index for index, item in enumerate(header) if item in dict_column]

                for data_index, data in enumerate(rd[1:]):  # skip header
                    for n, i in enumerate(data):
                        data = stat_convert(data, n, i, list_column=list_column, int_column=int_column,
                                            float_column=float_column, dict_column=dict_column)
                    rd[data_index + 1] = {header[index]: stuff for index, stuff in enumerate(data)}
                troop_data = rd[1:]
            unit_file.close()
            return troop_data
        except FileNotFoundError as b:
            print(b)
            return {}
