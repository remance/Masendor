import pygame


def battle_mouse_process(self, mouse_left_up, mouse_right_up, double_mouse_right, mouse_left_down, mouse_right_down,
                         key_state, key_press):
    if self.event_log.scroll.rect.collidepoint(self.mouse_pos):  # Must check mouse collide for scroll before event log ui
        self.click_any = True
        if mouse_left_down or mouse_left_up:
            self.click_any = True
            new_row = self.event_log.scroll.player_input(self.mouse_pos)
            if self.event_log.current_start_row != new_row:
                self.event_log.current_start_row = new_row
                self.event_log.recreate_image()

    elif self.event_log.rect.collidepoint(self.mouse_pos):  # check mouse collide for event log ui
        self.click_any = True

    elif self.time_ui.rect.collidepoint(self.mouse_pos):  # check mouse collide for time bar ui
        self.click_any = True
        for index, button in enumerate(self.time_button):  # Event log button and timer button click
            if button.rect.collidepoint(self.mouse_pos) and mouse_left_up:
                if button.event == "pause":  # pause button
                    self.game_speed = 0
                elif button.event == "decrease":  # reduce speed button
                    new_index = self.game_speed_list.index(self.game_speed) - 1
                    if new_index >= 0:
                        self.game_speed = self.game_speed_list[new_index]
                elif button.event == "increase":  # increase speed button
                    new_index = self.game_speed_list.index(self.game_speed) + 1
                    if new_index < len(self.game_speed_list):
                        self.game_speed = self.game_speed_list[new_index]
                self.speed_number.speed_update(self.game_speed)
                break

    elif self.click_any is False:
        for index, button in enumerate(self.event_log_button):  # Event log button and timer button click
            if button.rect.collidepoint(self.mouse_pos):
                if index in (0, 1, 2, 3, 4, 5):  # event_log button
                    self.click_any = True
                    if mouse_left_up:
                        if button.event in (0, 1, 2, 3):  # change tab mode
                            self.event_log.change_mode(button.event)
                        elif button.event == 4:  # delete tab log button
                            self.event_log.clear_tab()
                        elif button.event == 5:  # delete all tab log button
                            self.event_log.clear_tab(all_tab=True)
                break

    elif self.ui_mouse_click():  # check mouse collide for other ui
        pass

    # v code that only run when any unit is selected
    if self.current_selected is not None and self.current_selected.state != 100:
        if self.inspect_button.rect.collidepoint(self.mouse_pos) or (self.inspect and self.new_unit_click):  # click on inspect ui open/close button
            if self.new_unit_click is False:
                self.click_any = True
            if self.inspect_button.rect.collidepoint(self.mouse_pos):
                self.button_name_popup.pop(self.mouse_pos, "Inspect Subunit")
                self.battle_ui_updater.add(self.button_name_popup)
            if mouse_left_up:
                if self.inspect is False:  # Add unit inspect ui when left click at ui button or when change subunit with inspect open
                    self.inspect = True
                    self.battle_ui_updater.add(*self.troop_card_button,
                                               self.troop_card_ui, self.inspect_ui)
                    self.change_inspect_subunit()

                    self.inspect_selected_border.pop(self.subunit_selected.pos)
                    self.battle_ui_updater.add(self.inspect_selected_border)
                    self.troop_card_ui.value_input(who=self.subunit_selected.who, split=self.split_happen)

                    if self.troop_card_ui.option == 2:  # blit skill icon is previous mode is skill
                        self.trait_skill_icon_blit()
                        self.effect_icon_blit()
                        self.countdown_skill_icon()

                elif self.inspect:  # Remove when click again and the ui already open
                    self.battle_ui_updater.remove(*self.inspect_subunit, self.inspect_selected_border, self.troop_card_button,
                                                  self.troop_card_ui, self.inspect_ui)
                    self.inspect = False
                    self.new_unit_click = False

        elif self.command_ui in self.battle_ui_updater:  # mouse position on command ui
            if (mouse_left_up or mouse_right_up) and self.command_ui.rect.collidepoint(self.mouse_pos):
                self.click_any = True
            # and ( or key_press is not None)
            if self.current_selected.player_control and mouse_left_up:
                if self.behaviour_switch_button[0].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_g:
                    if mouse_left_up or key_press == pygame.K_g:  # rotate skill condition when clicked
                        self.current_selected.skill_cond += 1
                        if self.current_selected.skill_cond > 3:
                            self.current_selected.skill_cond = 0
                        self.behaviour_switch_button[0].event = self.current_selected.skill_cond
                    if self.behaviour_switch_button[0].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Free Skill Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.behaviour_switch_button[0].event])
                        self.battle_ui_updater.add(self.button_name_popup)

                elif self.behaviour_switch_button[1].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_f:
                    if mouse_left_up or key_press == pygame.K_f:  # rotate fire at will condition when clicked
                        self.current_selected.fire_at_will += 1
                        if self.current_selected.fire_at_will > 1:
                            self.current_selected.fire_at_will = 0
                        self.behaviour_switch_button[1].event = self.current_selected.fire_at_will
                    if self.behaviour_switch_button[1].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Fire at will", "Hold fire until order")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.behaviour_switch_button[1].event])
                        self.battle_ui_updater.add(self.button_name_popup)

                elif self.behaviour_switch_button[2].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_h:
                    if mouse_left_up or key_press == pygame.K_h:  # rotate hold condition when clicked
                        self.current_selected.hold += 1
                        if self.current_selected.hold > 2:
                            self.current_selected.hold = 0
                        self.behaviour_switch_button[2].event = self.current_selected.hold
                    if self.behaviour_switch_button[2].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.behaviour_switch_button[2].event])
                        self.battle_ui_updater.add(self.button_name_popup)

                elif self.behaviour_switch_button[3].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_j:
                    if mouse_left_up or key_press == pygame.K_j:  # rotate min range condition when clicked
                        self.current_selected.use_min_range += 1
                        if self.current_selected.use_min_range > 1:
                            self.current_selected.use_min_range = 0
                        self.behaviour_switch_button[3].event = self.current_selected.use_min_range
                    if self.behaviour_switch_button[3].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Minimum Shoot Range", "Maximum Shoot range")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.behaviour_switch_button[3].event])
                        self.battle_ui_updater.add(self.button_name_popup)

                elif self.behaviour_switch_button[4].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_j:
                    if mouse_left_up or key_press == pygame.K_j:  # rotate min range condition when clicked
                        self.current_selected.shoot_mode += 1
                        if self.current_selected.shoot_mode > 2:
                            self.current_selected.shoot_mode = 0
                        self.behaviour_switch_button[4].event = self.current_selected.shoot_mode
                    if self.behaviour_switch_button[4].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Both Arc and Direct Shot", "Only Arc Shot", "Only Direct Shot")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.behaviour_switch_button[4].event])
                        self.battle_ui_updater.add(self.button_name_popup)

                elif self.behaviour_switch_button[5].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_j:
                    if mouse_left_up or key_press == pygame.K_j:  # rotate min range condition when clicked
                        self.current_selected.run_toggle += 1
                        if self.current_selected.run_toggle > 1:
                            self.current_selected.run_toggle = 0
                        self.behaviour_switch_button[5].event = self.current_selected.run_toggle
                    if self.behaviour_switch_button[5].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Toggle Walk", "Toggle Run")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.behaviour_switch_button[5].event])
                        self.battle_ui_updater.add(self.button_name_popup)

                elif self.behaviour_switch_button[6].rect.collidepoint(self.mouse_pos):  # or key_press == pygame.K_j
                    if mouse_left_up:  # or key_press == pygame.K_j  # rotate min range condition when clicked
                        self.current_selected.attack_mode += 1
                        if self.current_selected.attack_mode > 2:
                            self.current_selected.attack_mode = 0
                        self.behaviour_switch_button[6].event = self.current_selected.attack_mode
                    if self.behaviour_switch_button[6].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Frontline Attack Only", "Keep Formation", "All Out Attack")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.behaviour_switch_button[6].event])
                        self.battle_ui_updater.add(self.button_name_popup)

                elif self.col_split_button in self.battle_ui_updater and self.col_split_button.rect.collidepoint(self.mouse_pos):
                    self.button_name_popup.pop(self.mouse_pos, "Split By Middle Column")
                    self.battle_ui_updater.add(self.button_name_popup)
                    if mouse_left_up and self.current_selected.state != 10:
                        self.current_selected.split_unit(1)
                        self.split_happen = True
                        self.current_selected.check_split()
                        self.battle_ui_updater.remove(*self.leader_now)
                        self.leader_now = self.current_selected.leader
                        self.battle_ui_updater.add(*self.leader_now)
                        self.unit_selector.setup_unit_icon(self.unit_icon, self.all_team_unit[self.team_selected])

                elif self.row_split_button in self.battle_ui_updater and self.row_split_button.rect.collidepoint(self.mouse_pos):
                    self.button_name_popup.pop(self.mouse_pos, "Split by Middle Row")
                    self.battle_ui_updater.add(self.button_name_popup)
                    if mouse_left_up and self.current_selected.state != 10:
                        self.current_selected.split_unit(0)
                        self.split_happen = True
                        self.current_selected.check_split()
                        self.battle_ui_updater.remove(*self.leader_now)
                        self.leader_now = self.current_selected.leader
                        self.battle_ui_updater.add(*self.leader_now)
                        self.unit_selector.setup_unit_icon(self.unit_icon, self.all_team_unit[self.team_selected])

                # elif self.button_ui[7].rect.collidepoint(self.mouse_pos):  # decimation effect
                #     self.button_name_popup.pop(self.mouse_pos, "Decimation")
                #     self.battle_ui.add(self.button_name_popup)
                #     if mouse_left_up and self.last_selected.state == 0:
                #         for subunit in self.last_selected.subunit_sprite:
                #             subunit.status_effect[98] = self.troop_data.status_list[98].copy()
                #             subunit.unit_health -= round(subunit.unit_health * 0.1)

            if self.leader_command_ui_mouse_over(mouse_right_up):
                self.battle_ui_updater.remove(self.button_name_popup)
                pass
        else:
            self.battle_ui_updater.remove(self.leader_popup)  # remove leader name popup if no mouseover on any button
            self.battle_ui_updater.remove(self.button_name_popup)  # remove popup if no mouseover on any button

        if self.inspect:  # if inspect ui is open
            if mouse_left_up or mouse_right_up:
                if self.inspect_ui.rect.collidepoint(self.mouse_pos):  # if mouse pos inside unit ui when click
                    self.click_any = True  # for avoiding clicking subunit under ui
                    for this_subunit in self.inspect_subunit:
                        if this_subunit.rect.collidepoint(
                                self.mouse_pos) and this_subunit in self.battle_ui_updater:  # Change showing stat to the clicked subunit one
                            if mouse_left_up:
                                self.subunit_selected = this_subunit
                                self.inspect_selected_border.pop(self.subunit_selected.pos)
                                self.event_log.add_log(
                                    [0, str(self.subunit_selected.who.board_pos) + " " + str(
                                        self.subunit_selected.who.name) + " in " +
                                     self.subunit_selected.who.unit.leader[0].name + "'s unit is selected"], [3])
                                self.battle_ui_updater.add(self.inspect_selected_border)
                                self.troop_card_ui.value_input(who=self.subunit_selected.who, split=self.split_happen)

                                if self.troop_card_ui.option == 2:
                                    self.trait_skill_icon_blit()
                                    self.effect_icon_blit()
                                    self.countdown_skill_icon()
                                else:
                                    self.kill_effect_icon()

                            elif mouse_right_up:
                                self.popout_lorebook(3, this_subunit.who.troop_id)
                            break

                elif self.troop_card_ui.rect.collidepoint(self.mouse_pos):  # mouse position in subunit card
                    self.click_any = True  # for avoiding clicking subunit under ui
                    self.troop_card_button_click(self.subunit_selected.who)

            if self.troop_card_ui.option == 2:
                if self.effect_icon_mouse_over(self.skill_icon, mouse_right_up):
                    pass
                elif self.effect_icon_mouse_over(self.effect_icon, mouse_right_up):
                    pass
                else:
                    self.battle_ui_updater.remove(self.effect_popup)

        else:
            self.kill_effect_icon()

        if mouse_right_up and self.click_any is False:  # Unit command
            self.current_selected.player_input(self.command_mouse_pos, mouse_left_up, mouse_right_up, mouse_left_down,
                                               mouse_right_down,  double_mouse_right, self.last_mouseover, key_state)

    if mouse_right_up and self.current_selected is None and self.click_any is False:  # draw terrain popup ui when right click at map with no selected unit
        if 1 <= self.command_mouse_pos[0] <= 999 and \
                1 <= self.command_mouse_pos[1] <= 999:  # not draw if pos is off the map
            terrain_pop, feature_pop = self.battle_map_feature.get_feature(self.command_mouse_pos, self.battle_map_base)
            feature_pop = self.battle_map_feature.feature_mod[feature_pop]
            height_pop = self.battle_map_height.get_height(self.command_mouse_pos)
            self.terrain_check.pop(self.mouse_pos, feature_pop, height_pop)
            self.battle_ui_updater.add(self.terrain_check)
