import pygame
import os


def compare_surfaces(surface_a, surface_b, error_margin = 0):
    if surface_a.get_size() != surface_b.get_size():
        return False
    for x in range(surface_a.get_size()[0]):
        for y in range(surface_a.get_size()[1]):
            if sum((abs(surface_a.get_at((x,y))[i]-surface_b.get_at((x,y))[i]) for i in range(3))) > error_margin: 
                return False
    return True


def test_recolour_man_and_build_move_and_def_arrays():
    from engine.battlemap import BeautifulMap
    from engine.battlemap import BaseMap
    from engine.battlemap import FeatureMap
    from engine.battlemap import HeightMap
    from engine import datamap

    class MinifiedBattle:

        def __init__(self):
            self.map_move_array = []  # array for pathfinding
            self.map_def_array = []  # array for defence calculation

    main_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')
    screen_scale = (1.0, 1.0)
    ruleset_folder = "historical"
    language = "en"

    pygame.display.set_mode((0, 0), pygame.HIDDEN)
    battle_map_data = datamap.BattleMapData(main_dir, screen_scale, ruleset_folder, language)

    height_map = HeightMap()
    height_map.draw_image(pygame.image.load(os.path.join(main_dir, "tests/height_map.png")))

    battle_map = BeautifulMap(
        main_dir=main_dir,
        screen_scale=None,
        height_map=height_map,
    )
    battle_map.battle_map_colour = battle_map_data.battle_map_colour

    base_map = BaseMap(main_dir=main_dir)
    base_map.terrain_colour = battle_map_data.terrain_colour
    base_map.draw_image(pygame.image.load(os.path.join(main_dir, "tests/base_map.png")))

    feature_map = FeatureMap(main_dir=main_dir)
    feature_map.feature_colour = battle_map_data.feature_colour
    feature_map.draw_image(pygame.image.load(os.path.join(main_dir, "tests/feature_map.png")))
    feature_map.feature_mod = battle_map_data.feature_mod

    battle_map.image = pygame.Surface((len(base_map.map_array[0]), len(base_map.map_array)))

    mb = MinifiedBattle()
    battle_map.recolour_map_and_build_move_and_def_arrays(
        feature_map=feature_map,
        base_map=base_map,
        battle=mb,
    )

    assert compare_surfaces(
        battle_map.image,
        pygame.image.load(os.path.join(main_dir, "tests/map1.png")),
        error_margin=3
    )
