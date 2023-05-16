import os
from pathlib import Path

from engine import utility

csv_read = utility.csv_read
lore_csv_read = utility.lore_csv_read


class Localisation:
    def __init__(self):
        from engine.game.game import Game
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.module_dir = Game.module_dir
        self.language = Game.language

        # start with the creation of common UI localisation
        self.text = {"en": {"ui": csv_read(self.data_dir, "en.csv", ("localisation",), dict_value_return_as_str=True)},
                     self.language: {"ui": csv_read(self.data_dir, "en.csv", ("localisation",), dict_value_return_as_str=True)},}
        self.read_module_lore("concept", "concept")
        self.read_module_lore("history", "history")
        self.read_module_lore("faction", "faction")
        self.read_module_lore("troop", "troop")

        self.read_module_lore(("troop_weapon", "mount_weapon"), "weapon")
        self.read_module_lore("troop_armour", "troop_armour")
        self.read_module_lore("mount", "mount")
        self.read_module_lore("mount_armour", "mount_armour")
        self.read_module_lore("troop_class", "troop_class")
        self.read_module_lore(("troop_skill", "leader_skill", "commander_skill"), "skill")
        self.read_module_lore("troop_trait", "trait")
        self.read_module_lore("troop_status", "status")

        self.read_module_lore(("leader", "common_leader"), "leader")

        self.read_module_lore("terrain_effect", "terrain_effect")
        self.read_module_lore("weather", "weather")

        # Load map description
        self.text["en"]["custom_map"] = {}
        self.text["en"]["preset_map"] = {"info": {}}
        with open(os.path.join(self.module_dir, "localisation", "en",
                               "map", "custom_map.csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.text["en"]["custom_map"])  # load custom map
        edit_file.close()
        if self.language != "en":
            try:
                self.text[self.language]["custom_map"] = {}
                with open(os.path.join(self.module_dir, "localisation", self.language,
                                       "custom_map.csv"), encoding="utf-8", mode="r") as edit_file:
                    lore_csv_read(edit_file, self.text["custom_map"][self.language])
                edit_file.close()
            except FileNotFoundError:
                pass

        self.load_preset_map_lore("en")
        if self.language != "en":
            self.load_preset_map_lore(self.language)

    def load_preset_map_lore(self, language):
        # try:
        with open(os.path.join(self.module_dir, "localisation", self.language, "map", "preset", "info.csv"),
                  encoding="utf-8", mode="r") as edit_file:  # read campaign info file
            lore_csv_read(edit_file, self.text[language]["preset_map"]["info"])
        edit_file.close()

        read_folder = Path(os.path.join(self.module_dir, "localisation", language, "map", "preset"))
        sub1_directories = [x for x in read_folder.iterdir() if x.is_dir()]  # load preset map campaign
        for file_campaign in sub1_directories:
            campaign_id = os.path.split(file_campaign)[-1]
            self.text[language]["preset_map"][campaign_id] = {"info": {}}

            with open(os.path.join(self.module_dir, "localisation", self.language, "map", "preset",
                                   file_campaign, "info.csv"),
                      encoding="utf-8", mode="r") as edit_file:  # read campaign info file
                lore_csv_read(edit_file, self.text[language]["preset_map"][campaign_id]["info"])
            edit_file.close()

            read_folder = Path(os.path.join(self.module_dir, "localisation", language, "map", "preset",
                                            file_campaign))
            sub2_directories = [x for x in read_folder.iterdir() if x.is_dir()]
            for file_map in sub2_directories:
                file_map_name = os.path.split(file_map)[-1]
                self.text[language]["preset_map"][campaign_id][file_map_name] = {"source": {},
                                                                                 "eventlog": {}}
                read_folder = Path(os.path.join(self.module_dir, "localisation", language, "map", "preset",
                                                file_campaign, file_map_name))
                sub2_files = [f for f in os.listdir(read_folder) if f.endswith(".csv")]
                for data_file in sub2_files:  # load event log
                    if "eventlog" in data_file:
                        source_id = int(data_file.split(".csv")[0][-1])
                        self.text[language]["preset_map"][campaign_id][file_map_name][
                            "eventlog"][source_id] = {}
                        with open(os.path.join(self.module_dir, "localisation", self.language, "map", "preset",
                                               file_campaign, file_map_name, data_file),
                                  encoding="utf-8", mode="r") as edit_file:  # read source file
                            lore_csv_read(edit_file,
                                          self.text[language]["preset_map"][campaign_id][file_map_name][
                                              "eventlog"][source_id])
                        edit_file.close()

                    elif "source" in data_file:
                        with open(os.path.join(self.module_dir, "localisation", self.language, "map", "preset",
                                               file_campaign, file_map_name, "source.csv"),
                                  encoding="utf-8", mode="r") as edit_file:  # read source file
                            lore_csv_read(edit_file,
                                          self.text[language]["preset_map"][campaign_id][file_map_name]["source"])
                        edit_file.close()

    def read_module_lore(self, lore_type, lore_key):
        """
        Read module lore data
        :param lore_type: File names to read
        :param lore_key: key name
        :return:
        """
        self.text["en"][lore_key] = {}
        if not isinstance(lore_type, (list, tuple)):
            lore_type = [lore_type]
        for lore in lore_type:
            with open(os.path.join(self.module_dir, "localisation", "en",
                                   lore + ".csv"), encoding="utf-8", mode="r") as edit_file:
                lore_csv_read(edit_file, self.text["en"][lore_key])
            edit_file.close()
            if self.language != "en":
                try:
                    self.text[self.language][lore_key] = {}
                    with open(os.path.join(self.module_dir, "localisation", self.language,
                                           lore + ".csv"), encoding="utf-8", mode="r") as edit_file:
                        lore_csv_read(edit_file, self.text[self.language][lore_key])
                    edit_file.close()
                except FileNotFoundError:
                    pass

    def grab_text(self, key=(), alternative_text_data=None):
        """
        Find localisation of provided object key name,
        Return: Translated text if found in provided language, if not then English text, if not found anywhere then return key
        """
        text_data = self.text
        if alternative_text_data:
            text_data = alternative_text_data

        try:
            if self.language in text_data:
                return self.inner_grab_text(key, self.language, text_data)
            else:
                return self.inner_grab_text(key, "en", text_data)
        except KeyError:  # no translation found
            print(self.language, key, " not found, use input key instead")
            return str(key)

    def create_lore_data(self, key_type):
        lore_data = self.text["en"][key_type]
        if key_type in self.text[self.language]:  # replace english with available localisation of selected language
            for key in self.text[self.language][key_type]:
                lore_data[key] = self.text[self.language][key_type][key]
        return lore_data

    @staticmethod
    def inner_grab_text(key, language, text_data):
        next_level = text_data[language]
        for subkey in key:
            next_level = next_level[subkey]
        return next_level
