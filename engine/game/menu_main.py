def menu_main(self, esc_press):
    if self.preset_map_button.event:  # preset map list menu
        self.menu_state = "preset_map"
        self.play_map_type = "preset"
        self.last_select = self.menu_state

        self.unit_selected = None  # reset unit selected
        self.unit_model_room.add_preview_model()  # reset model room
        self.current_map_select = 0
        self.map_selected = self.preset_map_folder[self.current_map_select]

        self.remove_ui_updater(*self.start_menu_ui_only)

        self.change_battle_source()

        # reset preview mini map
        self.map_preview.change_mode(1, team_pos_list=self.team_pos, camp_pos_list=self.camp_pos)

        self.add_ui_updater(*self.unit_select_button, self.preset_map_list_box,
                            self.unit_selector, self.unit_selector.scroll, self.unit_model_room)

    elif self.custom_map_button.event:  # custom map list menu
        self.menu_state = "custom_map"
        self.play_map_type = "custom"
        self.last_select = self.menu_state
        self.camp_pos = {}
        self.play_map_data = {"info": {"weather": [[0, "09:00:00", 0, 0]]}, "unit": {"pos": {}}}
        self.unit_selected = None  # reset unit selected
        self.unit_model_room.add_preview_model()  # reset model room
        self.current_map_select = 0
        self.map_selected = self.battle_map_folder[self.current_map_select]
        self.custom_battle_map_list_box.items.on_select(self.current_map_select, self.map_selected)  # reset list

        self.remove_ui_updater(*self.start_menu_ui_only)

        self.create_preview_map()

        self.create_team_coa([None for _ in range(12)])

        for team in self.team_coa:
            if self.team_selected == team.team:
                team.change_select(True)

        self.add_ui_updater(*self.map_select_button, self.custom_battle_map_list_box,
                            self.custom_battle_faction_list_box,
                            self.custom_map_option_box, self.unit_selector,
                            self.unit_selector.scroll, self.weather_custom_select, self.wind_custom_select,
                            self.night_battle_tick_box, self.unit_model_room)

    elif self.game_edit_button.event:  # custom unit/sub-unit editor menu
        self.menu_state = "game_creator"
        self.remove_ui_updater(*self.start_menu_ui_only)

        self.add_ui_updater(*self.editor_button)

    elif self.lore_button.event:  # open encyclopedia
        self.before_lore_state = self.menu_state
        self.menu_state = "encyclopedia"
        self.add_ui_updater(self.encyclopedia_stuff)  # add sprite related to encyclopedia
        self.encyclopedia.change_section(0, self.lore_name_list, self.subsection_name, self.tag_filter_name,
                                         self.lore_name_list.scroll, self.filter_tag_list, self.filter_tag_list.scroll,
                                         self.page_button, self.main_ui_updater)

    elif self.option_button.event:  # change main menu to option menu
        self.menu_state = "option"
        self.remove_ui_updater(*self.start_menu_ui_only)

        self.add_ui_updater(self.option_menu_button, self.option_menu_sliders.values(), self.value_boxes.values(),
                            self.option_text_list, self.profile_box)
        # self.background = self.background_image["option"]

    elif self.quit_button.event or esc_press:  # open quit game confirmation input
        self.input_popup = ("confirm_input", "quit")
        self.confirm_ui.change_instruction("Quit Game?")
        self.add_ui_updater(self.confirm_ui_popup)
