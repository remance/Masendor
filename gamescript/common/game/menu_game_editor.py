def menu_game_editor(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.editor_back_button.event or esc_press:
        self.editor_back_button.event = False
        self.back_mainmenu()

    elif self.unit_edit_button.event:
        self.unit_edit_button.event = False

        self.filter_troop_list()

        setup_list(self.screen_scale, menu.NameList, self.current_unit_row,
                   tuple(self.custom_unit_preset_list.keys()),
                   self.unitpreset_namegroup, self.unit_preset_list_box,
                   self.battle_ui_updater)  # setup preset army list
        setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                   self.troop_namegroup, self.editor_troop_list_box,
                   self.battle_ui_updater)  # setup troop name list

        self.current_list_show = "troop"
        self.unit_preset_name = ""

        self.subunit_in_card = None  # current sub-subunit showing in subunit card

        self.main.create_team_coa([0], ui_class=self.battle_ui_updater, one_team=True,
                                  team1_set_pos=(self.editor_troop_list_box.rect.midleft[0] - int(
                                      (300 * self.screen_scale[0]) / 2),
                                                 self.editor_troop_list_box.rect.midleft[
                                                     1]))  # default faction select as all faction

        self.editor_troop_list_box.scroll.change_image(new_row=self.current_troop_row,
                                                       row_size=len(self.troop_list))  # change troop scroll image
