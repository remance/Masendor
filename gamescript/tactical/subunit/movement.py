import math
import random
import pygame

from gamescript import script_common

rotation_xy = script_common.rotation_xy
infinity = float("inf")


def rotate_logic(self, dt):
    rotate_cal = abs(self.new_angle - self.angle)  # amount of angle left to rotate
    rotate_check = 360 - rotate_cal  # rotate distance used for preventing angle calculation bug (pygame rotate related)
    self.radians_angle = math.radians(360 - self.angle)  # for all side rotate
    if self.angle < 0:  # negative angle (rotate to left side)
        self.radians_angle = math.radians(-self.angle)

    rotate_tiny = self.rotate_speed * dt  # rotate little by little according to time
    if self.new_angle > self.angle:  # rotate to angle more than the current one
        if rotate_cal > 180:  # rotate with the smallest angle direction
            self.angle -= rotate_tiny
            rotate_check -= rotate_tiny
            if rotate_check <= 0:
                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
        else:
            self.angle += rotate_tiny
            if self.angle > self.new_angle:
                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
    elif self.new_angle < self.angle:  # rotate to angle less than the current one
        if rotate_cal > 180:  # rotate with the smallest angle direction
            self.angle += rotate_tiny
            rotate_check -= rotate_tiny
            if rotate_check <= 0:
                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
        else:
            self.angle -= rotate_tiny
            if self.angle < self.new_angle:
                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle

    self.rotate()  # rotate sprite to new angle
    self.make_front_pos()  # generate new pos related to side
    self.front_height = self.height_map.get_height(self.front_pos)


def rotate(self):
    """rotate sprite image may use when subunit can change direction independently from unit"""
    self.image = pygame.transform.rotate(self.image_original, self.angle)
    if self.unit.selected and self.state != 100:
        self.selected_image = pygame.transform.rotate(self.selected_image_original, self.angle)
        self.image.blit(self.selected_image, self.selected_image_rect)
    self.rect = self.image.get_rect(center=self.pos)


def move_logic(self, dt, parent_state, collide_list):
    revert_move = True  # revert move check for in case subunit still need to rotate before moving
    if parent_state == 0 or self.unit.revert or (self.angle != self.unit.angle and self.unit.move_rotate is False):
        revert_move = False

    if (self.base_pos != self.base_target or self.charge_momentum > 1) and \
            (revert_move or self.angle == self.new_angle):  # cannot move if unit still need to rotate
        no_collide_check = False  # can move if front of unit not collided
        if (((self.unit.collide is False or self.frontline is False) or parent_state == 99)
                or (parent_state == 10 and ((self.frontline or self.unit.attack_mode == 2) and self.unit.attack_mode != 1)
                    or self.charge_momentum > 1)):
            no_collide_check = True

        enemy_collide_check = False  # for chance to move or charge through enemy
        if len(collide_list) > 0:
            enemy_collide_check = True
            if self.state in (96, 98, 99):  # escape
                enemy_collide_check = False
                no_collide_check = True  # bypass collide
            elif self.charge_skill in self.skill_effect and random.randint(0, 1) == 0:  # chance to charge through
                enemy_collide_check = False

        if self.stamina > 0 and no_collide_check and enemy_collide_check is False and \
                (len(self.same_front) == 0 and len(self.friend_front) == 0 or self.state in (96, 98, 99)):
            if self.charge_skill in self.skill_effect and self.base_pos == self.base_target and parent_state == 10:
                new_target = self.front_pos - self.base_pos  # keep charging pass original target until momentum run out
                self.base_target = self.base_target + new_target
                self.command_target = self.base_target

            move = self.base_target - self.base_pos
            move_length = move.length()  # convert length

            if move_length > 0:  # movement length longer than 0.1, not reach base_target yet
                move.normalize_ip()

                if parent_state in (1, 3, 5, 7):  # walking
                    speed = self.unit.walkspeed  # use walk speed
                    self.walk = True
                elif parent_state in (10, 99):  # run with its own speed instead of uniformed run
                    speed = self.speed / 15  # use its own speed when broken
                    self.run = True
                else:  # self.state in (2, 4, 6, 10, 96, 98, 99), running
                    speed = self.unit.runspeed  # use run speed
                    self.run = True
                if self.charge_skill in self.skill_effect:  # speed gradually decrease with momentum during charge
                    speed = speed * self.charge_momentum / 8
                if self.collide_penalty:  # reduce speed during moving through another unit
                    speed = speed / 2
                move = move * speed * dt
                new_move_length = move.length()
                new_pos = self.base_pos + move

                if speed > 0 and (self.state in (98, 99) or (self.state not in (98, 99) and
                                                             (0 < new_pos[0] < 999 and 0 < new_pos[1] < 999))):
                    # cannot go pass map unless in retreat state
                    if new_move_length <= move_length:  # move normally according to move speed
                        self.base_pos = new_pos
                        self.pos = self.base_pos * self.zoom
                        self.rect.center = list(int(v) for v in self.pos)  # list rect so the sprite gradually move to position
                        if self.stamina != infinity:
                            if self.walk:
                                self.stamina = self.stamina - (dt * 2)
                            elif self.run:
                                self.stamina = self.stamina - (dt * 5)

                    else:  # move length pass the base_target destination, set movement to stop exactly at base_target
                        move = self.base_target - self.base_pos  # simply change move to whatever remaining distance
                        self.base_pos += move  # adjust base position according to movement
                        self.pos = self.base_pos * self.zoom
                        self.rect.center = self.pos  # no need to do list
                    if len(self.combat_move_queue) > 0 and self.base_pos.distance_to(
                            pygame.Vector2(self.combat_move_queue[0])) < 0.1:  # reach the current queue point, remove from queue
                        self.combat_move_queue = self.combat_move_queue[1:]

                    self.make_front_pos()
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
                        self.unit.number_pos = rotation_xy(self.unit.base_pos, number_pos, self.unit.radians_angle)
                        self.unit.true_number_pos = self.unit.number_pos * (
                                11 - self.unit.zoom)  # find new position for troop number text

            else:  # Stopping subunit when reach base_target
                self.state = 0  # idle
