import pygame

from gamescript import weather, menu, battleui
from gamescript.common import utility

list_scroll = utility.list_scroll
setup_list = utility.setup_list


def battle_mouse(self, mouse_left_up, mouse_right_up, mouse_left_down, mouse_right_down, key_state):
    if mouse_left_up:
        self.click_any = False
        self.new_unit_click = False

    if self.terrain_check in self.battle_ui and (
            self.terrain_check.pos != self.mouse_pos or key_state[K_s] or key_state[K_w] or key_state[K_a] or key_state[K_d]):
        self.battle_ui.remove(self.terrain_check)  # remove terrain popup when move mouse or camera


def battle_state_mouse(self, mouse_left_up, mouse_right_up, double_mouse_right, mouse_left_down, mouse_right_down, key_state, key_press):
    if self.log_scroll.rect.collidepoint(self.mouse_pos):  # Must check mouse collide for scroll before event log ui
        self.ui_click = True
        if mouse_left_down or mouse_left_up:
            self.click_any = True
            new_row = self.log_scroll.user_input(self.mouse_pos)
            if self.event_log.current_start_row != new_row:
                self.event_log.current_start_row = new_row
                self.event_log.recreate_image()

    elif self.event_log.rect.collidepoint(self.mouse_pos):  # check mouse collide for event log ui
        if mouse_left_up:
            self.click_any = True
        self.ui_click = True

    elif self.time_ui.rect.collidepoint(self.mouse_pos):  # check mouse collide for time bar ui
        self.ui_click = True
        if mouse_left_up:
            self.click_any = True

            for index, button in enumerate(self.time_button):  # Event log button and timer button click
                if button.rect.collidepoint(self.mouse_pos):
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

    elif self.ui_mouse_over():  # check mouse collide for other ui
        pass

    elif self.button_mouse_over(mouse_right_up):  # check mouse collide for button
        pass

    elif mouse_right_up and self.last_selected is None and self.ui_click is False:  # draw terrain popup ui when right click at map with no selected unit
        if 0 <= self.battle_mouse_pos[1][0] <= 999 and \
                0 <= self.battle_mouse_pos[1][1] <= 999:  # not draw if pos is off the map
            terrain_pop, feature_pop = self.battle_map_feature.get_feature(self.battle_mouse_pos[1], self.battle_map_base)
            feature_pop = self.battle_map_feature.feature_mod[feature_pop]
            height_pop = self.battle_map_height.get_height(self.battle_mouse_pos[1])
            self.terrain_check.pop(self.mouse_pos, feature_pop, height_pop)
            self.battle_ui.add(self.terrain_check)

    elif self.ui_click is False:
        for index, button in enumerate(self.eventlog_button):  # Event log button and timer button click
            if button.rect.collidepoint(self.mouse_pos):
                if index in (0, 1, 2, 3, 4, 5):  # event_log button
                    self.ui_click = True
                    if mouse_left_up:
                        if button.event in (0, 1, 2, 3):  # change tab mode
                            self.event_log.change_mode(button.event)
                        elif button.event == 4:  # delete tab log button
                            self.event_log.clear_tab()
                        elif button.event == 5:  # delete all tab log button
                            self.event_log.clear_tab(all_tab=True)
                break

    # v code that only run when any unit is selected
    if self.last_selected is not None and self.last_selected.state != 100:
        if self.inspect_button.rect.collidepoint(self.mouse_pos) or (
                mouse_left_up and self.inspect and self.new_unit_click):  # click on inspect ui open/close button
            if self.inspect_button.rect.collidepoint(self.mouse_pos):
                self.button_name_popup.pop(self.mouse_pos, "Inspect Subunit")
                self.battle_ui.add(self.button_name_popup)
                if mouse_right_up:
                    self.ui_click = True  # for some reason the loop mouse check above does not work for inspect button, so it here instead
            if mouse_left_up:
                if self.inspect is False:  # Add unit inspect ui when left click at ui button or when change subunit with inspect open
                    self.inspect = True
                    self.battle_ui.add(*self.troop_card_button,
                                       self.troop_card_ui, self.inspect_ui)
                    self.subunit_selected = None

                    for index, this_subunit in enumerate(self.last_selected.subunit_sprite_array.flat):
                        if this_subunit is not None:
                            self.inspect_subunit[index].add_subunit(this_subunit)
                            self.battle_ui.add(self.inspect_subunit[index])
                            if self.subunit_selected is None:
                                self.subunit_selected = self.inspect_subunit[index]

                    self.subunit_selected_border.pop(self.subunit_selected.pos)
                    self.battle_ui.add(self.subunit_selected_border)
                    self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_list=self.all_weapon,
                                                   armour_list=self.all_armour,
                                                   split=self.split_happen)

                    if self.troop_card_ui.option == 2:  # blit skill icon is previous mode is skill
                        self.trait_skill_blit()
                        self.effect_icon_blit()
                        self.countdown_skill_icon()

                elif self.inspect:  # Remove when click again and the ui already open
                    self.battle_ui.remove(*self.inspect_subunit, self.subunit_selected_border, self.troop_card_button,
                                          self.troop_card_ui, self.inspect_ui)
                    self.inspect = False
                    self.new_unit_click = False

        elif self.command_ui in self.battle_ui and (
                self.command_ui.rect.collidepoint(self.mouse_pos) or key_press is not None):  # mouse position on command ui
            if self.last_selected.control:
                if self.switch_button[0].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_g:
                    if mouse_left_up or key_press == pygame.K_g:  # rotate skill condition when clicked
                        self.last_selected.skill_cond += 1
                        if self.last_selected.skill_cond > 3:
                            self.last_selected.skill_cond = 0
                        self.switch_button[0].event = self.last_selected.skill_cond
                    if self.switch_button[0].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Free Skill Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[0].event])
                        self.battle_ui.add(self.button_name_popup)

                elif self.switch_button[1].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_f:
                    if mouse_left_up or key_press == pygame.K_f:  # rotate fire at will condition when clicked
                        self.last_selected.fire_at_will += 1
                        if self.last_selected.fire_at_will > 1:
                            self.last_selected.fire_at_will = 0
                        self.switch_button[1].event = self.last_selected.fire_at_will
                    if self.switch_button[1].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Fire at will", "Hold fire until order")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[1].event])
                        self.battle_ui.add(self.button_name_popup)

                elif self.switch_button[2].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_h:
                    if mouse_left_up or key_press == pygame.K_h:  # rotate hold condition when clicked
                        self.last_selected.hold += 1
                        if self.last_selected.hold > 2:
                            self.last_selected.hold = 0
                        self.switch_button[2].event = self.last_selected.hold
                    if self.switch_button[2].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[2].event])
                        self.battle_ui.add(self.button_name_popup)

                elif self.switch_button[3].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_j:
                    if mouse_left_up or key_press == pygame.K_j:  # rotate min range condition when clicked
                        self.last_selected.use_min_range += 1
                        if self.last_selected.use_min_range > 1:
                            self.last_selected.use_min_range = 0
                        self.switch_button[3].event = self.last_selected.use_min_range
                    if self.switch_button[3].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Minimum Shoot Range", "Maximum Shoot range")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[3].event])
                        self.battle_ui.add(self.button_name_popup)

                elif self.switch_button[4].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_j:
                    if mouse_left_up or key_press == pygame.K_j:  # rotate min range condition when clicked
                        self.last_selected.shoot_mode += 1
                        if self.last_selected.shoot_mode > 2:
                            self.last_selected.shoot_mode = 0
                        self.switch_button[4].event = self.last_selected.shoot_mode
                    if self.switch_button[4].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Both Arc and Direct Shot", "Only Arc Shot", "Only Direct Shot")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[4].event])
                        self.battle_ui.add(self.button_name_popup)

                elif self.switch_button[5].rect.collidepoint(self.mouse_pos) or key_press == pygame.K_j:
                    if mouse_left_up or key_press == pygame.K_j:  # rotate min range condition when clicked
                        self.last_selected.run_toggle += 1
                        if self.last_selected.run_toggle > 1:
                            self.last_selected.run_toggle = 0
                        self.switch_button[5].event = self.last_selected.run_toggle
                    if self.switch_button[5].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Toggle Walk", "Toggle Run")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[5].event])
                        self.battle_ui.add(self.button_name_popup)

                elif self.switch_button[6].rect.collidepoint(self.mouse_pos):  # or key_press == pygame.K_j
                    if mouse_left_up:  # or key_press == pygame.K_j  # rotate min range condition when clicked
                        self.last_selected.attack_mode += 1
                        if self.last_selected.attack_mode > 2:
                            self.last_selected.attack_mode = 0
                        self.switch_button[6].event = self.last_selected.attack_mode
                    if self.switch_button[6].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                        pop_text = ("Frontline Attack Only", "Keep Formation", "All Out Attack")
                        self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[6].event])
                        self.battle_ui.add(self.button_name_popup)

                elif self.col_split_button in self.battle_ui and self.col_split_button.rect.collidepoint(self.mouse_pos):
                    self.button_name_popup.pop(self.mouse_pos, "Split By Middle Column")
                    self.battle_ui.add(self.button_name_popup)
                    if mouse_left_up and self.last_selected.state != 10:
                        self.split_unit(self.last_selected, 1)
                        self.split_happen = True
                        self.check_split(self.last_selected)
                        self.battle_ui.remove(*self.leader_now)
                        self.leader_now = self.last_selected.leader
                        self.battle_ui.add(*self.leader_now)
                        self.setup_unit_icon()

                elif self.row_split_button in self.battle_ui and self.row_split_button.rect.collidepoint(self.mouse_pos):
                    self.button_name_popup.pop(self.mouse_pos, "Split by Middle Row")
                    self.battle_ui.add(self.button_name_popup)
                    if mouse_left_up and self.last_selected.state != 10:
                        self.split_unit(self.last_selected, 0)
                        self.split_happen = True
                        self.check_split(self.last_selected)
                        self.battle_ui.remove(*self.leader_now)
                        self.leader_now = self.last_selected.leader
                        self.battle_ui.add(*self.leader_now)
                        self.setup_unit_icon()

                # elif self.button_ui[7].rect.collidepoint(self.mouse_pos):  # decimation effect
                #     self.button_name_popup.pop(self.mouse_pos, "Decimation")
                #     self.battle_ui.add(self.button_name_popup)
                #     if mouse_left_up and self.last_selected.state == 0:
                #         for subunit in self.last_selected.subunit_sprite:
                #             subunit.status_effect[98] = self.troop_data.status_list[98].copy()
                #             subunit.unit_health -= round(subunit.unit_health * 0.1)
            if self.leader_mouse_over(mouse_right_up):
                self.battle_ui.remove(self.button_name_popup)
                pass
        else:
            self.battle_ui.remove(self.leader_popup)  # remove leader name popup if no mouseover on any button
            self.battle_ui.remove(self.button_name_popup)  # remove popup if no mouseover on any button

        if self.inspect:  # if inspect ui is open
            if mouse_left_up or mouse_right_up:
                if self.inspect_ui.rect.collidepoint(self.mouse_pos):  # if mouse pos inside unit ui when click
                    self.click_any = True  # for avoiding right click or  subunit
                    self.ui_click = True  # for avoiding clicking subunit under ui
                    for this_subunit in self.inspect_subunit:
                        if this_subunit.rect.collidepoint(
                                self.mouse_pos) and this_subunit in self.battle_ui:  # Change showing stat to the clicked subunit one
                            if mouse_left_up:
                                self.subunit_selected = this_subunit
                                self.subunit_selected_border.pop(self.subunit_selected.pos)
                                self.event_log.add_log(
                                    [0, str(self.subunit_selected.who.board_pos) + " " + str(
                                        self.subunit_selected.who.name) + " in " +
                                     self.subunit_selected.who.unit.leader[0].name + "'s unit is selected"], [3])
                                self.battle_ui.add(self.subunit_selected_border)
                                self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_list=self.all_weapon,
                                                               armour_list=self.all_armour, split=self.split_happen)

                                if self.troop_card_ui.option == 2:
                                    self.trait_skill_blit()
                                    self.effect_icon_blit()
                                    self.countdown_skill_icon()
                                else:
                                    self.kill_effect_icon()

                            elif mouse_right_up:
                                self.popout_lorebook(3, this_subunit.who.troop_id)
                            break

                elif self.troop_card_ui.rect.collidepoint(self.mouse_pos):  # mouse position in subunit card
                    self.click_any = True
                    self.ui_click = True  # for avoiding clicking subunit under ui
                    self.troop_card_button_click(self.subunit_selected.who)

            if self.troop_card_ui.option == 2:
                if self.effect_icon_mouse_over(self.skill_icon, mouse_right_up):
                    pass
                elif self.effect_icon_mouse_over(self.effect_icon, mouse_right_up):
                    pass
                else:
                    self.battle_ui.remove(self.effect_popup)

        else:
            self.kill_effect_icon()

        if mouse_right_up and self.ui_click is False:  # Unit command
            self.last_selected.user_input(self.battle_mouse_pos[2], mouse_right_up, double_mouse_right,
                                          self.last_mouseover, key_state)

        self.before_selected = self.last_selected

    # ^ End subunit selected code


def editor_state_mouse(self, mouse_left_up, mouse_right_up, mouse_left_down, mouse_right_down, key_state, key_press):
    self.battle_ui.remove(self.leader_popup)
    if self.popup_listbox in self.battle_ui and self.popup_listbox.type == "leader" \
            and self.popup_listbox.rect.collidepoint(
        self.mouse_pos):  # this need to be at the top here to prioritise popup click
        self.ui_click = True
        for index, name in enumerate(self.popup_namegroup):  # change leader with the new selected one
            if name.rect.collidepoint(self.mouse_pos):
                if mouse_left_up and (self.show_in_card is not None and self.show_in_card.name != "None"):
                    if self.show_in_card.leader is not None and \
                            self.leader_now[self.show_in_card.leader.army_position].name != "None":  # remove old leader
                        self.leader_now[self.show_in_card.leader.army_position].change_preview_leader(1, self.leader_stat)
                        self.leader_now[self.show_in_card.leader.army_position].change_subunit(None)

                    true_index = [index for index, value in
                                  enumerate(list(self.leader_stat.leader_list.values())) if value["Name"] == name.name][0]
                    true_index = list(self.leader_stat.leader_list.keys())[true_index]
                    self.leader_now[self.selected_leader].change_preview_leader(true_index, self.leader_stat)
                    self.leader_now[self.selected_leader].change_subunit(self.show_in_card)
                    self.show_in_card.leader = self.leader_now[self.selected_leader]
                    self.preview_authority(self.leader_now)
                    self.troop_card_ui.value_input(who=self.show_in_card, weapon_list=self.all_weapon,
                                                   armour_list=self.all_armour, change_option=1)
                    unit_dict = self.convert_slot_dict("test")
                    if unit_dict is not None:
                        warn_list = []
                        leader_list = [int(item) for item in unit_dict['test'][-3].split(",")]
                        leader_list = [item for item in leader_list if 1 < item < 10000]
                        leader_list_set = set(leader_list)
                        if len(leader_list) != len(leader_list_set):  # unit has duplicate unique leader
                            warn_list.append(self.warning_msg.duplicateleader_warn)
                        if unit_dict['test'][-1] == "0":  # unit has leader/unit of multi faction
                            warn_list.append(self.warning_msg.multifaction_warn)
                        if len(warn_list) > 0:
                            self.warning_msg.warning(warn_list)
                            self.battle_ui.add(self.warning_msg)

                elif mouse_right_up:
                    self.popout_lorebook(8, self.current_pop_up_row + index + 1)

    elif self.unit_listbox.rect.collidepoint(self.mouse_pos) and self.unit_listbox in self.battle_ui:
        self.ui_click = True
        for index, name in enumerate(self.unitpreset_namegroup):
            if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:
                self.preset_select_border.change_pos(name.rect.topleft)  # change border to one selected
                if list(self.custom_unit_preset_list.keys())[index] != "New Preset":
                    self.unit_preset_name = name.name
                    unit_list = []
                    arraylist = list(self.custom_unit_preset_list[list(self.custom_unit_preset_list.keys())[index]])
                    for listnum in (0, 1, 2, 3, 4, 5, 6, 7):
                        unit_list += [int(item) if item.isdigit() else item
                                      for item in arraylist[listnum].split(",")]
                    leader_who_list = [int(item) if item.isdigit() else item
                                       for item in arraylist[8].split(",")]
                    leader_pos_list = [int(item) if item.isdigit() else item
                                       for item in arraylist[9].split(",")]

                    for unit_index, item in enumerate(unit_list):  # change all slot to whatever save in the selected preset
                        for slot in self.subunit_build:
                            if slot.game_id == unit_index:
                                slot.__init__(item, slot.game_id, self.unit_build_slot, slot.pos,
                                              100, 100, [1, 1], self.genre, "edit")
                                slot.kill()
                                break

                    for leader_index, item in enumerate(leader_who_list):
                        self.preview_leader[leader_index].leader = None
                        if self.preview_leader[leader_index].subunit is not None:
                            self.preview_leader[leader_index].subunit.leader = None

                        self.preview_leader[leader_index].change_preview_leader(item, self.leader_stat)

                        pos_index = 0
                        for slot in self.subunit_build:  # can't use game_id here as none subunit not count in position check
                            if pos_index == leader_pos_list[leader_index]:
                                self.preview_leader[leader_index].change_subunit(slot)
                                slot.leader = self.preview_leader[leader_index]
                                break
                            else:
                                if slot.name != "None":
                                    pos_index += 1

                    self.leader_now = [this_leader for this_leader in self.preview_leader]
                    self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
                    self.show_in_card = slot
                    self.command_ui.value_input(who=self.show_in_card)
                    self.troop_card_ui.value_input(who=self.show_in_card, weapon_list=self.all_weapon,
                                                   armour_list=self.all_armour)  # update subunit card on selected subunit
                    if self.troop_card_ui.option == 2:
                        self.trait_skill_blit()
                        self.effect_icon_blit()
                        self.countdown_skill_icon()
                    # self.previewauthority(self.preview_leader, 0)  # calculate authority

                else:  # new preset
                    self.unit_preset_name = ""
                    for slot in self.subunit_build:  # reset all sub-subunit slot
                        slot.__init__(0, slot.game_id, self.unit_build_slot, slot.pos, 100, 100, [1, 1], self.genre, "edit")
                        slot.kill()
                        slot.leader = None  # remove leader link in

                    for this_leader in self.preview_leader:
                        this_leader.change_subunit(None)  # remove subunit link in leader
                        this_leader.change_preview_leader(1, self.leader_stat)

                    self.leader_now = [this_leader for this_leader in self.preview_leader]
                    self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
                    self.show_in_card = slot
                    self.command_ui.value_input(who=self.show_in_card)

    elif self.command_ui in self.battle_ui and self.command_ui.rect.collidepoint(self.mouse_pos):
        self.ui_click = True
        for leader_index, this_leader in enumerate(self.leader_now):  # loop mouse pos on leader portrait
            if this_leader.rect.collidepoint(self.mouse_pos):
                army_position = self.leader_level[this_leader.army_position + 4]

                self.leader_popup.pop(self.mouse_pos,
                                      army_position + ": " + this_leader.name)  # popup leader name when mouse over
                self.battle_ui.add(self.leader_popup)

                if mouse_left_up:  # open list of leader to change leader in that slot
                    self.selected_leader = leader_index
                    self.popup_list_new_open(this_leader.rect.midright, self.leader_list, "leader")

                elif mouse_right_up:
                    self.popout_lorebook(8, this_leader.leader_id)
                break

    elif self.troop_card_ui.rect.collidepoint(self.mouse_pos):
        self.ui_click = True
        if self.show_in_card is not None and mouse_left_up:
            self.troop_card_button_click(self.show_in_card)

        if self.troop_card_ui.option == 2:
            for icon_list in (self.effect_icon, self.skill_icon):
                if self.effect_icon_mouse_over(self.skill_icon, mouse_right_up):
                    pass
                elif self.effect_icon_mouse_over(self.effect_icon, mouse_right_up):
                    pass
                else:
                    self.battle_ui.remove(self.effect_popup)

    elif mouse_left_up or mouse_left_down or mouse_right_up:  # left click for select, hold left mouse for scrolling, right click for encyclopedia
        if mouse_left_up or mouse_left_down:
            if self.popup_listbox in self.battle_ui:
                if self.popup_listbox.rect.collidepoint(self.mouse_pos):
                    self.ui_click = True
                    for index, name in enumerate(self.popup_namegroup):
                        if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # click on name in list
                            if self.popup_listbox.type == "terrain":
                                self.terrain_change_button.change_text(self.battle_map_base.terrain_list[index])
                                self.base_terrain = index
                                self.editor_map_change(map.terrain_colour[self.base_terrain],
                                                       map.feature_colour[self.feature_terrain])

                            elif self.popup_listbox.type == "feature":
                                self.feature_change_button.change_text(self.battle_map_feature.feature_list[index])
                                self.feature_terrain = index
                                self.editor_map_change(map.terrain_colour[self.base_terrain],
                                                       map.feature_colour[self.feature_terrain])

                            elif self.popup_listbox.type == "weather":
                                self.weather_type = int(index / 3)
                                self.weather_strength = index - (self.weather_type * 3)
                                self.weather_change_button.change_text(self.weather_list[index])
                                del self.current_weather
                                self.current_weather = weather.Weather(self.time_ui, self.weather_type + 1,
                                                                       self.weather_strength, self.all_weather)

                            if self.show_in_card is not None:  # reset subunit card as well
                                self.command_ui.value_input(who=self.show_in_card)
                                self.troop_card_ui.value_input(who=self.show_in_card, weapon_list=self.all_weapon,
                                                               armour_list=self.all_armour,
                                                               change_option=1)
                                if self.troop_card_ui.option == 2:
                                    self.trait_skill_blit()
                                    self.effect_icon_blit()
                                    self.countdown_skill_icon()

                            for this_name in self.popup_namegroup:  # remove troop name list
                                this_name.kill()
                                del this_name

                            self.battle_ui.remove(self.popup_listbox, self.popup_list_scroll)
                            break

                elif self.popup_list_scroll.rect.collidepoint(self.mouse_pos):  # scrolling on list
                    self.ui_click = True
                    self.current_pop_up_row = self.popup_list_scroll.user_input(
                        self.mouse_pos)  # update the scroll and get new current subsection
                    if self.popup_listbox.type == "terrain":
                        setup_list(self.screen_scale, menu.NameList, self.current_pop_up_row,
                                   self.battle_map_base.terrain_list,
                                   self.popup_namegroup, self.popup_listbox, self.battle_ui, layer=17)
                    elif self.popup_listbox.type == "feature":
                        setup_list(self.screen_scale, menu.NameList, self.current_pop_up_row,
                                   self.battle_map_feature.feature_list,
                                   self.popup_namegroup, self.popup_listbox, self.battle_ui, layer=17)
                    elif self.popup_listbox.type == "weather":
                        setup_list(self.screen_scale, menu.NameList, self.current_pop_up_row, self.weather_list,
                                   self.popup_namegroup,
                                   self.popup_listbox, self.battle_ui, layer=17)
                    elif self.popup_listbox.type == "leader":
                        setup_list(self.screen_scale, menu.NameList, self.current_pop_up_row, self.leader_list,
                                   self.popup_namegroup,
                                   self.popup_listbox, self.battle_ui, layer=19)

                else:
                    self.battle_ui.remove(self.popup_listbox, self.popup_list_scroll, *self.popup_namegroup)

            elif self.troop_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
                self.ui_click = True
                self.current_troop_row = self.troop_scroll.user_input(
                    self.mouse_pos)  # update the scroll and get new current subsection
                if self.current_list_show == "troop":
                    setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                               self.troop_namegroup,
                               self.troop_listbox, self.battle_ui)
                elif self.current_list_show == "faction":
                    setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.faction_list,
                               self.troop_namegroup,
                               self.troop_listbox, self.battle_ui)

            elif self.unit_preset_name_scroll.rect.collidepoint(self.mouse_pos):
                self.ui_click = True
                self.current_unit_row = self.unit_preset_name_scroll.user_input(
                    self.mouse_pos)  # update the scroll and get new current subsection
                setup_list(self.screen_scale, menu.NameList, self.current_unit_row, list(self.custom_unit_preset_list.keys()),
                           self.unitpreset_namegroup, self.unit_listbox, self.battle_ui)  # setup preset army list

            elif self.subunit_build in self.battle_ui:
                clicked_slot = None
                for slot in self.subunit_build:  # left click on any sub-subunit slot
                    if slot.rect.collidepoint(self.mouse_pos):
                        self.ui_click = True
                        clicked_slot = slot
                        break

                if clicked_slot is not None:
                    if key_state[pygame.K_LSHIFT] or key_state[
                        pygame.K_RSHIFT]:  # add all sub-subunit from the first selected
                        first_one = None
                        for new_slot in self.subunit_build:
                            if new_slot.game_id <= clicked_slot.game_id:
                                if first_one is None and new_slot.selected:  # found the previous selected sub-subunit
                                    first_one = new_slot.game_id
                                    if clicked_slot.game_id <= first_one:  # cannot go backward, stop loop
                                        break
                                    elif clicked_slot.selected is False:  # forward select, acceptable
                                        clicked_slot.selected = True
                                        self.unit_edit_border.add(
                                            battleui.SelectedSquad(clicked_slot.inspect_pos, 5))
                                        self.battle_ui.add(*self.unit_edit_border)
                                elif first_one is not None and new_slot.game_id > first_one and new_slot.selected is False:  # select from first select to clicked
                                    new_slot.selected = True
                                    self.unit_edit_border.add(
                                        battleui.SelectedSquad(new_slot.inspect_pos, 5))
                                    self.battle_ui.add(*self.unit_edit_border)

                    elif key_state[pygame.K_LCTRL] or key_state[
                        pygame.K_RCTRL]:  # add another selected sub-subunit with left ctrl + left mouse button
                        if clicked_slot.selected is False:
                            clicked_slot.selected = True
                            self.unit_edit_border.add(battleui.SelectedSquad(clicked_slot.inspect_pos, 5))
                            self.battle_ui.add(*self.unit_edit_border)

                    elif key_state[pygame.K_LALT] or key_state[pygame.K_RALT]:
                        if clicked_slot.selected and len(self.unit_edit_border) > 1:
                            clicked_slot.selected = False
                            for border in self.unit_edit_border:
                                if border.pos == clicked_slot.pos:
                                    border.kill()
                                    del border
                                    break

                    else:  # select one sub-subunit by normal left click
                        for border in self.unit_edit_border:  # remove all border first
                            border.kill()
                            del border
                        for new_slot in self.subunit_build:
                            new_slot.selected = False
                        clicked_slot.selected = True
                        self.unit_edit_border.add(battleui.SelectedSquad(clicked_slot.inspect_pos, 5))
                        self.battle_ui.add(*self.unit_edit_border)

                        if clicked_slot.name != "None":
                            self.battle_ui.remove(*self.leader_now)
                            self.leader_now = [this_leader for this_leader in self.preview_leader]
                            self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
                            self.show_in_card = slot
                            self.command_ui.value_input(who=self.show_in_card)
                            self.troop_card_ui.value_input(who=self.show_in_card, weapon_list=self.all_weapon,
                                                           armour_list=self.all_armour)  # update subunit card on selected subunit
                            if self.troop_card_ui.option == 2:
                                self.trait_skill_blit()
                                self.effect_icon_blit()
                                self.countdown_skill_icon()

        if mouse_left_up or mouse_right_up:
            if self.subunit_build in self.battle_ui and self.troop_listbox.rect.collidepoint(self.mouse_pos):
                self.ui_click = True
                for index, name in enumerate(self.troop_namegroup):
                    if name.rect.collidepoint(self.mouse_pos):
                        if self.current_list_show == "faction":
                            self.current_troop_row = 0

                            if mouse_left_up:
                                self.faction_pick = index
                                self.filter_troop_list()
                                if index != 0:  # pick faction
                                    self.leader_list = [item[1]["Name"] for this_index, item in
                                                        enumerate(self.leader_stat.leader_list.items())
                                                        if this_index > 0 and (item[1]["Name"] == "None" or
                                                                               (item[0] >= 10000 and item[1]["Faction"] in (
                                                                                   0, index)) or
                                                                               item[0] in
                                                                               self.all_faction.faction_list[index][
                                                                                   "Leader"])]

                                else:  # pick all faction
                                    self.leader_list = self.leader_list = [item[0] for item in
                                                                           self.leader_stat.leader_list.values()][1:]

                                setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                                           self.troop_namegroup,
                                           self.troop_listbox, self.battle_ui)  # setup troop name list
                                self.troop_scroll.change_image(new_row=self.current_troop_row,
                                                               log_size=len(self.troop_list))  # change troop scroll image

                                self.main.make_team_coa([index], ui_class=self.battle_ui, one_team=True,
                                                        team1_set_pos=(
                                                            self.troop_listbox.rect.midleft[0] - int(
                                                                (200 * self.screen_scale[0]) / 2),
                                                            self.troop_listbox.rect.midleft[1]))  # change team coa_list

                                self.current_list_show = "troop"

                            elif mouse_right_up:
                                self.popout_lorebook(2, index)

                        elif self.current_list_show == "troop":
                            if mouse_left_up:
                                for slot in self.subunit_build:
                                    if slot.selected:
                                        if key_state[pygame.K_LSHIFT]:  # change all sub-subunit in army
                                            for new_slot in self.subunit_build:
                                                if new_slot.army_id == slot.army_id:
                                                    slot.__init__(self.troop_index_list[index + self.current_troop_row],
                                                                  new_slot.game_id, self.unit_build_slot, slot.pos,
                                                                  100, 100, [1, 1], self.genre, "edit")
                                                    slot.kill()

                                        else:
                                            slot.__init__(self.troop_index_list[index + self.current_troop_row],
                                                          slot.game_id, self.unit_build_slot, slot.pos,
                                                          100, 100, [1, 1], self.genre, "edit")
                                            slot.kill()

                                        if slot.name != "None":  # update information of subunit that just got changed
                                            self.battle_ui.remove(*self.leader_now)
                                            self.leader_now = [this_leader for this_leader in self.preview_leader]
                                            self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
                                            self.show_in_card = slot
                                            self.preview_authority(self.leader_now)
                                            self.troop_card_ui.value_input(who=self.show_in_card,
                                                                           weapon_list=self.all_weapon,
                                                                           armour_list=self.all_armour)  # update subunit card on selected subunit
                                            if self.troop_card_ui.option == 2:
                                                self.trait_skill_blit()
                                                self.effect_icon_blit()
                                                self.countdown_skill_icon()
                                        elif slot.name == "None" and slot.leader is not None:  # remove leader from none subunit if any
                                            slot.leader.change_preview_leader(1, self.leader_stat)
                                            slot.leader.change_subunit(None)  # remove subunit link in leader
                                            slot.leader = None  # remove leader link in subunit
                                            self.preview_authority(self.leader_now)
                                unit_dict = self.convert_slot_dict("test")
                                if unit_dict is not None and unit_dict['test'][-1] == "0":
                                    self.warning_msg.warning([self.warning_msg.multifaction_warn])
                                    self.battle_ui.add(self.warning_msg)

                            elif mouse_right_up:  # open encyclopedia
                                self.popout_lorebook(3, self.troop_index_list[index + self.current_troop_row])
                        break

            elif self.filter_box.rect.collidepoint(self.mouse_pos):
                self.ui_click = True
                if mouse_left_up:
                    if self.team_change_button.rect.collidepoint(self.mouse_pos):
                        if self.team_change_button.event == 0:
                            self.team_change_button.event = 1

                        elif self.team_change_button.event == 1:
                            self.team_change_button.event = 0

                        self.unit_build_slot.team = self.team_change_button.event + 1

                        for slot in self.subunit_build:
                            slot.__init__(slot.troop_id, slot.game_id, self.unit_build_slot, slot.pos,
                                          100, 100, [1, 1], self.genre, "edit")
                            slot.kill()
                            self.command_ui.value_input(
                                who=slot)  # loop valueinput so it change team correctly

                    elif self.slot_display_button.rect.collidepoint(self.mouse_pos):
                        if self.slot_display_button.event == 0:  # hide
                            self.slot_display_button.event = 1
                            self.battle_ui.remove(self.unitsetup_stuff, self.leader_now)
                            self.kill_effect_icon()

                        elif self.slot_display_button.event == 1:  # show
                            self.slot_display_button.event = 0
                            self.battle_ui.add(self.unitsetup_stuff, self.leader_now)

                    elif self.deploy_button.rect.collidepoint(self.mouse_pos) and self.subunit_build in self.battle_ui:
                        can_deploy = True
                        subunit_count = 0
                        warning_list = []
                        for slot in self.subunit_build:
                            if slot.troop_id != 0:
                                subunit_count += 1
                        if subunit_count < 8:
                            can_deploy = False
                            warning_list.append(self.warning_msg.eightsubunit_warn)
                        if self.leader_now == [] or self.preview_leader[0].name == "None":
                            can_deploy = False
                            warning_list.append(self.warning_msg.mainleader_warn)

                        if can_deploy:
                            unit_game_id = 0
                            if len(self.all_unit_index) > 0:
                                unit_game_id = self.all_unit_index[-1] + 1
                            current_preset = self.convert_slot_dict(self.unit_preset_name,
                                                                    [str(int(self.base_camera_pos[0])),
                                                                     str(int(self.base_camera_pos[1]))], unit_game_id)
                            subunit_game_id = 0
                            if len(self.subunit) > 0:
                                for this_subunit in self.subunit:
                                    subunit_game_id = this_subunit.game_id
                                subunit_game_id = subunit_game_id + 1
                            for slot in self.subunit_build:  # just for grabing current selected team
                                current_preset[self.unit_preset_name] += (0, 100, 100, slot.team)
                                self.convert_edit_unit((self.team0_unit, self.team1_unit, self.team2_unit)[slot.team],
                                                       current_preset[self.unit_preset_name], self.team_colour[slot.team],
                                                       pygame.transform.scale(
                                                           self.coa_list[int(current_preset[self.unit_preset_name][-1])],
                                                           (60, 60)), subunit_game_id)
                                break
                            self.slot_display_button.event = 1
                            self.kill_effect_icon()
                            self.setup_unit_icon()
                            self.battle_ui.remove(self.unitsetup_stuff, self.leader_now)
                            for this_unit in self.all_unit_list:
                                this_unit.start_set(self.subunit)
                            for this_subunit in self.subunit:
                                this_subunit.gamestart(self.camera_scale)
                            for this_leader in self.leader_updater:
                                this_leader.gamestart()

                            for this_unit in self.all_unit_list:
                                this_unit.user_input(self.battle_mouse_pos[0], False, False, self.last_mouseover, None,
                                                     other_command=1)
                        else:
                            self.warning_msg.warning(warning_list)
                            self.battle_ui.add(self.warning_msg)
                    else:
                        for box in self.filter_tick_box:
                            if box in self.battle_ui and box.rect.collidepoint(self.mouse_pos):
                                if box.tick is False:
                                    box.change_tick(True)
                                else:
                                    box.change_tick(False)
                                if box.option == "meleeinf":
                                    self.filter_troop[0] = box.tick
                                elif box.option == "rangeinf":
                                    self.filter_troop[1] = box.tick
                                elif box.option == "meleecav":
                                    self.filter_troop[2] = box.tick
                                elif box.option == "rangecav":
                                    self.filter_troop[3] = box.tick
                                if self.current_list_show == "troop":
                                    self.current_troop_row = 0
                                    self.filter_troop_list()
                                    setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                                               self.troop_namegroup,
                                               self.troop_listbox, self.battle_ui)  # setup troop name list
            elif self.terrain_change_button.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # change map terrain button
                self.ui_click = True
                self.popup_list_new_open(self.terrain_change_button.rect.midtop, self.battle_map_base.terrain_list, "terrain")

            elif self.feature_change_button.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # change map feature button
                self.ui_click = True
                self.popup_list_new_open(self.feature_change_button.rect.midtop, self.battle_map_feature.feature_list,
                                        "feature")

            elif self.weather_change_button.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # change map weather button
                self.ui_click = True
                self.popup_list_new_open(self.weather_change_button.rect.midtop, self.weather_list, "weather")

            elif self.unit_delete_button.rect.collidepoint(self.mouse_pos) and mouse_left_up and \
                    self.unit_delete_button in self.battle_ui:  # delete preset button
                self.ui_click = True
                if self.unit_preset_name == "":
                    pass
                else:
                    self.text_input_popup = ("confirm_input", "delete_preset")
                    self.confirm_ui.change_instruction("Delete Selected Preset?")
                    self.battle_ui.add(*self.confirm_ui_popup)

            elif self.unit_save_button.rect.collidepoint(self.mouse_pos) and mouse_left_up and \
                    self.unit_save_button in self.battle_ui:  # save preset button
                self.ui_click = True
                self.text_input_popup = ("text_input", "save_unit")

                if self.unit_preset_name == "":
                    self.input_box.text_start("")
                else:
                    self.input_box.text_start(self.unit_preset_name)

                self.input_ui.change_instruction("Preset Name:")
                self.battle_ui.add(*self.input_ui_popup)

            elif self.warning_msg in self.battle_ui and self.warning_msg.rect.collidepoint(self.mouse_pos):
                self.battle_ui.remove(self.warning_msg)

            elif self.team_coa in self.battle_ui:
                for team in self.team_coa:
                    if team.rect.collidepoint(self.mouse_pos) and mouse_left_up:
                        self.ui_click = True
                        if self.current_list_show == "troop":
                            self.current_troop_row = 0
                            setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.faction_list,
                                       self.troop_namegroup,
                                       self.troop_listbox, self.battle_ui)
                            self.troop_scroll.change_image(new_row=self.current_troop_row,
                                                           log_size=len(self.faction_list))  # change troop scroll image
                            self.current_list_show = "faction"


def battle_key_press(self, key_press):
    if key_press == pygame.K_TAB:
        self.map_mode += 1  # change height map mode
        if self.map_mode > 2:
            self.map_mode = 0
        self.show_map.change_mode(self.map_mode)
        self.show_map.change_scale(self.camera_scale)

    elif key_press == pygame.K_o:  # Toggle unit number
        if self.show_troop_number:
            self.show_troop_number = False
            self.effect_updater.remove(*self.troop_number_sprite)
            self.battle_camera.remove(*self.troop_number_sprite)
        else:  # speed currently pause
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
        self.log_scroll.change_image(new_row=self.event_log.current_start_row)

    elif key_press == pygame.K_PAGEDOWN:  # Go to bottom of event log
        if self.event_log.len_check > self.event_log.max_row_show:
            self.event_log.current_start_row = self.event_log.len_check - self.event_log.max_row_show
            self.event_log.recreate_image()
            self.log_scroll.change_image(new_row=self.event_log.current_start_row)

    elif key_press == pygame.K_SPACE and self.last_selected is not None:
        self.last_selected.user_input(self.battle_mouse_pos[0], False, False, self.last_mouseover, None, other_command=2)

    # vv FOR DEVELOPMENT DELETE LATER
    # elif key_press == pygame.K_1:
    #     self.drama_text.queue.append("Hello and Welcome to update video")
    # elif key_press == pygame.K_2:
    #     self.drama_text.queue.append("Showcase: Just simple clarity update")
    # elif key_press == pygame.K_3:
    #     self.drama_text.queue.append("Before")
    # elif key_press == pygame.K_4:
    #     self.drama_text.queue.append("Where the hell is blue team, can only see red")
    # elif key_press == pygame.K_5:
    #     self.drama_text.queue.append("After")
    # elif key_press == pygame.K_6:
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



def battle_mouse_scrolling(self, mouse_scroll_up, mouse_scroll_down):
    if self.event_log.rect.collidepoint(self.mouse_pos):  # Scrolling when mouse at event log
        if mouse_scroll_up:
            self.event_log.current_start_row -= 1
            if self.event_log.current_start_row < 0:  # can go no further than the first log
                self.event_log.current_start_row = 0
            else:
                self.event_log.recreate_image()  # recreate event_log image
                self.log_scroll.change_image(new_row=self.event_log.current_start_row)
        elif mouse_scroll_down:
            self.event_log.current_start_row += 1
            if self.event_log.current_start_row + self.event_log.max_row_show - 1 < self.event_log.len_check and \
                    self.event_log.len_check > 9:
                self.event_log.recreate_image()
                self.log_scroll.change_image(new_row=self.event_log.current_start_row)
            else:
                self.event_log.current_start_row -= 1

    elif self.unit_selector.rect.collidepoint(self.mouse_pos):  # Scrolling when mouse at unit selector ui
        if mouse_scroll_up:
            self.unit_selector.current_row -= 1
            if self.unit_selector.current_row < 0:
                self.unit_selector.current_row = 0
            else:
                self.setup_unit_icon()
                self.select_scroll.change_image(new_row=self.unit_selector.current_row)
        elif mouse_scroll_down:
            self.unit_selector.current_row += 1
            if self.unit_selector.current_row < self.unit_selector.log_size:
                self.setup_unit_icon()
                self.select_scroll.change_image(new_row=self.unit_selector.current_row)
            else:
                self.unit_selector.current_row -= 1
                if self.unit_selector.current_row < 0:
                    self.unit_selector.current_row = 0

    elif self.popup_listbox in self.battle_ui:  # mouse scroll on popup list
        if self.popup_listbox.type == "terrain":
            self.current_pop_up_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.popup_list_scroll,
                                                  self.popup_listbox,
                                                  self.current_pop_up_row, self.battle_map_base.terrain_list,
                                                  self.popup_namegroup, self.battle_ui)
        elif self.popup_listbox.type == "feature":
            self.current_pop_up_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.popup_list_scroll,
                                                  self.popup_listbox,
                                                  self.current_pop_up_row, self.battle_map_feature.feature_list,
                                                  self.popup_namegroup, self.battle_ui)
        elif self.popup_listbox.type == "weather":
            self.current_pop_up_row = (mouse_scroll_up, mouse_scroll_down, self.popup_list_scroll,
                                       self.popup_listbox, self.current_pop_up_row, self.weather_list,
                                       self.popup_namegroup, self.battle_ui)
        elif self.popup_listbox.type == "leader":
            self.current_pop_up_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.popup_list_scroll,
                                                  self.popup_listbox, self.current_pop_up_row, self.leader_list,
                                                  self.popup_namegroup, self.battle_ui, layer=19)

    elif self.unit_listbox in self.battle_ui and self.unit_listbox.rect.collidepoint(self.mouse_pos):  # mouse scroll on unit preset list
        self.current_unit_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.unit_preset_name_scroll,
                                            self.unit_listbox,
                                            self.current_unit_row, list(self.custom_unit_preset_list.keys()),
                                            self.unitpreset_namegroup, self.battle_ui)
    elif self.troop_listbox in self.battle_ui and self.troop_listbox.rect.collidepoint(self.mouse_pos):
        if self.current_list_show == "troop":  # mouse scroll on troop list
            self.current_troop_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.troop_scroll,
                                                 self.troop_listbox, self.current_troop_row, self.troop_list,
                                                 self.troop_namegroup, self.battle_ui)
        elif self.current_list_show == "faction":  # mouse scroll on faction list
            self.current_troop_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.troop_scroll,
                                                 self.troop_listbox, self.current_troop_row, self.faction_list,
                                                 self.troop_namegroup, self.battle_ui)

    elif self.map_scale_delay == 0:  # Scrolling in self map to zoom
        if mouse_scroll_up:
            self.camera_scale += 1
            if self.camera_scale > 10:
                self.camera_scale = 10
            else:
                self.camera_pos[0] = self.base_camera_pos[0] * self.camera_scale
                self.camera_pos[1] = self.base_camera_pos[1] * self.camera_scale
                self.show_map.change_scale(self.camera_scale)
                if self.game_state == "battle":  # only have delay in battle mode
                    self.map_scale_delay = 0.001

        elif mouse_scroll_down:
            self.camera_scale -= 1
            if self.camera_scale < 1:
                self.camera_scale = 1
            else:
                self.camera_pos[0] = self.base_camera_pos[0] * self.camera_scale
                self.camera_pos[1] = self.base_camera_pos[1] * self.camera_scale
                self.show_map.change_scale(self.camera_scale)
                if self.game_state == "battle":  # only have delay in battle mode
                    self.map_scale_delay = 0.001


def selected_unit_process(self, mouse_left_up, mouse_right_up, double_mouse_right, mouse_left_down, mouse_right_down, key_state, key_press):
    if self.last_selected is not None:
        if self.game_state == "battle" and self.last_selected.state != 100:
            if self.before_selected is None:  # add back the pop-up ui, so it gets shown when click subunit with none selected before
                self.battle_ui.add(self.unitstat_ui, self.command_ui)  # add leader and top ui
                self.battle_ui.add(self.inspect_button)  # add inspection ui open/close button

                self.add_behaviour_ui(self.last_selected)

            elif self.before_selected != self.last_selected or self.split_happen:  # change subunit information when select other unit
                if self.inspect:  # change inspect ui
                    self.new_unit_click = True
                    self.battle_ui.remove(*self.inspect_subunit)

                    self.subunit_selected = None
                    for index, this_subunit in enumerate(self.last_selected.subunit_sprite_array.flat):
                        if this_subunit is not None:
                            self.inspect_subunit[index].add_subunit(this_subunit)
                            self.battle_ui.add(self.inspect_subunit[index])
                            if self.subunit_selected is None:
                                self.subunit_selected = self.inspect_subunit[index]

                    self.subunit_selected_border.pop(self.subunit_selected.pos)
                    self.battle_ui.add(self.subunit_selected_border)
                    self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_list=self.all_weapon,
                                                   armour_list=self.all_armour,
                                                   split=self.split_happen)
                self.battle_ui.remove(*self.leader_now)

                self.add_behaviour_ui(self.last_selected, else_check=True)

                if self.split_happen:  # end split check
                    self.split_happen = False

            else:  # Update unit stat ui and command ui value every 1.1 seconds
                if self.ui_timer >= 1.1:
                    self.unitstat_ui.value_input(who=self.last_selected, split=self.split_happen)
                    self.command_ui.value_input(who=self.last_selected, split=self.split_happen)

        elif self.game_state == "editor" and self.subunit_build not in self.battle_ui:
            if (mouse_right_up or mouse_right_down) and self.ui_click is False:  # Unit placement
                self.last_selected.placement(self.battle_mouse_pos[1], mouse_right_up, mouse_right_down, double_mouse_right)

            if key_state[pygame.K_DELETE]:
                for this_unit in self.troop_number_sprite:
                    if this_unit.who == self.last_selected:
                        this_unit.delete()
                        this_unit.kill()
                        del this_unit
                for this_subunit in self.last_selected.subunit_sprite:
                    this_subunit.delete()
                    self.all_subunit_list.remove(this_subunit)
                    this_subunit.kill()
                    del this_subunit
                for this_leader in self.last_selected.leader:
                    this_leader.delete()
                    this_leader.kill()
                    del this_leader
                del [self.team0_pos_list, self.team1_pos_list, self.team2_pos_list][self.last_selected.team][
                    self.last_selected.game_id]
                self.last_selected.delete()
                self.last_selected.kill()
                self.all_unit_list.remove(self.last_selected)
                self.all_unit_index.remove(self.last_selected.game_id)
                self.setup_unit_icon()
                self.last_selected = None

    # v Update value of the clicked subunit every 1.1 second
    if self.game_state == "battle" and self.inspect and ((self.ui_timer >= 1.1 and self.troop_card_ui.option != 0) or
                                                         self.before_selected != self.last_selected):
        self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_list=self.all_weapon, armour_list=self.all_armour,
                                       split=self.split_happen)
        if self.troop_card_ui.option == 2:  # skill and status effect card
            self.countdown_skill_icon()
            self.effect_icon_blit()
            if self.before_selected != self.last_selected:  # change subunit, reset trait icon as well
                self.trait_skill_blit()
                self.countdown_skill_icon()
        else:
            self.kill_effect_icon()
    # ^ End update value



def add_behaviour_ui(self, who_input, else_check=False):
    if who_input.control:
        # self.battle_ui.add(self.button_ui[7])  # add decimation button
        self.battle_ui.add(*self.switch_button[0:7])  # add unit behaviour change button
        self.switch_button[0].event = who_input.skill_cond
        self.switch_button[1].event = who_input.fire_at_will
        self.switch_button[2].event = who_input.hold
        self.switch_button[3].event = who_input.use_min_range
        self.switch_button[4].event = who_input.shoot_mode
        self.switch_button[5].event = who_input.run_toggle
        self.switch_button[6].event = who_input.attack_mode
        self.check_split(who_input)  # check if selected unit can split, if yes draw button
    elif else_check:
        if self.row_split_button in self.battle_ui:
            self.row_split_button.kill()
        if self.col_split_button in self.battle_ui:
            self.col_split_button.kill()
        # self.battle_ui.remove(self.button_ui[7])  # remove decimation button
        self.battle_ui.remove(*self.switch_button[0:7])  # remove unit behaviour change button

    self.leader_now = who_input.leader
    self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
    self.unitstat_ui.value_input(who=who_input, split=self.split_happen)
    self.command_ui.value_input(who=who_input, split=self.split_happen)