from engine.uimenu import uimenu
from engine import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll


def menu_custom_map_select(self, esc_press):
    if self.map_back_button.event or esc_press:

        self.remove_ui_updater(*self.map_select_button, self.custom_map_list_box, self.faction_list_box,
                               self.custom_map_option_box, self.unit_selector,
                               self.unit_selector.scroll, self.weather_custom_select, self.wind_custom_select,
                               self.map_option_box, self.night_battle_tick_box, self.map_preview)

        for group in (self.map_namegroup, self.team_coa):
            for stuff in group:
                stuff.kill()
                del stuff

        self.back_mainmenu()

    elif self.select_button.event:  # select this map and team, go to unit setup screen
        self.current_source_row = 0

        self.remove_ui_updater(*self.map_select_button)

        for stuff in self.map_namegroup:  # remove map name item
            stuff.kill()
            del stuff

        self.camp_pos = {}
        self.camp_icon = []

        self.play_map_data["unit"] = {"pos": {}}

        self.add_ui_updater(*self.team_select_button, self.custom_map_option_box, self.observe_mode_tick_box,
                            self.night_battle_tick_box, self.map_back_button, self.map_select_button,
                            self.source_list_box, self.source_list_box.scroll, self.unit_selector,
                            self.unit_selector.scroll, self.weather_custom_select, self.wind_custom_select)
        self.menu_state = "custom_team_select"
