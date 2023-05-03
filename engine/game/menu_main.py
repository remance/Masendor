from engine.uimenu import uimenu
from engine import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll


def menu_main(self, mouse_left_up):
    if self.preset_map_button.event:  # preset map list menu
        self.menu_state = "preset_map"
        self.map_type = "preset"
        self.last_select = self.menu_state

        self.current_map_select = 0
        self.map_selected = self.preset_map_folder[self.current_map_select]

        self.preset_map_button.event = False
        self.main_ui_updater.remove(*self.start_menu_ui_only)
        self.menu_button.remove(*self.menu_button)

        setup_list(uimenu.NameList, self.current_map_row, self.preset_map_list, self.map_namegroup,
                   self.map_list_box, self.main_ui_updater)
        self.create_preview_map(self.preset_map_folder, self.preset_map_list)

        for team in self.team_coa:
            if self.team_selected == team.team:
                team.change_select(True)

        self.change_battle_source()

        self.menu_button.add(*self.unit_select_button)
        self.main_ui_updater.add(*self.unit_select_button, self.map_list_box, self.map_title, self.map_list_box.scroll,
                                 self.map_option_box,
                                 self.observe_mode_tick_box, self.source_list_box, self.source_list_box.scroll,
                                 self.unit_selector,
                                 self.unit_selector.scroll, self.unit_model_room)

    elif self.custom_map_button.event:  # custom map list menu
        self.menu_state = "custom_map"
        self.map_type = "custom"
        self.last_select = self.menu_state

        self.current_map_select = 0
        self.map_selected = self.custom_map_folder[self.current_map_select]

        self.custom_map_button.event = False
        self.main_ui_updater.remove(*self.start_menu_ui_only, self.popup_list_box, self.popup_list_box.scroll)
        self.menu_button.remove(*self.menu_button)

        setup_list(uimenu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup,
                   self.map_list_box,
                   self.main_ui_updater)
        self.create_preview_map(self.custom_map_folder, self.custom_map_list, custom_map=True)

        self.menu_button.add(*self.map_select_button)
        self.main_ui_updater.add(*self.map_select_button, self.map_list_box, self.map_title, self.map_list_box.scroll)

    elif self.game_edit_button.event:  # custom unit/sub-unit editor menu
        self.menu_state = "game_creator"
        self.game_edit_button.event = False
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
        self.lore_button.event = False

    elif self.option_button.event:  # change start_set menu to option menu
        self.menu_state = "option"
        self.option_button.event = False
        self.main_ui_updater.remove(*self.start_menu_ui_only)
        self.menu_button.remove(*self.menu_button)

        self.menu_button.add(*self.option_menu_button)
        self.main_ui_updater.add(*self.menu_button, *self.option_menu_sliders.values(), *self.value_boxes.values(),
                                 *self.option_text_list)
        self.background = self.background_image["option"]

    elif mouse_left_up and self.profile_box.rect.collidepoint(self.mouse_pos):
        self.input_popup = ("text_input", "profile_name")
        self.input_box.text_start(self.profile_name)
        self.input_ui.change_instruction("Profile Name:")
        self.main_ui_updater.add(self.input_ui_popup)

    elif self.popup_list_box in self.main_ui_updater:
        if self.popup_list_box.rect.collidepoint(self.mouse_pos):
            self.ui_click = True
            for index, name in enumerate(self.popup_namegroup):
                if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # click on name in list
                    self.change_game_genre(index)

                    for this_name in self.popup_namegroup:  # remove troop name list
                        this_name.kill()
                        del this_name

                    self.main_ui_updater.remove(self.popup_list_box, self.popup_list_box.scroll)
                    break

        elif self.popup_list_box.scroll.rect.collidepoint(self.mouse_pos):  # scrolling on list
            self.ui_click = True
            self.current_popup_row = self.popup_list_box.scroll.player_input(
                self.mouse_pos)  # update the scroller and get new current subsection
            setup_list(uimenu.NameList, self.current_popup_row, self.genre_list,
                       self.popup_namegroup, self.popup_list_box, self.main_ui_updater)
