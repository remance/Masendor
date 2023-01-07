import random

import pygame
from gamescript.common import utility

rotation_xy = utility.rotation_xy
infinity = float("inf")


def move_logic(self, dt, unit_state, collide_list):
    revert_move = True  # revert move check for in case subunit still need to rotate before moving
    if unit_state == 0 or self.unit.revert or (self.angle != self.unit.angle and self.unit.move_rotate is False):
        revert_move = False

    if (self.base_pos != self.base_target or self.momentum > 1) and \
            (revert_move or self.angle == self.new_angle):  # cannot move if unit still need to rotate
        no_collide_check = False  # can move if front of unit not collided
        if self.unit.collide is False or self.broken or unit_state == 10 or self.momentum > 1:
            no_collide_check = True

        enemy_collide_check = False  # for chance to move or charge through enemy
        if len(collide_list) > 0:
            enemy_collide_check = True
            if self.state in (96, 98, 99):  # escape
                enemy_collide_check = False
                no_collide_check = True  # bypass collide
            elif 0 in self.skill_effect and random.randint(0, 1) == 0:  # chance to charge through
                enemy_collide_check = False

        if self.stamina > 0 and no_collide_check and enemy_collide_check is False and \
                (len(self.same_front) == 0 and len(self.friend_front) == 0 or self.state in (96, 98, 99)):
            if 0 in self.skill_effect and self.base_pos == self.base_target and unit_state == 10:
                new_target = self.front_pos - self.base_pos  # keep charging pass original target until momentum run out
                self.base_target = self.base_target + new_target
                self.command_target = self.base_target

            move = self.base_target - self.base_pos
            move_length = move.length()  # convert length

            if move_length > 0:  # movement length longer than 0.1, not reach base_target yet
                move.normalize_ip()

                if unit_state in (1, 3, 5, 7):  # walking
                    speed = self.unit.walk_speed  # use walk speed
                    self.walk = True
                elif unit_state in (10, 99):  # run with its own speed instead of uniformed run
                    speed = self.speed * self.momentum  # use its own speed when broken
                    self.run = True
                else:  # self.state in (2, 4, 6, 10, 96, 98, 99), running
                    speed = self.unit.run_speed * self.momentum  # use run speed
                    self.run = True
                if self.collide_penalty:  # reduce speed during moving through another unit
                    speed /= 2
                move *= speed * dt
                new_move_length = move.length()
                new_pos = self.base_pos + move

                if speed > 0 and (self.state in (98, 99) or (0 < new_pos[0] < self.map_corner[0] and
                                                             0 < new_pos[1] < self.map_corner[1])):
                    # cannot go pass map unless in retreat state
                    if new_move_length <= move_length:  # move normally according to move speed
                        self.base_pos += move
                        self.pos = self.base_pos * self.zoom
                        self.rect.center = list(
                            int(v) for v in self.pos)  # list rect so the sprite gradually move to position
                        self.dmg_rect.center = self.rect.center
                        if self.stamina != infinity:
                            if self.walk:
                                self.stamina = self.stamina - (dt * 2)
                            elif self.run:
                                self.stamina = self.stamina - (dt * 5)

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
                        if self.unit.move_rotate is False:
                            self.unit.base_pos += move
                        front_pos = (self.unit.base_pos[0],
                                     (self.unit.base_pos[1] - self.unit.base_height_box))  # find front position
                        self.unit.front_pos = rotation_xy(self.unit.base_pos, front_pos, self.unit.radians_angle)

                        number_pos = (self.unit.base_pos[0] - self.unit.base_width_box,
                                      (self.unit.base_pos[1] + self.unit.base_height_box))
                        self.unit.base_number_pos = rotation_xy(self.unit.base_pos, number_pos, self.unit.radians_angle)
                        self.unit.change_pos_scale()

                    if self.run:  # charge skill only when running to melee
                        if self.momentum < 1:
                            self.momentum += dt * self.acceleration / 100
                        elif self.momentum >= 1 and self.state == 4 and self.attacking and self.unit.move_rotate is False:
                            self.use_skill(self.charge_skill)  # Use charge skill
                            self.unit.charging = True
                            self.momentum = 1

                    elif self.momentum > 0.1:  # reset charge momentum if charge skill not active
                        self.momentum -= dt
                        if self.momentum <= 0.5:
                            self.unit.charging = False
                            if self.momentum <= 0.1:
                                self.momentum = 0.1

            elif self.broken is False:  # Stopping subunit when reach base_target
                self.state = 0  # idle
