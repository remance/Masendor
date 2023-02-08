import pygame

melee_attack_command_action = ({"name": "Action 0", "melee attack": True}, {"name": "Action 1", "melee attack": True})

range_attack_command_action = {True: ({"name": "Action 0", "range attack": True, "arc shot": True},
                                      {"name": "Action 1", "range attack": True, "arc shot": True}),
                               False: ({"name": "Action 0", "range attack": True, "arc shot": False},
                                       {"name": "Action 1", "range attack": True, "arc shot": False})}

range_move_attack_command_action = {True: ({"name": "Action 0", "range attack": True, "move attack": True,
                                            "movable": True, "arc shot": True},
                                           {"name": "Action 1", "range attack": True, "move attack": True,
                                            "movable": True, "arc shot": True}),
                                    False: ({"name": "Action 0", "range attack": True, "move attack": True,
                                             "movable": True, "arc shot": False},
                                            {"name": "Action 1", "range attack": True, "move attack": True,
                                             "movable": True, "arc shot": False})}


def combat_ai_logic(self):
    if self.nearest_enemy[0][1] < self.melee_distance_zone:  # enemy in subunit's melee zone
        if self.enemy_in_melee_distance:  # Check if in melee combat or not
            self.in_melee_combat_timer = 3  # consider to be in melee for 3 seconds before reset
            self.melee_target = self.enemy_in_melee_distance[0]
            self.new_angle = self.set_rotate(self.melee_target.base_pos)
            if self.equipped_weapon != self.melee_weapon_set[0]:  # swap to melee weapon when enemy near
                self.swap_weapon(self.melee_weapon_set[0])

            if not self.command_action and not self.current_action:  # if melee combat (engaging anyone on any side)
                for weapon in self.weapon_cooldown:
                    if self.weapon_cooldown[weapon] >= self.weapon_speed[weapon]:
                        self.command_action = melee_attack_command_action[weapon]
                        break

    elif not self.command_action:  # no nearby enemy melee threat
        self.close_target = None
        self.attack_target = None
        can_shoot = False
        if self.ammo_now:  # range attack
            if self.equipped_weapon not in self.ammo_now:
                for this_set in self.range_weapon_set:  # find weapon set with range weapon that has ammo
                    self.swap_weapon(this_set)
                    break

            if self.move is False or self.check_special_effect("Shoot While Moving"):  # Find target to shoot
                if self.shoot_range[0] >= self.nearest_enemy[0][1] or self.shoot_range[1] >= self.nearest_enemy[0][1]: # has enemy in range
                    for enemy in self.nearest_enemy:
                        for weapon in self.ammo_now[self.equipped_weapon]:
                            # can shoot if reload finish, in shoot range and attack pos target exist
                            if self.ammo_now[self.equipped_weapon][weapon] > 0 and \
                                    self.shoot_range[weapon] >= enemy[1]:
                                weapon_arc_shot = self.check_special_effect("Arc Shot", weapon=weapon)
                                if self.check_special_effect("Arc Shot Only",
                                                             weapon=weapon) is False:  # find the closest enemy subunit not block by friend
                                    if self.check_line_of_sight(enemy[0].base_pos) is False:
                                        can_shoot = True
                                        arc_shot = False

                                if can_shoot is False and weapon_arc_shot:  # check for arc shot
                                    can_shoot = True
                                    arc_shot = True

                                if can_shoot:
                                    self.attack_target = enemy[0]  # replace attack_target with enemy unit object
                                    self.attack_pos = self.attack_target.base_pos  # replace attack_pos with enemy unit pos
                                    if self.move and self.check_special_effect("Shoot While Moving"):  # shoot while moving
                                        self.command_action = range_move_attack_command_action[arc_shot][weapon]
                                    else:
                                        self.command_action = range_attack_command_action[arc_shot][weapon]

                                    if self.move is False:
                                        self.new_angle = self.set_rotate(self.attack_target.base_pos)
                                    break
                        if can_shoot:  # found target to shoot
                            break

        # if can_shoot is False:  # reset base_target every update to command base_target outside of combat
        #     if self.base_target != self.command_target:
        #         self.base_target = self.command_target
        #         self.new_angle = self.set_rotate(self.base_target)
        #     elif self.leader is not None:
        #         if self.angle != self.leader.angle:  # reset angle
        #             self.new_angle = self.leader.angle
