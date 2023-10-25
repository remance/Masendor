import pygame
import os
import unittest

from test import Test
from engine.utils.utility import load_images


def compare_surfaces(surface_a, surface_b, error_margin = 0):
    if surface_a.get_size() != surface_b.get_size():
        return False
    for x in range(surface_a.get_size()[0]):
        for y in range(surface_a.get_size()[1]):
            if sum((abs(surface_a.get_at((x,y))[i]-surface_b.get_at((x,y))[i]) for i in range(3))) > error_margin: 
                return False
    return True

#
# def test_recolour_man_and_build_move_and_def_arrays():
#     from engine.battlemap.battlemap import FinalMap
#     from engine.battlemap.battlemap import BaseMap
#     from engine.battlemap.battlemap import FeatureMap
#     from engine.battlemap.battlemap import HeightMap
#     from engine.data import datamap
#
#     class MinifiedBattle:
#
#         def __init__(self):
#             self.map_move_array = []  # array for pathfinding
#             self.map_def_array = []  # array for defence calculation
#
#     main_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')
#     screen_scale = (1.0, 1.0)
#     language = "en"
#
#     pygame.display.set_mode((0, 0), pygame.HIDDEN)
#     battle_map_data = datamap.BattleMapData()
#
#     height_map = HeightMap()
#     height_map.draw_image(pygame.image.load(os.path.join(main_dir, "tests/height_map.png")))
#
#     battle_map = FinalMap(
#         main_dir=main_dir,
#         screen_scale=None,
#         height_map=height_map,
#     )
#     battle_map.battle_map_colour = battle_map_data.battle_map_colour
#
#     base_map = BaseMap(main_dir=main_dir)
#     base_map.terrain_colour = battle_map_data.terrain_colour
#     base_map.draw_image(pygame.image.load(os.path.join(main_dir, "tests/base_map.png")))
#
#     feature_map = FeatureMap(main_dir=main_dir)
#     feature_map.feature_colour = battle_map_data.feature_colour
#     feature_map.draw_image(pygame.image.load(os.path.join(main_dir, "tests/feature_map.png")))
#     feature_map.feature_mod = battle_map_data.feature_mod
#
#     battle_map.image = pygame.Surface((len(base_map.map_array[0]), len(base_map.map_array)))
#
#     mb = MinifiedBattle()
#     battle_map.recolour_map_and_build_move_and_def_arrays(
#         feature_map=feature_map,
#         base_map=base_map,
#         battle=mb,
#     )


class TestBattleMap(unittest.TestCase, Test):
    def test(self):
        from engine.battlemap.battlemap import FinalMap
        from engine.battlemap.battlemap import BaseMap
        from engine.battlemap.battlemap import FeatureMap
        from engine.battlemap.battlemap import HeightMap
        from engine.data import datamap
        from engine.game.game import Game

        Test.__init__(self, "en", "historical")

        map_selected = "kadesh"

        pygame.display.set_mode((0, 0), pygame.HIDDEN)
        battle_map_data = datamap.BattleMapData()

        height_map = HeightMap()
        height_map.draw_image(pygame.image.load(os.path.join(Game.main_dir, "tests/height_map.png")))

        battle_map = FinalMap(
            height_map=height_map,
        )
        battle_map.battle_map_colour = battle_map_data.battle_map_colour

        base_map = BaseMap()
        base_map.terrain_colour = battle_map_data.terrain_colour

        feature_map = FeatureMap()
        feature_map.feature_colour = battle_map_data.feature_colour
        feature_map.feature_mod = battle_map_data.feature_mod

        images = load_images(Game.module_dir,
                             subfolder=("map", "preset", battle_map_data.battle_campaign[map_selected],
                                        map_selected))
        if not images:  # check custom map
            images = load_images(Game.module_dir,
                                 subfolder=("map", "custom", map_selected))
        base_map.draw_image(images["base"])
        feature_map.draw_image(images["feature"])
        height_map.draw_image(images["height"])

        if "place_name" in images:  # place_name map layer is optional, if not existed in folder then assign None
            place_name_map = images["place_name"]
        else:
            place_name_map = None

        battle_map.draw_image(base_map, feature_map, place_name_map, {}, debug=True)

        assert battle_map
