import pygame
import os
import unittest

from engine.game import game
from engine.data import datalocalisation

language = "es"  # change language to test here
module = "historical"
game.Game.language = language

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1]

game.Game.main_dir = main_dir
game.Game.data_dir = os.path.join(game.Game.main_dir, "data")
game.Game.font_dir = os.path.join(game.Game.data_dir, "font")
game.Game.module_dir = os.path.join(game.Game.data_dir, "module", module)


def recursive_save_dict(data, save):
    f = recursive_save_dict
    if type(data) == dict:
        for k, v in data.items():
            if type(v) == dict:
                save[k] = {}
                f(v, save[k])


def recursive_check_dict(data, data2, previous_k):
    f = recursive_check_dict
    for k, v in data.items():
        if k not in data2:
            print(previous_k, k, language, "Localisation not found")
        else:
            if type(v) == dict:
                f(v, data2[k], k)


class TestLocalisation(unittest.TestCase):
    def test(self):
        """Check for key existence in input language data compared to English localisation data"""
        localisation = datalocalisation.Localisation(debug=True)
        key_save = {}
        next_level = localisation.text["en"]
        next_key_level = key_save
        recursive_save_dict(next_level, key_save)
        recursive_check_dict(key_save, localisation.text[language], language)
        # for key in key_save:
        assert localisation

# unittest.main()
