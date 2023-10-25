import os

from engine.game.game import Game
from engine.data import datalocalisation
from engine.utils.utility import csv_read


class Test:
    def __init__(self, language, module):
        Game.language = language

        current_dir = os.path.split(os.path.abspath(__file__))[0]
        main_dir = current_dir[:current_dir.rfind("\\") + 1]

        Game.main_dir = main_dir
        Game.data_dir = os.path.join(Game.main_dir, "data")
        Game.font_dir = os.path.join(Game.data_dir, "font")
        Game.module_dir = os.path.join(Game.data_dir, "module", module)
        Game.ui_font = csv_read(Game.module_dir, "ui_font.csv", ("ui",), header_key=True)
        localisation = datalocalisation.Localisation()
        Game.localisation = localisation
        for item in Game.ui_font:  # add ttf file extension for font data reading.
            Game.ui_font[item] = os.path.join(Game.font_dir, Game.ui_font[item]["Font"] + ".ttf")