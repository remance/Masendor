import pygame


def battle_keyboard_process(self, key_press):
    if key_press == pygame.K_TAB:  # Open unit command wheel ui
        self.battle_ui_updater.add(self.wheel_ui)
        self.previous_player_input_state = self.player_input_state
        self.player_input_state = self.wheel_ui
        self.wheel_ui.generate(self.unit_behaviour_wheel["Main"])

    elif key_press == pygame.K_F1:
        self.drama_text.queue.append("Hello and welcome to showcase video")
    elif key_press == pygame.K_F2:
        self.drama_text.queue.append("Custom map battle")
    elif key_press == pygame.K_F3:
        self.drama_text.queue.append("See video description for more detail")
    elif key_press == pygame.K_F4:
        self.drama_text.queue.append("He juggled his sword and sing the Song of Roland")
    elif key_press == pygame.K_F5:
        self.drama_text.queue.append("Rushed to the English line, he fought valiantly alone")
    elif key_press == pygame.K_F6:
        self.drama_text.queue.append("The Saxon swarmed him and left him death, that they shall atone")
    elif key_press == pygame.K_F7:
        self.drama_text.queue.append("For his name will be remember in the song singed by people")
    elif key_press == pygame.K_F8:
        self.drama_text.queue.append("And that is the end of this tale, don't expect a sequel")
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

    # FOR DEVELOPMENT DELETE LATER

    # elif key_press == pygame.K_l and self.current_selected is not None:
    #     for subunit in self.current_selected.subunit_sprite:
    #         subunit.base_morale = 0
    elif key_press == pygame.K_k and self.player_char:
        # for index, subunit in enumerate(self.current_selected.subunit_sprite):
        #     subunit.unit_health -= subunit.unit_health
        self.player_char.health = 0
    elif key_press == pygame.K_m and self.player_char is not None:
        for follower in self.player_char.alive_troop_follower:
            follower.health = 0
    elif key_press == pygame.K_n and self.player_char is not None:
        for follower in self.player_char.alive_leader_follower:
            follower.health = 0
    elif key_press == pygame.K_b and self.player_char is not None:
        for follower in self.player_char.alive_leader_follower:
            for follower2 in follower.alive_troop_follower:
                follower2.health = 0
