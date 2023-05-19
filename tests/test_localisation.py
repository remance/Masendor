import pygame
import os
import unittest

from engine.game import game
from engine.data import datalocalisation

language = "en"
game.Game.language = language  # change language here

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1]

game.Game.main_dir = main_dir
game.Game.data_dir = os.path.join(game.Game.main_dir, "data")
game.Game.font_dir = os.path.join(game.Game.data_dir, "font")


class MyTestCase(unittest.TestCase):
    def test(self):
        localisation = datalocalisation.Localisation(debug=True)
        for key in localisation["en"]:
            localisation[language]
unittest.main()