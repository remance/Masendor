def change_battle_state(self):
    self.previous_game_state = self.game_state
    if self.game_state == "battle":  # change to battle state
        self.camera_mode = self.start_zoom_mode
        self.mini_map.draw_image(self.show_map.true_image, self.camera)

        if self.current_selected is not None:  # any unit is selected
            self.current_selected = None  # reset last_selected
            self.before_selected = None  # reset before selected unit after remove last selected

        # self.command_ui.rect = self.command_ui.image.get_rect(
        #     center=(self.command_ui.image.get_width() / 2, self.command_ui.image.get_height() / 2))  # change leader ui position back
        self.troop_card_ui.rect = self.troop_card_ui.image.get_rect(
            center=self.troop_card_ui.pos)  # change subunit card position back

        self.troop_card_button[0].rect = self.troop_card_button[0].image.get_rect(
            center=(self.troop_card_ui.rect.topleft[0] + (self.troop_card_button[0].image.get_width() / 2),
                    self.troop_card_ui.rect.topleft[1] + (self.troop_card_button[2].image.get_width() * 3)))  # description button
        self.troop_card_button[1].rect = self.troop_card_button[1].image.get_rect(
            center=(self.troop_card_ui.rect.topleft[0] + (self.troop_card_button[1].image.get_width() / 2),
                    self.troop_card_ui.rect.topleft[1] + (self.troop_card_button[2].image.get_width())))  # stat button
        self.troop_card_button[2].rect = self.troop_card_button[2].image.get_rect(
            center=(self.troop_card_ui.rect.topleft[0] + (self.troop_card_button[2].image.get_width() / 2),
                    self.troop_card_ui.rect.topleft[1] + (self.troop_card_button[2].image.get_width()) * 2))  # skill button
        self.troop_card_button[3].rect = self.troop_card_button[3].image.get_rect(
            center=(self.troop_card_ui.rect.topleft[0] + (self.troop_card_button[3].image.get_width() / 2),
                    self.troop_card_ui.rect.topleft[1] + (self.troop_card_button[2].image.get_width() * 4)))  # equipment button

        self.battle_ui_updater.remove(self.filter_stuff, self.unit_setup_stuff, self.leader_now, self.button_ui, self.warning_msg)
        self.battle_ui_updater.add(self.event_log, self.event_log.scroll)

        self.game_speed = 1

        # Run starting method
        for this_unit in self.unit_updater:
            this_unit.start_set()
        for this_subunit in self.subunit_updater:
            this_subunit.start_set(self.camera_zoom, self.subunit_animation_pool)
        for this_leader in self.leader_updater:
            this_leader.start_set()

    elif self.game_state == "editor":  # change to editor state
        self.camera_mode = "Free"
        self.inspect = False  # reset inspect ui
        self.mini_map.draw_image(self.show_map.true_image, self.camera)  # reset mini_map
        for arrow in self.range_attacks:  # remove all range melee_attack
            arrow.kill()
            del arrow

        for this_unit in self.battle.all_team_unit["alive"]:  # reset all unit state
            this_unit.player_input(self.battle_mouse_pos, False, False, False, self.last_mouseover, None, other_command=2)

        self.troop_card_ui.rect = self.troop_card_ui.image.get_rect(bottomright=(self.screen_rect.width,
                                                                                 self.screen_rect.height))  # troop info card ui
        self.troop_card_button[0].rect = self.troop_card_button[0].image.get_rect(
            center=(self.troop_card_ui.rect.topleft[0] + (self.troop_card_button[0].image.get_width() / 2),
                    self.troop_card_ui.rect.topleft[1] + (self.troop_card_button[2].image.get_width() * 3)))  # description button
        self.troop_card_button[1].rect = self.troop_card_button[1].image.get_rect(
            center=(self.troop_card_ui.rect.topleft[0] + (self.troop_card_button[1].image.get_width() / 2),
                    self.troop_card_ui.rect.topleft[1] + (self.troop_card_button[2].image.get_width())))  # stat button
        self.troop_card_button[2].rect = self.troop_card_button[2].image.get_rect(
            center=(self.troop_card_ui.rect.topleft[0] + (self.troop_card_button[2].image.get_width() / 2),
                    self.troop_card_ui.rect.topleft[1] + (self.troop_card_button[2].image.get_width()) * 2))  # skill button
        self.troop_card_button[3].rect = self.troop_card_button[3].image.get_rect(
            center=(self.troop_card_ui.rect.topleft[0] + (self.troop_card_button[3].image.get_width() / 2),
                    self.troop_card_ui.rect.topleft[1] + (self.troop_card_button[2].image.get_width() * 4)))  # equipment button

        self.battle_ui_updater.remove(self.event_log, self.event_log.scroll, self.troop_card_button, self.col_split_button, self.row_split_button,
                                      self.event_log_button, self.time_button, self.unitstat_ui, self.inspect_ui, self.leader_now, self.inspect_subunit,
                                      self.inspect_selected_border, self.inspect_button, self.behaviour_switch_button)

        self.leader_now = [this_leader for this_leader in self.preview_leader]  # reset leader in command ui
        self.battle_ui_updater.add(self.filter_stuff, self.unit_setup_stuff, self.test_button, self.command_ui, self.troop_card_ui, self.leader_now,
                                   self.time_button)
        self.slot_display_button.event = 0  # reset display editor ui button to show
        self.game_speed = 0  # pause battle

        # for slot in self.subunit_build:
        #     if slot.troop_id != 0:
        #         self.command_ui.value_input(who=slot)
        #         break

        self.unit_selector.setup_unit_icon(self.unit_icon, self.all_team_unit[self.team_selected])
        self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row)

    self.speed_number.speed_update(self.game_speed)
