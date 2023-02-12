import random
import math
import pygame

follow_distance = 15
stay_formation_distance = 5


def move_ai_logic(self):
    if self.not_broken:
        if self.leader is not None:
            if not self.command_action:  # Not currently in melee
                if self.is_leader is False:
                    if self.leader.follow_order != "Free":  # move to assigned location
                        if self.leader.follow_order == ("Stay Formation", "Stay Here"):
                            follow = stay_formation_distance
                            stay_distance = 5
                        else:
                            follow = follow_distance
                            stay_distance = self.stay_distance_zone
                        if self.leader.follow_order != "Stay Here":  # find new pos from formation
                            self.follow_target = self.leader.formation_pos_list[self]
                        distance_to_move = self.follow_target.distance_to(self.base_pos)

                        if self.attack_target is not None and distance_to_move < stay_distance:  # enemy nearby and self not too far from follow_target
                            distance = self.attack_target.base_pos.distance_to(self.front_pos)
                            attack_distance = 0
                            if distance > self.melee_charge_range[0] > 0:
                                attack_index = 0
                                attack_distance = self.melee_charge_range[0]
                            elif distance > self.melee_charge_range[1] > 0:
                                attack_index = 1
                                attack_distance = self.melee_charge_range[1]
                            if self.leader.follow_order == "Stay Formation":
                                attack_distance /= 3
                            if attack_distance > 0:
                                # charge to random position near target
                                if "move loop" in self.current_action and "Charge" not in self.current_action["name"]:
                                    self.interrupt_animation = True
                                self.command_action = self.charge_command_action[attack_index].copy()
                                self.command_target = move_to_near_enemy(self.attack_target)
                                self.command_action["move speed"] = self.run_speed

                        elif distance_to_move > follow:  # too far from follow target pos, start moving toward it
                            self.command_target = self.follow_target
                            if 0 < distance_to_move < 20:  # only walk if not too far
                                if "move loop" in self.current_action:
                                    self.interrupt_animation = True
                                self.command_action = self.walk_command_action.copy()
                                self.command_action["move speed"] = self.walk_speed
                            else:  # run if too far
                                if "move loop" in self.current_action:
                                    self.interrupt_animation = True
                                self.command_action = self.run_command_action.copy()
                                self.command_action["move speed"] = self.run_speed
                    else:  # move to attack nearby enemy in free order
                        distance = self.nearest_enemy[0][0].base_pos.distance_to(self.front_pos)
                        if self.shoot_range[0] + self.shoot_range[1] > 0:  # has range weapon, move to maximum shoot range position
                            max_shoot = max(self.shoot_range[0], self.shoot_range[1])
                            if distance > max_shoot:  # further than can shoot
                                distance = distance - max_shoot
                                angle = self.set_rotate(self.nearest_enemy[0][0].base_pos)
                                self.follow_target = pygame.Vector2(self.base_pos[0] - (distance * math.sin(math.radians(angle))),
                                                                    self.base_pos[1] - (distance * math.cos(math.radians(angle))))
                                self.command_action = self.run_command_action.copy()
                        elif distance > self.melee_range[0] > 0 and distance > self.melee_range[1] > 0:  # melee
                            self.follow_target = move_to_near_enemy(self.nearest_enemy[0][0])
                            if distance > self.melee_range[0] > 0:
                                self.command_action = self.charge_command_action[0].copy()
                            else:
                                self.command_action = self.charge_command_action[1].copy()
                        self.command_target = self.follow_target
                        self.command_action["move speed"] = self.run_speed

    else:
        if "move loop" in self.current_action:
            self.interrupt_animation = True
        self.command_action = self.flee_command_action.copy()
        self.command_action["move speed"] = self.run_speed
            # else:
            #     pass
        # impetus


def move_to_near_enemy(enemy):
    """Find random position near enemy target"""
    angle = random.uniform(0, 2.0 * math.pi)
    vector = pygame.Vector2(random.randint(1, 10) * math.cos(angle),
                            random.randint(1, 10) * math.sin(angle))
    return enemy.base_pos + vector
