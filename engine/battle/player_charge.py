from math import cos, sin, radians

from pygame import Vector2

from engine.uibattle.uibattle import AimTarget


def player_charge(self):
    """
    Manual player aim control for charge attack
    """
    base_target_pos = self.command_cursor_pos
    target_pos = self.base_cursor_pos

    who_charge = []
    can_charge = (True, True)
    for this_unit in self.player_unit.alive_troop_follower:
        if this_unit.in_melee_combat_timer == 0 and "uncontrollable" not in this_unit.current_action and \
                "uncontrollable" not in this_unit.command_action:  # currently not in melee
            this_unit.manual_control = True
            if this_unit.equipped_weapon != this_unit.charge_weapon_set:  # swap to best charge weapon set for charge
                this_unit.command_action = this_unit.swap_weapon_command_action[this_unit.charge_weapon_set]
            else:
                who_charge.append(this_unit)

                if self.player_input_state == "line charge":
                    angle = self.player_unit.set_rotate(self.command_cursor_pos)
                    distance = self.player_unit.base_pos.distance_to(self.command_cursor_pos)
                    base_target_pos = Vector2(this_unit.base_pos[0] - (distance * sin(radians(angle))),
                                              this_unit.base_pos[1] - (distance * cos(radians(angle))))
                    target_pos = (base_target_pos[0] * 5 * self.screen_scale[0],
                                  base_target_pos[1] * 5 * self.screen_scale[1])

                if this_unit.shoot_line:
                    if this_unit.shoot_line not in self.battle_camera:  # add back target icon
                        self.battle_camera.add(this_unit.shoot_line)
                    this_unit.shoot_line.update(base_target_pos, target_pos, can_charge)
                else:
                    AimTarget(this_unit)
                    self.battle_camera.add(this_unit.shoot_line)
                    this_unit.shoot_line.update(base_target_pos, target_pos, can_charge)

        else:
            if this_unit.shoot_line in self.battle_camera:  # remove target icon
                self.battle_camera.remove(this_unit.shoot_line)

    if self.player1_key_press["Order Menu"] or not self.player_unit.alive:
        # Cancel manual aim with order menu input or player die
        self.player_cancel_input()

    elif self.player1_key_press["Main Weapon Attack"] or self.player1_key_press["Sub Weapon Attack"]:
        for this_unit in who_charge:
            weapon = 0
            if self.player1_key_press["Sub Weapon Attack"] or not this_unit.melee_range[0]:
                weapon = 1
                if not this_unit.melee_range[1]:  # at least 1 weapon is melee from equipped charge set
                    weapon = 0
            this_unit.command_action = this_unit.charge_command_action[weapon]
            this_unit.charge_target = this_unit.shoot_line.base_target_pos

    else:
        self.camera_process()
