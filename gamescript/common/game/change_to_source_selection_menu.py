from gamescript import menu
from gamescript.common import utility

setup_list = utility.setup_list
load_image = utility.load_image


def change_to_source_selection_menu(self):
    for team in self.team_coa:
        if self.team_selected == team.team:
            team.change_select(True)

    openfolder = self.preset_map_folder
    if self.last_select == "custom":
        openfolder = self.custom_map_folder
    try:
        self.source_list = self.read_selected_map_data(openfolder, "source_" + self.language + ".csv")
        self.source_name_list = [value["Source"] for value in list(self.source_list.values())]
        self.source_scale_text = [value["Number Text"] for value in list(self.source_list.values())]
        self.source_scale = [{0: float(value["Team 0 Scale"]), 1: float(value["Team 1 Scale"]),
                              2: float(value["Team 2 Scale"]), 3: float(value["Team 3 Scale"])}
                             for value in list(self.source_list.values())]
        self.source_text = [value["Description"] for value in list(self.source_list.values())]
    except FileNotFoundError:  # no source file, crash game
        self.error_log.write("\n No source for map: " + str(self.map_title.name))
        no_source

    setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.source_name_list,
               self.source_namegroup, self.source_list_box, self.main_ui_updater)

    for index, team in enumerate(self.team_coa):
        if index == 0:
            self.army_stat.add(
                menu.ArmyStat(self.screen_scale,
                              (team.rect.bottomleft[0], self.screen_rect.height / 1.5),
                              load_image(self.main_dir, self.screen_scale, "stat.png",
                                         ("ui", "mapselect_ui"))))  # left army stat
        else:
            self.army_stat.add(
                menu.ArmyStat(self.screen_scale,
                              (team.rect.bottomright[0], self.screen_rect.height / 1.5),
                              load_image(self.main_dir, self.screen_scale, "stat.png",
                                         ("ui", "mapselect_ui"))))  # right army stat

    team_army, team_leader = self.read_battle_source(
        [self.source_scale_text[self.map_source], self.source_text[self.map_source]])
    self.change_battle_source(self.source_scale[self.map_source], team_army, team_leader)

    self.menu_button.add(*self.team_select_button)
    self.main_ui_updater.add(*self.team_select_button, self.map_option_box, self.enactment_tick_box,
                             self.source_list_box, self.source_list_box.scroll, self.army_stat)
