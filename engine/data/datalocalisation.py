from engine import utility

csv_read = utility.csv_read


class Localisation:
    def __init__(self):
        from engine.game.game import Game
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.module_dir = Game.module_dir
        self.language = Game.language
        self.text = {"ui": {"en": csv_read(self.data_dir, "en.csv", ("localisation",), dict_value_return_as_str=True)}}
        if self.language != "en":
            self.text["ui"][self.language] = csv_read(self.data_dir, self.language + ".csv", ("localisation",),
                                                      dict_value_return_as_str=True)

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
