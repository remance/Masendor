from engine.uimenu import uimenu
from engine import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll


def menu_main(self, esc_press):
    if self.preset_map_button.event:  # preset map list menu
        self.menu_state = "preset_map"
        self.play_map_type = "preset"
        self.last_select = self.menu_state

        self.current_map_select = 0
        self.map_selected = self.preset_map_folder[self.current_map_select]

        self.main_ui_updater.remove(*self.start_menu_ui_only)
        self.menu_button.remove(*self.menu_button)

        self.change_battle_source()

        for team in self.team_coa:
            if self.team_selected == team.team:
                team.change_select(True)

        # reset preview mini map
        self.map_preview.change_mode(1, team_pos_list=self.team_pos, camp_pos_list=self.camp_pos)

        self.menu_button.add(*self.unit_select_button)
        self.main_ui_updater.add(*self.unit_select_button, self.preset_map_list_box,
                                 self.source_list_box, self.source_list_box.scroll,
                                 self.unit_selector,
                                 self.unit_selector.scroll, self.unit_model_room)

    elif self.custom_map_button.event:  # custom map list menu
        self.menu_state = "custom_map"
        self.play_map_type = "custom"
        self.last_select = self.menu_state
        self.current_map_select = 0
        self.map_selected = self.battle_map_folder[self.current_map_select]
        self.custom_map_list_box.items.on_select(self.current_map_select, self.map_selected)  # reset list

        self.main_ui_updater.remove(*self.start_menu_ui_only)
        self.menu_button.remove(*self.menu_button)

        self.create_preview_map()

        self.menu_button.add(*self.map_select_button)
        self.main_ui_updater.add(*self.map_select_button, self.custom_map_list_box, self.faction_list_box,
                                 self.custom_map_option_box, self.unit_selector,
                                 self.unit_selector.scroll, self.weather_custom_select, self.wind_custom_select,
                                 self.map_option_box, self.night_battle_tick_box)

    elif self.game_edit_button.event:  # custom unit/sub-unit editor menu
        self.menu_state = "game_creator"
        self.main_ui_updater.remove(*self.start_menu_ui_only)
        self.menu_button.remove(*self.menu_button)

        self.menu_button.add(*self.editor_button)
        self.main_ui_updater.add(*self.editor_button)

    elif self.lore_button.event:  # open encyclopedia
        self.before_lore_state = self.menu_state
        self.menu_state = "encyclopedia"
        self.main_ui_updater.add(self.encyclopedia_stuff)  # add sprite related to encyclopedia
        self.encyclopedia.change_section(0, self.lore_name_list, self.subsection_name, self.tag_filter_name,
                                         self.lore_name_list.scroll, self.filter_tag_list, self.filter_tag_list.scroll,
                                         self.page_button, self.main_ui_updater)

    elif self.option_button.event:  # change start_set menu to option menu
        self.menu_state = "option"
        self.main_ui_updater.remove(*self.start_menu_ui_only)
        self.menu_button.remove(*self.menu_button)

        self.menu_button.add(*self.option_menu_button)
        self.main_ui_updater.add(*self.menu_button, *self.option_menu_sliders.values(), *self.value_boxes.values(),
                                 *self.option_text_list)
        # self.background = self.background_image["option"]

    elif self.quit_button.event or esc_press:  # change start_set menu to option menu
        self.input_popup = ("confirm_input", "quit")
        self.confirm_ui.change_instruction("Quit Game?")
        self.main_ui_updater.add(*self.confirm_ui_popup)

    elif self.profile_box.event:
        self.input_popup = ("text_input", "profile_name")
        self.input_box.text_start(self.profile_name)
        self.input_ui.change_instruction("Profile Name:")
        self.main_ui_updater.add(self.input_ui_popup)
