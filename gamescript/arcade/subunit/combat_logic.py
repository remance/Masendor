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


def combat_logic(self, dt, unit_state):
    self.melee_target = None
    collide_list = self.enemy_front + self.enemy_side

    for weapon in self.weapon_cooldown:
        if self.weapon_cooldown[weapon] < self.weapon_speed[weapon]:
            self.weapon_cooldown[weapon] += dt
        if self.equipped_weapon in self.ammo_now and weapon in self.ammo_now[self.equipped_weapon] and \
                self.ammo_now[self.equipped_weapon][weapon] < 1:  # reloading magazine
            if type(self.troop_id) == str or self.weapon_cooldown[weapon] >= self.weapon_speed[
                weapon]:  # finish reload, add ammo. hero char reload instantly for gameplay effect
                self.ammo_now[self.equipped_weapon][weapon] = self.magazine_size[self.equipped_weapon][weapon]
                self.magazine_count[self.equipped_weapon][weapon] -= 1
                self.weapon_cooldown[weapon] = 0

    if self.player_manual_control is False:
        if collide_list:  # Check if in combat or not with enemy collision
            for subunit in collide_list:
                if self.state not in (96, 98, 99):
                    self.state = 10
                    self.melee_target = subunit
                    if self.enemy_front == []:  # no enemy in front try to rotate to enemy at side
                        # self.base_target = self.melee_target.base_pos
                        self.new_angle = self.set_rotate(self.melee_target.base_pos)
                else:  # no way to retreat, Fight to the death
                    if self.enemy_front and self.enemy_side:  # if both front and any side got attacked
                        if 9 not in self.status_effect:
                            self.status_effect[9] = self.status_list[9].copy()  # fight to the death status
                if unit_state not in (10, 96, 98, 99):
                    unit_state = 10
                    self.unit.state = 10
                if self.melee_target is not None:
                    self.unit.attack_target = self.melee_target.unit
                break

        else:  # range attack
            self.melee_target = None
            self.close_target = None
            if self in self.battle.combat_path_queue:
                self.battle.combat_path_queue.remove(self)
            self.attack_target = None
            self.combat_move_queue = []
            if unit_state == 11:
                self.state = 0  # reset all subunit to idle first if unit in shooting state
            if self.equipped_weapon in self.ammo_now:
                if unit_state == 11:  # unit in range attack state
                    if any(weapon_range >= self.attack_pos.distance_to(self.base_pos) for weapon_range in
                           self.shoot_range.values()):
                        self.state = 11  # can shoot if troop have magazine_left and in shoot range, enter range combat state

                elif self.unit.fire_at_will == 0 and (self.state == 0 or
                                                      (self.state in (1, 2, 3, 4, 5, 6, 7) and
                                                       self.check_special_effect(
                                                           "Shoot While Moving"))):  # Fire at will
                    if self.unit.nearby_enemy != {} and self.attack_target is None:
                        self.find_shooting_target(unit_state)  # shoot the nearest target

        if self.state == 10:  # if melee combat (engaging anyone on any side)
            for weapon in self.weapon_cooldown:
                if self.weapon_cooldown[weapon] >= self.weapon_speed[weapon]:
                    collide_list = [subunit for subunit in self.enemy_front]
                    for subunit in collide_list:
                        angle_check = abs(self.angle - subunit.angle)  # calculate which side arrow hit the subunit
                        if angle_check >= 135:  # front
                            hit_side = 0
                        elif angle_check >= 45:  # side
                            hit_side = 1
                        else:  # rear
                            hit_side = 2
                        self.hit_register(weapon, subunit, 0, hit_side, self.battle.troop_data.status_list)
                        self.command_action = melee_attack_command_action[weapon]
                        self.stamina -= self.weapon_weight[self.equipped_weapon][weapon]
                        self.weapon_cooldown[weapon] -= self.weapon_speed[weapon]
                    break

        elif self.state in (11, 12, 13):  # range combat
            if self.attack_target is not None:  # For fire at will
                if self.attack_target.state == 100:  # enemy dead
                    self.attack_pos = None  # reset attack_pos to none
                    self.attack_target = None  # reset attack_target to none
                    for target, pos in self.unit.nearby_enemy.items():  # find other nearby base_target to shoot
                        self.attack_pos = pos
                        self.attack_target = target
                        break  # found new target, break loop
            elif self.attack_target is None:
                self.attack_target = self.unit.attack_target
                if self.attack_target is not None:
                    self.attack_pos = self.attack_target.base_pos
            if self.attack_pos is not None and not self.command_action and not self.current_action:
                for weapon in self.ammo_now[self.equipped_weapon]:
                    # can shoot if reload finish and base_target existed and not dead. Non arc_shot cannot shoot if forbid
                    if self.ammo_now[self.equipped_weapon][weapon] > 0 and \
                            self.shoot_range[weapon] >= self.attack_pos.distance_to(self.base_pos):
                        can_shoot = False
                        weapon_arc_shot = self.check_special_effect("Arc Shot", weapon=weapon)
                        if self.unit.shoot_mode in (0, 2):  # check for direct shot first, find line of sight
                            if len(self.attack_target.alive_subunit_list) > 0:  # find the closest enemy subunit not block by friend
                                target_hit = self.find_attack_target(
                                    self.attack_target.alive_subunit_list, check_line_of_sight=True)
                                if target_hit is not None:
                                    can_shoot = True
                                    arc_shot = False

                        if can_shoot is False and self.unit.shoot_mode in (
                        0, 1) and weapon_arc_shot:  # check for arc shot
                            can_shoot = True
                            arc_shot = True

                        if can_shoot:
                            if self.state in (12, 13):  # shoot while moving
                                self.command_action = range_move_attack_command_action[arc_shot][weapon]
                            else:
                                self.command_action = range_attack_command_action[arc_shot][weapon]
                            break

    return unit_state, collide_list
