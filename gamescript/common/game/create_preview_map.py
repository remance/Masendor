import random

from gamescript import battlemap
from gamescript.common import utility

load_images = utility.load_images


def create_preview_map(self, map_folder_list, map_list, custom_map=False):
    # Create map preview image
    if self.menu_state == "preset_map":
        map_images = load_images(self.main_dir, subfolder=("module", self.module_folder, "map", "preset",
                                                           map_folder_list[self.current_map_select]))
    else:
        if map_folder_list[self.current_map_select] != "Random":
            map_images = load_images(self.main_dir, subfolder=("module", self.module_folder, "map", "custom",
                                                               map_folder_list[self.current_map_select]))
            if not map_images:  # try loading from preset map list
                map_images = load_images(self.main_dir, subfolder=("module", self.module_folder, "map", "preset",
                                                                   map_folder_list[self.current_map_select]))
        else:  # random map
            terrain, feature, height = battlemap.create_random_map(self.battle_map_data.terrain_colour,
                                                                   self.battle_map_data.feature_colour,
                                                                   random.randint(1, 3), random.randint(4, 9),
                                                                   random.randint(1, 4))
            map_images = {"base": terrain, "feature": feature, "height": height}
    self.map_preview.change_map(map_images["base"], map_images["feature"], map_images["height"])
    self.main_ui_updater.add(self.map_preview)

    # Create map title at the top
    self.map_title.change_name(map_list[self.current_map_select])
    self.main_ui_updater.add(self.map_title)

    # Create map description
    self.map_data = self.read_selected_map_data(map_folder_list, "info_" + self.language + ".csv")

    for key in self.map_data:
        for key2 in self.map_data[key]:
            if "Team " in key2:
                if type(self.map_data[key][key2]) == int:
                    self.map_data[key][key2] = [self.map_data[key][key2]]
                elif type(self.map_data[key][key2]) == str:
                    self.map_data[key][key2] = [int(item) for item in self.map_data[key][key2].split(",")]
    description = [self.map_data[map_list[self.current_map_select]]["Description 1"],
                   self.map_data[map_list[self.current_map_select]]["Description 2"]]
    self.map_description.change_text(description)
    self.main_ui_updater.add(self.map_description)

    if custom_map is False:
        self.create_team_coa([self.map_data[self.map_title.name][data] for data in self.map_data[self.map_title.name] if
                              "Team " in data], self.main_ui_updater)
