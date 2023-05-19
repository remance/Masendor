from math import cos, sin, radians

from pygame import Vector2

follow_distance = 30
stay_formation_distance = 1


def ai_move(self):
    # TODO add condition to check for moving to camp for respawn troop
    if self.leader:  # has higher leader
        if self.is_leader:
            follow_order = self.leader.group_follow_order
        else:
            follow_order = self.leader.troop_follow_order

        if follow_order in ("Stay Formation", "Stay Here"):
            follow = stay_formation_distance
        else:
            follow = follow_distance

        move_target = self.follow_target
    else:  # movement for unit leader
        if self.move_path:
            move_target = self.move_path[0]
        else:
            move_target = self.follow_target
        follow_order = "Free"
        follow = 1

    move_distance = self.follow_target.distance_to(self.base_pos)
    if follow_order != "Free":  # move to assigned location
        if self.leader and "charge" in self.leader.current_action and follow_order != "Stay Here":  # charge TODO change charge to include all momentum (reset right away when attack enemy with non full charge) and self charge without unit
            # leader charging, charge with leader do not auto move to enemy on its own
            if self.equipped_weapon != self.charge_weapon_set:  # swap to best charge weapon set for charge
                self.swap_weapon(self.charge_weapon_set)
                self.in_melee_combat_timer = 3  # consider as in melee to prevent swap back to range weapon
            else:  # already equipped melee weapon
                # charge movement based on angle instead of formation pos
                if self.available_move_skill and not self.command_action:  # use move skill first
                    self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                else:
                    if self.is_leader and self.nearest_enemy:
                        charge_target = self.nearest_enemy[0].base_pos
                    else:
                        charge_target = Vector2(self.base_pos[0] -
                                                (self.run_speed * sin(radians(self.leader.angle))),
                                                self.base_pos[1] -
                                                (self.run_speed * cos(radians(self.leader.angle))))
                    if charge_target.distance_to(self.base_pos) > 0:
                        self.command_target = charge_target
                        attack_index = 0
                        if not self.melee_range[0]:
                            attack_index = 1

                        if "charge" not in self.current_action:
                            self.interrupt_animation = True
                        self.command_action = self.charge_command_action[attack_index]
                        self.move_speed = self.run_speed

        elif move_distance > follow:  # too far from follow target pos, start moving toward it
            self.command_target = move_target
            if 0 < move_distance < 20:  # walk if not too far
                if ("movable" in self.current_action and "walk" not in self.current_action) or \
                        "hold" in self.current_action:
                    self.interrupt_animation = True
                self.command_action = self.walk_command_action
                self.move_speed = self.walk_speed
            else:  # run if too far
                if move_distance > 100 and self.is_leader and self.available_move_far_skill and not self.command_action:
                    # use move far skill first if leader
                    self.skill_command_input(0, self.available_move_far_skill, pos_target=self.base_pos)
                elif self.available_move_skill and not self.command_action:  # use move skill
                    self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                else:
                    if (
                            "movable" in self.current_action and "run" not in self.current_action) or "hold" in self.current_action:
                        self.interrupt_animation = True
                    self.command_action = self.run_command_action
                    self.move_speed = self.run_speed

        elif self.attack_unit and self.max_melee_range > 0:  # enemy nearby and follow target not too far
            move_distance = self.attack_unit.base_pos.distance_to(self.base_pos) - self.max_melee_range
            if move_distance < follow or self.impetuous:
                # enemy nearby and self not too far from move_target
                if move_distance > self.max_melee_range:  # move closer to enemy in range
                    # charge to front of near target
                    if move_distance > 100 and self.is_leader and self.available_move_far_skill and not self.command_action:  # use move far skill first if leader
                        self.skill_command_input(0, self.available_move_far_skill, pos_target=self.base_pos)
                    elif self.available_move_skill and not self.command_action:  # use move skill
                        self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                    else:
                        if "movable" in self.current_action and "charge" not in self.current_action:
                            self.interrupt_animation = True

                        if self.melee_range[0] > 0:
                            self.command_action = self.charge_command_action[0]
                        else:
                            self.command_action = self.charge_command_action[1]

                        # move enough to be in melee attack range
                        base_angle = self.set_rotate(self.attack_unit.base_pos)
                        self.command_target = Vector2(self.base_pos[0] - (move_distance * sin(radians(base_angle))),
                                                      self.base_pos[1] - (move_distance * cos(radians(base_angle))))
                        self.move_speed = self.run_speed

    else:  # move to attack nearby enemy in free order
        if not self.attack_unit and self.nearest_enemy:  # no enemy to hit yet
            move_distance = self.nearest_enemy[0].base_pos.distance_to(self.front_pos)
            if self.shoot_range[0] + self.shoot_range[1] > 0:  # has range weapon, move to maximum shoot range position
                max_shoot = max(self.shoot_range[0], self.shoot_range[1])
                if self.leader and self in self.leader.troop_distance_list:  # possible that unit not in list yet from recent change of leader
                    # use distance of formation to make unit not cluster at same distance
                    max_shoot -= self.leader.troop_distance_list[self][1]
                if move_distance > max_shoot:  # further than can shoot
                    move_distance -= max_shoot
                    if move_distance > 100 and self.is_leader and self.available_move_far_skill and not self.command_action:  # use move far skill first if leader
                        self.skill_command_input(0, self.available_move_far_skill, pos_target=self.base_pos)
                    elif self.available_move_skill and not self.command_action:  # use move skill first
                        self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                    else:
                        angle = self.set_rotate(self.nearest_enemy[0].base_pos)
                        self.command_action = self.run_command_action
                        self.command_target = Vector2(self.base_pos[0] - (move_distance * sin(radians(angle))),
                                                      self.base_pos[1] - (move_distance * cos(radians(angle))))
                        self.move_speed = self.run_speed

            else:  # no range weapon, move to melee
                move_distance = self.nearest_enemy[0].base_pos.distance_to(self.base_pos)
                if move_distance > self.max_melee_range > 0:  # too far move closer
                    if move_distance > 100 and self.is_leader and self.available_move_far_skill and not self.command_action:
                        # use move far skill first if leader
                        self.skill_command_input(0, self.available_move_far_skill, pos_target=self.base_pos)
                    elif self.available_move_skill and not self.command_action:  # use move skill first
                        self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                    else:
                        if move_distance > self.charge_melee_range:
                            if "movable" in self.current_action and "charge" in self.current_action:  # run instead
                                self.interrupt_animation = True
                            self.command_action = self.run_command_action
                        else:
                            if "movable" in self.current_action and "charge" not in self.current_action:
                                self.interrupt_animation = True
                            if move_distance > self.melee_range[0] > 0:
                                self.command_action = self.charge_command_action[0]
                            else:
                                self.command_action = self.charge_command_action[1]
                        self.command_target = self.nearest_enemy[0].base_pos
                        self.move_speed = self.run_speed

    if not self.current_action and not self.command_action and self.available_idle_skill:  # idle, use idle skill
        self.skill_command_input(0, self.available_idle_skill, pos_target=self.base_pos)
