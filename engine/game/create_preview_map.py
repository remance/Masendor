import random

from engine.battlemap.battlemap import create_random_map
from engine.utility import load_images


def create_preview_map(self):
    # Create map preview image
    map_name = self.battle_map_folder[self.current_map_select]

    if self.menu_state == "preset_map":
        self.map_title.change_name(self.localisation.grab_text(key=("preset_map", "info", self.campaign_selected, "Name")) +
                                   " / " + self.localisation.grab_text(key=("preset_map", self.campaign_selected, "info", self.map_selected, "Name")) + " / " +
                                   self.localisation.grab_text(key=("preset_map", self.campaign_selected, self.map_selected, "source", self.map_source_selected, "Source")))

    else:
        self.map_title.change_name(
            self.localisation.grab_text(key=("preset_map", "info", self.campaign_selected, "Name")) +
            " / " + self.localisation.grab_text(
                key=("preset_map", self.campaign_selected, "info", self.map_selected, "Name")))

    if map_name != "Random":
        if map_name in self.battle_campaign:
            map_images = load_images(self.module_dir, subfolder=("map", "preset", self.battle_campaign[map_name],
                                                                 map_name))  # check campaign preset map first
        else:  # custom map
            map_images = load_images(self.module_dir,
                                     subfolder=("map", "custom", self.battle_map_folder[self.current_map_select]))
    else:  # random map
        terrain, feature, height = create_random_map(self.battle_map_data.terrain_colour,
                                                     self.battle_map_data.feature_colour,
                                                     random.randint(1, 3), random.randint(4, 9),
                                                     random.randint(1, 4))
        map_images = {"base": terrain, "feature": feature, "height": height}
    self.map_preview.change_map(map_images["base"], map_images["feature"], map_images["height"])
    self.add_ui_updater(self.map_preview)

    # Create map description
    self.map_info = self.read_selected_map_lore()

    # description = [self.map_info["Description 1"], self.map_info["Description 2"]]
    # self.map_description.change_text(description, self.mouse_pos)
