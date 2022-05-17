import numpy as np
import pygame

from gamescript.common import utility

rotation_xy = utility.rotation_xy


def destroyed(self, battle, morale_hit=True):
    """remove unit when it dies"""
    group = battle.all_team_unit[self.team]
    enemy_group = [this_unit for this_unit in battle.all_team_unit["alive"] if this_unit.team != self.team]

    battle.team_pos_list[self.team].pop(self)

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

    battle.all_team_unit["alive"].remove(self)
    group.remove(self)
    self.got_killed = True

    self.battle.setup_unit_icon()  # reset army icon (remove dead one)


def move_leader_subunit(this_leader, old_army_subunit, new_army_subunit, already_pick=()):
    """old_army_subunit is subunit_list list that the subunit currently in and need to be move out to the new one (new_army_subunit),
    already_pick is list of position need to be skipped"""
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
    """Check if unit can be splitted, if not remove splitting button"""
    # v split by middle column
    if np.array_split(who.subunit_list, 2, axis=1)[0].size >= 10 and np.array_split(who.subunit_list, 2, axis=1)[1].size >= 10 and \
            who.leader[1].name != "None":  # can only split if both unit size will be larger than 10 and second leader exist
        self.battle_ui_updater.add(self.col_split_button)
    elif self.col_split_button in self.battle_ui_updater:
        self.battle_ui_updater.remove(self.col_split_button)
    # ^ End col

    # v split by middle row
    if np.array_split(who.subunit_list, 2)[0].size >= 10 and np.array_split(who.subunit_list, 2)[1].size >= 10 and \
            who.leader[1].name != "None":
        self.battle_ui_updater.add(self.row_split_button)
    elif self.row_split_button in self.battle_ui_updater:
        self.battle_ui_updater.remove(self.row_split_button)


def split_unit(battle, who, how):
    """split unit either by row or column into two seperate unit"""  # TODO check split when moving
    from gamescript import unit, leader
    from gamescript.tactical.subunit import fight
    from gamescript.tactical.battle import setup

    move_leader_subunit = fight.move_leader_subunit
    add_new_unit = setup.split_new_unit

    if how == 0:  # split by row
        new_army_subunit = np.array_split(who.subunit_list, 2)[1]
        who.subunit_list = np.array_split(who.subunit_list, 2)[0]
        new_pos = pygame.Vector2(who.base_pos[0], who.base_pos[1] + (who.base_height_box / 2))
        new_pos = rotation_xy(who.base_pos, new_pos, who.radians_angle)  # new unit pos (back)
        base_pos = pygame.Vector2(who.base_pos[0], who.base_pos[1] - (who.base_height_box / 2))
        who.base_pos = rotation_xy(who.base_pos, base_pos, who.radians_angle)  # new position for original unit (front)
        who.base_height_box /= 2

    else:  # split by column
        new_army_subunit = np.array_split(who.subunit_list, 2, axis=1)[1]
        who.subunit_list = np.array_split(who.subunit_list, 2, axis=1)[0]
        new_pos = pygame.Vector2(who.base_pos[0] + (who.base_width_box / 3.3), who.base_pos[1])  # 3.3 because 2 make new unit position overlap
        new_pos = rotation_xy(who.base_pos, new_pos, who.radians_angle)  # new unit pos (right)
        base_pos = pygame.Vector2(who.base_pos[0] - (who.base_width_box / 2), who.base_pos[1])
        who.base_pos = rotation_xy(who.base_pos, base_pos, who.radians_angle)  # new position for original unit (left)
        who.base_width_box /= 2
        frontpos = (who.base_pos[0], (who.base_pos[1] - who.base_height_box))  # find new front position of unit
        who.front_pos = rotation_xy(who.base_pos, frontpos, who.radians_angle)
        who.set_target(who.front_pos)

    if who.leader[
        1].subunit.game_id not in new_army_subunit.flat:  # move the left sub-general leader subunit if it not in new one
        who.subunit_list, new_army_subunit, new_position = move_leader_subunit(who.leader[1], who.subunit_list, new_army_subunit)
        who.leader[1].subunit_pos = new_position[0] * new_position[1]
    who.leader[1].subunit.unit_leader = True  # make the sub-unit of this leader a start_set leader sub-unit

    already_pick = []
    for this_leader in (who.leader[0], who.leader[2], who.leader[3]):  # move other leader subunit to original one if they are in new one
        if this_leader.subunit.game_id not in who.subunit_list:
            new_army_subunit, who.subunit_list, new_position = move_leader_subunit(this_leader, new_army_subunit,
                                                                                who.subunit_list, already_pick)
            this_leader.subunit_pos = new_position[0] * new_position[1]
            already_pick.append(new_position)

    new_leader = [who.leader[1], leader.Leader(1, 0, 1, who, battle.leader_data), leader.Leader(1, 0, 2, who, battle.leader_data),
                  leader.Leader(1, 0, 3, who, battle.leader_data)]  # create new leader list for new unit

    who.subunit_position_list = []

    width, height = 0, 0
    subunit_number = 0  # Number of subunit based on the position in row and column
    for this_subunit in who.subunit_list.flat:
        width += who.image_size[0]
        who.subunit_position_list.append((width, height))
        subunit_number += 1
        if subunit_number >= len(who.subunit_list[0]):  # Reach the last subunit in the row, go to the next one
            width = 0
            height += who.image_size[1]
            subunit_number = 0

    # v Sort so the new leader subunit position match what set before
    subunit_sprite = [this_subunit for this_subunit in who.subunits if
                      this_subunit.game_id in new_army_subunit.flat]  # new list of sprite not sorted yet
    new_subunit_sprite = []
    for this_id in new_army_subunit.flat:
        for this_subunit in subunit_sprite:
            if this_id == this_subunit.game_id:
                new_subunit_sprite.append(this_subunit)

    subunit_sprite = [this_subunit for this_subunit in who.subunits if
                      this_subunit.game_id in who.subunit_list.flat]
    who.subunits = []
    for this_id in who.subunit_list.flat:
        for this_subunit in subunit_sprite:
            if this_id == this_subunit.game_id:
                who.subunits.append(this_subunit)
    # ^ End sort

    # v Reset position of subunit in inspect_ui for both old and new unit
    for sprite in (who.subunits, new_subunit_sprite):
        width, height = 0, 0
        subunit_number = 0
        for this_subunit in sprite:
            width += battle.icon_sprite_width

            if subunit_number >= len(who.subunit_list[0]):
                width = 0
                width += battle.icon_sprite_width
                height += battle.icon_sprite_height
                subunit_number = 0

            this_subunit.inspect_pos = (width + battle.inspect_ui_pos[0], height + battle.inspect_ui_pos[1])
            this_subunit.rect = this_subunit.image.get_rect(topleft=this_subunit.inspect_pos)
            this_subunit.pos = pygame.Vector2(this_subunit.rect.centerx, this_subunit.rect.centery)
            subunit_number += 1
    # ^ End reset position

    # v Change the original unit stat and sprite
    original_leader = [who.leader[0], who.leader[2], who.leader[3], leader.Leader(1, 0, 3, who, battle.leader_data)]
    for index, this_leader in enumerate(original_leader):  # Also change army position of all leader in that unit
        this_leader.army_position = index  # Change army position to new one
        this_leader.image_position = this_leader.base_image_position[this_leader.army_position]
        this_leader.rect = this_leader.image.get_rect(center=this_leader.image_position)
    team_commander = who.team_commander
    who.team_commander = team_commander
    who.leader = original_leader

    add_new_unit(battle, who, False)
    # ^ End change original unit

    # v start making new unit
    new_game_id = battle.all_team_unit["alive"][-1].game_id + 1

    new_unit = unit.Unit(start_pos=new_pos, gameid=new_game_id, squadlist=new_army_subunit, colour=who.colour,
                         control=who.control, coa=who.coa_list, commander=False, startangle=who.angle, team=who.team)

    battle.all_team_unit[who.team].add(new_unit)
    new_unit.team_commander = team_commander
    new_unit.leader = new_leader
    new_unit.subunits = new_subunit_sprite

    for this_subunit in new_unit.subunits:
        this_subunit.unit = new_unit

    for index, this_leader in enumerate(new_unit.leader):  # Change army position of all leader in new unit
        this_leader.unit = new_unit  # Set leader unit to new one
        this_leader.army_position = index  # Change army position to new one
        this_leader.image_position = this_leader.base_image_position[this_leader.army_position]  # Change image pos
        this_leader.rect = this_leader.image.get_rect(center=this_leader.image_position)
        this_leader.pos_change_stat(this_leader)  # Change stat based on new army position

    add_new_unit(battle, new_unit)
    # ^ End making new unit


def skirmish(self):
    # v skirmishing
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
    # v Chase base_target and rotate accordingly
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
            self.base_attack_pos = None
            self.process_command(self.front_pos, other_command=1)
    # ^ End chase


def retreat(self):
    if self.retreat_way is None:  # not yet start retreat or previous retreat way got blocked
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
        self.retreat_way = [rotation_xy(self.base_pos, self.retreat_way, self.radians_angle), this_index]
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
