from gamescript import battleui
from gamescript.common import utility

from gamescript.common.ui import common_ui_selector

change_group = utility.change_group

setup_unit_icon = common_ui_selector.setup_unit_icon

def setup_battle_ui(self, change):
    """Change can be either 'add' or 'remove' for adding or removing ui"""
    if change == "add":
        self.unitstat_ui.change_pos((self.screen_rect.width - self.unitstat_ui.image.get_width() / 2,
                                     self.unitstat_ui.image.get_height() / 2))
        self.inspect_button.change_pos((self.unitstat_ui.rect.topleft[0] - (self.inspect_button.image.get_width() / 2), self.unitstat_ui.pos[1]))

        self.inspect_ui.change_pos((self.screen_rect.width - self.inspect_ui.image.get_width() / 2,
                                    self.unitstat_ui.image.get_height() + (self.inspect_ui.image.get_height() / 2)))

        self.troop_card_ui.change_pos((self.inspect_ui.rect.bottomleft[0] + self.troop_card_ui.image.get_width() / 2,
                                       (self.inspect_ui.rect.bottomleft[1] + self.troop_card_ui.image.get_height() / 2)))

        self.time_ui.change_pos(self.unit_selector.rect.topright, self.time_number, speed_number=self.speed_number)
        self.time_button[0].change_pos((self.time_ui.rect.center[0] - self.time_button[0].image.get_width(),
                                        self.time_ui.rect.center[1]))  # time pause button
        self.time_button[1].change_pos((self.time_ui.rect.center[0], self.time_ui.rect.center[1]))  # time decrease button
        self.time_button[2].change_pos((self.time_ui.rect.midright[0] - self.time_button[2].image.get_width() * 2,
                                        self.time_ui.rect.center[1]))  # time increase button

        self.scale_ui.change_pos(self.time_ui.rect.bottomleft)
        self.test_button.change_pos((self.scale_ui.rect.bottomleft[0] + (self.test_button.image.get_width() / 2),
                                    self.scale_ui.rect.bottomleft[1] + (self.test_button.image.get_height() / 2)))
        self.warning_msg.change_pos(self.test_button.rect.bottomleft)

        self.command_ui.change_pos((self.command_ui.image.get_size()[0] / 2,
                                    (self.command_ui.image.get_size()[1] / 2) + self.unit_selector.image.get_height()))

        self.col_split_button.change_pos((self.command_ui.rect.midleft[0] + (self.col_split_button.image.get_width() / 2),
                                          self.command_ui.rect.midleft[1]))
        self.row_split_button.change_pos((self.command_ui.rect.midleft[0] + (self.row_split_button.image.get_width() / 2),
                                          self.command_ui.rect.midleft[1] + (self.col_split_button.image.get_height() * 3)))
        self.decimation_button.change_pos((self.command_ui.rect.midleft[0] + (self.decimation_button.image.get_width() / 2),
                                           self.command_ui.rect.midleft[1] + (self.decimation_button.image.get_height() * 2)))

        self.behaviour_switch_button[0].change_pos((self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[0].image.get_width()),
                                                    self.command_ui.rect.bottomleft[1] - (self.behaviour_switch_button[0].image.get_height() / 2)))  # skill condition button
        self.behaviour_switch_button[1].change_pos((self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[1].image.get_width() * 2),
                                                    self.command_ui.rect.bottomleft[1] - (self.behaviour_switch_button[1].image.get_height() / 2)))  # fire at will button
        self.behaviour_switch_button[2].change_pos((self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[2].image.get_width() * 3),
                                                    self.command_ui.rect.bottomleft[1] - (self.behaviour_switch_button[2].image.get_height() / 2)))  # behaviour button
        self.behaviour_switch_button[3].change_pos((self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[3].image.get_width() * 4),
                                                    self.command_ui.rect.bottomleft[1] - (self.behaviour_switch_button[3].image.get_height() / 2)))  # shoot range button
        self.behaviour_switch_button[4].change_pos((self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[4].image.get_width() * 5),
                                                    self.command_ui.rect.bottomleft[1] - (self.behaviour_switch_button[4].image.get_height() / 2)))  # arc_shot button
        self.behaviour_switch_button[5].change_pos((self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[5].image.get_width() * 6),
                                                    self.command_ui.rect.bottomleft[1] - (self.behaviour_switch_button[5].image.get_height() / 2)))  # toggle run button
        self.behaviour_switch_button[6].change_pos((self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[6].image.get_width() * 7),
                                                    self.command_ui.rect.bottomleft[1] - (self.behaviour_switch_button[6].image.get_height() / 2)))  # toggle melee mode

        self.event_log_button[0].change_pos((self.event_log.pos[0] + (self.event_log_button[0].image.get_width() / 2),
                                             self.event_log.pos[1] - self.event_log.image.get_height() - (self.event_log_button[0].image.get_height() / 2)))
        self.event_log_button[1].change_pos((self.event_log_button[0].pos[0] + self.event_log_button[0].image.get_width(),
                                             self.event_log_button[0].pos[1]))  # army tab log button
        self.event_log_button[2].change_pos((self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 2),
                                             self.event_log_button[0].pos[1]))  # leader tab log button
        self.event_log_button[3].change_pos((self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 3),
                                             self.event_log_button[0].pos[1]))  # subunit tab log button
        self.event_log_button[4].change_pos((self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 5),
                                             self.event_log_button[0].pos[1]))  # delete current tab log button
        self.event_log_button[5].change_pos((self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 6),
                                             self.event_log_button[0].pos[1]))  # delete all log button

        inspect_ui_pos = [self.unitstat_ui.rect.bottomleft[0] - self.icon_sprite_width / 1.25,
                          self.unitstat_ui.rect.bottomleft[1]]
        width, height = inspect_ui_pos[0], inspect_ui_pos[1]
        sub_unit_number = 0  # Number of subunit based on the position in row and column
        imgsize = (self.icon_sprite_width, self.icon_sprite_height)
        for this_subunit in list(range(0, 64)):
            width += imgsize[0]
            self.inspect_subunit.append(battleui.InspectSubunit((width, height)))
            sub_unit_number += 1
            if sub_unit_number == 8:  # Reach the last subunit in the row, go to the next one
                width = inspect_ui_pos[0]
                height += imgsize[1]
                sub_unit_number = 0

    change_group(self.unit_selector, self.battle_ui_updater, change)
    change_group(self.unit_selector_scroll, self.battle_ui_updater, change)

    change_group(self.col_split_button, self.button_ui, change)
    change_group(self.row_split_button, self.button_ui, change)
    change_group(self.time_button, self.battle_ui_updater, change)
    change_group(self.scale_ui, self.battle_ui_updater, change)



def change_state(self):
    self.previous_game_state = self.game_state
    setup_unit_icon(self.unit_selector, self.unit_icon,
                    self.team_unit_dict[self.player_team_check], self.unit_selector_scroll)
    self.unit_selector_scroll.change_image(new_row=self.unit_selector.current_row)
    if self.game_state == "battle":  # change to battle state
        self.camera_mode = self.start_zoom_mode
        self.mini_map.draw_image(self.show_map.true_image, self.camera)

        if self.current_selected is not None:  # any unit is selected
            self.current_selected = None  # reset last_selected
            self.before_selected = None  # reset before selected unit after remove last selected

        self.command_ui.rect = self.command_ui.image.get_rect(
            center=self.command_ui.pos)  # change leader ui position back
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
        self.battle_ui_updater.add(self.event_log, self.log_scroll, self.event_log_button, self.time_button)

        self.game_speed = 1

        # Run starting method
        for this_unit in self.alive_unit_list:
            this_unit.start_set(self.subunit)
        for this_subunit in self.subunit:
            this_subunit.start_set(self.camera_zoom)
        for this_leader in self.leader_updater:
            this_leader.start_set()

    elif self.game_state == "editor":  # change to editor state
        self.camera_mode = "Free"
        self.inspect = False  # reset inspect ui
        self.mini_map.draw_image(self.show_map.true_image, self.camera)  # reset mini_map
        for arrow in self.range_attacks:  # remove all range melee_attack
            arrow.kill()
            del arrow

        for this_unit in self.alive_unit_list:  # reset all unit state
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

        self.battle_ui_updater.remove(self.event_log, self.log_scroll, self.troop_card_button, self.col_split_button, self.row_split_button,
                                      self.event_log_button, self.time_button, self.unitstat_ui, self.inspect_ui, self.leader_now, self.inspect_subunit,
                                      self.subunit_selected_border, self.inspect_button, self.behaviour_switch_button)

        self.leader_now = [this_leader for this_leader in self.preview_leader]  # reset leader in command ui
        self.battle_ui_updater.add(self.filter_stuff, self.unit_setup_stuff, self.test_button, self.command_ui, self.troop_card_ui, self.leader_now,
                                   self.time_button)
        self.slot_display_button.event = 0  # reset display editor ui button to show
        self.game_speed = 0  # pause battle

        for slot in self.subunit_build:
            if slot.troop_id != 0:
                self.command_ui.value_input(who=slot)
                break

    self.speed_number.speed_update(self.game_speed)
