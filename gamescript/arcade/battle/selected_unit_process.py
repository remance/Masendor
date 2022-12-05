import pygame

from gamescript import unit
from gamescript.common import utility

list_scroll = utility.list_scroll
setup_list = utility.setup_list
clean_object = utility.clean_object

team_colour = unit.team_colour


def selected_unit_process(self, mouse_left_up, mouse_right_up, double_mouse_right, mouse_left_down, mouse_right_down,
                          key_state, key_press):
    if self.current_selected is not None:
        if self.game_state == "battle" and self.current_selected.state != 100:
            if self.before_selected is None:  # add the unit ui, so it gets shown if not show before
                self.change_inspect_subunit()
                self.battle_ui_updater.add(self.inspect_ui, self.inspect_subunit)  # add leader and top ui

                # self.add_behaviour_ui(self.current_selected)

            elif self.before_selected != self.current_selected:  # change subunit information when select other unit
                if self.inspect:  # change inspect ui
                    self.new_unit_click = True

                    self.subunit_selected = None
                    self.change_inspect_subunit()

                    self.inspect_selected_border.pop(self.subunit_selected.pos)
                    self.battle_ui_updater.add(self.inspect_selected_border)
                    self.troop_card_ui.value_input(who=self.subunit_selected.who)
                self.battle_ui_updater.remove(*self.leader_now)

                self.add_behaviour_ui(self.current_selected, else_check=True)

            else:  # Update unit stat ui and command ui value every 1.1 seconds
                if self.ui_timer >= 1.1:
                    who_in_command_ui = self.current_selected
                    if self.command_ui.ui_type == "hero":
                        who_in_command_ui = self.player_char
                    self.command_ui.value_input(who=who_in_command_ui)

        elif self.game_state == "editor" and self.subunit_build not in self.battle_ui_updater:
            if (mouse_right_up or mouse_right_down) and self.click_any is False:  # Unit placement
                self.current_selected.placement(self.command_mouse_pos, mouse_right_up, mouse_right_down,
                                                double_mouse_right)

            if key_state[pygame.K_DELETE]:
                for this_unit in self.troop_number_sprite:
                    if this_unit.who == self.current_selected:
                        clean_object(this_unit)
                for this_subunit in self.current_selected.subunit_list:
                    clean_object(this_subunit)
                for this_leader in self.current_selected.leader:
                    clean_object(this_leader)
                del self.team_pos_list[self.current_selected.team][self.current_selected]
                self.all_team_unit["alive"].remove(self.current_selected)
                clean_object(self.current_selected)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.all_team_unit[self.team_selected])
                self.current_selected = None

    # Update value of the clicked subunit every 1.1 second
    if self.game_state == "battle" and self.inspect and ((self.ui_timer >= 1.1 and self.troop_card_ui.option != 0) or
                                                         self.before_selected != self.current_selected):
        self.troop_card_ui.value_input(who=self.subunit_selected.who)
        if self.troop_card_ui.option == 2:  # skill and status effect card
            self.countdown_skill_icon()
            self.effect_icon_blit()
            if self.before_selected != self.current_selected:  # change subunit, reset trait icon as well
                self.trait_skill_icon_blit()
                self.countdown_skill_icon()
        else:
            self.kill_effect_icon()

    self.before_selected = self.current_selected
