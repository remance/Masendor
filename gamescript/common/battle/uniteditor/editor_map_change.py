import pygame


def editor_map_change(self, base_colour, feature_colour):
    map_images = (
    pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000), pygame.SRCALPHA), None)
    map_images[0].fill(base_colour)  # start with temperate terrain
    map_images[1].fill(feature_colour)  # start with plain feature
    map_images[2].fill((255, 100, 100, 125))  # start with height 100 plain

    self.battle_map_base.draw_image(map_images[0])
    self.battle_map_feature.draw_image(map_images[1])
    self.battle_map_height.draw_image(map_images[2])
    self.battle_map.draw_image(self.battle_map_base, self.battle_map_feature, self.battle_map_height, None, self, True)
    self.mini_map.draw_image(self.battle_map.true_image, self.camera)
    self.battle_map.change_scale(self.camera_zoom)

    for subunit in self.subunit_build:
        subunit.terrain, subunit.feature = subunit.get_feature((500, 500), self.battle_map_base)
        subunit.height = self.battle_map_height.get_height((500, 500))
