from gamescript import battleui
from gamescript.common import utility

change_group = utility.change_group


def setup_battle_ui(self, change):
    """Change can be either 'add' or 'remove' for adding or removing ui"""
    if change == "add":
        self.unitstat_ui.change_pos((self.screen_rect.width - self.unitstat_ui.image.get_width() / 2,
                                     self.unitstat_ui.image.get_height() / 2))
        self.inspect_button.change_pos(
            (self.unitstat_ui.rect.topleft[0] - (self.inspect_button.image.get_width() / 2), self.unitstat_ui.pos[1]))

        self.inspect_ui.change_pos((self.screen_rect.width - self.inspect_ui.image.get_width() / 2,
                                    self.unitstat_ui.image.get_height() + (self.inspect_ui.image.get_height() / 2)))

        self.troop_card_ui.change_pos((self.inspect_ui.rect.bottomleft[0] + self.troop_card_ui.image.get_width() / 2,
                                       (self.inspect_ui.rect.bottomleft[
                                            1] + self.troop_card_ui.image.get_height() / 2)))

        self.time_ui.change_pos(self.unit_selector.rect.topright, self.time_number, speed_number=self.speed_number)
        self.time_button[0].change_pos((self.time_ui.rect.center[0] - self.time_button[0].image.get_width(),
                                        self.time_ui.rect.center[1]))  # time pause button
        self.time_button[1].change_pos(
            (self.time_ui.rect.center[0], self.time_ui.rect.center[1]))  # time decrease button
        self.time_button[2].change_pos((self.time_ui.rect.midright[0] - self.time_button[2].image.get_width() * 2,
                                        self.time_ui.rect.center[1]))  # time increase button

        self.battle_scale_ui.change_pos(self.time_ui.rect.bottomleft)
        self.test_button.change_pos((self.battle_scale_ui.rect.bottomleft[0] + (self.test_button.image.get_width() / 2),
                                     self.battle_scale_ui.rect.bottomleft[1] + (
                                                 self.test_button.image.get_height() / 2)))
        self.warning_msg.change_pos(self.test_button.rect.bottomleft)

        self.command_ui.change_pos((self.command_ui.image.get_size()[0] / 2,
                                    (self.command_ui.image.get_size()[1] / 2) + self.unit_selector.image.get_height()))

        self.col_split_button.change_pos(
            (self.command_ui.rect.midleft[0] + (self.col_split_button.image.get_width() / 2),
             self.command_ui.rect.midleft[1]))
        self.row_split_button.change_pos(
            (self.command_ui.rect.midleft[0] + (self.row_split_button.image.get_width() / 2),
             self.command_ui.rect.midleft[1] + (self.col_split_button.image.get_height() * 3)))
        # self.decimation_button.change_pos(
        #     (self.command_ui.rect.midleft[0] + (self.decimation_button.image.get_width() / 2),
        #      self.command_ui.rect.midleft[1] + (self.decimation_button.image.get_height() * 2)))

        self.behaviour_switch_button[0].change_pos(
            (self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[0].image.get_width()),
             self.command_ui.rect.bottomleft[1] - (
                         self.behaviour_switch_button[0].image.get_height() / 2)))  # skill condition button
        self.behaviour_switch_button[1].change_pos(
            (self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[1].image.get_width() * 2),
             self.command_ui.rect.bottomleft[1] - (
                         self.behaviour_switch_button[1].image.get_height() / 2)))  # fire at will button
        self.behaviour_switch_button[2].change_pos(
            (self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[2].image.get_width() * 3),
             self.command_ui.rect.bottomleft[1] - (
                         self.behaviour_switch_button[2].image.get_height() / 2)))  # behaviour button
        self.behaviour_switch_button[3].change_pos(
            (self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[3].image.get_width() * 4),
             self.command_ui.rect.bottomleft[1] - (
                         self.behaviour_switch_button[3].image.get_height() / 2)))  # shoot range button
        self.behaviour_switch_button[4].change_pos(
            (self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[4].image.get_width() * 5),
             self.command_ui.rect.bottomleft[1] - (
                         self.behaviour_switch_button[4].image.get_height() / 2)))  # arc_shot button
        self.behaviour_switch_button[5].change_pos(
            (self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[5].image.get_width() * 6),
             self.command_ui.rect.bottomleft[1] - (
                         self.behaviour_switch_button[5].image.get_height() / 2)))  # toggle run button
        self.behaviour_switch_button[6].change_pos(
            (self.command_ui.rect.bottomleft[0] + (self.behaviour_switch_button[6].image.get_width() * 7),
             self.command_ui.rect.bottomleft[1] - (
                         self.behaviour_switch_button[6].image.get_height() / 2)))  # toggle melee mode

        self.event_log_button[0].change_pos((self.event_log.pos[0] + (self.event_log_button[0].image.get_width() / 2),
                                             self.event_log.pos[1] - self.event_log.image.get_height() - (
                                                         self.event_log_button[0].image.get_height() / 2)))
        self.event_log_button[1].change_pos(
            (self.event_log_button[0].pos[0] + self.event_log_button[0].image.get_width(),
             self.event_log_button[0].pos[1]))  # army tab log button
        self.event_log_button[2].change_pos(
            (self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 2),
             self.event_log_button[0].pos[1]))  # leader tab log button
        self.event_log_button[3].change_pos(
            (self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 3),
             self.event_log_button[0].pos[1]))  # subunit tab log button
        self.event_log_button[4].change_pos(
            (self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 5),
             self.event_log_button[0].pos[1]))  # delete current tab log button
        self.event_log_button[5].change_pos(
            (self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 6),
             self.event_log_button[0].pos[1]))  # delete all log button

        width = self.unitstat_ui.rect.bottomleft[0] - self.subunit_inspect_sprite_size[0] / 1.25
        height = self.unitstat_ui.rect.bottomleft[1]
        sub_unit_number = 0  # Number of subunit based on the position in row and column
        for _ in list(range(0, self.main.unit_size[0] * self.main.unit_size[1])):
            width += self.subunit_inspect_sprite_size[0]
            self.inspect_subunit.append(battleui.InspectSubunit((width, height)))
            sub_unit_number += 1
            if sub_unit_number == self.main.unit_size[0]:  # Reach the last subunit in the row, go to the next one
                width = self.unitstat_ui.rect.bottomleft[0] - self.subunit_inspect_sprite_size[0] / 1.25
                height += self.subunit_inspect_sprite_size[1]
                sub_unit_number = 0

    change_group(self.unit_selector, self.battle_ui_updater, change)
    change_group(self.unit_selector.scroll, self.battle_ui_updater, change)

    change_group(self.col_split_button, self.button_ui, change)
    change_group(self.row_split_button, self.button_ui, change)
    change_group(self.time_button, self.battle_ui_updater, change)
    change_group(self.battle_scale_ui, self.battle_ui_updater, change)
