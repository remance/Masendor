from math import cos, sin, radians

from pygame import Vector2


def player_aim(self):
    """
    Manual player aim control for range attack
    """
    shoot_text = ""
    shoot_ready = [0, 0]
    has_ammo = [0, 0]
    shoot_ready_list = [[], []]
    self.add_ui_updater(self.single_text_popup)
    base_target_pos = self.command_cursor_pos
    target_pos = self.base_cursor_pos

    who_shoot = ()
    if self.player_input_state == "leader aim":
        who_shoot = (self.player_unit,)
    elif self.player_input_state == "line aim" or self.player_input_state == "focus aim":
        who_shoot = self.player_unit.alive_troop_follower

    for this_unit in who_shoot:
        can_shoot = [False, False]
        this_unit.manual_shoot = True
        if this_unit.in_melee_combat_timer == 0 and "uncontrollable" not in this_unit.current_action and \
                "uncontrollable" not in this_unit.command_action and "weapon" not in this_unit.current_action and \
                "weapon" not in this_unit.command_action:

            if self.player_input_state == "line aim":
                angle = self.player_unit.set_rotate(self.command_cursor_pos)
                distance = self.player_unit.base_pos.distance_to(self.command_cursor_pos)
                base_target_pos = Vector2(this_unit.base_pos[0] - (distance * sin(radians(angle))),
                                          this_unit.base_pos[1] - (distance * cos(radians(angle))))
                target_pos = (base_target_pos[0] * 5 * self.screen_scale[0],
                              base_target_pos[1] * 5 * self.screen_scale[1])

            for weapon in (0, 1):
                if this_unit.equipped_weapon in this_unit.ammo_now:
                    if weapon in this_unit.ammo_now[this_unit.equipped_weapon]:
                        has_ammo[weapon] += 1
                        if this_unit.ammo_now[this_unit.equipped_weapon][weapon] > 0 and \
                                this_unit.shoot_range[weapon] >= this_unit.base_pos.distance_to(
                            base_target_pos) and \
                                ((this_unit.move_speed and this_unit.shoot_while_moving and
                                  not this_unit.check_special_effect("Stationary", weapon=weapon)) or
                                 not this_unit.move_speed):
                            shoot_ready_list[weapon].append(this_unit)
                            shoot_ready[weapon] += 1
                            can_shoot[weapon] = True

        if True in can_shoot:
            if this_unit.shoot_line not in self.battle_camera:  # add back shoot line
                self.battle_camera.add(this_unit.shoot_line)
            this_unit.shoot_line.update(base_target_pos, target_pos, can_shoot)
        else:  # no weapon in current equipped weapon set
            if this_unit.shoot_line in self.battle_camera:  # remove shoot line
                self.battle_camera.remove(this_unit.shoot_line)

        shoot_text = str(shoot_ready[0]) + "/" + str(has_ammo[0]) + ", " + str(shoot_ready[1]) + "/" + str(has_ammo[1])

    self.single_text_popup.popup(self.player1_battle_cursor.rect, shoot_text)

    if self.player1_key_press["Order Menu"] or not self.player_unit.alive:
        # Cancel manual aim with order menu input or player die
        self.player_cancel_input()

    elif self.player1_key_press["Main Weapon Attack"] or self.player1_key_press["Sub Weapon Attack"]:
        weapon = 0
        if self.player1_key_press["Sub Weapon Attack"]:
            weapon = 1
        if shoot_ready[weapon] > 0:
            for this_unit in shoot_ready_list[weapon]:
                if "movable" in this_unit.current_action and "charge" not in this_unit.current_action:
                    # shoot while moving
                    this_unit.show_frame = 0  # just restart frame
                    if "walk" in this_unit.current_action:
                        this_unit.current_action = this_unit.range_walk_command_action[weapon]
                    elif "run" in this_unit.current_action:
                        this_unit.current_action = this_unit.range_run_command_action[weapon]
                else:
                    this_unit.new_angle = this_unit.set_rotate(this_unit.shoot_line.base_target_pos)
                    this_unit.command_action = this_unit.range_attack_command_action[weapon]
                    this_unit.attack_pos = this_unit.shoot_line.base_target_pos

    else:
        self.camera_process()
        self.player_unit.player_input(self.command_cursor_pos)
