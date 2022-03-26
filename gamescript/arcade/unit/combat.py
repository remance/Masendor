import numpy as np
import pygame


def destroyed(self, battle, morale_hit=True):
    """remove unit when it dies"""
    if self.team == 1:
        group = battle.team1_unit
        enemy_group = battle.team2_unit
        battle.team1_pos_list.pop(self)
    else:
        group = battle.team2_unit
        enemy_group = battle.team1_unit
        battle.team2_pos_list.pop(self)

    if morale_hit:
        if self.commander:  # more morale penalty if the unit is a command unit
            for army in group:
                for this_subunit in army.subunits:
                    this_subunit.base_morale -= 30

        for this_army in enemy_group:  # get bonus authority to the another army
            this_army.authority += 5

        for this_army in group:  # morale dmg to every subunit in army when allied unit destroyed
            for this_subunit in this_army.subunits:
                this_subunit.base_morale -= 20

    battle.alive_unit_list.remove(self)
    battle.alive_unit_index.remove(self.game_id)
    group.remove(self)
    self.got_killed = True

    self.battle.setup_unit_icon()  # reset army icon (remove dead one)


def move_leader_subunit(this_leader, old_army_subunit, new_army_subunit, already_pick=()):
    """dold_army_subunit is subunit_list list that the subunit currently in and need to be move out to the new one (new_army_subunit),
    already_pick is list of position need to be skippe"""
    replace = [np.where(old_army_subunit == this_leader.subunit.game_id)[0][0],
               np.where(old_army_subunit == this_leader.subunit.game_id)[1][0]]  # grab old array position of subunit
    new_row = int((len(new_army_subunit) - 1) / 2)  # set up new row subunit will be place in at the middle at the start
    new_place = int((len(new_army_subunit[new_row]) - 1) / 2)  # setup new column position
    place_done = False  # finish finding slot to place yet

    while place_done is False:
        if this_leader.subunit.unit.subunit_list.flat[new_row * new_place] != 0:
            for this_subunit in this_leader.subunit.unit.subunits:
                if this_subunit.game_id == this_leader.subunit.unit.subunit_list.flat[new_row * new_place]:
                    if this_subunit.leader is not None or (new_row, new_place) in already_pick:
                        new_place += 1
                        if new_place > len(new_army_subunit[new_row]) - 1:  # find new column
                            new_place = 0
                        elif new_place == int(
                                len(new_army_subunit[new_row]) / 2):  # find in new row when loop back to the first one
                            new_row += 1
                        place_done = False
                    else:  # found slot to replace
                        place_done = True
                        break
        else:  # fill in the subunit if the slot is empty
            place_done = True

    old_army_subunit[replace[0]][replace[1]] = new_army_subunit[new_row][new_place]
    new_army_subunit[new_row][new_place] = this_leader.subunit.game_id
    new_position = (new_place, new_row)
    return old_army_subunit, new_army_subunit, new_position


def check_split(self, who):
    """No split unit function in arcade mode"""
    pass


def split_unit(**args):
    """No split unit function in arcade mode"""
    pass


def auth_recal(self):
    """Not used in arcade mode since authority calculated from only one leader in the unit"""
    pass


def skirmish(self):
    # v skirmishing  # TODO change to AI related and not auto
    if self.hold == 1 and self.state not in (97, 98, 99):
        min_range = self.min_range  # run away from enemy that reach minimum range
        if min_range < 50:
            min_range = 50  # for in case min_range is 0 (melee troop only)
        target_list = list(self.near_target.values())
        if len(target_list) > 0 and target_list[0].distance_to(self.base_pos) <= min_range:  # if there is any enemy in minimum range
            self.state = 96  # retreating
            base_target = self.base_pos - ((list(self.near_target.values())[0] - self.base_pos) / 5)  # generate base_target to run away

            if base_target[0] < 1:  # can't run away when reach corner of map same for below if elif
                base_target[0] = 1
            elif base_target[0] > 998:
                base_target[0] = 998
            if base_target[1] < 1:
                base_target[1] = 1
            elif base_target[1] > 998:
                base_target[1] = 998

            self.process_command(base_target, True, True)  # set base_target position to run away
    # ^ End skirmishing


def chase(self):
    # v Chase base_target and rotate accordingly  # TODO change to AI related and not auto
    if self.state in (3, 4, 5, 6, 10) and self.command_state in (3, 4, 5, 6) and self.attack_target is not None and self.hold == 0:
        if self.attack_target.state != 100:
            if self.collide is False:
                self.state = self.command_state  # resume melee_attack command
                if self.base_pos.distance_to(self.attack_target.base_pos) < 10:
                    self.set_target(self.attack_target.leader_subunit.base_pos)  # set base_target to cloest enemy's side
                else:
                    self.set_target(self.attack_target.base_pos)
                self.base_attack_pos = self.base_target
                self.new_angle = self.set_rotate()  # keep rotating while chasing
        else:  # enemy dead stop chasing
            self.attack_target = None
            self.base_attack_pos = 0
            self.process_command(self.front_pos, other_command=1)
    # ^ End chase


def retreat(self):
    if self.retreat_way is None:  # not yet start retreat or previous retreat way got blocked  # TODO change to AI related and not auto
        retreat_side = (
            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[0] if subunit != 0) + 2,
            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[1] if subunit != 0) + 1,
            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[2] if subunit != 0) + 1,
            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[3] if subunit != 0))

        this_index = retreat_side.index(min(retreat_side))  # find side with least subunit fighting to retreat, rear always prioritised
        if this_index == 0:  # front
            self.retreat_way = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find position to retreat
        elif this_index == 1:  # left
            self.retreat_way = (self.base_pos[0] - self.base_width_box, self.base_pos[1])  # find position to retreat
        elif this_index == 2:  # right
            self.retreat_way = (self.base_pos[0] + self.base_width_box, self.base_pos[1])  # find position to retreat
        else:  # rear
            self.retreat_way = (self.base_pos[0], (self.base_pos[1] + self.base_height_box))  # find rear position to retreat
        self.retreat_way = [rotationxy(self.base_pos, self.retreat_way, self.radians_angle), this_index]
        base_target = self.base_pos + ((self.retreat_way[0] - self.base_pos) * 1000)

        self.process_retreat(base_target)
        # if random.randint(0, 100) > 99:  # change side via surrender or betrayal
        #     if self.team == 1:
        #         self.battle.allunitindex = self.switchfaction(self.battle.team1_unit, self.battle.team2_unit,
        #                                                         self.battle.team1_pos_list, self.battle.allunitindex,
        #                                                         self.battle.enactment)
        #     else:
        #         self.battle.allunitindex = self.switchfaction(self.battle.team2_unit, self.battle.team1_unit,
        #                                                         self.battle.team2_pos_list, self.battle.allunitindex,
        #                                                         self.battle.enactment)
        #     self.battle.event_log.addlog([0, str(self.leader[0].name) + "'s unit surrender"], [0, 1])
        #     self.battle.setuparmyicon()


def switch_faction(self, old_group, new_group, old_pos_list, enactment):
    """Change army group and game_id when change side"""
    self.colour = (144, 167, 255)  # team1 colour
    self.control = True  # TODO need to change later when player can choose team

    if self.team == 2:
        self.team = 1  # change to team 1
    else:  # originally team 1, new team would be 2
        self.team = 2  # change to team 2
        self.colour = (255, 114, 114)  # team2 colour
        if enactment is False:
            self.control = False

    old_group.remove(self)  # remove from old team group
    new_group.append(self)  # add to new team group
    old_pos_list.pop(self.game_id)  # remove from old pos list
    # self.changescale() # reset scale to the current zoom
    self.icon.change_image(change_side=True)  # change army icon to new team
