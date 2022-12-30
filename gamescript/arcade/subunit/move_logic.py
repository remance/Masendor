import random

import pygame
from gamescript.common import utility

rotation_xy = utility.rotation_xy
infinity = float("inf")


def move_logic(self, dt, unit_state, collide_list):
    self.base_target = self.command_target  # always attempt to catch up to command target
    if self.base_pos != self.base_target and (not self.current_action or "movable" in self.current_action):
        no_collide_check = False  # can move if front of unit not collided
        if (((self.unit.collide is False or self.frontline is False) or unit_state == 99)
                or (unit_state == 10 and ((self.frontline or self.unit.attack_mode == 2) and self.unit.attack_mode != 1)
                    or self.momentum > 1)):
            no_collide_check = True

        enemy_collide_check = False  # for chance to move or charge through enemy
        if len(collide_list) > 0:
            enemy_collide_check = True
            if self.state in (96, 98, 99):  # retreat
                enemy_collide_check = False
                no_collide_check = True  # bypass collide
            elif 0 in self.skill_effect and random.randint(0,
                                                           1) == 0:  # chance to charge through TODO add charge power vs def
                enemy_collide_check = False

        if no_collide_check and enemy_collide_check is False and \
                (len(self.friend_front) == 0 or self.state in (96, 98, 99)):
            move = self.base_target - self.base_pos
            move_length = move.length()  # convert length
            if move_length > 0:  # movement length longer than 0.1, not reach base_target yet
                move.normalize_ip()
                self.state = unit_state
                if move_length > 10 or unit_state == 99:  # use its own speed when catch up or broken
                    if unit_state != 99:
                        self.state = 2
                    speed = self.speed * self.momentum
                    self.run = True
                elif unit_state in (1, 3, 5, 7):  # walking
                    speed = self.unit.walk_speed  # use walk speed
                    self.walk = True
                else:  # self.state in (2, 4, 6, 10, 96, 98, 99), running
                    speed = self.unit.run_speed * self.momentum  # use run speed
                    self.run = True
                    if unit_state == 0:
                        self.state = 2
                if self.collide_penalty:  # reduce speed during moving through another unit
                    speed /= 2
                move *= speed * dt
                new_move_length = move.length()
                new_pos = self.base_pos + move

                if speed > 0 and (self.state in (98, 99) or (self.state not in (98, 99) and
                                                             (0 < new_pos[0] < 1000 and 0 < new_pos[1] < 1000))):
                    # cannot go pass map unless in retreat state
                    if new_move_length <= move_length:  # move normally according to move speed
                        self.base_pos += move
                        self.pos = self.base_pos * self.zoom
                        self.rect.center = list(
                            int(v) for v in self.pos)  # list rect so the sprite gradually move to position
                        self.dmg_rect.center = self.rect.center
                        self.new_angle = self.set_rotate(self.base_target)
                        if self.walk:
                            if self.stamina != infinity:
                                self.stamina = self.stamina - dt
                        elif self.run:
                            if self.stamina != infinity:
                                self.stamina = self.stamina - (dt * 2)
                    else:  # move length pass the base_target destination, set movement to stop exactly at base_target
                        move = self.base_target - self.base_pos  # simply change move to whatever remaining distance
                        self.base_pos += move  # adjust base position according to movement

                    if len(self.combat_move_queue) > 0 and self.base_pos.distance_to(
                            pygame.Vector2(
                                self.combat_move_queue[0])) < 0.1:  # reach the current queue point, remove from queue
                        self.combat_move_queue = self.combat_move_queue[1:]

                    self.change_pos_scale()
                    self.front_pos = self.make_front_pos()
                    self.make_pos_range()

                    self.terrain, self.feature = self.get_feature(self.base_pos,
                                                                  self.base_map)  # get new terrain and feature at each subunit position
                    self.height = self.height_map.get_height(self.base_pos)  # get new height
                    self.front_height = self.height_map.get_height(self.front_pos)
                    self.last_pos = self.base_pos

                    if self.unit_leader and new_move_length > 0:
                        self.unit.base_pos += move
                        front_pos = (self.unit.base_pos[0],
                                     (self.unit.base_pos[1] - self.unit.base_height_box))  # find front position
                        self.unit.front_pos = rotation_xy(self.unit.base_pos, front_pos, self.unit.radians_angle)

                        number_pos = (self.unit.base_pos[0] - self.unit.base_width_box,
                                      (self.unit.base_pos[1] + self.unit.base_height_box))  # TODO change to flag team
                        self.unit.number_pos = rotation_xy(self.unit.base_pos, number_pos, self.unit.radians_angle)
                        self.unit.true_number_pos = self.unit.number_pos * (
                                11 - self.unit.zoom)  # find new position for troop number text

                    # momentum calculation
                    if self.run:
                        # if self.leader is not None:
                        #     print(self.momentum, self.acceleration, dt)
                        if self.momentum < 1:
                            self.momentum += dt * self.acceleration / 100
                            if self.momentum > 1:
                                self.momentum = 1

                    elif self.momentum > 0.1:  # reset charge momentum if charge skill not active
                        self.momentum -= dt
                        if self.momentum <= 0.1:
                            self.momentum = 0.1
