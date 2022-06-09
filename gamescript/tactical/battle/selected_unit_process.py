import pygame

from gamescript import weather, menu, battleui, unit
from gamescript.common import utility

list_scroll = utility.list_scroll
setup_list = utility.setup_list

team_colour = unit.team_colour


def selected_unit_process(self, mouse_left_up, mouse_right_up, double_mouse_right, mouse_left_down, mouse_right_down, key_state, key_press):
    if self.current_selected is not None:
        if self.game_state == "battle" and self.current_selected.state != 100:
            if self.before_selected is None:  # add back the pop-up ui, so it gets shown when click subunit with none selected before
                self.battle_ui_updater.add(self.unitstat_ui, self.command_ui)  # add leader and top ui
                self.battle_ui_updater.add(self.inspect_button)  # add inspection ui open/close button

                self.add_behaviour_ui(self.current_selected)

            elif self.before_selected != self.current_selected or self.split_happen:  # change subunit information when select other unit
                if self.inspect:  # change inspect ui
                    self.new_unit_click = True
                    self.battle_ui_updater.remove(*self.inspect_subunit)

                    self.change_inspect_subunit()

                    self.inspect_selected_border.pop(self.subunit_selected.pos)
                    self.battle_ui_updater.add(self.inspect_selected_border)
                    self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_data=self.weapon_data,
                                                   armour_data=self.armour_data,
                                                   split=self.split_happen)
                self.battle_ui_updater.remove(*self.leader_now)

                self.add_behaviour_ui(self.current_selected, else_check=True)

                if self.split_happen:  # end split check
                    self.split_happen = False

            else:  # Update unit stat ui and command ui value every 1.1 seconds
                if self.ui_timer >= 1.1:
                    self.unitstat_ui.value_input(who=self.current_selected, split=self.split_happen)
                    self.command_ui.value_input(who=self.current_selected, split=self.split_happen)

        elif self.game_state == "editor" and self.subunit_build not in self.battle_ui_updater:
            if (mouse_right_up or mouse_right_down) and self.click_any is False:  # Unit placement
                self.current_selected.placement(self.command_mouse_pos, mouse_right_up, mouse_right_down, double_mouse_right)

            if key_state[pygame.K_DELETE]:
                for this_unit in self.troop_number_sprite:
                    if this_unit.who == self.current_selected:
                        this_unit.delete()
                        this_unit.kill()
                        del this_unit
                for this_subunit in self.current_selected.subunit_list:
                    this_subunit.delete()
                    self.alive_subunit_list.remove(this_subunit)
                    this_subunit.kill()
                    del this_subunit
                for this_leader in self.current_selected.leader:
                    this_leader.delete()
                    this_leader.kill()
                    del this_leader
                del self.team_pos_list[self.current_selected.team][self.current_selected]
                self.current_selected.delete()
                self.current_selected.kill()
                self.all_team_unit["alive"].remove(self.current_selected)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.all_team_unit[self.team_selected])
                self.current_selected = None

    # v Update value of the clicked subunit every 1.1 second
    if self.game_state == "battle" and self.inspect and ((self.ui_timer >= 1.1 and self.troop_card_ui.option != 0) or
                                                         self.before_selected != self.current_selected):
        self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_data=self.weapon_data, armour_data=self.armour_data,
                                       split=self.split_happen)
        if self.troop_card_ui.option == 2:  # skill and status effect card
            self.countdown_skill_icon()
            self.effect_icon_blit()
            if self.before_selected != self.current_selected:  # change subunit, reset trait icon as well
                self.trait_skill_icon_blit()
                self.countdown_skill_icon()
        else:
            self.kill_effect_icon()

    self.before_selected = self.current_selected
