import math
import random

import numpy as np
import pygame
import pygame.freetype
from gamescript import script_common
from gamescript.tactical import script_other
from gamescript.tactical.unit import combat
from pygame.transform import scale

rotationxy = script_common.rotation_xy

class DirectionArrow(pygame.sprite.Sprite):  # TODO make it work so it can be implemented again
    def __init__(self, who):
        """Layer must be called before sprite_init"""
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.who = who
        self.pos = self.who.pos
        self.who.direction_arrow = self
        self.length_gap = self.who.image.get_height() / 2
        self.length = self.who.pos.distance_to(self.who.base_target) + self.length_gap
        self.previous_length = self.length
        self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        # self.image_original = self.image.copy()
        # pygame.draw.line(self.image, (0, 0, 0), (self.image.get_width()/2, 0),(self.image.get_width()/2,self.image.get_height()), 5)
        self.image = pygame.transform.rotate(self.image, self.who.angle)
        self.rect = self.image.get_rect(midbottom=self.who.front_pos)

    def update(self, zoom):
        self.length = self.who.pos.distance_to(self.who.base_target) + self.length_gap
        distance = self.who.front_pos.distance_to(self.who.base_target) + self.length_gap
        if self.length != self.previous_length and distance > 2 and self.who.state != 0:
            self.pos = self.who.pos
            self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
            self.image.fill((0, 0, 0))
            self.image = pygame.transform.rotate(self.image, self.who.angle)
            self.rect = self.image.get_rect(midbottom=self.who.front_pos)
            self.previous_length = self.length
        elif distance < 2 or self.who.state in (0, 10, 11, 100):
            self.who.direction_arrow = False
            self.kill()


class TroopNumber(pygame.sprite.Sprite):
    def __init__(self, screen_scale, who):
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.screen_scale = screen_scale
        self.who = who
        self.text_colour = pygame.Color("blue")
        if self.who.team == 2:
            self.text_colour = pygame.Color("red")
        self.pos = self.who.true_number_pos
        self.number = self.who.troop_number
        self.zoom = 0

        self.font = pygame.font.SysFont("timesnewroman", int(12 * self.screen_scale[1]))

        self.image = self.render(str(self.number), self.font, self.text_colour)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, *args, **kwargs) -> None:
        if self.pos != self.who.true_number_pos:  # new position
            self.pos = self.who.true_number_pos
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.zoom != args[2]:  # zoom argument
            self.zoom = int(args[2])
            zoom = (11 - self.zoom) / 2
            if zoom < 1:
                zoom = 1
            new_font_size = int(60 / zoom * self.screen_scale[1])
            self.font = pygame.font.SysFont("timesnewroman", new_font_size)
            self.image = self.render(str(self.number), self.font, self.text_colour)
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.number != self.who.troop_number:  # new troop number
            self.number = self.who.troop_number
            self.image = self.render(str(self.number), self.font, self.text_colour)
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.who.state == 100:
            self.kill()
            self.delete()

    def circle_points(self, r):
        """Calculate text point to add background"""
        circle_cache = {}
        r = int(round(r))
        if r in circle_cache:
            return circle_cache[r]
        x, y, e = r, 0, 1 - r
        circle_cache[r] = points = []
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points

    def render(self, text, font, gf_colour=pygame.Color("black"), o_colour=(255, 255, 255), opx=2):
        """Render text with background border"""
        text_surface = font.render(text, True, gf_colour).convert_alpha()
        w = text_surface.get_width() + 2 * opx
        h = font.get_height()

        osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
        osurf.fill((0, 0, 0, 0))

        surface = osurf.copy()

        osurf.blit(font.render(text, True, o_colour).convert_alpha(), (0, 0))

        for dx, dy in self.circle_points(opx):
            surface.blit(osurf, (dx + opx, dy + opx))

        surface.blit(text_surface, (opx, opx))

        return surface

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.who


class Unit(pygame.sprite.Sprite):
    images = []
    status_list = None  # status effect list
    max_zoom = 10  # max zoom allow
    battle = None
    destroyed = combat.destroyed  # destroyed script
    set_rotate = script_common.set_rotate
    form_change_timer = 10
    image_size = None

    def __init__(self, start_pos, game_id, subunit_list, colour, control, coa, commander, start_angle, start_hp=100, start_stamina=100, team=0):
        """Although unit in code, this is referred as subunit ingame"""
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icon = None  # for linking with army selection ui, got linked when icon created in game_ui.ArmyIcon
        self.team_commander = None  # commander leader
        self.start_where = []
        self.subunit_sprite_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
        self.subunit_sprite = []
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
        self.base_attack_pos = 0  # position of attack base_target
        self.angle = start_angle  # start at this angle
        if self.angle == 360:  # 360 is 0 angle at the start, not doing this cause angle glitch when self start
            self.angle = 0
        self.new_angle = self.angle
        self.radians_angle = math.radians(360 - start_angle)  # radians for apply angle to position (allsidepos and subunit)
        front_pos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
        self.front_pos = rotationxy(self.base_pos, front_pos, self.radians_angle)
        self.movement_queue = []
        self.base_target = self.front_pos
        self.command_target = self.front_pos
        number_pos = (self.base_pos[0] - self.base_width_box,
                     (self.base_pos[1] + self.base_height_box))  # find position for number text
        self.number_pos = rotationxy(self.base_pos, number_pos, self.radians_angle)
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
        self.forced_melee = False  # Force unit to melee attack
        self.attack_place = False  # attack position instead of enemy
        self.forcedmarch = False
        self.change_faction = False  # For initiating change faction function
        self.run_toggle = 0  # 0 = double right click to run, 1 = only one right click will make unit run
        self.shoot_mode = 0  # 0 = both arc and non-arc shot, 1 = arc shot only, 2 = forbid arc shot
        self.attack_mode = 0  # frontline attack, 1 = formation attack, 2 = free for all attack,
        self.hold = 0  # 0 = not hold, 1 = skirmish/scout/avoid, 2 = hold
        self.fire_at_will = 0  # 0 = fire at will, 1 = no fire
        self.retreat_start = False
        self.retreat_way = None
        self.collide = False  # for checking if subunit collide, if yes then stop moving
        self.range_combat_check = False
        self.attack_target = None  # attack base_target, can be either int or unit object
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
        self.battle.all_unit_list.append(self)
        self.battle.all_unit_index.append(self.game_id)

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
        for subunit in self.subunit_list.flat:
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

    def setup_army(self, battle_start=True):
        """Grab stat from all subunit in the unit"""
        self.troop_number = 0
        self.stamina = 0
        self.morale = 0
        all_speed = []  # list of subunit speed, use to get the slowest one
        self.ammo = 0
        how_many = 0
        all_shoot_range = []  # list of shoot range, use to get the shortest and longest one

        # v Grab subunit stat
        not_broken = False
        for subunit in self.subunit_sprite:
            if subunit.state != 100:  # only get stat from alive subunit
                self.troop_number += subunit.troop_number
                self.stamina += subunit.stamina
                self.morale += subunit.morale
                all_speed.append(subunit.speed)
                self.ammo += subunit.magazine_left
                if subunit.shoot_range > 0:
                    all_shoot_range.append(subunit.shoot_range)
                subunit.skill_cond = self.skill_cond
                how_many += 1
                if subunit.state != 99:  # check if unit completely broken
                    not_broken = True
        self.troop_number = int(self.troop_number)  # convert to int to prevent float decimal

        if not_broken is False:
            self.state = 99  # completely broken
            self.can_split_row = False  # can not split unit
            self.can_split_col = False
        # ^ End grab subunit stat

        # v calculate stat for unit related calculation
        if self.troop_number > 0:
            self.stamina = self.stamina / how_many  # Average stamina of all subunit
            self.morale = self.morale / how_many  # Average morale of all subunit
            self.speed = min(all_speed)  # use the slowest subunit
            self.walk_speed, self.runs_peed = self.speed / 20, self.speed / 15
            if self.state in (1, 3, 5):
                self.rotate_speed = self.walk_speed * 50 / (len(self.subunit_list[0]) * len(
                    self.subunit_list))  # rotate speed is based on move speed and unit block size (not subunit total number)
            else:
                self.rotate_speed = self.runs_peed * 50 / (len(self.subunit_list[0]) * len(self.subunit_list))

            if self.rotate_speed > 20:
                self.rotate_speed = 20  # state 10 melee combat rotate is auto placement
            if self.rotate_speed < 1:  # no less than speed 1, it will be too slow or can't rotate with speed 0
                self.rotate_speed = 1

            if len(all_shoot_range) > 0:
                self.max_range = max(all_shoot_range)  # Max shoot range of all subunit
                self.min_range = min(all_shoot_range)  # Min shoot range of all subunit
            if battle_start is False:  # Only do once when self start
                self.max_stamina = self.stamina
                self.last_health_state, self.last_stamina_state = 4, 4
                self.max_morale = self.morale
                self.max_health = self.troop_number
            self.morale_state = 100
            self.stamina_state = 100
            if self.max_morale != float("inf"):
                self.morale_state = round((self.morale * 100) / self.max_morale)
            if self.max_stamina != float("inf"):
                self.stamina_state = round((self.stamina * 100) / self.max_stamina)
        # ^ End cal stat

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
                        for subunit in self.subunit_sprite:
                            subunit.unit_position = (subunit.unit_position[0], subunit.unit_position[1] - (self.image_size[1] / 8))
                    elif index == 1:  # left side
                        self.subunit_list = np.delete(self.subunit_list, 0, 1)
                        for subunit in self.subunit_sprite:
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
                        self.number_pos = rotationxy(self.base_pos, number_pos, self.radians_angle)
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
                        self.base_pos = rotationxy(self.base_pos, new_pos, self.radians_angle)
                        self.last_base_pos = self.base_pos

                        front_pos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
                        self.front_pos = rotationxy(self.base_pos, front_pos, self.radians_angle)
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
                for subunit in self.subunit_sprite:
                    if subunit.game_id == stuff:
                        self.frontline_object[array_index][index] = subunit
                        break

        for subunit in self.subunit_sprite:  # assign frontline variable to subunit for only front side
            subunit.frontline = False
            if subunit in self.frontline_object[0]:
                subunit.frontline = True

        self.auth_penalty = 0
        for subunit in self.subunit_sprite:
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

            for subunit in self.subunit_sprite:  # generate position of each subunit
                if subunit.state != 99 or (subunit.state == 99 and self.retreat_start):
                    new_target = unit_topleft + subunit.unit_position
                    if reset_path:
                        subunit.command_target.append(pygame.Vector2(
                            rotationxy(self.base_pos, new_target, self.radians_angle)))
                    else:
                        subunit.command_target = pygame.Vector2(
                            rotationxy(self.base_pos, new_target, self.radians_angle))  # rotate according to sprite current rotation
                        subunit.new_angle = self.new_angle

        else:  # moving unit to specific target position
            unit_topleft = pygame.Vector2(target[0] - self.base_width_box,
                                          target[1])  # get the top left corner of sprite to generate subunit position

            for subunit in self.subunit_sprite:  # generate position of each subunit
                if subunit.state != 99 or (subunit.state == 99 and self.retreat_start):
                    subunit.new_angle = self.new_angle
                    new_target = unit_topleft + subunit.unit_position
                    if reset_path:
                        subunit.command_target.append(pygame.Vector2(
                            rotationxy(target, new_target, self.radians_angle)))
                    else:
                        subunit.command_target = pygame.Vector2(
                            rotationxy(target, new_target, self.radians_angle))  # rotate according to sprite current rotation

    def auth_recal(self):
        """recalculate authority from all alive leaders"""
        self.authority = (self.leader[0].authority / 2) + (self.leader[1].authority / 4) + \
                         (self.leader[2].authority / 4) + (self.leader[3].authority / 10)
        self.leader_social = self.leader[0].social
        if self.authority > 0:
            big_army_size = self.subunit_list > 0
            big_army_size = big_army_size.sum()
            if big_army_size > 20:  # army size larger than 20 will reduce gamestart leader authority
                self.authority = (self.team_commander.authority / 2) + (self.leader[0].authority / 2 * (100 - big_army_size) / 100) + \
                                 (self.leader[1].authority / 2) + (self.leader[2].authority / 2) + (self.leader[3].authority / 4)
            else:
                self.authority = self.authority + (self.team_commander.authority / 2)

    def start_set(self, subunit_group):
        """Setup various variables at the start of battle or when new unit spawn/split"""
        self.setup_army(False)
        self.setup_frontline()
        self.oldarmyhealth, self.oldarmystamina = self.troop_number, self.stamina
        self.sprite_array = self.subunit_list
        self.leader_social = self.leader[0].social

        # v assign team leader commander to every unit in team if this is commander unit
        if self.commander:
            which_army = self.battle.team1_unit
            if self.team == 2:  # team2
                which_army = self.battle.team2_unit
            for army in which_army:
                army.team_commander = self.leader[0]
        # ^ End assign commander

        self.auth_recal()
        self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                            (self.leader[0].cavcommand - 5) * 0.1]  # unit leader command buff

        for subunit in subunit_group:
            self.sprite_array = np.where(self.sprite_array == subunit.game_id, subunit, self.sprite_array)

        unit_top_left = pygame.Vector2(self.base_pos[0] - self.base_width_box,
                                           # get the top left corner of sprite to generate subunit position
                                           self.base_pos[1] - self.base_height_box)
        for subunit in self.subunit_sprite:  # generate start position of each subunit
            subunit.base_pos = unit_top_left + subunit.unit_position
            subunit.base_pos = pygame.Vector2(rotationxy(self.base_pos, subunit.base_pos, self.radians_angle))
            subunit.pos = subunit.base_pos * subunit.zoom
            subunit.rect.center = subunit.pos
            subunit.base_target = subunit.base_pos
            subunit.command_target = subunit.base_pos  # rotate according to sprite current rotation
            subunit.make_front_pos()

        self.change_pos_scale()

    def update(self, weather, squadgroup, dt, zoom, mousepos, mouseup):
        # v Camera zoom change
        if self.last_zoom != zoom:
            if self.last_zoom != zoom:  # camera zoom is changed
                self.last_zoom = zoom
                self.zoom_change = True
                self.zoom = 11 - zoom  # save scale
                self.change_pos_scale()  # update unit sprite according to new scale
        # ^ End zoom

        # v Setup frontline again when any subunit destroyed
        if self.dead_change:
            if len(self.subunit_list) > 0 and (len(self.subunit_list) > 1 or any(subunit != 0 for subunit in self.subunit_list[0])):
                self.setup_frontline()

                for subunit in self.subunit_sprite:
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
            self.ally_pos_list[self.game_id] = self.base_pos  # update current position to team position list

            if self.just_selected:  # add highlight to subunit in selected unit
                for subunit in self.subunit_sprite:
                    subunit.zoom_scale()
                self.just_selected = False

            elif self.selected and self.battle.last_selected != self:  # no longer selected
                self.selected = False
                for subunit in self.subunit_sprite:  # remove highlight
                    subunit.image_original = subunit.image_original2.copy()
                    subunit.rotate()
                    subunit.selected = False

            if dt > 0:  # Set timer for complex calculation that cannot happen every loop as it drop too much fps
                self.timer += dt
                self.battle.team_troopnumber[self.team] += self.troop_number
                if self.timer >= 1:
                    self.setup_army()

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
                        for subunit in self.subunit_sprite:
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
                    self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                                        (self.leader[0].cavcommand - 5) * 0.1]
                    self.leader_change = False
                # ^ End recal stat when leader destroyed

                if self.range_combat_check:
                    self.state = 11  # can only shoot if range_combat_check is true

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

                # v Chase base_target and rotate accordingly
                if self.state in (3, 4, 5, 6, 10) and self.command_state in (3, 4, 5, 6) and self.attack_target is not None and self.hold == 0:
                    if self.attack_target.state != 100:
                        if self.collide is False:
                            self.state = self.command_state  # resume attack command
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
                # ^ End retreat function

                # v Rotate Function
                if self.angle != self.new_angle and self.charging is False and self.state != 10 and self.stamina > 0 and self.collide is False:
                    self.rotate_cal = abs(self.new_angle - self.angle)  # amount of angle left to rotate
                    self.rotate_check = 360 - self.rotate_cal  # rotate distance used for preventing angle calculation bug (pygame rotate related)
                    self.move_rotate = True
                    self.radians_angle = math.radians(360 - self.angle)  # for subunit rotate
                    if self.angle < 0:  # negative angle (rotate to left side)
                        self.radians_angle = math.radians(-self.angle)
                    # vv Rotate logic to continuously rotate based on angle and shortest length
                    rotate_tiny = self.rotate_speed * dt  # rotate little by little according to time
                    if self.new_angle > self.angle:  # rotate to angle more than the current one
                        if self.rotate_cal > 180:  # rotate with the smallest angle direction
                            self.angle -= rotate_tiny
                            self.rotate_check -= rotate_tiny
                            if self.rotate_check <= 0:
                                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                        else:
                            self.angle += rotate_tiny
                            if self.angle > self.new_angle:
                                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                    elif self.new_angle < self.angle:  # rotate to angle less than the current one
                        if self.rotate_cal > 180:  # rotate with the smallest angle direction
                            self.angle += rotate_tiny
                            self.rotate_check -= rotate_tiny
                            if self.rotate_check <= 0:
                                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                        else:
                            self.angle -= rotate_tiny
                            if self.angle < self.new_angle:
                                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                    # ^^ End rotate tiny
                    self.set_subunit_target()  # generate new pos related to side

                elif self.move_rotate and abs(self.angle - self.new_angle) < 1:  # Finish
                    self.move_rotate = False
                    if self.rotate_only is False:  # continue moving to base_target after finish rotate
                        self.set_subunit_target(self.base_target)
                    else:
                        self.state = 0  # idle state
                        self.process_command(self.base_target, other_command=1)
                        self.rotate_only = False  # reset rotate only condition
                # ^ End rotate function

                if self.state not in (0, 95) and self.front_pos.distance_to(self.command_target) < 1:  # reach destination and not in combat
                    not_halt = False  # check if any subunit in combat
                    for subunit in self.subunit_sprite:
                        if subunit.state == 10:
                            not_halt = True
                        if subunit.unit_leader and subunit.state != 10:
                            not_halt = False
                            break
                    if not_halt is False:
                        self.retreat_start = False  # reset retreat
                        self.revert = False  # reset revert order
                        self.process_command(self.base_target, other_command=1)  # reset command base_target state will become 0 idle

                # v Perform range attack, can only enter range attack state after finishing rotate
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
                    self.state = self.command_state  # set state to attack command state
                    self.range_combat_check = False  # stop range combat check
                    self.set_target(self.attack_target.base_pos)  # move to new base_target
                    self.new_angle = self.set_rotate()  # also keep rotate to base_target
                # ^ End range attack state

        else:  # dead unit
            # v unit just got killed
            if self.got_killed is False:
                if self.team == 1:
                    self.destroyed(self.battle)
                else:
                    self.destroyed(self.battle)

                self.battle.setup_unit_icon()  # reset army icon (remove dead one)
                self.battle.event_log.add_log([0, str(self.leader[0].name) + "'s unit is destroyed"],
                                              [0, 1])  # put destroyed event in troop and army log

                self.kill()
                for subunit in self.subunit_sprite:
                    subunit.kill()
            # ^ End got killed

    def set_target(self, pos):
        """set new base_target, scale base_target from base_target according to zoom scale"""
        self.base_target = pygame.Vector2(pos)  # Set new base base_target
        self.set_subunit_target(self.base_target)

    def revert_move(self):
        """Only subunit will rotate to move, not the entire unit"""
        self.new_angle = self.angle
        self.move_rotate = False  # will not rotate to move
        self.revert = True
        new_angle = self.set_rotate()
        for subunit in self.subunit_sprite:
            subunit.new_angle = new_angle

    def process_command(self, target_pos, runcommand=False, revert_move=False, enemy=None, other_command=0):
        """Process input order into state and subunit base_target action
        other_command parameter 0 is default command, 1 is natural pause, 2 is order pause"""
        if other_command == 0:  # move or attack command
            self.state = 1

            if self.attack_place or (enemy is not None and (self.team != enemy.team)):  # attack
                if self.ammo <= 0 or self.forced_melee:  # no magazine_left to shoot or forced attack command
                    self.state = 3  # move to melee
                elif self.ammo > 0:  # have magazine_left to shoot
                    self.state = 5  # Move to range attack
                if self.attack_place:  # attack specific location
                    self.set_target(target_pos)
                    # if self.magazine_left > 0:
                    self.base_attack_pos = target_pos
                else:
                    self.attack_target = enemy
                    self.base_attack_pos = enemy.base_pos
                    self.set_target(self.base_attack_pos)

            else:
                self.set_target(target_pos)

            if runcommand or self.run_toggle == 1:
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
        self.leader[0].authority -= self.auth_penalty  # retreat reduce gamestart leader authority
        if self.charging:  # change order when attacking will cause authority penalty
            self.leader[0].authority -= self.auth_penalty
        self.auth_recal()
        self.retreat_start = True  # start retreat process
        self.set_target(pos)
        self.revert_move()
        self.command_target = self.base_target

    def command(self, pos, mouse_right, double_mouse_right, target, key_state, other_command=0):
        """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
        if self.control and self.state not in (95, 97, 98, 99):
            self.revert = False
            self.retreat_start = False  # reset retreat
            self.rotate_only = False
            self.forced_melee = False
            self.attack_target = None
            self.base_attack_pos = 0
            self.attack_place = False
            self.range_combat_check = False

            # register user keyboard
            if key_state is not None and (key_state[pygame.K_LCTRL] or key_state[pygame.K_RCTRL]):
                self.forced_melee = True
            if key_state is not None and (key_state[pygame.K_LALT] or key_state[pygame.K_RALT]):
                self.attack_place = True

            if self.state != 100:
                if mouse_right and 1 <= pos[0] < 998 and 1 <= pos[1] < 998:
                    if self.state in (10, 96) and target is None:
                        self.process_retreat(pos)  # retreat
                    else:
                        for subunit in self.subunit_sprite:
                            subunit.attacking = True
                        # if self.state == 10:
                        if key_state is not None and (key_state[pygame.K_LSHIFT] or key_state[pygame.K_RSHIFT]):
                            self.rotate_only = True
                        if key_state is not None and key_state[pygame.K_z]:
                            self.revert = True
                        self.process_command(pos, double_mouse_right, self.revert, target)
                elif other_command != 0:
                    self.process_command(pos, double_mouse_right, self.revert, target, other_command)

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
        self.game_id = newgameid  # change self id
        # self.changescale() # reset scale to the current zoom
        self.icon.change_image(change_side=True)  # change army icon to new team

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
        self.front_pos = rotationxy(self.base_pos, front_pos, self.radians_angle)
        number_pos = (self.base_pos[0] - self.base_width_box,
                     (self.base_pos[1] + self.base_height_box))  # find position for number text
        self.number_pos = rotationxy(self.base_pos, number_pos, self.radians_angle)
        self.change_pos_scale()

        self.base_target = self.base_pos
        self.command_target = self.base_target  # reset command base_target
        unit_topleft = pygame.Vector2(self.base_pos[0] - self.base_width_box,
                                      # get the top left corner of sprite to generate subunit position
                                      self.base_pos[1] - self.base_height_box)

        for subunit in self.subunit_sprite:  # generate position of each subunit
            new_target = unit_topleft + subunit.unit_position
            subunit.base_pos = pygame.Vector2(
                rotationxy(self.base_pos, new_target, self.radians_angle))  # rotate according to sprite current rotation
            subunit.pos = subunit.base_pos * subunit.zoom  # pos is for showing on screen
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
            del self.subunit_sprite
            del self.near_target
            del self.leader
            del self.frontline_object
            del self.attack_target
            del self.leader_subunit
