import pygame


def battle_keyboard_process(self, key_press):
    if key_press == pygame.K_TAB:
        self.map_mode += 1  # change height map mode
        if self.map_mode > 2:
            self.map_mode = 0
        self.show_map.change_mode(self.map_mode)
        self.show_map.change_scale(self.camera_zoom)

    elif key_press == pygame.K_o:  # Toggle unit number
        if self.show_troop_number:
            self.show_troop_number = False
            self.effect_updater.remove(*self.troop_number_sprite)
            self.battle_camera.remove(*self.troop_number_sprite)
        else:
            self.show_troop_number = True
            self.effect_updater.add(*self.troop_number_sprite)
            self.battle_camera.add(*self.troop_number_sprite)

    elif key_press == pygame.K_p:  # Speed Pause/unpause Button
        if self.game_speed >= 0.5:  #
            self.game_speed = 0  # pause self speed
        else:  # speed currently pause
            self.game_speed = 1  # unpause self and set to speed 1
        self.speed_number.speed_update(self.game_speed)

    elif key_press == pygame.K_KP_MINUS:  # reduce self speed
        new_index = self.game_speed_list.index(self.game_speed) - 1
        if new_index >= 0:  # cannot reduce self speed than what is available
            self.game_speed = self.game_speed_list[new_index]
        self.speed_number.speed_update(self.game_speed)

    elif key_press == pygame.K_KP_PLUS:  # increase self speed
        new_index = self.game_speed_list.index(self.game_speed) + 1
        if new_index < len(self.game_speed_list):  # cannot increase self speed than what is available
            self.game_speed = self.game_speed_list[new_index]
        self.speed_number.speed_update(self.game_speed)

    elif key_press == pygame.K_PAGEUP:  # Go to top of event log
        self.event_log.current_start_row = 0
        self.event_log.recreate_image()
        self.event_log.scroll.change_image(new_row=self.event_log.current_start_row)

    elif key_press == pygame.K_PAGEDOWN:  # Go to bottom of event log
        if self.event_log.len_check > self.event_log.max_row_show:
            self.event_log.current_start_row = self.event_log.len_check - self.event_log.max_row_show
            self.event_log.recreate_image()
            self.event_log.scroll.change_image(new_row=self.event_log.current_start_row)

    elif key_press == pygame.K_SPACE and self.current_selected is not None:
        self.current_selected.player_input(self.command_mouse_pos, other_command="Stop")

    # vv FOR DEVELOPMENT DELETE LATER
    elif key_press == pygame.K_F1:
        self.drama_text.queue.append("Hello and Welcome to update video")
    elif key_press == pygame.K_F2:
        self.drama_text.queue.append("Showcase: Unit movement comparison between Arcade and Tactical mode")
    elif key_press == pygame.K_F3:
        self.drama_text.queue.append("Tactical Mode use similar system like RTS games to move unit")
    # elif key_press == pygame.K_F4:
    #     self.drama_text.queue.append("Where the hell is blue team, can only see red")
    # elif key_press == pygame.K_F5:
    #     self.drama_text.queue.append("After")
    # elif key_press == pygame.K_F6:
    #     self.drama_text.queue.append("Now much more clear")
    # elif key_press == pygame.K_n and self.last_selected is not None:
    #     if self.last_selected.team == 1:
    #         self.last_selected.switchfaction(self.team1_unit, self.team2_unit, self.team1_pos_list, self.enactment)
    #     else:
    #         self.last_selected.switchfaction(self.team2_unit, self.team1_unit, self.team2_pos_list, self.enactment)
    # elif key_press == pygame.K_l and self.last_selected is not None:
    #     for subunit in self.last_selected.subunit_sprite:
    #         subunit.base_morale = 0
    # elif key_press == pygame.K_k and self.last_selected is not None:
    #     # for index, subunit in enumerate(self.last_selected.subunit_sprite):
    #     #     subunit.unit_health -= subunit.unit_health
    #     self.subunit_selected.self.unit_health -= self.subunit_selected.self.unit_health
    # elif key_press == pygame.K_m and self.last_selected is not None:
    #     # self.last_selected.leader[0].health -= 1000
    #     self.subunit_selected.self.leader.health -= 1000
    #     # self.subunit_selected.self.base_morale -= 1000
    #     # self.subunit_selected.self.broken_limit = 80
    #     # self.subunit_selected.self.state = 99
    # elif key_press == pygame.K_COMMA and self.last_selected is not None:
    #     for index, subunit in enumerate(self.last_selected.subunit_sprite):
    #         subunit.stamina -= subunit.stamina
    # ^^ End For development test
    # ^ End register input
