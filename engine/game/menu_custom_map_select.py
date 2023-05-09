from engine.uimenu import uimenu
from engine import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll


def menu_custom_map_select(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if mouse_left_up or mouse_left_down:
        if mouse_left_up:
            for index, name in enumerate(self.map_namegroup):  # user click on map name, change map
                if name.rect.collidepoint(self.mouse_pos):
                    self.current_map_select = index
                    self.map_selected = self.battle_map_folder[self.current_map_select]
                    self.create_preview_map()
                    break

        if self.map_list_box.scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
            self.current_map_row = self.map_list_box.scroll.player_input(
                self.mouse_pos)  # update the scroll and get new current subsection
            setup_list(self.screen_scale, uimenu.NameList, self.current_map_row, self.preset_map_list,
                       self.map_namegroup, self.map_list_box,
                       self.main_ui_updater)

    if self.map_list_box.rect.collidepoint(self.mouse_pos):
        self.current_map_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                           self.map_list_box.scroll, self.map_list_box, self.current_map_row,
                                           self.preset_map_list, self.map_namegroup, self.main_ui_updater)

    if self.map_back_button.event or esc_press:
        self.map_back_button.event = False
        self.current_map_row = 0

        self.main_ui_updater.remove(self.map_list_box, self.map_preview, self.map_list_box.scroll, self.team_coa, self.map_title)

        for group in (self.map_namegroup, self.team_coa):
            for stuff in group:
                stuff.kill()
                del stuff

        self.back_mainmenu()

    elif self.select_button.event:  # select this map, go to team/source selection screen
        self.current_source_row = 0
        self.select_button.event = False

        self.main_ui_updater.remove(*self.map_select_button, self.map_list_box, self.map_list_box.scroll,
                                    self.map_description)
        self.menu_button.remove(*self.map_select_button)

        for stuff in self.map_namegroup:  # remove map name item
            stuff.kill()
            del stuff

        self.camp_pos = {}
        self.camp_icon = []

        setup_list(self.screen_scale, uimenu.NameList, self.current_source_row, ["None"] +
                   self.faction_data.faction_name_list, self.source_namegroup, self.source_list_box,
                   self.main_ui_updater)

        self.menu_button.add(*self.team_select_button)

        self.create_team_coa([None for _ in range(10)], self.main_ui_updater)

        self.map_data["unit"] = {"pos": {}}

        self.main_ui_updater.add(*self.team_select_button, self.custom_map_option_box, self.observe_mode_tick_box,
                                 self.night_battle_tick_box, self.map_back_button, self.map_select_button,
                                 self.source_list_box, self.source_list_box.scroll, self.unit_selector,
                                 self.unit_selector.scroll, self.weather_custom_select, self.wind_custom_select,
                                 self.map_option_box)
        self.menu_state = "custom_team_select"
