import random

from engine.battlemap import battlemap
from engine import utility

load_images = utility.load_images


def create_preview_map(self, map_folder_list, map_list, custom_map=False):
    # Create map preview image
    if self.menu_state == "preset_map":
        map_images = load_images(self.module_dir, subfolder=("map", "preset", map_folder_list[self.current_map_select]))
    else:
        if map_folder_list[self.current_map_select] != "Random":
            map_images = load_images(self.module_dir,
                                     subfolder=("map", "custom", map_folder_list[self.current_map_select]))
            if not map_images:  # try loading from preset map list
                map_images = load_images(self.module_dir,
                                         subfolder=("map", "preset", map_folder_list[self.current_map_select]))
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
    self.map_info = self.read_selected_map_data(map_folder_list, "info_" + self.language + ".csv")

    description = [self.map_info[map_list[self.current_map_select]]["Description 1"],
                   self.map_info[map_list[self.current_map_select]]["Description 2"]]
    self.map_description.change_text(description)

    if custom_map is False:
        self.map_data = self.read_selected_map_data(map_folder_list, "source" + ".csv")
        team_coa = []
        key = 0
        for key2 in self.map_data[key]:
            if "Team " in key2 and "Camp " not in key2:
                if type(self.map_data[key][key2]) == int:
                    self.map_data[key][key2] = [self.map_data[key][key2]]
                elif type(self.map_data[key][key2]) == str:
                    self.map_data[key][key2] = [int(item) for item in self.map_data[key][key2].split(",")]
                team_coa.append(self.map_data[key][key2])
        self.create_team_coa(team_coa, self.main_ui_updater)
