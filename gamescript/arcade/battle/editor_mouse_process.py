import pygame

from gamescript import weather, menu, battleui, unit, battlemap
from gamescript.common import utility

list_scroll = utility.list_scroll
setup_list = utility.setup_list

team_colour = unit.team_colour


def editor_mouse_process(self, mouse_left_up, mouse_right_up, mouse_left_down, mouse_right_down, key_state, key_press):
    if self.popup_list_box in self.battle_ui_updater \
            and self.popup_list_box.type == "leader" \
            and self.popup_list_box.rect.collidepoint(self.mouse_pos):  # need to be first to prioritise popup click
        self.click_any = True
        for index, name in enumerate(self.popup_namegroup):  # change leader with the new selected one
            if name.rect.collidepoint(self.mouse_pos):
                if mouse_left_up and (self.subunit_in_card is not None and self.subunit_in_card.name != "None"):
                    if self.subunit_in_card.leader is not None and \
                            self.leader_now[self.subunit_in_card.leader.role].name != "None":  # remove old leader
                        self.leader_now[self.subunit_in_card.leader.role].change_preview_leader(1, self.leader_data)
                        self.leader_now[self.subunit_in_card.leader.role].change_subunit(None)

                    true_index = [index for index, value in
                                  enumerate(list(self.leader_data.leader_list.values())) if value["Name"] == name.name][
                        0]
                    true_index = list(self.leader_data.leader_list.keys())[true_index]
                    self.leader_now[self.selected_leader].change_preview_leader(true_index, self.leader_data)
                    self.leader_now[self.selected_leader].change_subunit(self.subunit_in_card)
                    self.subunit_in_card.leader = self.leader_now[self.selected_leader]
                    self.preview_authority(self.leader_now)
                    self.troop_card_ui.value_input(who=self.subunit_in_card, change_option=1)
                    unit_dict = self.convert_unit_slot_to_dict("test")
                    if unit_dict is not None:
                        warn_list = []
                        leader_list = [int(item) for item in unit_dict['test'][-3].split(",")]
                        leader_list = [item for item in leader_list if 1 < item < 10000]
                        leader_list_set = set(leader_list)
                        if len(leader_list) != len(leader_list_set):  # unit has duplicate unique leader
                            warn_list.append(self.warning_msg.duplicate_leader_warn)
                        if unit_dict['test'][-1] == "0":  # unit has leader/unit of multi faction
                            warn_list.append(self.warning_msg.multi_faction_warn)
                        if len(warn_list) > 0:
                            self.warning_msg.warning(warn_list)
                            self.battle_ui_updater.add(self.warning_msg)

                elif mouse_right_up:
                    self.popout_lorebook(8, self.current_pop_up_row + index + 1)

    elif self.unit_preset_list_box.rect.collidepoint(
            self.mouse_pos) and self.unit_preset_list_box in self.battle_ui_updater:
        self.click_any = True
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

                    for slot_index, slot in enumerate(
                            self.subunit_build):  # change all slot to whatever save in the selected preset
                        slot.kill()
                        slot.__init__(unit_list[slot_index], slot.game_id, self.unit_build_slot, slot.pos,
                                      100, 100, [1, 1], self.genre, "edit")  # TODO init cause issue
                        slot.kill()
                        self.subunit_build.add(slot)
                        self.battle_ui_updater.add(slot)

                    for leader_index, item in enumerate(leader_who_list):
                        self.preview_leader[leader_index].leader = None
                        if self.preview_leader[leader_index].subunit is not None:
                            self.preview_leader[leader_index].subunit.leader = None

                        self.preview_leader[leader_index].change_preview_leader(item, self.leader_data)

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
                    self.battle_ui_updater.add(*self.leader_now)  # add leader portrait to draw
                    self.subunit_in_card = slot
                    self.command_ui.value_input(who=self.subunit_in_card)
                    self.troop_card_ui.value_input(who=self.subunit_in_card)  # update subunit card on selected subunit
                    if self.troop_card_ui.option == 2:
                        self.trait_skill_icon_blit()
                        self.effect_icon_blit()
                        self.countdown_skill_icon()

                else:  # new preset
                    self.unit_preset_name = ""
                    for slot in self.subunit_build:  # reset all sub-subunit slot
                        slot.kill()
                        slot.__init__(0, slot.game_id, self.unit_build_slot, slot.pos, 100, 100, [1, 1], self.genre,
                                      "edit")
                        slot.kill()
                        self.subunit_build.add(slot)
                        self.battle_ui_updater.add(slot)
                        slot.leader = None  # remove leader link in

                    for this_leader in self.preview_leader:
                        this_leader.change_subunit(None)  # remove subunit link in leader
                        this_leader.change_preview_leader(1, self.leader_data)

                    self.leader_now = [this_leader for this_leader in self.preview_leader]
                    self.battle_ui_updater.add(*self.leader_now)  # add leader portrait to draw
                    self.subunit_in_card = slot
                    self.command_ui.value_input(who=self.subunit_in_card)

    elif self.command_ui in self.battle_ui_updater and self.command_ui.rect.collidepoint(self.mouse_pos):
        self.click_any = True
        for leader_index, this_leader in enumerate(self.leader_now):  # loop mouse pos on leader portrait
            if this_leader.rect.collidepoint(self.mouse_pos):
                army_position = self.leader_level[this_leader.role + 4]

                self.single_text_popup.pop(self.mouse_pos,
                                      army_position + ": " + this_leader.name)  # popup leader name when mouse over
                self.battle_ui_updater.add(self.single_text_popup)

                if mouse_left_up:  # open list of leader to change leader in that slot
                    self.selected_leader = leader_index
                    self.popup_list_open(this_leader.rect.midright, self.leader_list, "leader", "topleft",
                                         self.battle_ui_updater)

                elif mouse_right_up:
                    self.popout_lorebook(8, this_leader.leader_id)
                break

    elif self.troop_card_ui.rect.collidepoint(self.mouse_pos):
        self.click_any = True
        if self.subunit_in_card is not None and mouse_left_up:
            self.troop_card_button_click(self.subunit_in_card)

        if self.troop_card_ui.option == 2:
            for icon_list in (self.effect_icon, self.skill_icon):
                if self.effect_icon_mouse_over(self.skill_icon, mouse_right_up):
                    pass
                elif self.effect_icon_mouse_over(self.effect_icon, mouse_right_up):
                    pass

    elif mouse_left_up or mouse_left_down or mouse_right_up:  # left click for select, hold left mouse for scrolling, right click for encyclopedia
        if mouse_left_up or mouse_left_down:
            if self.popup_list_box in self.battle_ui_updater:
                if self.popup_list_box.rect.collidepoint(self.mouse_pos):
                    self.click_any = True
                    for index, name in enumerate(self.popup_namegroup):
                        if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # click on name in list
                            if self.popup_list_box.type == "terrain":
                                self.terrain_change_button.change_text(self.battle_map_base.terrain_list[index])
                                self.base_terrain = index
                                self.editor_map_change(battlemap.terrain_colour[self.base_terrain],
                                                       battlemap.feature_colour[self.feature_terrain])

                            elif self.popup_list_box.type == "feature":
                                self.feature_change_button.change_text(self.battle_map_feature.feature_list[index])
                                self.feature_terrain = index
                                self.editor_map_change(battlemap.terrain_colour[self.base_terrain],
                                                       battlemap.feature_colour[self.feature_terrain])

                            elif self.popup_list_box.type == "weather":
                                self.weather_type = int(index / 3)
                                self.weather_strength = index - (self.weather_type * 3)
                                self.weather_change_button.change_text(self.weather_list[index])
                                self.current_weather.__init__(self.time_ui, self.weather_type + 1,
                                                              self.weather_strength, self.weather_data)

                            if self.subunit_in_card is not None:  # reset subunit card as well
                                self.command_ui.value_input(who=self.subunit_in_card)
                                self.troop_card_ui.value_input(who=self.subunit_in_card, change_option=1)
                                if self.troop_card_ui.option == 2:
                                    self.trait_skill_icon_blit()
                                    self.effect_icon_blit()
                                    self.countdown_skill_icon()

                            for this_name in self.popup_namegroup:  # remove troop name list
                                this_name.kill()
                                del this_name

                            self.battle_ui_updater.remove(self.popup_list_box, self.popup_list_box.scroll)
                            break

                elif self.popup_list_box.scroll.rect.collidepoint(self.mouse_pos):  # scrolling on list
                    self.click_any = True
                    self.current_pop_up_row = self.popup_list_box.scroll.player_input(
                        self.mouse_pos)  # update the scroll and get new current subsection
                    if self.popup_list_box.type == "terrain":
                        setup_list(self.screen_scale, menu.NameList, self.current_pop_up_row,
                                   self.battle_map_base.terrain_list,
                                   self.popup_namegroup, self.popup_list_box, self.battle_ui_updater, layer=17)
                    elif self.popup_list_box.type == "feature":
                        setup_list(self.screen_scale, menu.NameList, self.current_pop_up_row,
                                   self.battle_map_feature.feature_list,
                                   self.popup_namegroup, self.popup_list_box, self.battle_ui_updater, layer=17)
                    elif self.popup_list_box.type == "weather":
                        setup_list(self.screen_scale, menu.NameList, self.current_pop_up_row, self.weather_list,
                                   self.popup_namegroup,
                                   self.popup_list_box, self.battle_ui_updater, layer=17)
                    elif self.popup_list_box.type == "leader":
                        setup_list(self.screen_scale, menu.NameList, self.current_pop_up_row, self.leader_list,
                                   self.popup_namegroup,
                                   self.popup_list_box, self.battle_ui_updater, layer=19)

                else:
                    self.battle_ui_updater.remove(self.popup_list_box, self.popup_list_box.scroll,
                                                  *self.popup_namegroup)

            elif self.editor_troop_list_box.scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
                self.click_any = True
                self.current_troop_row = self.editor_troop_list_box.scroll.player_input(
                    self.mouse_pos)  # update the scroll and get new current subsection
                if self.current_list_show == "troop":
                    setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                               self.troop_namegroup,
                               self.editor_troop_list_box, self.battle_ui_updater)
                elif self.current_list_show == "faction":
                    setup_list(self.screen_scale, menu.NameList, self.current_troop_row,
                               self.faction_data.faction_name_list,
                               self.troop_namegroup,
                               self.editor_troop_list_box, self.battle_ui_updater)

            elif self.unit_preset_list_box.scroll.rect.collidepoint(self.mouse_pos):
                self.click_any = True
                self.current_unit_row = self.unit_preset_list_box.scroll.player_input(
                    self.mouse_pos)  # update the scroll and get new current subsection
                setup_list(self.screen_scale, menu.NameList, self.current_unit_row,
                           list(self.custom_unit_preset_list.keys()),
                           self.unitpreset_namegroup, self.unit_preset_list_box,
                           self.battle_ui_updater)  # setup preset army list

            elif self.subunit_build in self.battle_ui_updater:
                clicked_slot = None
                for slot in self.subunit_build:  # left click on any sub-subunit slot
                    if slot.rect.collidepoint(self.mouse_pos):
                        self.click_any = True
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
                                        self.battle_ui_updater.add(*self.unit_edit_border)
                                elif first_one is not None and new_slot.game_id > first_one and new_slot.selected is False:  # select from first select to clicked
                                    new_slot.selected = True
                                    self.unit_edit_border.add(
                                        battleui.SelectedSquad(new_slot.inspect_pos, 5))
                                    self.battle_ui_updater.add(*self.unit_edit_border)

                    elif key_state[pygame.K_LCTRL] or key_state[
                        pygame.K_RCTRL]:  # add another selected sub-subunit with left ctrl + left mouse button
                        if clicked_slot.selected is False:
                            clicked_slot.selected = True
                            self.unit_edit_border.add(battleui.SelectedSquad(clicked_slot.inspect_pos, 5))
                            self.battle_ui_updater.add(*self.unit_edit_border)

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
                        self.battle_ui_updater.add(*self.unit_edit_border)

                        if clicked_slot.name != "None":
                            self.battle_ui_updater.remove(*self.leader_now)
                            self.leader_now = [this_leader for this_leader in self.preview_leader]
                            self.battle_ui_updater.add(*self.leader_now)  # add leader portrait to draw
                            self.subunit_in_card = slot
                            self.command_ui.value_input(who=self.subunit_in_card)
                            self.troop_card_ui.value_input(
                                who=self.subunit_in_card)  # update subunit card on selected subunit
                            if self.troop_card_ui.option == 2:
                                self.trait_skill_icon_blit()
                                self.effect_icon_blit()
                                self.countdown_skill_icon()

        if mouse_left_up or mouse_right_up:
            if self.subunit_build in self.battle_ui_updater and self.editor_troop_list_box.rect.collidepoint(
                    self.mouse_pos):
                self.click_any = True
                for index, name in enumerate(self.troop_namegroup):
                    if name.rect.collidepoint(self.mouse_pos):
                        if self.current_list_show == "faction":
                            self.current_troop_row = 0

                            if mouse_left_up:
                                self.faction_pick = index
                                self.filter_troop_list()
                                if index != 0:  # pick faction
                                    self.leader_list = [item[1]["Name"] for this_index, item in
                                                        enumerate(self.leader_data.leader_list.items())
                                                        if this_index > 0 and (item[1]["Name"] == "None" or
                                                                               (item[0] >= 10000 and item[1][
                                                                                   "Faction"] in (0, index)) or
                                                                               item[0] in
                                                                               self.faction_data.faction_list[index][
                                                                                   "Leader"])]

                                else:  # pick all faction
                                    self.leader_list = self.leader_list = [item[0] for item in
                                                                           self.leader_data.leader_list.values()][1:]

                                setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                                           self.troop_namegroup,
                                           self.editor_troop_list_box, self.battle_ui_updater)  # setup troop name list
                                self.editor_troop_list_box.scroll.change_image(new_row=self.current_troop_row,
                                                                               row_size=len(
                                                                                   self.troop_list))  # change troop scroll image

                                self.main.create_team_coa([index], ui_class=self.battle_ui_updater, one_team=True,
                                                          team1_set_pos=(
                                                              self.editor_troop_list_box.rect.midleft[0] - int(
                                                                  (200 * self.screen_scale[0]) / 2),
                                                              self.editor_troop_list_box.rect.midleft[
                                                                  1]))  # change team coa_list

                                self.current_list_show = "troop"

                            elif mouse_right_up:
                                self.popout_lorebook(2, index)

                        elif self.current_list_show == "troop":
                            if mouse_left_up:
                                for slot in self.subunit_build:
                                    if slot.selected:
                                        if key_state[pygame.K_LSHIFT]:  # change all sub-subunit in army
                                            for new_slot in self.subunit_build:
                                                slot.kill()
                                                slot.__init__(self.troop_index_list[index + self.current_troop_row],
                                                              new_slot.game_id, self.unit_build_slot, slot.pos,
                                                              100, 100, [1, 1], self.genre, "edit")
                                                slot.kill()
                                                self.subunit_build.add(slot)
                                                self.battle_ui_updater.add(slot)
                                        else:
                                            slot.kill()
                                            slot.__init__(self.troop_index_list[index + self.current_troop_row],
                                                          slot.game_id, self.unit_build_slot, slot.pos,
                                                          100, 100, [1, 1], self.genre, "edit")
                                            slot.kill()
                                            self.subunit_build.add(slot)
                                            self.battle_ui_updater.add(slot)

                                        if slot.name != "None":  # update information of subunit that just got changed
                                            self.battle_ui_updater.remove(*self.leader_now)
                                            self.leader_now = [this_leader for this_leader in self.preview_leader]
                                            self.battle_ui_updater.add(*self.leader_now)  # add leader portrait to draw
                                            self.subunit_in_card = slot
                                            self.preview_authority(self.leader_now)
                                            self.troop_card_ui.value_input(
                                                who=self.subunit_in_card)  # update subunit card on selected subunit
                                            if self.troop_card_ui.option == 2:
                                                self.trait_skill_icon_blit()
                                                self.effect_icon_blit()
                                                self.countdown_skill_icon()
                                        elif slot.name == "None" and slot.leader is not None:  # remove leader from none subunit if any
                                            slot.leader.change_preview_leader(1, self.leader_data)
                                            slot.leader.change_subunit(None)  # remove subunit link in leader
                                            slot.leader = None  # remove leader link in subunit
                                            self.preview_authority(self.leader_now)
                                unit_dict = self.convert_unit_slot_to_dict("test")
                                if unit_dict is not None and unit_dict['test'][-1] == "0":
                                    self.warning_msg.warning([self.warning_msg.multi_faction_warn])
                                    self.battle_ui_updater.add(self.warning_msg)

                            elif mouse_right_up:  # open encyclopedia
                                self.popout_lorebook(3, self.troop_index_list[index + self.current_troop_row])
                        break

            elif self.filter_box.rect.collidepoint(self.mouse_pos):
                self.click_any = True
                if mouse_left_up:
                    if self.team_change_button.rect.collidepoint(self.mouse_pos):
                        if self.team_change_button.event == 0:
                            self.team_change_button.event = 1

                        elif self.team_change_button.event == 1:
                            self.team_change_button.event = 0

                        self.unit_build_slot.team = self.team_change_button.event + 1

                        for slot in self.subunit_build:
                            show = False
                            if slot in self.battle_ui_updater:
                                show = True
                            slot.kill()
                            slot.__init__(slot.troop_id, slot.game_id, self.unit_build_slot, slot.pos,
                                          100, 100, [1, 1], self.genre, "edit")
                            slot.kill()
                            self.subunit_build.add(slot)
                            if show:  # has ui showing
                                self.battle_ui_updater.add(slot)
                            self.command_ui.value_input(
                                who=slot)  # loop value input so it changes team correctly

                    elif self.slot_display_button.rect.collidepoint(self.mouse_pos):
                        if self.slot_display_button.event == 0:  # hide
                            self.slot_display_button.event = 1
                            self.battle_ui_updater.remove(self.unit_setup_stuff, self.leader_now)
                            self.kill_effect_icon()

                        elif self.slot_display_button.event == 1:  # show
                            self.slot_display_button.event = 0
                            self.battle_ui_updater.add(self.unit_setup_stuff, self.leader_now)

                    elif self.deploy_button.rect.collidepoint(
                            self.mouse_pos) and self.subunit_build in self.battle_ui_updater:
                        can_deploy = True
                        subunit_count = 0
                        warning_list = []
                        for slot in self.subunit_build:
                            if slot.troop_id != 0:
                                subunit_count += 1
                        if subunit_count < 8:
                            can_deploy = False
                            warning_list.append(self.warning_msg.min_subunit_warn)
                        if self.leader_now == [] or self.preview_leader[0].name == "None":
                            can_deploy = False
                            warning_list.append(self.warning_msg.min_leader_warn)

                        if can_deploy:
                            unit_game_id = 0
                            if len(self.all_team_unit["alive"]) > 0:
                                unit_game_id = self.all_team_unit["alive"][-1].game_id + 1
                            current_preset = self.convert_unit_slot_to_dict(self.unit_preset_name,
                                                                            [str(int(self.base_camera_pos[0] /
                                                                                     self.screen_scale[0])),
                                                                             str(int(self.base_camera_pos[1] /
                                                                                     self.screen_scale[1]))],
                                                                            unit_game_id)
                            subunit_game_id = 0
                            if len(self.subunit) > 0:
                                for this_subunit in self.subunit:
                                    subunit_game_id = this_subunit.game_id
                                subunit_game_id = subunit_game_id + 1
                            for slot in self.subunit_build:  # just for grabbing current selected team
                                current_preset[self.unit_preset_name] += (0, 100, 100, slot.team)
                                self.unit_editor_convert(self.all_team_unit[slot.team],
                                                         current_preset[self.unit_preset_name], team_colour[slot.team],
                                                         pygame.transform.scale(
                                                             self.coa_list[
                                                                 int(current_preset[self.unit_preset_name][-1])],
                                                             (60, 60)), subunit_game_id)
                                break
                            self.slot_display_button.event = 1
                            self.kill_effect_icon()
                            self.unit_selector.setup_unit_icon(self.unit_icon, self.all_team_unit[self.team_selected])
                            self.battle_ui_updater.remove(self.unit_setup_stuff, self.leader_now)
                            for this_unit in self.battle.all_team_unit["alive"]:
                                this_unit.start_set(self.subunit)
                            for this_leader in self.leader_updater:
                                this_leader.start_set()
                            for this_subunit in self.subunit:
                                this_subunit.start_set(self.camera_zoom, self.subunit_animation_pool)

                            for this_unit in self.battle.all_team_unit["alive"]:
                                this_unit.player_input(self.command_mouse_pos, other_command=1)
                        else:
                            self.warning_msg.warning(warning_list)
                            self.battle_ui_updater.add(self.warning_msg)
                    else:
                        for box in self.filter_tick_box:
                            if box in self.battle_ui_updater and box.rect.collidepoint(self.mouse_pos):
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
                                    setup_list(self.screen_scale, menu.NameList, self.current_troop_row,
                                               self.troop_list,
                                               self.troop_namegroup,
                                               self.editor_troop_list_box,
                                               self.battle_ui_updater)  # setup troop name list
            elif self.terrain_change_button.rect.collidepoint(
                    self.mouse_pos) and mouse_left_up:  # change map terrain button
                self.click_any = True
                self.popup_list_open(self.terrain_change_button.rect.midtop, self.battle_map_base.terrain_list,
                                         "terrain", "midbottom", self.battle_ui_updater)

            elif self.feature_change_button.rect.collidepoint(
                    self.mouse_pos) and mouse_left_up:  # change map feature button
                self.click_any = True
                self.popup_list_open(self.feature_change_button.rect.midtop, self.battle_map_feature.feature_list,
                                         "feature", "midbottom", self.battle_ui_updater)

            elif self.weather_change_button.rect.collidepoint(
                    self.mouse_pos) and mouse_left_up:  # change map weather button
                self.click_any = True
                self.popup_list_open(self.weather_change_button.rect.midtop, self.weather_list, "weather", "midbottom",
                                     self.battle_ui_updater)

            elif self.unit_delete_button.rect.collidepoint(self.mouse_pos) and mouse_left_up and \
                    self.unit_delete_button in self.battle_ui_updater:  # delete preset button
                self.click_any = True
                if self.unit_preset_name == "":
                    pass
                else:
                    self.input_popup = ("confirm_input", "delete_preset")
                    self.confirm_ui.change_instruction("Delete Selected Preset?")
                    self.battle_ui_updater.add(*self.confirm_ui_popup)

            elif self.unit_save_button.rect.collidepoint(self.mouse_pos) and mouse_left_up and \
                    self.unit_save_button in self.battle_ui_updater:  # save preset button
                self.click_any = True
                self.input_popup = ("text_input", "save_unit")

                if self.unit_preset_name == "":
                    self.input_box.text_start("")
                else:
                    self.input_box.text_start(self.unit_preset_name)

                self.input_ui.change_instruction("Preset Name:")
                self.battle_ui_updater.add(*self.input_ui_popup)

            elif self.warning_msg in self.battle_ui_updater and self.warning_msg.rect.collidepoint(self.mouse_pos):
                self.battle_ui_updater.remove(self.warning_msg)

            elif self.team_coa in self.battle_ui_updater:
                for team in self.team_coa:
                    if team.rect.collidepoint(self.mouse_pos) and mouse_left_up:
                        self.click_any = True
                        if self.current_list_show == "troop":
                            self.current_troop_row = 0
                            setup_list(self.screen_scale, menu.NameList, self.current_troop_row,
                                       self.faction_data.faction_name_list,
                                       self.troop_namegroup,
                                       self.editor_troop_list_box, self.battle_ui_updater)
                            self.editor_troop_list_box.scroll.change_image(new_row=self.current_troop_row,
                                                                           row_size=len(
                                                                               self.faction_data.faction_name_list))  # change troop scroll image
                            self.current_list_show = "faction"
