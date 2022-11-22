import pygame


def battle_keyboard_process(self, key_press):
    if key_press == pygame.K_q:  # Open unit command wheel ui
        self.battle_ui_updater.add(self.eight_wheel_ui)
        self.player_input_state = self.eight_wheel_ui
        self.eight_wheel_ui.change_text_icon(self.unit_behaviour_wheel["Main"])

    # elif key_press == pygame.K_p:  # Speed Pause/unpause Button

    # elif key_press == pygame.K_KP_MINUS:  # reduce self speed
    #
    # elif key_press == pygame.K_KP_PLUS:  # increase self speed

    # elif key_press == pygame.K_PAGEUP:  # Go to top of event log
    #     self.event_log.current_start_row = 0
    #     self.event_log.recreate_image()
    #     self.log_scroll.change_image(new_row=self.event_log.current_start_row)
    #
    # elif key_press == pygame.K_PAGEDOWN:  # Go to bottom of event log
    #     if self.event_log.len_check > self.event_log.max_row_show:
    #         self.event_log.current_start_row = self.event_log.len_check - self.event_log.max_row_show
    #         self.event_log.recreate_image()
    #         self.log_scroll.change_image(new_row=self.event_log.current_start_row)

    # elif key_press == pygame.K_SPACE and self.current_selected is not None:
    #     self.current_selected.user_input(self.command_mouse_pos, False, False, False, self.last_mouseover, None, other_command=2)

    # FOR DEVELOPMENT DELETE LATER
    elif key_press == pygame.K_F1:
        self.drama_text.queue.append("Hello and Welcome to update video")
    elif key_press == pygame.K_F2:
        self.drama_text.queue.append("Showcase: Update to arcade mode so far")
    elif key_press == pygame.K_F3:
        self.drama_text.queue.append("Formation system")
    elif key_press == pygame.K_F4:
        self.drama_text.queue.append("Range attack aim control")
    elif key_press == pygame.K_F5:
        self.drama_text.queue.append("Unit line shifting")
    # elif key_press == pygame.K_F6:
    #     self.drama_text.queue.append("Now much more clear")
    # elif key_press == pygame.K_n and self.current_selected is not None:
    #     if self.current_selected.team == 1:
    #         self.current_selected.switchfaction(self.team1_unit, self.team2_unit, self.team1_pos_list, self.enactment)
    #     else:
    #         self.current_selected.switchfaction(self.team2_unit, self.team1_unit, self.team2_pos_list, self.enactment)
    # elif key_press == pygame.K_l and self.current_selected is not None:
    #     for subunit in self.current_selected.subunit_sprite:
    #         subunit.base_morale = 0
    elif key_press == pygame.K_k and self.current_selected is not None:
        # for index, subunit in enumerate(self.current_selected.subunit_sprite):
        #     subunit.unit_health -= subunit.unit_health
        self.current_selected.leader_subunit.subunit_health = 0
    # elif key_press == pygame.K_m and self.current_selected is not None:
    #     # self.current_selected.leader[0].health -= 1000
    #     self.subunit_selected.self.leader.health -= 1000
    #     # self.subunit_selected.self.base_morale -= 1000
    #     # self.subunit_selected.self.broken_limit = 80
    #     # self.subunit_selected.self.state = 99
    # elif key_press == pygame.K_COMMA and self.current_selected is not None:
    #     for index, subunit in enumerate(self.current_selected.subunit_sprite):
    #         subunit.stamina -= subunit.stamina
