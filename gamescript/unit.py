import math
import random

import numpy as np
import pygame
import pygame.freetype
from gamescript.common import utility

rotation_xy = utility.rotation_xy

team_colour = {0: (255, 255, 255), 1: (144, 167, 255), 2: (255, 114, 114)}  # team colour, Neutral, 1, 2


def change_unit_genre(genre):
    """Change game genre and add appropriate method to subunit class"""
    if genre == "tactical":
        from gamescript.tactical.unit import combat, mobalise, player, update
    elif genre == "arcade":
        from gamescript.arcade.unit import combat, mobalise, player, update

    Unit.skirmish = combat.skirmish
    Unit.chase = combat.chase
    Unit.destroyed = combat.destroyed  # destroyed script
    Unit.retreat = combat.retreat
    Unit.switch_faction = combat.switch_faction
    Unit.user_input = player.user_input
    Unit.rotate_logic = mobalise.rotate_logic
    Unit.revert_move = mobalise.revert_move
    Unit.selection = update.selection
    Unit.auth_recal = update.auth_recal
    Unit.setup_unit = update.setup_unit


class Unit(pygame.sprite.Sprite):
    images = []
    max_zoom = 10  # max zoom allow
    battle = None
    form_change_timer = 10
    image_size = None
    battle_camera = None

    set_rotate = utility.set_rotate

    # method that change based on genre
    skirmish = None
    chase = None
    destroyed = None
    retreat = None
    switch_faction = None
    auth_recal = None
    user_input = None
    rotate_logic = None
    revert_move = None
    selection = None

    def __init__(self, game_id, start_pos, subunit_list, colour, control, coa, commander, start_angle, start_hp=100, start_stamina=100, team=0):
        """Although unit in code, this is referred as subunit ingame"""
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icon = None  # for linking with army selection ui, got linked when icon created in game_ui.ArmyIcon
        self.team_commander = None  # commander leader
        self.start_where = []
        self.subunits_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
        self.subunits = []
        self.leader = []
        self.leader_subunit = None  # subunit that general is in, get added in leader first update
        self.near_target = {}  # list dict of nearby enemy unit, sorted by distance
        self.game_id = game_id  # id of unit for reference in many function
        self.control = control  # player control or not
        self.start_hp = start_hp  # starting hp percentage
        self.start_stamina = start_stamina  # starting stamina percentage
        self.subunit_list = subunit_list  # subunit array
        self.colour = colour  # box colour according to team
        self.commander = commander  # commander unit if true

        self.zoom = 10  # start with the closest zoom
        self.last_zoom = 1  # zoom level without calculate with 11 - zoom for scale

        self.base_width_box, self.base_height_box = len(self.subunit_list[0]) * (self.image_size[0] + 10) / 20, len(self.subunit_list) * (
                self.image_size[1] + 2) / 20

        self.base_pos = pygame.Vector2(start_pos)  # base_pos is for true pos that is used for battle calculation
        self.last_base_pos = self.base_pos
        self.base_attack_pos = 0  # position of melee_attack base_target
        self.angle = start_angle  # start at this angle
        if self.angle == 360:  # 360 is 0 angle at the start, not doing this cause angle glitch when self start
            self.angle = 0
        self.new_angle = self.angle
        self.radians_angle = math.radians(360 - start_angle)  # radians for apply angle to position (allsidepos and subunit)
        front_pos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
        self.front_pos = rotation_xy(self.base_pos, front_pos, self.radians_angle)
        self.movement_queue = []
        self.base_target = self.front_pos
        self.command_target = self.front_pos
        number_pos = (self.base_pos[0] - self.base_width_box,
                      (self.base_pos[1] + self.base_height_box))  # find position for number text
        self.number_pos = rotation_xy(self.base_pos, number_pos, self.radians_angle)
        self.change_pos_scale()

        # v Setup default behaviour check # TODO add volley, divide behaviour ui into 3 types: combat, shoot, other (move)
        self.next_rotate = False
        self.selected = False  # for checking if it currently selected or not
        self.just_selected = False  # for light up subunit when click
        self.zoom_change = False
        self.revert = False
        self.move_rotate = False  # for checking if the movement require rotation first or not
        self.rotate_cal = 0  # for calculate how much angle to rotate to the base_target
        self.rotate_check = 0  # for checking if the new angle rotate pass the base_target angle or not
        self.just_split = False  # subunit just got split
        self.leader_change = False
        self.direction_arrow = False
        self.rotate_only = False  # Order unit to rotate to base_target direction
        self.charging = False  # For subunit charge skill activation
        self.forced_melee = False  # Force unit to melee melee_attack
        self.attack_place = False  # melee_attack position instead of enemy
        self.forced_march = False
        self.change_faction = False  # For initiating change faction function
        self.run_toggle = 0  # 0 = double right click to run, 1 = only one right click will make unit run
        self.shoot_mode = 0  # 0 = both arc and non-arc shot, 1 = arc shot only, 2 = forbid arc shot
        self.attack_mode = 0  # frontline melee_attack, 1 = formation melee_attack, 2 = free for all melee_attack,
        self.hold = 0  # 0 = not hold, 1 = skirmish/scout/avoid, 2 = hold
        self.fire_at_will = 0  # 0 = fire at will, 1 = no fire
        self.retreat_start = False
        self.retreat_way = None
        self.collide = False  # for checking if subunit collide, if yes then stop moving
        self.range_combat_check = False
        self.attack_target = None  # melee_attack base_target, can be either int or unit object
        self.got_killed = False  # for checking if destroyed() was performed when subunit destroyed yet
        # ^ End behaviour check

        # v setup default starting value
        self.troop_number = 0  # sum
        self.stamina = 0  # average from all subunit
        self.morale = 0  # average from all subunit
        self.ammo = 0  # total magazine_left left of the whole unit
        self.old_ammo = 0  # previous number of magazine_left for magazine_left bar checking
        self.min_range = 0  # minimum shoot range of all subunit inside this unit
        self.max_range = 0  # maximum shoot range of all subunit inside this unit
        self.use_min_range = 0  # use min or max range for walk/run (range) command
        self.skill_cond = 0  # skill condition for stamina reservation
        self.state = 0  # see battle_ui.py topbar for name of each state
        self.command_state = self.state
        self.dead_change = False  # for checking when subunit dead and run related code
        self.timer = random.random()
        self.state_delay = 3  # some state has delay before can change state, default at 3 seconds
        self.rotate_speed = 1
        # ^ End default starting value

        # check if can split unit
        self.can_split_row = False
        if np.array_split(self.subunit_list, 2)[0].size > 10 and np.array_split(self.subunit_list, 2)[1].size > 10:
            self.can_split_row = True

        self.can_split_col = False
        if np.array_split(self.subunit_list, 2, axis=1)[0].size > 10 and np.array_split(self.subunit_list, 2, axis=1)[1].size > 10:
            self.can_split_col = True

        self.auth_penalty = 0  # authority penalty
        self.tactic_effect = {}
        self.coa = coa  # coat of arm image
        team_pos_list = (self.battle.team0_pos_list, self.battle.team1_pos_list, self.battle.team2_pos_list)
        self.battle.alive_unit_list.add(self)
        self.battle.alive_unit_index.append(self.game_id)

        self.team = team  # team
        self.ally_pos_list = team_pos_list[self.team]
        if self.team == 1:
            self.enemy_pos_list = team_pos_list[2]
        elif self.team == 2:
            self.enemy_pos_list = team_pos_list[1]

        self.subunit_position_list = []
        self.frontline = {0: [], 1: [], 2: [], 3: []}  # frontline keep list of subunit at the front of each side in combat, same list index as above
        self.frontline_object = {0: [], 1: [], 2: [], 3: []}  # same as above but save object instead of index order:front, left, right, rear

        # v Set up subunit position list for drawing
        width, height = 0, 0
        subunit_number = 0  # Number of subunit based on the position in row and column
        for this_subunit in self.subunit_list.flat:
            width += self.image_size[0]
            self.subunit_position_list.append((width, height))
            subunit_number += 1
            if subunit_number >= len(self.subunit_list[0]):  # Reach the last subunit in the row, go to the next one
                width = 0
                height += self.image_size[1]
                subunit_number = 0
        # ^ End subunit position list

    def change_pos_scale(self):
        """Change position variable to new camera scale"""
        self.true_number_pos = self.number_pos * (11 - self.zoom)

    def setup_frontline(self):
        """Setup frontline array"""

        # v check if completely empty side row/col, then delete and re-adjust array
        stop_loop = False
        while stop_loop is False:  # loop until no longer find completely empty row/col
            stop_loop = True
            who_array = self.subunit_list
            full_who_array = [who_array, np.fliplr(who_array.swapaxes(0, 1)), np.rot90(who_array),
                            np.fliplr([who_array])[0]]  # rotate the array based on the side
            who_array = [who_array[0], full_who_array[1][0], full_who_array[2][0], full_who_array[3][0]]
            for index, who_frontline in enumerate(who_array):
                if any(subunit != 0 for subunit in who_frontline) is False:  # has completely empty outer row or column, remove them
                    if index == 0:  # front side
                        self.subunit_list = self.subunit_list[1:]
                        for subunit in self.subunits:
                            subunit.unit_position = (subunit.unit_position[0], subunit.unit_position[1] - (self.image_size[1] / 8))
                    elif index == 1:  # left side
                        self.subunit_list = np.delete(self.subunit_list, 0, 1)
                        for subunit in self.subunits:
                            subunit.unit_position = (subunit.unit_position[0] - (self.image_size[0] / 8), subunit.unit_position[1])
                    elif index == 2:  # right side
                        self.subunit_list = np.delete(self.subunit_list, -1, 1)
                    elif index == 3:  # rear side
                        self.subunit_list = np.delete(self.subunit_list, -1, 0)

                    if len(self.subunit_list) > 0:  # still has row left
                        old_width_box, old_height_box = self.base_width_box, self.base_height_box
                        self.base_width_box, self.base_height_box = len(self.subunit_list[0]) * (self.image_size[0] + 10) / 20, \
                                                                    len(self.subunit_list) * (self.image_size[1] + 2) / 20

                        number_pos = (self.base_pos[0] - self.base_width_box,
                                      (self.base_pos[1] + self.base_height_box))  # find position for number text
                        self.number_pos = rotation_xy(self.base_pos, number_pos, self.radians_angle)
                        self.change_pos_scale()

                        old_width_box = old_width_box - self.base_width_box
                        old_height_box = old_height_box - self.base_height_box
                        if index == 0:  # front
                            new_pos = (self.base_pos[0], self.base_pos[1] + old_height_box)
                        elif index == 1:  # left
                            new_pos = (self.base_pos[0] + old_width_box, self.base_pos[1])
                        elif index == 2:  # right
                            new_pos = (self.base_pos[0] - old_width_box, self.base_pos[1])
                        else:  # rear
                            new_pos = (self.base_pos[0], self.base_pos[1] - old_height_box)
                        self.base_pos = rotation_xy(self.base_pos, new_pos, self.radians_angle)
                        self.last_base_pos = self.base_pos

                        front_pos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
                        self.front_pos = rotation_xy(self.base_pos, front_pos, self.radians_angle)
                    stop_loop = False
        # ^ End check completely empty row

        got_another = True  # keep finding another subunit while true

        for index, who_frontline in enumerate(who_array):
            newwhofrontline = who_frontline.copy()
            dead = np.where((newwhofrontline == 0))  # replace the dead in frontline with other subunit in the same column
            for dead_subunit in dead[0]:
                run = 0
                while got_another:
                    if full_who_array[index][run, dead_subunit] != 0:
                        newwhofrontline[dead_subunit] = full_who_array[index][run, dead_subunit]
                        got_another = False
                    else:
                        run += 1
                        if len(full_who_array[index]) == run:
                            newwhofrontline[dead_subunit] = 0
                            got_another = False
                got_another = True  # reset for another loop
            empty_array = newwhofrontline
            newwhofrontline = empty_array.copy()

            self.frontline[index] = newwhofrontline

        self.frontline_object = self.frontline.copy()  # frontline array as object instead of index
        for array_index, who_frontline in enumerate(list(self.frontline.values())):
            self.frontline_object[array_index] = self.frontline_object[array_index].tolist()
            for index, stuff in enumerate(who_frontline):
                for subunit in self.subunits:
                    if subunit.game_id == stuff:
                        self.frontline_object[array_index][index] = subunit
                        break

        for subunit in self.subunits:  # assign frontline variable to subunit for only front side
            subunit.frontline = False
            if subunit in self.frontline_object[0]:
                subunit.frontline = True

        self.auth_penalty = 0
        for subunit in self.subunits:
            if subunit.state != 100:
                self.auth_penalty += subunit.auth_penalty  # add authority penalty of all alive subunit

    # def useskill(self,which_skill):
    #     #charge skill
    #     skillstat = self.skill[list(self.skill)[0]].copy()
    #     if which_skill == 0:
    #         self.skill_effect[self.charge_skill] = skillstat
    #         if skillstat[26] != 0:
    #             self.status_effect[self.charge_skill] = skillstat[26]
    #         self.skill_cooldown[self.charge_skill] = skillstat[4]
    #     # other skill
    #     else:
    #         if skillstat[1] == 1:
    #             self.skill[which_skill]
    #         self.skill_cooldown[which_skill] = skillstat[4]
    # self.skill_cooldown[which_skill] =

    def set_subunit_target(self, target="rotate", reset_path=False):
        """generate all four side, hitbox and subunit positions
        target parameter can be "rotate" for simply rotate whole unit but not move or tuple/vector2 for target position to move
        reset_path argument True will reset subunit command queue"""
        if target == "rotate":  # rotate unit before moving
            unit_topleft = pygame.Vector2(self.base_pos[0] - self.base_width_box,  # get the top left corner of sprite to generate subunit position
                                          self.base_pos[1] - self.base_height_box)

            for subunit in self.subunits:  # generate position of each subunit
                if subunit.state != 99 or (subunit.state == 99 and self.retreat_start):
                    new_target = unit_topleft + subunit.unit_position
                    if reset_path:
                        subunit.command_target.append(pygame.Vector2(
                            rotation_xy(self.base_pos, new_target, self.radians_angle)))
                    else:
                        subunit.command_target = pygame.Vector2(
                            rotation_xy(self.base_pos, new_target, self.radians_angle))  # rotate according to sprite current rotation
                        subunit.new_angle = self.new_angle

        else:  # moving unit to specific target position
            unit_topleft = pygame.Vector2(target[0] - self.base_width_box,
                                          target[1])  # get the top left corner of sprite to generate subunit position

            for subunit in self.subunits:  # generate position of each subunit
                if subunit.state != 99 or (subunit.state == 99 and self.retreat_start):
                    subunit.new_angle = self.new_angle
                    new_target = unit_topleft + subunit.unit_position
                    if reset_path:
                        subunit.command_target.append(pygame.Vector2(
                            rotation_xy(target, new_target, self.radians_angle)))
                    else:
                        subunit.command_target = pygame.Vector2(
                            rotation_xy(target, new_target, self.radians_angle))  # rotate according to sprite current rotation

    def start_set(self, subunit_group):
        """Setup various variables at the start of battle or when new unit spawn/split"""
        self.setup_unit(battle_start=False)
        self.setup_frontline()
        self.old_troop_health, self.old_troop_stamina = self.troop_number, self.stamina
        self.sprite_array = self.subunit_list
        self.leader_social = self.leader[0].social

        # v assign team leader commander to every unit in team if this is commander unit
        if self.commander:
            which_unit = self.battle.team1_unit
            if self.team == 2:  # team2
                which_unit = self.battle.team2_unit
            for this_unit in which_unit:
                this_unit.team_commander = self.leader[0]
        # ^ End assign commander

        self.auth_recal()
        self.command_buff = [(self.leader[0].melee_command - 5) * 0.1, (self.leader[0].range_command - 5) * 0.1,
                             (self.leader[0].cav_command - 5) * 0.1]  # unit leader command buff

        for subunit in subunit_group:
            self.sprite_array = np.where(self.sprite_array == subunit.game_id, subunit, self.sprite_array)

        unit_top_left = pygame.Vector2(self.base_pos[0] - self.base_width_box,
                                           # get the top left corner of sprite to generate subunit position
                                           self.base_pos[1] - self.base_height_box)
        for subunit in self.subunits:  # generate start position of each subunit
            subunit.base_pos = unit_top_left + subunit.unit_position
            subunit.base_pos = pygame.Vector2(rotation_xy(self.base_pos, subunit.base_pos, self.radians_angle))
            subunit.zoom_scale()
            subunit.base_target = subunit.base_pos
            subunit.command_target = subunit.base_pos  # rotate according to sprite current rotation
            subunit.make_front_pos()

        self.change_pos_scale()

    def update(self, weather, squad_group, dt, zoom, mouse_pos, mouse_up):
        # v Camera zoom change
        if self.last_zoom != zoom:  # camera zoom is changed
            self.zoom_change = True
            self.zoom = 11 - zoom  # save scale
            self.change_pos_scale()  # update unit sprite according to new scale
            for subunit in self.subunits:
                if self.zoom == 1:  # revert back to default layer at other zoom
                    if subunit.state != 100:
                        self.battle_camera.change_layer(subunit, 4)
            self.last_zoom = zoom
        # ^ End zoom

        # v Setup frontline again when any subunit destroyed
        if self.dead_change:
            if len(self.subunit_list) > 0 and (len(self.subunit_list) > 1 or any(subunit != 0 for subunit in self.subunit_list[0])):
                self.setup_frontline()

                for subunit in self.subunits:
                    subunit.base_morale -= (30 * subunit.mental)
                self.dead_change = False

            # v remove when troop number reach 0
            else:
                self.stamina, self.morale, self.speed = 0, 0, 0

                leader_list = [leader for leader in self.leader]  # create temp list to remove leader
                for leader in leader_list:  # leader retreat
                    if leader.state < 90:  # Leaders flee when unit destroyed
                        leader.state = 96
                        leader.gone()

                self.state = 100
            # ^ End remove
        # ^ End setup frontline when subunit destroyed

        if self.state != 100:
            self.ally_pos_list[self] = self.base_pos  # update current position to team position list

            self.selection()

            if dt > 0:  # Set timer for complex calculation that cannot happen every loop as it drop too much fps
                self.timer += dt
                self.battle.team_troop_number[self.team] += self.troop_number
                if self.timer >= 1:
                    self.setup_unit()

                    # v Find near enemy base_target
                    self.near_target = {}  # Near base_target is enemy that is nearest
                    for n, this_side in self.enemy_pos_list.items():
                        self.near_target[n] = pygame.Vector2(this_side).distance_to(self.base_pos)
                    self.near_target = {k: v for k, v in sorted(self.near_target.items(), key=lambda item: item[1])}  # sort to the closest one
                    for n in self.enemy_pos_list:
                        self.near_target[n] = self.enemy_pos_list[n]  # change back near base_target list value to vector with sorted order
                    # ^ End find near base_target

                    # v Check if any subunit still fighting, if not change to idle state
                    if self.state == 10:
                        stop_fight = True
                        for subunit in self.subunits:
                            if subunit.state == 10:
                                stop_fight = False
                                break
                        if stop_fight:
                            self.state = 0
                    # ^ End check fighting

                    self.timer -= 1  # reset timer, not reset to 0 because higher speed can cause inconsistency in update timing

                # v Recal stat involve leader if one destroyed
                if self.leader_change:
                    self.auth_recal()
                    self.command_buff = [(self.leader[0].melee_command - 5) * 0.1, (self.leader[0].range_command - 5) * 0.1,
                                         (self.leader[0].cav_command - 5) * 0.1]
                    self.leader_change = False
                # ^ End recal stat when leader destroyed

                if self.range_combat_check:
                    self.state = 11  # can only shoot if range_combat_check is true

                self.skirmish()
                self.chase()
                # v Morale/authority state function
                if self.authority <= 0:  # disobey
                    self.state = 95
                    if random.randint(0, 100) == 100 and self.leader[0].state < 90:  # chance to recover
                        self.leader[0].authority += 20
                        self.auth_recal()

                if self.morale <= 10:  # Retreat state when morale lower than 10
                    if self.state not in (98, 99):
                        self.state = 98
                    if self.retreat_start is False:
                        self.retreat_start = True

                elif self.state == 98 and self.morale >= 50:  # quit retreat when morale reach increasing limit
                    self.state = 0  # become idle, not resume previous command
                    self.retreat_start = False
                    self.retreat_way = None
                    self.process_command(self.base_pos, False, False, other_command=1)

                if self.retreat_start and self.state != 96:
                    self.retreat()

                self.rotate_logic(dt)  # Rotate Function

                if self.state not in (0, 95) and self.front_pos.distance_to(self.command_target) < 1:  # reach destination and not in combat
                    not_halt = False  # check if any subunit in combat
                    for subunit in self.subunits:
                        if subunit.state == 10:
                            not_halt = True
                        if subunit.unit_leader and subunit.state != 10:
                            not_halt = False
                            break
                    if not_halt is False:
                        self.retreat_start = False  # reset retreat
                        self.revert = False  # reset revert order
                        self.process_command(self.base_target, other_command=1)  # reset command base_target state will become 0 idle

                # v Perform range melee_attack, can only enter range melee_attack state after finishing rotate
                shoot_range = self.max_range
                if self.use_min_range == 0:  # use minimum range to shoot
                    shoot_range = self.min_range

                if self.state in (5, 6) and self.move_rotate is False and (
                        (self.attack_target is not None and self.base_pos.distance_to(self.attack_target.base_pos) <= shoot_range)
                        or self.base_pos.distance_to(self.base_attack_pos) <= shoot_range):  # in shoot range
                    self.set_target(self.front_pos)
                    self.range_combat_check = True  # set range combat check to start shooting
                elif self.state == 11 and self.attack_target is not None and self.base_pos.distance_to(self.attack_target.base_pos) > shoot_range \
                        and self.hold == 0 and self.collide is False:  # chase base_target if it go out of range and hold condition not hold
                    self.state = self.command_state  # set state to melee_attack command state
                    self.range_combat_check = False  # stop range combat check
                    self.set_target(self.attack_target.base_pos)  # move to new base_target
                    self.new_angle = self.set_rotate()  # also keep rotate to base_target
                # ^ End range melee_attack state

        else:  # destroyed unit
            if self.got_killed is False:
                self.destroyed(self.battle)
                self.battle.event_log.add_log([0, str(self.leader[0].name) + "'s unit is destroyed"],
                                              [0, 1])  # put destroyed event in troop and army log
                self.kill()
                for subunit in self.subunits:
                    subunit.kill()

    def set_target(self, pos):
        """set new base_target, scale base_target from base_target according to zoom scale"""
        self.base_target = pygame.Vector2(pos)  # Set new base base_target
        self.set_subunit_target(self.base_target)

    def process_command(self, target_pos, run_command=False, revert_move=False, enemy=None, other_command=0):
        """Process input order into state and subunit base_target action
        other_command parameter 0 is default command, 1 is natural pause, 2 is order pause"""
        if other_command == 0:  # move or melee_attack command
            self.state = 1

            if self.attack_place or (enemy is not None and (self.team != enemy.team)):  # melee_attack
                if self.ammo <= 0 or self.forced_melee:  # no magazine_left to shoot or forced melee_attack command
                    self.state = 3  # move to melee
                elif self.ammo > 0:  # have magazine_left to shoot
                    self.state = 5  # Move to range melee_attack
                if self.attack_place:  # melee_attack specific location
                    self.set_target(target_pos)
                    # if self.magazine_left > 0:
                    self.base_attack_pos = target_pos
                else:
                    self.attack_target = enemy
                    self.base_attack_pos = enemy.base_pos
                    self.set_target(self.base_attack_pos)

            else:
                self.set_target(target_pos)

            if run_command or self.run_toggle == 1:
                self.state += 1  # run state

            self.command_state = self.state

            self.range_combat_check = False
            self.command_target = self.base_target
            self.new_angle = self.set_rotate()

            if revert_move:  # revert subunit without rotate, cannot run in this state
                self.revert_move()
                # if runcommand or self.run_toggle:
                #     self.state -= 1

            if self.charging:  # change order when attacking will cause authority penalty
                self.leader[0].authority -= self.auth_penalty
                self.auth_recal()

        elif other_command in (1, 2) and self.state != 10:  # Pause all action command except combat
            if self.charging and other_command == 2:  # halt order instead of auto halt
                self.leader[0].authority -= self.auth_penalty  # decrease authority of the first leader for stop charge
                self.auth_recal()  # recal authority

            self.state = 0  # go into idle state
            self.command_state = self.state  # reset command state
            self.set_target(self.front_pos)  # set base_target at self
            self.command_target = self.base_target  # reset command base_target
            self.range_combat_check = False  # reset range combat check
            self.new_angle = self.set_rotate()  # set rotation base_target

    def process_retreat(self, pos):
        self.state = 96  # controlled retreat state (not same as 98)
        self.command_state = self.state  # command retreat
        self.leader[0].authority -= self.auth_penalty  # retreat reduce start_set leader authority
        if self.charging:  # change order when attacking will cause authority penalty
            self.leader[0].authority -= self.auth_penalty
        self.auth_recal()
        self.retreat_start = True  # start retreat process
        self.set_target(pos)
        self.revert_move()
        self.command_target = self.base_target

    def placement(self, mouse_pos, mouse_right, mouse_rightdown, double_mouse_right):
        if double_mouse_right:  # move unit to new pos
            self.base_pos = mouse_pos
            self.last_base_pos = self.base_pos

        elif mouse_right or mouse_rightdown:  # rotate unit
            self.angle = self.set_rotate(mouse_pos)
            self.new_angle = self.angle
            self.radians_angle = math.radians(360 - self.angle)  # for subunit rotate
            if self.angle < 0:  # negative angle (rotate to left side)
                self.radians_angle = math.radians(-self.angle)

        front_pos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
        self.front_pos = rotation_xy(self.base_pos, front_pos, self.radians_angle)
        number_pos = (self.base_pos[0] - self.base_width_box,
                      (self.base_pos[1] + self.base_height_box))  # find position for number text
        self.number_pos = rotation_xy(self.base_pos, number_pos, self.radians_angle)
        self.change_pos_scale()

        self.base_target = self.base_pos
        self.command_target = self.base_target  # reset command base_target
        unit_topleft = pygame.Vector2(self.base_pos[0] - self.base_width_box,
                                      # get the top left corner of sprite to generate subunit position
                                      self.base_pos[1] - self.base_height_box)

        for subunit in self.subunits:  # generate position of each subunit
            new_target = unit_topleft + subunit.unit_position
            subunit.base_pos = pygame.Vector2(
                rotation_xy(self.base_pos, new_target, self.radians_angle))  # rotate according to sprite current rotation
            subunit.zoom_scale()
            subunit.angle = self.angle
            subunit.rotate()

        self.process_command(self.base_pos, double_mouse_right, self.revert, self.base_target, 1)

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.icon
            del self.team_commander
            del self.start_where
            del self.subunits
            del self.near_target
            del self.leader
            del self.frontline_object
            del self.attack_target
            del self.leader_subunit
