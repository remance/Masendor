from gamescript.common import utility

load_images = utility.load_images


def create_preview_map(self, map_folder_list, map_list):
    # v Create map preview image
    if self.menu_state == "preset_map":
        map_images = load_images(self.main_dir, self.screen_scale, ["ruleset", self.ruleset_folder, "map",
                                                                    map_folder_list[self.current_map_select]],
                                 load_order=False)
    else:
        map_images = load_images(self.main_dir, self.screen_scale, ["ruleset", self.ruleset_folder, "map/custom",
                                                                    map_folder_list[self.current_map_select]],
                                 load_order=False)
    self.map_show.change_map(map_images["base.png"], map_images["feature.png"])
    self.main_ui_updater.add(self.map_show)
    # ^ End map preview

    # v Create map title at the top
    self.map_title.change_name(map_list[self.current_map_select])
    self.main_ui_updater.add(self.map_title)
    # ^ End map title

    # v Create map description
    self.map_data = self.read_selected_map_data(map_folder_list, "info.csv")
    description = [self.map_data[map_list[self.current_map_select]]["Description 1"],
                   self.map_data[map_list[self.current_map_select]]["Description 2"]]
    self.map_description.change_text(description)
    self.main_ui_updater.add(self.map_description)
    # ^ End map description

    self.create_team_coa([self.map_data[self.map_title.name]["Team 1"],
                          self.map_data[self.map_title.name]["Team 2"]], self.main_ui_updater)