import math

import pygame


def manual_aim(self, mouse_left_up, mouse_right_up, key_state, key_press):
    """
    Range attack aim with player manual control.
    """
    shoot_text = ""
    shoot_ready = [0, 0]
    has_ammo = [0, 0]
    shoot_ready_list = [[], []]
    self.battle_ui_updater.add(self.single_text_popup)
    base_target_pos = self.command_mouse_pos
    target_pos = self.base_mouse_pos

    who_shoot = ()
    if self.player_input_state == "leader aim":
        who_shoot = (self.player_char,)
    elif self.player_input_state == "line aim" or self.player_input_state == "focus aim":
        who_shoot = self.player_char.alive_troop_follower

    for this_subunit in who_shoot:
        range_weapon_check = [False, False]
        can_shoot = [False, False]
        arc_shot = [False, False]
        if this_subunit.in_melee_combat_timer == 0 and "uncontrollable" not in this_subunit.current_action and \
                "uncontrollable" not in this_subunit.command_action and "weapon" not in this_subunit.current_action and \
                "weapon" not in this_subunit.command_action:
            this_subunit.manual_shoot = True

            if self.player_input_state == "line aim":
                angle = self.player_char.set_rotate(self.command_mouse_pos)
                distance = self.player_char.base_pos.distance_to(self.command_mouse_pos)
                base_target_pos = pygame.Vector2(
                    this_subunit.base_pos[0] - (distance * math.sin(math.radians(angle))),
                    this_subunit.base_pos[1] - (distance * math.cos(math.radians(angle))))
                target_pos = (base_target_pos[0] * 5 * self.screen_scale[0],
                              base_target_pos[1] * 5 * self.screen_scale[1])

            for weapon in (0, 1):
                if this_subunit.equipped_weapon in this_subunit.ammo_now:
                    if weapon in this_subunit.ammo_now[this_subunit.equipped_weapon]:
                        range_weapon_check[weapon] = True
                        has_ammo[weapon] += 1
                        if this_subunit.ammo_now[this_subunit.equipped_weapon][weapon] > 0:
                            if this_subunit.shoot_range[weapon] >= this_subunit.base_pos.distance_to(base_target_pos):
                                arc_shot[weapon] = this_subunit.check_special_effect("Arc Shot", weapon=weapon)
                                shoot_ready_list[weapon].append(this_subunit)
                                shoot_ready[weapon] += 1
                                can_shoot[weapon] = True

        if True in range_weapon_check:
            if this_subunit.shoot_line not in self.battle_camera:  # add back shoot line
                self.battle_camera.add(this_subunit.shoot_line)
            this_subunit.shoot_line.update(base_target_pos, target_pos, can_shoot)
        else:  # no weapon in current equipped weapon set
            if this_subunit.shoot_line in self.battle_camera:  # remove shoot line
                self.battle_camera.remove(this_subunit.shoot_line)

        shoot_text = str(shoot_ready[0]) + "/" + str(has_ammo[0]) + ", " + str(shoot_ready[1]) + "/" + str(has_ammo[1])

    self.single_text_popup.pop(self.cursor.rect.bottomright, shoot_text)

    if key_press == pygame.K_TAB or not self.player_char.alive:  # Cancel manual aim when move or player die
        if self.player_char.alive:
            self.camera_mode = "Follow"
        self.cursor.change_image("normal")
        self.battle_ui_updater.remove(self.single_text_popup)
        self.previous_player_input_state = self.player_input_state
        self.player_input_state = None
        for shoot_line in self.shoot_lines:
            shoot_line.delete()  # reset shoot guide lines

    elif mouse_left_up or mouse_right_up:
        weapon = 0
        if mouse_right_up:
            weapon = 1
        if shoot_ready[weapon] > 0:
            for this_subunit in shoot_ready_list[weapon]:
                this_subunit.new_angle = this_subunit.set_rotate(this_subunit.shoot_line.base_target_pos)
                this_subunit.command_action = this_subunit.range_attack_command_action[weapon]
                this_subunit.attack_pos = this_subunit.shoot_line.base_target_pos

    else:
        self.camera_process(key_state)
        self.player_char.player_input(self.command_mouse_pos)
