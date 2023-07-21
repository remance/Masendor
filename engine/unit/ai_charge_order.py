from math import cos, sin, radians

from pygame import Vector2


def ai_charge_order(self, target):
    for this_unit in self.alive_troop_follower:
        if this_unit.in_melee_combat_timer == 0 and "uncontrollable" not in this_unit.current_action and \
                "uncontrollable" not in this_unit.command_action:  # currently not in melee
            this_unit.manual_control = True
            if this_unit.equipped_weapon != this_unit.charge_weapon_set:  # swap to best charge weapon set for charge
                if this_unit.original_melee_range[this_unit.charge_weapon_set][0]:
                    this_unit.command_action = this_unit.charge_swap_command_action[this_unit.charge_weapon_set][0]
                elif this_unit.original_melee_range[this_unit.charge_weapon_set][1]:
                    this_unit.command_action = this_unit.charge_swap_command_action[this_unit.charge_weapon_set][1]
            else:
                if this_unit.melee_range[0]:
                    this_unit.command_action = this_unit.charge_command_action[0]
                elif this_unit.melee_range[1]:
                    this_unit.command_action = this_unit.charge_command_action[1]
            angle = self.set_rotate(target)
            distance = self.base_pos.distance_to(target)
            base_target_pos = Vector2(this_unit.base_pos[0] - (distance * sin(radians(angle))),
                                      this_unit.base_pos[1] - (distance * cos(radians(angle))))
            this_unit.charge_target = base_target_pos
