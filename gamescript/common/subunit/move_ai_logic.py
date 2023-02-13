import random
import math
import pygame

follow_distance = 30
stay_formation_distance = 1


def move_ai_logic(self):
    if self.leader is not None:
        if not self.command_action:
            if self.is_leader is False:
                if self.leader.follow_order != "Free":  # move to assigned location
                    if self.leader.follow_order in ("Stay Formation", "Stay Here"):
                        follow = stay_formation_distance
                        stay_distance = 5
                    else:
                        follow = follow_distance
                        stay_distance = self.stay_distance_zone
                    distance_to_move = self.follow_target.distance_to(self.base_pos)
                    if "charge" in self.leader.current_action and self.leader.follow_order != "Stay Here":
                        # leader charging, charge with leader do not auto move to enemy on its own
                        attack_index = None
                        self.command_target = self.follow_target
                        if self.melee_range[0] > 0:
                            attack_index = 0
                        elif self.melee_range[1] > 0:
                            attack_index = 1

                        if attack_index is not None:
                            if "charge" not in self.current_action:
                                self.interrupt_animation = True
                            self.command_action = self.charge_command_action[attack_index]
                        else:
                            self.command_action = self.run_command_action
                        self.move_speed = self.run_speed

                    elif distance_to_move > follow:  # too far from follow target pos, start moving toward it
                        self.command_target = self.follow_target
                        if 0 < distance_to_move < 20:  # only walk if not too far
                            if "move loop" in self.current_action:
                                self.interrupt_animation = True
                            self.command_action = self.walk_command_action
                            self.move_speed = self.walk_speed
                        else:  # run if too far
                            if "move loop" in self.current_action:
                                self.interrupt_animation = True
                            self.command_action = self.run_command_action
                            self.move_speed = self.run_speed

                    elif self.attack_target is not None and self.max_melee_range > 0:
                        distance = self.attack_target.base_pos.distance_to(self.base_pos) - self.max_melee_range
                        if distance < follow or self.impetuous:
                            # enemy nearby and self not too far from follow_target
                            if distance > self.max_melee_range:  # move closer to enemy in range
                                # charge to front of near target
                                if "move loop" in self.current_action and "Charge" not in self.current_action["name"]:
                                    self.interrupt_animation = True

                                if self.melee_range[0] > 0:
                                    self.command_action = self.charge_command_action[0]
                                else:
                                    self.command_action = self.charge_command_action[1]

                                # move enough to be in melee attack range
                                base_angle = self.set_rotate(self.attack_target.base_pos)
                                self.command_target = pygame.Vector2(self.base_pos[0] -
                                                                     (distance * math.sin(math.radians(base_angle))),
                                                                     self.base_pos[1] -
                                                                     (distance * math.cos(math.radians(base_angle))))
                                self.move_speed = self.run_speed

                else:  # move to attack nearby enemy in free order
                    distance = self.nearest_enemy[0].base_pos.distance_to(self.front_pos)
                    if self.shoot_range[0] + self.shoot_range[1] > 0:  # has range weapon, move to maximum shoot range position
                        max_shoot = max(self.shoot_range[0], self.shoot_range[1])
                        if distance > max_shoot:  # further than can shoot
                            distance = distance - max_shoot
                            angle = self.set_rotate(self.nearest_enemy[0].base_pos)
                            self.follow_target = pygame.Vector2(self.base_pos[0] - (distance * math.sin(math.radians(angle))),
                                                                self.base_pos[1] - (distance * math.cos(math.radians(angle))))
                            self.command_action = self.run_command_action
                    elif distance > self.max_melee_range > 0:  # melee
                        self.follow_target = self.nearest_enemy[0].base_pos  # TODO Change this to match above when ready
                        if distance > self.melee_range[0] > 0:
                            self.command_action = self.charge_command_action[0]
                        else:
                            self.command_action = self.charge_command_action[1]
                    self.command_target = self.follow_target
                    self.move_speed = self.run_speed


def move_to_near_enemy(enemy):
    """Find random position near enemy target"""
    angle = random.uniform(0, 2.0 * math.pi)
    vector = pygame.Vector2(random.randint(1, 10) * math.cos(angle),
                            random.randint(1, 10) * math.sin(angle))
    return enemy.base_pos + vector
