from gamescript import battleui


def change_battle_state(self):
    self.previous_game_state = self.game_state
    if self.game_state == "battle":  # change to battle state
        self.camera_mode = self.start_camera_mode
        self.mini_map.draw_image(self.battle_map_base, self.battle_map.mini_map_image, self.camera)

        # self.command_ui.rect = self.command_ui.image.get_rect(
        #     center=(self.command_ui.image.get_width() / 2, self.command_ui.image.get_height() / 2))  # change leader ui position back

        self.battle_ui_updater.add(self.event_log, self.event_log.scroll)

        self.game_speed = 1

        # Run enter_battle method
        for this_subunit in self.subunit_updater:
            this_subunit.enter_battle(self.subunit_animation_pool)
            battleui.SpriteIndicator(this_subunit.hitbox_image, this_subunit, self)

        # Setup formation for leader
        for this_subunit in self.subunit_updater:
            this_subunit.ai_troop()
            if this_subunit.is_leader:
                if this_subunit.alive_troop_follower:
                    this_subunit.change_formation("troop")
                if this_subunit.alive_leader_follower:
                    this_subunit.change_formation("unit")

            if self.char_selected is not None:  # select player char by default if control only one
                if this_subunit.game_id == self.char_selected:  # get player char
                    self.player_char = this_subunit
                    self.player_char.player_manual_control = True
                    self.battle_camera.change_layer(self.player_char, 999999)
                    self.command_ui.add_leader_image(this_subunit.portrait)
                    if self.camera_mode == "Follow":
                        self.true_camera_pos = self.player_char.base_pos
                        self.camera_fix()
