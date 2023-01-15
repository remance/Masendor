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


def combat_ai_logic(self, dt, unit_state, collide_list):
    if collide_list:  # Check if in melee combat or not
        if self.state not in (96, 98, 99):
            self.state = 10
            self.melee_target = collide_list[0]
            self.unit.attack_target = self.melee_target.unit
            self.new_angle = self.set_rotate(self.melee_target.base_pos)

    elif unit_state == 10:  # no nearby enemy to hit while parent unit in melee fight state
        if self.attacking and self.unit.collide:
            if self.momentum == 1 and self.unit.attack_mode == 1:  # attack to the nearest target instead
                if self.melee_target is None and self.unit.attack_target is not None:
                    self.melee_target = self.unit.attack_target.alive_subunit_list[0]
                if self.melee_target is not None:
                    if self.close_target is None:  # movement queue is empty regenerate new one
                        self.close_target = self.find_attack_target(
                            self.melee_target.unit.alive_subunit_list)  # find new close target

                        if self.close_target is not None:  # found target to fight
                            if self not in self.battle.combat_path_queue:
                                self.battle.combat_path_queue.append(self)

                        else:  # no target to fight move back to command pos first
                            self.base_target = self.attack_target.base_pos
                            self.new_angle = self.set_rotate(self.base_target)

                    if self.melee_target.unit.state != 100:
                        if self.move_timer == 0:
                            self.move_timer = 0.1  # recalculate again in 10 seconds if not in fight
                            # if len(self.same_front) != 0 and len(self.enemy_front) == 0: # collide with friend try move to base_target first before enemy
                            # self.combat_move_queue = [] # clean queue since the old one no longer without collide
                        else:
                            self.move_timer += dt
                            if len(self.enemy_in_melee_distance) != 0 or len(self.enemy_collide) != 0:  # in fight, stop timer
                                self.move_timer = 0

                            elif self.move_timer > 10 or len(
                                    self.combat_move_queue) == 0:  # # time up, or no path. reset path
                                self.move_timer = 0
                                self.close_target = None
                                if self in self.battle.combat_path_queue:
                                    self.battle.combat_path_queue.remove(self)

                            elif len(self.combat_move_queue) > 0:  # no collide move to enemy
                                self.base_target = pygame.Vector2(self.combat_move_queue[0])
                                self.new_angle = self.set_rotate(self.base_target)

                    else:  # whole targeted enemy unit destroyed, reset target and state
                        self.close_target = None
                        if self in self.battle.combat_path_queue:
                            self.battle.combat_path_queue.remove(self)

                        self.attack_target = None
                        self.base_target = self.command_target
                        self.new_angle = self.unit.angle

        elif self.attacking is False:  # not in fight anymore, rotate and move back to original position
            self.close_target = None
            if self in self.battle.combat_path_queue:
                self.battle.combat_path_queue.remove(self)

            self.attack_target = None
            self.base_target = self.command_target
            self.new_angle = self.unit.angle

        if self.state != 10 and self.manual_shoot is False and \
                (self.magazine_count[self.equipped_weapon][0] > 0 or
                 self.magazine_count[self.equipped_weapon][1] > 0) and self.unit.fire_at_will == 0 and \
                self.momentum == 1:  # Range attack when unit in melee state
            self.state = 11
            if self.unit.nearby_enemy != {} and (self.attack_target is None or self.attack_pos is None):
                self.find_shooting_target(unit_state)

    elif self.state < 90:  # range attack
        self.close_target = None
        if self in self.battle.combat_path_queue:
            self.battle.combat_path_queue.remove(self)
        self.attack_target = None
        self.combat_move_queue = []
        if self.ammo_now:
            if unit_state == 11:  # unit in range attack state
                if any(weapon_range >= self.attack_pos.distance_to(self.base_pos) for weapon_range in
                       self.shoot_range.values()):
                    self.state = 11  # can shoot if troop have magazine_left and in shoot range, enter range combat state

            elif self.unit.fire_at_will == 0 and (self.state == 0 or
                                                  ((self.walk or self.run) and
                                                   self.check_special_effect("Shoot While Moving"))):  # Fire at will
                if self.unit.nearby_enemy != {} and self.attack_target is None:
                    self.find_shooting_target(unit_state)  # shoot the nearest target

    if self.state == 10 and not self.command_action and not self.current_action:  # if melee combat (engaging anyone on any side)
        for weapon in self.weapon_cooldown:
            if self.weapon_cooldown[weapon] >= self.weapon_speed[weapon]:
                if self.melee_target is not None:
                    self.command_action = melee_attack_command_action[weapon]
                break

    elif self.state in (11, 12, 13) and self.manual_shoot is False:  # range combat
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
                    if self.check_special_effect("Arc Shot Only", weapon=weapon) is False and \
                            len(self.attack_target.alive_subunit_list) > 0:  # find the closest enemy subunit not block by friend
                        target_hit = self.find_attack_target(
                            self.attack_target.alive_subunit_list, check_line_of_sight=True)
                        if target_hit is not None:
                            can_shoot = True
                            arc_shot = False

                    if can_shoot is False and self.unit.shoot_mode == 0 and weapon_arc_shot:  # check for arc shot
                        can_shoot = True
                        arc_shot = True

                    if can_shoot:
                        if self.state in (12, 13):  # shoot while moving
                            self.command_action = range_move_attack_command_action[arc_shot][weapon]
                        else:
                            self.command_action = range_attack_command_action[arc_shot][weapon]
                        break

    else:  # reset base_target every update to command base_target outside of combat
        if self.base_target != self.command_target:
            self.base_target = self.command_target
            if unit_state == 0:
                self.new_angle = self.set_rotate(self.base_target)
        elif self.angle != self.unit.angle:  # reset angle
            self.new_angle = self.unit.angle

    return unit_state
