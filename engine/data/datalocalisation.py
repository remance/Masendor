import os

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
        self.text = {"ui": {"en": csv_read(self.data_dir, "en.csv", ("localisation",), dict_value_return_as_str=True)}}
        self.module_lore_read("concept", "concept")
        self.module_lore_read("history", "history")
        self.module_lore_read("faction", "faction")
        self.module_lore_read("troop", "troop")

        self.module_lore_read(("troop_weapon", "mount_weapon"), "weapon")
        self.module_lore_read("troop_armour", "troop_armour")
        self.module_lore_read("mount", "mount")
        self.module_lore_read("mount_armour", "mount_armour")
        self.module_lore_read("troop_class", "troop_class")
        self.module_lore_read(("troop_skill", "leader_skill", "commander_skill"), "skill")
        self.module_lore_read("troop_trait", "trait")
        self.module_lore_read("troop_status", "status")

        self.module_lore_read(("leader", "common_leader"), "leader")

        self.module_lore_read("terrain_effect", "terrain_effect")
        self.module_lore_read("weather", "weather")

        self.text["map"] = {}

    def map_lore_read(self):
        pass


    def module_lore_read(self, lore_type, lore_key):
        """
        Read module lore data
        :param lore_type: File names to read
        :param lore_key: key name
        :return:
        """
        self.text[lore_key] = {"en": {}}
        if not isinstance(lore_type, (list, tuple)):
            lore_type = [lore_type]
        for lore in lore_type:
            with open(os.path.join(self.module_dir, "localisation", "en",
                                   lore + ".csv"), encoding="utf-8", mode="r") as edit_file:
                lore_csv_read(edit_file, self.text[lore_key]["en"], output_dict=True)
            edit_file.close()
            if self.language != "en":
                try:
                    self.text[lore_key][self.language] = csv_read(self.data_dir, self.language + ".csv", ("localisation",),
                                                                   dict_value_return_as_str=True)
                    with open(os.path.join(self.module_dir, "localisation", self.language,
                                           lore + ".csv"), encoding="utf-8", mode="r") as edit_file:
                        lore_csv_read(edit_file, self.text[lore_key][self.language], output_dict=True)
                    edit_file.close()
                except FileNotFoundError:
                    pass

    def grab_text(self, key_type, key):
        """
        Find localisation of provided object key name,
        Return: Translated text if found in provided language, if not then English text, if not found anywhere then return key
        """
        if self.language in self.text[key_type]:
            if key in self.text[key_type][self.language]:
                return self.text[key_type][self.language][key]
            else:  # translation not found
                if key in self.text[key_type]["en"]:
                    return self.text[key_type]["en"][key]
                else:
                    print(key_type, key, self.language, " not found, use input key instead")
                    return key
        else:  # no translation found
            if key in self.text[key_type]["en"]:
                return self.text[key_type]["en"][key]
            else:
                print(key_type, key, self.language, " not found, use input key instead")
                return key
