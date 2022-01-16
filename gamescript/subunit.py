import math
import random

import numpy as np
import pygame
import pygame.freetype
from gamescript import script_common, rangeattack
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pygame.transform import scale

infinity = float("inf")
rotation_xy = script_common.rotation_xy


class Subunit(pygame.sprite.Sprite):
    images = []
    battle = None
    base_map = None  # base map
    feature_map = None  # feature map
    height_map = None  # height map
    weapon_list = None
    armour_list = None
    stat_list = None
    max_zoom = 10  # max zoom allow

    def __init__(self, troop_id, game_id, unit, start_pos, start_hp, start_stamina, unit_scale, genre):
        """Although subunit in code, this is referred as sub-subunit ingame"""
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.get_feature = self.feature_map.get_feature
        self.get_height = self.height_map.get_height

        self.who_last_select = None
        self.leader = None  # Leader in the sub-subunit if there is one, got add in leader gamestart
        self.board_pos = None  # Used for event log position of subunit (Assigned in battle subunit setup)
        self.walk = False  # currently walking
        self.run = False  # currently running
        self.frontline = False  # on front line of unit or not
        self.unit_leader = False  # contain the general or not, making it leader subunit
        self.attack_target = None
        self.melee_target = None  # current target of melee combat
        self.close_target = None  # closet target to move to in melee
        self.attacking = False  # For checking if unit in attacking state or not for using charge skill
        self.unit = unit  # reference to the parent uit of this subunit

        self.enemy_front = []  # list of front collide sprite
        self.enemy_side = []  # list of side collide sprite
        self.friend_front = []  # list of friendly front collide sprite
        self.same_front = []  # list of same unit front collide sprite
        self.full_merge = []  # list of sprite that collide and almost overlap with this sprite
        self.collide_penalty = False
        self.team = self.unit.team
        self.battle.all_subunit_list.append(self)
        if self.team == 1:  # add sprite to team subunit group for collision
            group_collide = self.battle.team1_subunit
        elif self.team == 2:
            group_collide = self.battle.team2_subunit
        group_collide.add(self)

        self.status_list = self.unit.status_list

        self.game_id = game_id  # ID of this
        self.troop_id = int(troop_id)  # ID of preset used for this subunit

        self.angle = self.unit.angle
        self.new_angle = self.unit.angle
        self.radians_angle = math.radians(360 - self.angle)  # radians for apply angle to position (allsidepos and subunit)
        self.parent_angle = self.unit.angle  # angle subunit will face when not moving or

        self.red_border = False  # red corner to indicate taking melee_dmg in inspect ui
        self.state = 0  # Current subunit state, similar to unit state
        self.timer = random.random()  # may need to use random.random()
        self.move_timer = 0  # timer for moving to front position before attacking nearest enemy
        self.charge_momentum = 1  # charging momentum to reach target before choosing nearest enemy
        self.ammo_now = 0
        self.zoom = 1
        self.last_zoom = 10
        self.skill_cond = 0
        self.broken_limit = 0  # morale require for unit to stop broken state, will increase everytime broken state stop

        # v Setup troop stat
        stat = self.stat_list.troop_list[self.troop_id].copy()
        stat_header = self.stat_list.troop_list_header
        weapon_header = self.weapon_list.weapon_list_header
        armour_header = self.armour_list.armour_list_header
        grade_header = self.stat_list.grade_list_header
        mount_header = self.stat_list.mount_list_header
        mount_grade_header = self.stat_list.mount_grade_list_header

        self.name = stat[0]  # name according to the preset
        self.grade = stat[stat_header["Grade"]]  # training level/class grade
        self.race = stat[stat_header["Race"]]  # creature race
        self.trait = stat[stat_header["Trait"]]  # trait list from preset
        self.trait = self.trait + self.stat_list.grade_list[self.grade][grade_header["Trait"]]  # add trait from grade
        skill = stat[stat_header["Skill"]]  # skill list according to the preset
        self.skill_cooldown = {}
        self.cost = stat[stat_header["Cost"]]
        grade_stat = self.stat_list.grade_list[self.grade]
        self.base_attack = stat[stat_header["Melee Attack"]] + \
                           grade_stat[grade_header["Melee Attack Bonus"]]  # base melee attack with grade bonus
        self.base_melee_def = stat[stat_header["Melee Defence"]] + \
                              grade_stat[grade_header["Defence Bonus"]]  # base melee defence with grade bonus
        self.base_range_def = stat[stat_header["Ranged Defence"]] + \
                              grade_stat[grade_header["Defence Bonus"]]  # base range defence with grade bonus
        self.armour_gear = stat[stat_header["Armour"]]  # armour equipment
        self.base_armour = self.armour_list.armour_list[self.armour_gear[0]][1] \
                           * self.armour_list.quality[self.armour_gear[1]]  # armour stat is calculated from based armour * quality
        self.base_accuracy = stat[stat_header["Accuracy"]] + grade_stat[grade_header["Accuracy Bonus"]]
        self.base_sight = stat[stat_header["Sight"]]  # base sight range
        self.magazine_left = stat[stat_header["Ammunition"]]  # amount of ammunition
        self.base_reload = stat[stat_header["Reload"]] + grade_stat[grade_header["Reload Bonus"]]
        self.base_charge = stat[stat_header["Charge"]]
        self.base_charge_def = 50  # All infantry subunit has default 50 charge defence
        self.charge_skill = stat[stat_header["Charge Skill"]]  # For easier reference to check what charge skill this subunit has
        self.skill = [self.charge_skill] + skill  # Add charge skill as first item in the list
        self.troop_health = stat[stat_header["Health"]] * grade_stat[grade_header["Health Effect"]]  # Health of each troop
        self.stamina = stat[stat_header["Stamina"]] * grade_stat[grade_header["Stamina Effect"]] * (
                    start_stamina / 100)  # starting stamina with grade
        self.mana = stat[stat_header["Mana"]]  # Resource for magic skill

        # vv Weapon stat
        self.primary_main_weapon = stat[stat_header["Primary Main Weapon"]]
        self.primary_sub_weapon = stat[stat_header["Primary Sub Weapon"]]
        self.secondary_main_weapon = stat[stat_header["Secondary Main Weapon"]]
        self.secondary_sub_weapon = stat[stat_header["Secondary Sub Weapon"]]

        self.weight = 0
        self.melee_dmg = [0, 0]
        self.melee_penetrate = 0
        self.range_dmg = [0, 0]
        self.range_penetrate = 0
        self.base_range = 0
        self.melee_speed = 0
        self.magazine_size = 0

        self.base_morale = stat[stat_header["Morale"]] + grade_stat[grade_header["Morale Bonus"]]  # morale with grade bonus
        self.base_discipline = stat[stat_header["Discipline"]] + grade_stat[grade_header["Discipline Bonus"]]  # discilpline with grade bonus
        self.mental = stat[stat_header["Mental"]] + grade_stat[
            grade_header["Mental Bonus"]]  # mental resistance from morale melee_dmg and mental status effect
        self.troop_number = stat[stat_header["Troop"]] * unit_scale[
            self.team - 1] * start_hp / 100  # number of starting troop, team -1 to become list index
        self.base_speed = 50  # All infantry has base speed at 50
        self.subunit_type = stat[stat_header["Troop Class"]] - 1  # 0 is melee infantry and 1 is range for command buff
        self.feature_mod = 1  # the starting column in unit_terrainbonus of infantry
        self.authority = 100  # default start at 100

        # vv Elemental stat
        self.base_elem_melee = 0  # start with physical element for melee weapon
        self.base_elem_range = 0  # start with physical for range weapon
        self.elem_count = [0, 0, 0, 0, 0]  # Elemental threshold count in this order fire,water,air,earth,poison
        self.temp_count = 0  # Temperature threshold count
        self.elem_res = [0, 0, 0, 0, 0]  # fire, water, air, earth, poison in this order
        self.magic_res = 0  # Resistance to any magic
        self.heat_res = 0  # Resistance to heat temperature
        self.cold_res = 0  # Resistance to cold temperature
        # ^^ End elemental

        self.reload_time = 0  # Unit can only refill magazine when reload_time is equal or more than reload stat
        self.crit_effect = 1  # critical extra modifier
        self.front_dmg_effect = 1  # Some skill affect only frontal combat melee_dmg
        self.side_dmg_effect = 1  # Some skill affect melee_dmg for side combat as well (AOE)
        self.corner_atk = False  # Check if subunit can attack corner enemy or not
        self.flank_bonus = 1  # Combat bonus when flanking
        self.base_auth_penalty = 0.1  # penalty to authority when bad event happen
        self.bonus_morale_dmg = 0  # extra morale melee_dmg
        self.bonus_stamina_dmg = 0  # extra stamina melee_dmg
        self.auth_penalty = 0.1  # authority penalty for certain activities/order
        self.base_hp_regen = 0  # hp regeneration modifier, will not resurrect dead troop by default
        self.base_stamina_regen = 2  # stamina regeneration modifier
        self.morale_regen = 2  # morale regeneration modifier
        self.status_effect = {}  # list of current status effect
        self.skill_effect = {}  # list of activate skill effect
        self.base_inflict_status = {}  # list of status that this subunit will inflict to enemy when attack
        self.special_status = []

        # vv Set up trait variable
        self.arcshot = False
        self.anti_inf = False
        self.anti_cav = False
        self.shootmove = False
        self.agileaim = False
        self.no_range_penal = False
        self.long_range_acc = False
        self.ignore_chargedef = False
        self.ignore_def = False
        self.full_def = False
        self.temp_full_def = False
        self.backstab = False
        self.oblivious = False
        self.flanker = False
        self.unbreakable = False
        self.temp_unbreakable = False
        self.stationplace = False
        # ^^ End setup trait variable

        self.trait = list(set([trait for trait in self.trait if trait != 0]))  # remove empty and duplicate traits
        if len(self.trait) > 0:
            self.trait = {x: self.stat_list.trait_list[x] for x in self.trait if
                          x in self.stat_list.trait_list}  # Any trait not available in ruleset will be ignored
            self.add_trait()
        self.battle.start_troopnumber[self.team] += self.troop_number  # add troop number to counter how many troop join battle
        # ^ End setup stat

        # self.loyalty

        if genre == "tactical":
            global script_other, script_battle, script_subunit
            from gamescript.tactical.subunit import fight, start, movement
            self.dmg_cal = fight.dmg_cal
            self.add_weapon_stat = start.add_weapon_stat
            self.add_mount_stat = start.add_mount_statset_rotate
            self.set_rotate = script_other.set_rotate
            self.change_leader = fight.change_leader
            self.rotate_logic = movement.rotate_logic
            self.rotate = movement.rotate_logic
            self.move_logic = movement.move_logic

            self.add_weapon_stat(weapon_header)

            self.melee_speed = int(self.melee_speed)

            if self.melee_penetrate < 0:
                self.melee_penetrate = 0  # melee melee_penetrate cannot be lower than 0
            if self.range_penetrate < 0:
                self.range_penetrate = 0
            # ^^ End weapon stat

            # vv Mount stat
            self.mount = self.stat_list.mount_list[stat[stat_header["Mount"]][0]]  # mount this subunit use
            self.mount_grade = self.stat_list.mount_grade_list[stat[stat_header["Mount"]][1]]
            self.mount_armour = self.stat_list.mount_armour_list[stat[stat_header["Mount"]][2]]
            if stat[stat_header["Mount"]][0] != 1:  # have a mount, add mount stat with its grade to subunit stat
                self.add_mount_stat(mount_header, mount_grade_header)
            # ^^ End mount stat

            self.last_health_state = 4  # state start at full
            self.last_stamina_state = 4

            self.max_stamina = self.stamina
            self.stamina75 = self.stamina * 0.75
            self.stamina50 = self.stamina * 0.5
            self.stamina25 = self.stamina * 0.25
            self.stamina5 = self.stamina * 0.05

            self.unit_health = self.troop_health * self.troop_number  # Total health of subunit from all troop
            self.max_health = self.unit_health  # health percentage
            self.health_list = (self.unit_health * 0.75, self.unit_health * 0.5, self.unit_health * 0.25, 0)

            self.old_last_health, self.old_last_stamina = self.unit_health, self.stamina  # save previous health and stamina in previous update
            self.max_troop = self.troop_number  # max number of troop at the start
            self.morale_state = self.base_morale / self.max_morale  # turn into percentage
            self.stamina_state = (self.stamina * 100) / self.max_stamina  # turn into percentage
            self.stamina_state_cal = self.stamina_state / 100  # for using as modifier on stat

            sprite_dict = script_battle.create_sprite(self)
            self.image = sprite_dict["sprite"]
            self.image_original = sprite_dict["original"]
            self.image_original2 = sprite_dict["original2"]
            self.image_original3 = sprite_dict["original3"]
            self.block = sprite_dict["block"]
            self.block_original = sprite_dict["block_original"]
            self.selected_image = sprite_dict["selected"]
            self.selected_image_rect = sprite_dict["selected_image_rect"]
            self.selected_image_original = sprite_dict["selected_original"]
            self.selected_image_original2 = sprite_dict["selected_original2"]
            self.far_image = sprite_dict["far"]
            self.far_selected_image = sprite_dict["far_selected"]
            self.health_image_rect = sprite_dict["health_rect"]
            self.health_block_rect = sprite_dict["health_block_rect"]
            self.stamina_image_rect = sprite_dict["stamina_rect"]
            self.stamina_block_rect = sprite_dict["stamina_block_rect"]
            self.corner_image_rect = sprite_dict["corner_rect"]
            self.health_image_list = sprite_dict["health_list"]
            self.stamina_image_list = sprite_dict["stamina_list"]

        self.skill = {x: self.stat_list.skill_list[x].copy() for x in self.skill if
                      x != 0 and x in self.stat_list.skill_list}  # grab skill stat into dict
        for skill in list(self.skill.keys()):  # remove skill if class mismatch
            skill_troop_cond = self.skill[skill][self.skill_troop_type]
            if skill_troop_cond == 0 or (self.subunit_type == 2 and skill_troop_cond == 2) or (self.subunit_type != 2 and skill_troop_cond != 2):
                pass
            else:
                self.skill.pop(skill)

        # v Weight calculation
        self.weight += self.armour_list.armour_list[self.armour_gear[0]][armour_header["Weight"]] + \
                       self.mount_armour[2]  # Weight from both melee and range weapon and armour
        if self.subunit_type == 2:  # cavalry has half weight penalty
            self.weight = self.weight / 2
        # ^ End weight cal

        self.trait += self.armour_list.armour_list[self.armour_gear[0]][armour_header["Trait"]]  # Apply armour trait to subunit
        self.base_speed = (self.base_speed * ((100 - self.weight) / 100)) + grade_stat[
            grade_header["Speed Bonus"]]  # finalise base speed with weight and grade bonus
        self.size = stat[stat_header["Size"]]
        self.description = stat[-1]  # subunit description for inspect ui
        # if self.hidden

        # vv Stat variable after receive modifier effect from various sources, used for activity and effect calculation
        self.max_morale = self.base_morale
        self.attack = self.base_attack
        self.melee_def = self.base_melee_def
        self.range_def = self.base_range_def
        self.armour = self.base_armour
        self.speed = self.base_speed
        self.accuracy = self.base_accuracy
        self.reload = self.base_reload
        self.morale = self.base_morale
        self.discipline = self.base_discipline
        self.shoot_range = self.base_range
        self.charge = self.base_charge
        self.charge_def = self.base_charge_def
        self.auth_penalty = self.base_auth_penalty
        self.hp_regen = self.base_hp_regen
        self.stamina_regen = self.base_stamina_regen
        self.inflict_status = self.base_inflict_status
        self.elem_melee = self.base_elem_melee
        self.elem_range = self.base_elem_range
        # ^^ End stat for status effect

        if self.mental < 0:  # cannot be negative
            self.mental = 0
        elif self.mental > 200:  # cannot exceed 100
            self.mental = 200
        self.mental_text = self.mental - 100
        self.mental = (200 - self.mental) / 100  # convert to percentage

        self.corner_atk = False  # cannot attack corner enemy by default
        self.temp_full_def = False

        # v position related
        self.unit_position = (start_pos[0] / 10, start_pos[1] / 10)  # position in unit sprite
        unit_top_left = pygame.Vector2(self.unit.base_pos[0] - self.unit.base_width_box / 2,
                                      self.unit.base_pos[
                                              1] - self.unit.base_height_box / 2)  # get top left corner position of unit to calculate true pos
        self.base_pos = pygame.Vector2(unit_top_left[0] + self.unit_position[0],
                                       unit_top_left[1] + self.unit_position[1])  # true position of subunit in map
        self.last_pos = self.base_pos

        self.movement_queue = []
        self.combat_move_queue = []
        self.base_target = self.base_pos  # base_target to move
        self.command_target = self.base_pos  # actual base_target outside of combat
        self.pos = self.base_pos * self.zoom  # pos is for showing on screen

        self.image_height = (self.image.get_height() - 1) / 20  # get real half height of circle sprite

        self.front_pos = (self.base_pos[0], (self.base_pos[1] - self.image_height))  # generate front side position
        self.front_pos = rotation_xy(self.base_pos, self.front_pos, self.radians_angle)  # rotate the new front side according to sprite rotation

        self.attack_pos = self.unit.base_attack_pos
        self.terrain, self.feature = self.get_feature(self.base_pos, self.base_map)  # get new terrain and feature at each subunit position
        self.height = self.height_map.get_height(self.base_pos)  # current terrain height
        self.front_height = self.height_map.get_height(self.front_pos)  # terrain height at front position
        # ^ End position related

        self.rect = self.image.get_rect(center=self.pos)

    def zoom_scale(self):
        """camera zoom change and rescale the sprite and position scale"""
        if self.zoom != 1:
            self.image_original = self.image_original3.copy()  # reset image for new scale
            scale_width = self.image_original.get_width() * self.zoom / self.max_zoom
            scale_height = self.image_original.get_height() * self.zoom / self.max_zoom
            dim = pygame.Vector2(scale_width, scale_height)
            self.image = pygame.transform.scale(self.image_original, (int(dim[0]), int(dim[1])))

            if self.unit.selected and self.state != 100:
                self.selected_image_original = pygame.transform.scale(self.selected_image_original2, (int(dim[0]), int(dim[1])))
        else:
            self.image_original = self.far_image.copy()
            self.image = self.image_original.copy()
            if self.unit.selected and self.state != 100:
                self.selected_image_original = self.far_selected_image.copy()
        self.image_original = self.image.copy()
        self.image_original2 = self.image.copy()
        self.change_pos_scale()
        self.rotate()

    def change_pos_scale(self):
        """Change position variable to new camera scale"""
        self.pos = self.base_pos * self.zoom
        self.rect = self.image.get_rect(center=self.pos)

    def use_skill(self, which_skill):
        if which_skill == 0:  # charge skill need to seperate since charge power will be used only for charge skill
            skill_stat = self.skill[list(self.skill)[0]].copy()  # get skill stat
            self.skill_effect[self.charge_skill] = skill_stat  # add stat to skill effect
            self.skill_cooldown[self.charge_skill] = skill_stat[self.skill_cd]  # add skill cooldown
        else:  # other skill
            skill_stat = self.skill[which_skill].copy()  # get skill stat
            self.skill_effect[which_skill] = skill_stat  # add stat to skill effect
            self.skill_cooldown[which_skill] = skill_stat[self.skill_cd]  # add skill cooldown
        self.stamina -= skill_stat[9]
        # self.skill_cooldown[which_skill] =

    # def receiveskill(self,which_skill):

    def check_skill_condition(self):
        """Check which skill can be used, cooldown, condition state, discipline, stamina are checked. charge skill is excepted from this check"""
        if self.skill_cond == 1 and self.staminastate < 50:  # reserve 50% stamina, don't use any skill
            self.available_skill = []
        elif self.skill_cond == 2 and self.staminastate < 25:  # reserve 25% stamina, don't use any skill
            self.available_skill = []
        else:  # check all skill
            self.available_skill = [skill for skill in self.skill if skill not in self.skill_cooldown.keys()
                                    and self.state in self.skill[skill][self.skill_condition] and self.discipline >= self.skill[skill][
                                        self.skill_discipline_req]
                                    and self.stamina > self.skill[skill][self.skill_stamina_cost] and skill != self.charge_skill]

    def find_nearby_subunit(self):
        """Find nearby friendly squads in the same unit for applying buff"""
        self.nearby_subunit_list = []
        corner_subunit = []
        for row_index, row_list in enumerate(self.unit.subunit_list.tolist()):
            if self.game_id in row_list:
                if row_list.index(self.game_id) - 1 != -1:  # get subunit from left if not at first column
                    self.nearby_subunit_list.append(self.unit.sprite_array[row_index][row_list.index(self.game_id) - 1])  # index 0
                else:  # not exist
                    self.nearby_subunit_list.append(0)  # add number 0 instead

                if row_list.index(self.game_id) + 1 != len(row_list):  # get subunit from right if not at last column
                    self.nearby_subunit_list.append(self.unit.sprite_array[row_index][row_list.index(self.game_id) + 1])  # index 1
                else:  # not exist
                    self.nearby_subunit_list.append(0)  # add number 0 instead

                if row_index != 0:  # get top subunit
                    self.nearby_subunit_list.append(self.unit.sprite_array[row_index - 1][row_list.index(self.game_id)])  # index 2
                    if row_list.index(self.game_id) - 1 != -1:  # get top left subunit
                        corner_subunit.append(self.unit.sprite_array[row_index - 1][row_list.index(self.game_id) - 1])  # index 3
                    else:  # not exist
                        corner_subunit.append(0)  # add number 0 instead
                    if row_list.index(self.game_id) + 1 != len(row_list):  # get top right
                        corner_subunit.append(self.unit.sprite_array[row_index - 1][row_list.index(self.game_id) + 1])  # index 4
                    else:  # not exist
                        corner_subunit.append(0)  # add number 0 instead
                else:  # not exist
                    self.nearby_subunit_list.append(0)  # add number 0 instead

                if row_index != len(self.unit.sprite_array) - 1:  # get bottom subunit
                    self.nearby_subunit_list.append(self.unit.sprite_array[row_index + 1][row_list.index(self.game_id)])  # index 5
                    if row_list.index(self.game_id) - 1 != -1:  # get bottom left subunit
                        corner_subunit.append(self.unit.sprite_array[row_index + 1][row_list.index(self.game_id) - 1])  # index 6
                    else:  # not exist
                        corner_subunit.append(0)  # add number 0 instead
                    if row_list.index(self.game_id) + 1 != len(row_list):  # get bottom  right subunit
                        corner_subunit.append(self.unit.sprite_array[row_index + 1][row_list.index(self.game_id) + 1])  # index 7
                    else:  # not exist
                        corner_subunit.append(0)  # add number 0 instead
                else:  # not exist
                    self.nearby_subunit_list.append(0)  # add number 0 instead
        self.nearby_subunit_list = self.nearby_subunit_list + corner_subunit

    def status_to_friend(self, aoe, status_id, status_list):
        """apply status effect to nearby subunit depending on aoe stat"""
        if aoe in (2, 3):
            if aoe > 1:  # only direct nearby friendly subunit
                for subunit in self.nearby_subunit_list[0:4]:
                    if subunit != 0 and subunit.state != 100:  # only apply to exist and alive squads
                        subunit.status_effect[status_id] = status_list  # apply status effect
            if aoe > 2:  # all nearby including corner friendly subunit
                for subunit in self.nearby_subunit_list[4:]:
                    if subunit != 0 and subunit.state != 100:  # only apply to exist and alive squads
                        subunit.status_effect[status_id] = status_list  # apply status effect
        elif aoe == 4:  # apply to whole unit
            for subunit in self.unit.sprite_array.flat:
                if subunit.state != 100:  # only apply to alive squads
                    subunit.status_effect[status_id] = status_list  # apply status effect

    def threshold_count(self, elem, t1status, t2status):
        """apply elemental status effect when reach elemental threshold"""
        if elem > 50:
            self.status_effect[t1status] = self.status_list[t1status].copy()  # apply tier 1 status
            if elem > 100:
                self.status_effect[t2status] = self.status_list[t2status].copy()  # apply tier 2 status
                del self.status_effect[t1status]  # remove tier 1 status
                elem = 0  # reset elemental count
        return elem

    def find_close_target(self, subunit_list):
        """Find close enemy sub-unit to move to fight"""
        close_list = {subunit: subunit.base_pos.distance_to(self.base_pos) for subunit in subunit_list}
        close_list = dict(sorted(close_list.items(), key=lambda item: item[1]))
        max_random = 3
        if len(close_list) < 4:
            max_random = len(close_list) - 1
            if max_random < 0:
                max_random = 0
        if len(close_list) > 0:
            close_target = list(close_list.keys())[random.randint(0, max_random)]
            # if close_target.base_pos.distance_to(self.base_pos) < 20: # in case can't find close target
        return close_target

    def status_update(self, this_weather=None):
        """calculate stat from stamina, morale state, skill, status, terrain"""

        if self.red_border and self.unit.selected:  # have red border (taking melee_dmg) on inspect ui, reset image
            self.block.blit(self.block_original, self.corner_image_rect)
            self.red_border = False

        # v reset stat to default and apply morale, stamina, command buff to stat
        if self.max_stamina > 100:
            self.max_stamina = self.max_stamina - (self.timer * 0.05)  # Max stamina gradually decrease over time - (self.timer * 0.05)
            self.stamina75 = self.max_stamina * 0.75
            self.stamina50 = self.max_stamina * 0.5
            self.stamina25 = self.max_stamina * 0.25
            self.stamina5 = self.max_stamina * 0.05

        self.morale = self.base_morale
        self.authority = self.unit.authority  # unit total authoirty
        self.commandbuff = self.unit.commandbuff[
                               self.subunit_type] * 100  # command buff from gamestart leader according to this subunit subunit type
        self.discipline = self.base_discipline
        self.attack = self.base_attack
        self.melee_def = self.base_melee_def
        self.range_def = self.base_range_def
        self.accuracy = self.base_accuracy
        self.reload = self.base_reload
        self.charge_def = self.base_charge_def
        self.speed = self.base_speed
        self.charge = self.base_charge
        self.shoot_range = self.base_range

        self.crit_effect = 1  # default critical effect
        self.front_dmg_effect = 1  # default frontal melee_dmg
        self.side_dmg_effect = 1  # default side melee_dmg

        self.corner_atk = False  # cannot attack corner enemy by default
        self.temp_full_def = False

        self.auth_penalty = self.base_auth_penalty
        self.hp_regen = self.base_hp_regen
        self.stamina_regen = self.base_stamina_regen
        self.inflict_status = self.base_inflict_status
        self.elem_melee = self.base_elem_melee
        self.elem_range = self.base_elem_range
        # ^ End default stat

        # v Apply status effect from trait
        if len(self.trait) > 1:
            for trait in self.trait.values():
                if trait[18] != [0]:
                    for effect in trait[18]:  # aplly status effect from trait
                        self.status_effect[effect] = self.status_list[effect].copy()
                        if trait[1] > 1:  # status buff range to nearby friend
                            self.status_to_friend(trait[1], effect, self.status_list[effect].copy())
        # ^ End trait

        # v apply effect from weather"""
        weather_temperature = 0
        if this_weather is not None:
            weather = this_weather
            self.attack += weather.melee_atk_buff
            self.melee_def += weather.melee_def_buff
            self.range_def += weather.range_def_buff
            self.armour += weather.armour_buff
            self.speed += weather.speed_buff
            self.accuracy += weather.accuracy_buff
            self.reload += weather.reload_buff
            self.charge += weather.charge_buff
            self.charge_def += weather.charge_def_buff
            self.hp_regen += weather.hp_regen_buff
            self.stamina_regen += weather.stamina_regen_buff
            self.morale += (weather.morale_buff * self.mental)
            self.discipline += weather.discipline_buff
            if weather.elem[0] != 0:  # Weather can cause elemental effect such as wet
                self.elem_count[weather.elem[0]] += (weather.elem[1] * (100 - self.elem_res[weather.elem[0]]) / 100)
            weather_temperature = weather.temperature
        # ^ End weather

        # v Map feature modifier to stat
        map_feature_mod = self.feature_map.feature_mod[self.feature]
        if map_feature_mod[self.feature_mod] != 1:  # speed/charge
            speed_mod = map_feature_mod[self.feature_mod]  # get the speed mod appropiate to subunit type
            self.speed *= speed_mod
            self.charge *= speed_mod

        if map_feature_mod[self.feature_mod + 1] != 1:  # melee attack
            # combatmod = self.unit.feature_map.feature_mod[self.unit.feature][self.feature_mod + 1]
            self.attack *= map_feature_mod[self.feature_mod + 1]  # get the attack mod appropiate to subunit type

        if map_feature_mod[self.feature_mod + 2] != 1:  # melee/charge defence
            combatmod = map_feature_mod[self.feature_mod + 2]  # get the defence mod appropiate to subunit type
            self.melee_def *= combatmod
            self.charge_def *= combatmod

        self.range_def += map_feature_mod[7]  # range defence bonus from terrain bonus
        self.accuracy -= (map_feature_mod[7] / 2)  # range def bonus block subunit sight as well so less accuracy
        self.discipline += map_feature_mod[9]  # discipline defence bonus from terrain bonus

        if map_feature_mod[11] != [0]:  # Some terrain feature can also cause status effect such as swimming in water
            if 1 in map_feature_mod[11]:  # Shallow water type terrain
                self.status_effect[31] = self.status_list[31].copy()  # wet
            if 5 in map_feature_mod[11]:  # Deep water type terrain
                self.status_effect[93] = self.status_list[93].copy()  # drench

                if self.weight > 60 or self.stamina <= 0:  # weight too much or tired will cause drowning
                    self.status_effect[102] = self.status_list[102].copy()  # Drowning

                elif self.weight > 30:  # Medium weight subunit has trouble travel through water and will sink and progressively lose troops
                    self.status_effect[101] = self.status_list[101].copy()  # Sinking

                elif self.weight < 30:  # Light weight subunit has no trouble travel through water
                    self.status_effect[104] = self.status_list[104].copy()  # Swiming

            if 2 in map_feature_mod[11]:  # Rot type terrain
                self.status_effect[54] = self.status_list[54].copy()

            if 3 in map_feature_mod[11]:  # Poison type terrain
                self.elem_count[4] += ((100 - self.elem_res[4]) / 100)
        # self.hidden += self.unit.feature_map[self.unit.feature][6]
        tempreach = map_feature_mod[10] + weather_temperature  # temperature the subunit will change to based on current terrain feature and weather
        # ^ End map feature

        # v Apply effect from skill
        # For list of status and skill effect column index used in statusupdate see script_other.py load_game_data()
        if len(self.skill_effect) > 0:
            for status in self.skill_effect:  # apply elemental effect to melee_dmg if skill has element
                cal_status = self.skill_effect[status]
                if cal_status[self.skill_type] == 0 and cal_status[self.skill_element] != 0:  # melee elemental effect
                    self.elem_melee = cal_status[self.skill_element]
                elif cal_status[self.skill_type] == 1 and cal_status[self.skill_element] != 0:  # range elemental effect
                    self.elem_range = cal_status[self.skill_element]
                self.attack = self.attack * cal_status[self.skill_melee_attack]
                self.melee_def = self.melee_def * cal_status[self.skill_melee_defence]
                self.range_def = self.range_def * cal_status[self.skill_range_defence]
                self.speed = self.speed * cal_status[self.skill_speed]
                self.accuracy = self.accuracy * cal_status[self.skill_accuracy]
                self.shoot_range = self.shoot_range * cal_status[self.skill_range]
                self.reload = self.reload / cal_status[
                    self.skill_reload]  # different than other modifier the higher mod reduce reload time (decrease stat)
                self.charge = self.charge * cal_status[self.skill_charge]
                self.charge_def = self.charge_def + cal_status[self.skill_charge_defence]
                self.hp_regen += cal_status[self.skill_hp_regen]
                self.stamina_regen += cal_status[self.skill_stamina_regen]
                self.morale = self.morale + (cal_status[self.skill_morale] * self.mental)
                self.discipline = self.discipline + cal_status[self.skill_discipline]
                # self.sight += cal_status[self.skill_sight]
                # self.hidden += cal_status[self.skill_hide]
                self.crit_effect = self.crit_effect * cal_status[self.skill_critical]
                self.front_dmg_effect = self.front_dmg_effect * cal_status[self.skill_damage]
                if cal_status[self.skill_aoe] in (2, 3) and cal_status[self.skill_damage] != 100:
                    self.side_dmg_effect = self.side_dmg_effect * cal_status[self.skill_damage]
                    if cal_status[self.skill_aoe] == 3:
                        self.corner_atk = True  # if aoe 3 mean it can attack enemy on all side

                # v Apply status to friendly if there is one in skill effect
                if cal_status[self.skill_status] != [0]:
                    for effect in cal_status[self.skill_status]:
                        self.status_effect[effect] = self.status_list[effect].copy()
                        if self.status_effect[effect][2] > 1:
                            self.status_to_friend(self.status_effect[effect][2], effect, self.status_list)
                # ^ End apply status to

                self.bonus_morale_dmg += cal_status[self.skill_moraledmg]
                self.bonus_stamina_dmg += cal_status[self.skill_staminadmg]
                if cal_status[self.skill_enemy_status] != [0]:  # Apply inflict status effect to enemy from skill to inflict list
                    for effect in cal_status[self.skill_enemy_status]:
                        if effect != 0:
                            self.inflict_status[effect] = cal_status[self.skill_aoe]
            if self.charge_skill in self.skill_effect:
                self.auth_penalty += 0.5  # higher authority penalty when attacking (retreat while attacking)
        # ^ End skill effect

        # v Apply effect and modifer from status effect
        # """special status: 0 no control, 1 hostile to all, 2 no retreat, 3 no terrain effect, 4 no attack, 5 no skill, 6 no spell, 7 no exp gain,
        # 7 immune to bad mind, 8 immune to bad body, 9 immune to all effect, 10 immortal""" Not implemented yet
        if len(self.status_effect) > 0:
            for status in self.status_effect:
                cal_status = self.status_list[status]
                self.attack = self.attack * cal_status[self.status_melee_attack]
                self.melee_def = self.melee_def * cal_status[self.status_melee_defence]
                self.range_def = self.range_def * cal_status[self.status_range_defence]
                self.armour = self.armour * cal_status[self.status_armour]
                self.speed = self.speed * cal_status[self.status_speed]
                self.accuracy = self.accuracy * cal_status[self.status_accuracy]
                self.reload = self.reload / cal_status[self.status_reload]
                self.charge = self.charge * cal_status[self.status_charge]
                self.charge_def += cal_status[self.status_charge_defence]
                self.hp_regen += cal_status[self.status_hp_regen]
                self.stamina_regen += cal_status[self.status_stamina_regen]
                self.morale = self.morale + (cal_status[self.status_morale] * self.mental)
                self.discipline += cal_status[self.status_discipline]
                # self.sight += cal_status[self.status_sight]
                # self.hidden += cal_status[self.status_hide]
                tempreach += cal_status[self.status_temperature]
                if status == 91:  # All round defence status
                    self.temp_full_def = True
        # ^ End status effect

        # v Temperature mod function from terrain and weather
        for status in self.status_effect.values():
            tempreach += status[19]  # add more from status effect
        if tempreach < 0:  # cold temperature
            tempreach = tempreach * (100 - self.cold_res) / 100  # lowest temperature the subunit will change based on cold resist
        else:  # hot temperature
            tempreach = tempreach * (100 - self.heat_res) / 100  # highest temperature the subunit will change based on heat resist

        if self.temp_count != tempreach:  # move temp_count toward tempreach
            if tempreach > 0:
                if self.temp_count < tempreach:
                    self.temp_count += (100 - self.heat_res) / 100 * self.timer  # increase temperature, rate depends on heat resistance (- is faster)
            elif tempreach < 0:
                if self.temp_count > tempreach:
                    self.temp_count -= (100 - self.cold_res) / 100 * self.timer  # decrease temperature, rate depends on cold resistance
            else:  # tempreach is 0, subunit temp revert back to 0
                if self.temp_count > 0:
                    self.temp_count -= (1 + self.heat_res) / 100 * self.timer  # revert faster with higher resist
                else:
                    self.temp_count += (1 + self.cold_res) / 100 * self.timer
        # ^ End temperature

        # v Elemental effect
        if self.elem_count != [0, 0, 0, 0, 0]:  # Apply effect if elem threshold reach 50 or 100
            self.elem_count[0] = self.threshold_count(self.elem_count[0], 28, 92)
            self.elem_count[1] = self.threshold_count(self.elem_count[1], 31, 93)
            self.elem_count[2] = self.threshold_count(self.elem_count[2], 30, 94)
            self.elem_count[3] = self.threshold_count(self.elem_count[3], 23, 35)
            self.elem_count[4] = self.threshold_count(self.elem_count[4], 26, 27)
            self.elem_count = [elem - self.timer if elem > 0 else elem for elem in self.elem_count]
        # ^ End elemental effect

        # v Temperature effect
        if self.temp_count > 50:  # Hot
            self.status_effect[96] = self.status_list[96].copy()
            if self.temp_count > 100:  # Extremely hot
                self.status_effect[97] = self.status_list[97].copy()
                del self.status_effect[96]
        if self.temp_count < -50:  # Cold
            self.status_effect[95] = self.status_list[95].copy()
            if self.temp_count < -100:  # Extremely cold
                self.status_effect[29] = self.status_list[29].copy()
                del self.status_effect[95]
        # ^ End temperature effect related function

        self.moralestate = self.morale / self.max_morale  # for using as modifer to stat
        if self.moralestate > 3 or math.isnan(self.moralestate):  # morale state more than 3 give no more benefit
            self.moralestate = 3

        self.staminastate = (self.stamina * 100) / self.max_stamina
        self.staminastatecal = 1
        if self.stamina != infinity:
            self.staminastatecal = self.staminastate / 100  # for using as modifer to stat

        self.discipline = (self.discipline * self.moralestate * self.staminastatecal) + self.unit.leader_social[
            self.grade + 1] + (self.authority / 10)  # use morale, stamina, leader social vs grade (+1 to skip class name) and authority
        self.attack = (self.attack * (self.moralestate + 0.1)) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff
        self.melee_def = (self.melee_def * (
                self.moralestate + 0.1)) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff
        self.range_def = (self.range_def * (self.moralestate + 0.1)) * self.staminastatecal + (
                self.commandbuff / 2)  # use morale, stamina and half command buff
        self.accuracy = self.accuracy * self.staminastatecal + self.commandbuff  # use stamina and command buff
        self.reload = self.reload * (2 - self.staminastatecal)  # the less stamina, the higher reload time
        self.charge_def = (self.charge_def * (
                self.moralestate + 0.1)) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff
        heightdiff = (self.height / self.front_height) ** 2  # walking down hill increase speed while walking up hill reduce speed
        self.speed = self.speed * self.staminastatecal * heightdiff  # use stamina
        self.charge = (self.charge + self.speed) * (
                self.moralestate + 0.1) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff

        fullmergelen = len(self.full_merge) + 1
        if fullmergelen > 1:  # reduce discipline if there are overlap sub-unit
            self.discipline = self.discipline / fullmergelen

        # v Rounding up, add discipline to stat and forbid negative int stat
        disciplinecal = self.discipline / 200
        self.attack = self.attack + (self.attack * disciplinecal)
        self.melee_def = self.melee_def + (self.melee_def * disciplinecal)
        self.range_def = self.range_def + (self.range_def * disciplinecal)
        # self.armour = self.armour
        self.speed = self.speed + (self.speed * disciplinecal / 2)
        # self.accuracy = self.accuracy
        # self.reload = self.reload
        self.charge_def = self.charge_def + (self.charge_def * disciplinecal)
        self.charge = self.charge + (self.charge * disciplinecal)

        if self.magazine_left == 0 and self.ammo_now == 0:
            self.shoot_range = 0
        if self.attack < 0:  # seem like using if 0 is faster than max(0,)
            self.attack = 0
        if self.melee_def < 0:
            self.melee_def = 0
        if self.range_def < 0:
            self.range_def = 0
        if self.armour < 1:  # Armour cannot be lower than 1
            self.armour = 1
        if self.speed < 1:
            self.speed = 1
            if 105 in self.status_effect:  # collapse state enforce 0 speed
                self.speed = 0
        if self.accuracy < 0:
            self.accuracy = 0
        if self.reload < 0:
            self.reload = 0
        if self.charge < 0:
            self.charge = 0
        if self.charge_def < 0:
            self.charge_def = 0
        if self.discipline < 0:
            self.discipline = 0
        # ^ End rounding up

        self.rotate_speed = self.unit.rotate_speed * 2  # rotate speed for subunit only use for self rotate not subunit rotate related
        if self.state in (0, 99):
            self.rotate_speed = self.speed

        # v cooldown, active and effect timer function
        self.skill_cooldown = {key: val - self.timer for key, val in self.skill_cooldown.items()}  # cooldown decrease overtime
        self.skill_cooldown = {key: val for key, val in self.skill_cooldown.items() if val > 0}  # remove cooldown if time reach 0
        for a, b in self.skill_effect.items():  # Can't use dict comprehension here since value include all other skill stat
            b[3] -= self.timer
        self.skill_effect = {key: val for key, val in self.skill_effect.items() if
                             val[3] > 0 and self.state in val[6]}  # remove effect if time reach 0 or restriction state is not met
        for a, b in self.status_effect.items():
            b[3] -= self.timer
        self.status_effect = {key: val for key, val in self.status_effect.items() if val[3] > 0}
        # ^ End timer effectrangedamage

    def find_shooting_target(self, parentstate):
        """get nearby enemy base_target from list if not targeting anything yet"""
        self.attack_pos = list(self.unit.near_target.values())[0]  # replace attack_pos with enemy unit pos
        self.attack_target = list(self.unit.near_target.keys())[0]  # replace attack_target with enemy unit id
        if self.shoot_range >= self.attack_pos.distance_to(self.base_pos):
            self.state = 11
            if parentstate in (1, 3, 5):  # Walk and shoot
                self.state = 12
            elif parentstate in (2, 4, 6):  # Run and shoot
                self.state = 13

    def make_front_pos(self):
        """create new pos for front side of sprite"""
        self.front_pos = (self.base_pos[0], (self.base_pos[1] - self.image_height))

        self.front_pos = rotation_xy(self.base_pos, self.front_pos, self.radians_angle)

    def make_pos_range(self):
        """create range of sprite pos for pathfinding"""
        self.pos_range = (range(int(max(0, self.base_pos[0] - (self.image_height - 1))), int(min(1000, self.base_pos[0] + self.image_height))),
                          range(int(max(0, self.base_pos[1] - (self.image_height - 1))), int(min(1000, self.base_pos[1] + self.image_height))))

    def gamestart(self, zoom):
        """run once when self start or subunit just get created"""
        self.zoom = zoom
        self.make_front_pos()
        self.make_pos_range()
        self.zoom_scale()
        self.find_nearby_subunit()
        self.status_update()
        self.terrain, self.feature = self.get_feature(self.base_pos, self.base_map)
        self.height = self.height_map.get_height(self.base_pos)

    def update(self, weather, newdt, zoom, combat_timer, mousepos, mouseup):
        if self.last_zoom != zoom:  # camera zoom is changed
            self.last_zoom = zoom
            self.zoom_change = True
            self.zoom = zoom  # save scale
            self.zoom_scale()  # update unit sprite according to new scale

        if self.unit_health > 0:  # only run these when not dead
            # v Mouse collision detection
            if self.battle.game_state == 1 or (
                    self.battle.game_state == 2 and self.battle.unit_build_slot not in self.battle.battle_ui):
                if self.rect.collidepoint(mousepos):
                    self.battle.last_mouseover = self.unit  # last mouse over on this unit
                    if mouseup and self.battle.ui_click is False:
                        self.battle.last_selected = self.unit  # become last selected unit
                        if self.unit.selected is False:
                            self.unit.just_selected = True
                            self.unit.selected = True
                        self.who_last_select = self.game_id
                        self.battle.click_any = True
            # ^ End mouse detect

            dt = newdt
            if dt > 0:  # only run these when self not pause
                self.timer += dt

                self.walk = False  # reset walk
                self.run = False  # reset run

                parent_state = self.unit.state
                if parent_state in (1, 2, 3, 4):
                    self.attacking = True
                elif self.attacking and parent_state not in (1, 2, 3, 4, 10):  # cancel charge when no longer move to melee or in combat
                    self.attacking = False
                if self.state not in (95, 97, 98, 99) and parent_state in (0, 1, 2, 3, 4, 5, 6, 95, 96, 97, 98, 99):
                    self.state = parent_state  # Enforce unit state to subunit when moving and breaking

                self.attack_target = self.unit.attack_target
                self.attack_pos = self.unit.base_attack_pos

                if self.timer > 1:  # Update status and skill use around every 1 second
                    self.status_update(weather)
                    self.available_skill = []

                    if self.skill_cond != 3:  # any skill condition behaviour beside 3 (forbid skill) will check available skill to use
                        self.check_skill_condition()

                    if self.state in (4, 13) and parent_state != 10 and self.attacking and self.unit.move_rotate is False and \
                            self.base_pos.distance_to(self.base_target) < 50:  # charge skill only when running to melee

                        self.charge_momentum += self.timer * (self.speed / 50)
                        if self.charge_momentum >= 5:
                            self.use_skill(0)  # Use charge skill
                            self.unit.charging = True
                            self.charge_momentum = 5

                    elif self.charge_momentum > 1:  # reset charge momentum if charge skill not active
                        self.charge_momentum -= self.timer * (self.speed / 50)
                        if self.charge_momentum <= 1:
                            self.unit.charging = False
                            self.charge_momentum = 1

                    skillchance = random.randint(0, 10)  # random chance to use random available skill
                    if len(self.available_skill) > 0 and skillchance >= 6:
                        self.use_skill(self.available_skill[random.randint(0, len(self.available_skill) - 1)])
                    self.timer -= 1

                # if parent_state not in (96,97,98,99) and self.state != 99:
                collide_list = []
                if self.enemy_front != [] or self.enemy_side != []:  # Check if in combat or not with collision
                    collide_list = self.enemy_front + self.enemy_side
                    for subunit in collide_list:
                        if self.state not in (96, 98, 99):
                            self.state = 10
                            self.melee_target = subunit
                            if self.enemy_front == []:  # no enemy in front try rotate to enemy at side
                                # self.base_target = self.melee_target.base_pos
                                self.new_angle = self.set_rotate(self.melee_target.base_pos)
                        else:  # no way to retreat, Fight to the death
                            if self.enemy_front != [] and self.enemy_side != []:  # if both front and any side got attacked
                                if 9 not in self.status_effect:
                                    self.status_effect[9] = self.status_list[9].copy()  # fight to the death status
                        if parent_state not in (10, 96, 98, 99):
                            parent_state = 10
                            self.unit.state = 10
                        if self.melee_target is not None:
                            self.unit.attack_target = self.melee_target.parentunit
                        break

                elif parent_state == 10:  # no collide enemy while parent unit in fight state
                    if self.attacking and self.unit.collide:
                        if self.charge_momentum == 1 and (
                                self.frontline or self.unit.attack_mode == 2) and self.unit.attack_mode != 1:  # attack to nearest target instead
                            if self.melee_target is None and self.unit.attack_target is not None:
                                self.melee_target = self.unit.attack_target.subunit_sprite[0]
                            if self.melee_target is not None:
                                if self.close_target is None:  # movement queue is empty regenerate new one
                                    self.close_target = self.find_close_target(self.melee_target.parentunit.subunit_sprite)  # find new close target

                                    if self.close_target is not None:  # found target to fight
                                        if self not in self.battle.combat_path_queue:
                                            self.battle.combat_path_queue.append(self)

                                    else:  # no target to fight move back to command pos first)
                                        self.base_target = self.attack_target.base_pos
                                        self.new_angle = self.set_rotate()

                                if self.melee_target.parentunit.state != 100:
                                    if self.move_timer == 0:
                                        self.move_timer = 0.1  # recalculate again in 10 seconds if not in fight
                                        # if len(self.same_front) != 0 and len(self.enemy_front) == 0: # collide with friend try move to base_target first before enemy
                                        # self.combat_move_queue = [] # clean queue since the old one no longer without collide
                                    else:
                                        self.move_timer += dt
                                        if len(self.enemy_front) != 0 or len(self.enemy_side) != 0:  # in fight, stop timer
                                            self.move_timer = 0

                                        elif self.move_timer > 10 or len(self.combat_move_queue) == 0:  # # time up, or no path. reset path
                                            self.move_timer = 0
                                            self.close_target = None
                                            if self in self.battle.combat_path_queue:
                                                self.battle.combat_path_queue.remove(self)

                                        elif len(self.combat_move_queue) > 0:  # no collide move to enemy
                                            self.base_target = pygame.Vector2(self.combat_move_queue[0])
                                            self.new_angle = self.set_rotate()

                                else:  # whole targeted enemy unit destroyed, reset target and state
                                    self.melee_target = None
                                    self.close_target = None
                                    if self in self.battle.combat_path_queue:
                                        self.battle.combat_path_queue.remove(self)

                                    self.attack_target = None
                                    self.base_target = self.command_target
                                    self.new_angle = self.set_rotate()
                                    self.new_angle = self.unit.angle
                                    self.state = 0

                    elif self.attacking is False:  # not in fight anymore, rotate and move back to original position
                        self.melee_target = None
                        self.close_target = None
                        if self in self.battle.combat_path_queue:
                            self.battle.combat_path_queue.remove(self)

                        self.attack_target = None
                        self.base_target = self.command_target
                        self.new_angle = self.unit.angle
                        self.state = 0

                    if self.state != 10 and self.magazine_left > 0 and self.unit.fire_at_will == 0 and (self.arcshot or self.frontline) and \
                            self.charge_momentum == 1:  # Range attack when unit in melee state with arcshot
                        self.state = 11
                        if self.unit.near_target != {} and (self.attack_target is None or self.attack_pos == 0):
                            self.find_shooting_target(parent_state)
                # ^ End melee check

                else:  # range attack
                    self.melee_target = None
                    self.close_target = None
                    if self in self.battle.combat_path_queue:
                        self.battle.combat_path_queue.remove(self)
                    self.attack_target = None
                    self.combat_move_queue = []

                    # v Range attack function
                    if parent_state == 11:  # Unit in range attack state
                        self.state = 0  # Default state at idle
                        if (self.magazine_left > 0 or self.ammo_now > 0) and self.attack_pos != 0 and \
                                self.shoot_range >= self.attack_pos.distance_to(self.base_pos):
                            self.state = 11  # can shoot if have magazine_left and in shoot range, enter range combat state

                    elif self.magazine_left > 0 and self.unit.fire_at_will == 0 and \
                            (self.state == 0 or (self.state not in (95, 96, 97, 98, 99) and
                                                 parent_state in (1, 2, 3, 4, 5, 6) and self.shootmove)):  # Fire at will
                        if self.unit.near_target != {} and self.attack_target is None:
                            self.find_shooting_target(parent_state)  # shoot nearest target

                if self.state in (11, 12, 13) and self.magazine_left > 0 and self.ammo_now == 0:  # reloading magazine_left
                    self.reload_time += dt
                    if self.reload_time >= self.reload:
                        self.ammo_now = self.magazine_size
                        self.magazine_left -= 1
                        self.reload_time = 0
                    self.stamina = self.stamina - (dt * 2)  # use stamina while reloading
                # ^ End range attack function

                # v Combat action related
                if combat_timer >= 0.5:  # combat is calculated every 0.5 second in self time
                    if self.state == 10:  # if melee combat (engaging anyone on any side)
                        collide_list = [subunit for subunit in self.enemy_front]
                        for subunit in collide_list:
                            anglecheck = abs(self.angle - subunit.angle)  # calculate which side arrow hit the subunit
                            if anglecheck >= 135:  # front
                                hitside = 0
                            elif anglecheck >= 45:  # side
                                hitside = 1
                            else:  # rear
                                hitside = 2
                            self.dmg_cal(subunit, 0, hitside, self.battle.troop_data.status_list, combat_timer)
                            self.stamina = self.stamina - (combat_timer * 5)

                    elif self.state in (11, 12, 13):  # range combat
                        if type(self.attack_target) == int:  # For fire at will, which attacktarget is int
                            all_unit_index = self.battle.all_unit_index
                            if self.attack_target in all_unit_index:  # if the attack base_target still alive (if dead it would not be in index list)
                                self.attack_target = self.battle.all_unit_list[
                                    all_unit_index.index(self.attack_target)]  # change attack_target index into sprite
                            else:  # enemy dead
                                self.attack_pos = 0  # reset attack_pos to 0
                                self.attack_target = None  # reset attack_target to 0

                                for target in list(self.unit.near_target.values()):  # find other nearby base_target to shoot
                                    if target in all_unit_index:  # check if base_target alive
                                        self.attack_pos = target[1]
                                        self.attack_target = target[1]
                                        self.attack_target = self.battle.all_unit_list[all_unit_index.index(self.attack_target)]
                                        break  # found new base_target break loop
                        elif self.attack_target is None:
                            self.attack_target = self.unit.attack_target

                        if self.ammo_now > 0 and ((self.attack_target is not None and self.attack_target.state != 100) or
                                                  (self.attack_target is None and self.attack_pos != 0)) \
                                and (self.arcshot or (self.arcshot is False and self.unit.shoot_mode != 1)):
                            # can shoot if reload finish and base_target existed and not dead. Non arcshot cannot shoot if forbidded
                            # TODO add line of sight for range attack
                            rangeattack.RangeArrow(self, self.base_pos.distance_to(self.attack_pos), self.shoot_range, self.zoom)  # Shoot
                            self.ammo_now -= 1  # use 1 magazine_left in magazine
                        elif self.attack_target is not None and self.attack_target.state == 100:  # if base_target destroyed when it about to shoot
                            self.unit.range_combat_check = False
                            self.unit.attack_target = 0  # reset range combat check and base_target
                # ^ End combat related

                if parent_state != 10:  # reset base_target every update to command base_target outside of combat
                    if self.base_target != self.command_target:
                        self.base_target = self.command_target
                        if parent_state == 0:
                            self.new_angle = self.set_rotate()
                    elif self.base_pos == self.base_target and self.angle != self.unit.angle:  # reset angle
                        self.new_angle = self.set_rotate()
                        self.new_angle = self.unit.angle

                if self.angle != self.new_angle:  # Rotate Function
                    self.rotate_logic(dt)

                self.move_logic(dt, parent_state, collide_list)  # Move function

                # v Morale check
                if self.max_morale != infinity:
                    if self.base_morale < self.max_morale:
                        if self.morale <= 10:  # Enter retreat state when morale reach 0
                            if self.state not in (98, 99):
                                self.state = 98  # retreat state
                                maxrandom = 1 - (self.mental / 100)
                                if maxrandom < 0:
                                    maxrandom = 0
                                self.morale_regen -= random.uniform(0, maxrandom)  # morale regen slower per broken state
                                if self.morale_regen < 0:  # begin checking broken state
                                    self.state = 99  # Broken state
                                    self.change_leader("broken")

                                    cornerlist = [[0, self.base_pos[1]], [1000, self.base_pos[1]], [self.base_pos[0], 0], [self.base_pos[0], 1000]]
                                    whichcorner = [self.base_pos.distance_to(cornerlist[0]), self.base_pos.distance_to(cornerlist[1]),
                                                   self.base_pos.distance_to(cornerlist[2]),
                                                   self.base_pos.distance_to(cornerlist[3])]  # find closest map corner to run to
                                    foundcorner = whichcorner.index(min(whichcorner))
                                    self.base_target = pygame.Vector2(cornerlist[foundcorner])
                                    self.command_target = self.base_target
                                    self.new_angle = self.set_rotate()

                                for subunit in self.unit.subunit_sprite:
                                    subunit.base_morale -= (
                                            15 * subunit.mental)  # reduce morale of other subunit, creating panic when seeing friend panic and may cause mass panic
                            if self.morale < 0:
                                self.morale = 0  # morale cannot be lower than 0

                        if self.state not in (95, 99) and parent_state not in (10, 99):  # If not missing gamestart leader can replenish morale
                            self.base_morale += (dt * self.staminastatecal * self.morale_regen)  # Morale replenish based on stamina

                        if self.base_morale < 0:  # morale cannot be negative
                            self.base_morale = 0

                    elif self.base_morale > self.max_morale:
                        self.base_morale -= dt  # gradually reduce morale that exceed the starting max amount

                    if self.state == 95:  # disobey state, morale gradually decrease until recover
                        self.base_morale -= dt * self.mental

                    elif self.state == 98:
                        if parent_state not in (98, 99):
                            self.unit_health -= (dt * 100)  # Unit begin to desert if retreating but unit not retreat/broken
                            if self.moralestate > 0.2:
                                self.state = 0  # Reset state to 0 when exit retreat state
                # ^ End morale check

                # v Hp and stamina regen
                if self.stamina != infinity:
                    if self.stamina < self.max_stamina:
                        if self.stamina <= 0:  # Collapse and cannot act
                            self.stamina = 0
                            self.status_effect[105] = self.status_list[105].copy()  # receive collapse status
                        self.stamina = self.stamina + (dt * self.stamina_regen)  # regen
                    else:  # stamina cannot exceed the max stamina
                        self.stamina = self.max_stamina
                if self.unit_health != infinity:
                    if self.hp_regen > 0 and self.unit_health % self.troop_health != 0:  # hp regen cannot ressurect troop only heal to max hp
                        alivehp = self.troop_number * self.troop_health  # max hp possible for the number of alive subunit
                        self.unit_health += self.hp_regen * dt  # regen hp back based on time and regen stat
                        if self.unit_health > alivehp:
                            self.unit_health = alivehp  # Cannot exceed health of alive subunit (exceed mean resurrection)
                    elif self.hp_regen < 0:  # negative regen can kill
                        self.unit_health += self.hp_regen * dt  # use the same as positive regen (negative regen number * dt will reduce hp)
                        remain = self.unit_health / self.troop_health
                        if remain.is_integer() is False:  # always round up if there is decimal number
                            remain = int(remain) + 1
                        else:
                            remain = int(remain)
                        wound = random.randint(0, (self.troop_number - remain))  # chance to be wounded instead of dead
                        self.battle.death_troopnumber[self.team] += self.troop_number - remain - wound
                        self.battle.wound_troopnumber[self.team] += wound
                        self.troop_number = remain  # Recal number of troop again in case some destroyed from negative regen

                    if self.unit_health < 0:
                        self.unit_health = 0  # can't have negative hp
                    elif self.unit_health > self.max_health:
                        self.unit_health = self.max_health  # hp can't exceed max hp (would increase number of troop)

                    if self.oldlasthealth != self.unit_health:
                        remain = self.unit_health / self.troop_health
                        if remain.is_integer() is False:  # always round up if there is decimal number
                            remain = int(remain) + 1
                        else:
                            remain = int(remain)
                        wound = random.randint(0, (self.troop_number - remain))  # chance to be wounded instead of dead
                        self.battle.death_troopnumber[self.team] += self.troop_number - remain - wound
                        if self.state in (98, 99) and len(self.enemy_front) + len(
                                self.enemy_side) > 0:  # fleeing or broken got captured instead of wound
                            self.battle.capture_troopnumber[self.team] += wound
                        else:
                            self.battle.wound_troopnumber[self.team] += wound
                        self.troop_number = remain  # Recal number of troop again in case some destroyed from negative regen

                        # v Health bar
                        for index, health in enumerate(self.health_list):
                            if self.unit_health > health:
                                if self.last_health_state != abs(4 - index):
                                    self.image_original3.blit(self.health_image_list[index + 1], self.health_image_rect)
                                    self.block_original.blit(self.health_image_list[index + 1], self.health_block_rect)
                                    self.block.blit(self.block_original, self.corner_image_rect)
                                    self.last_health_state = abs(4 - index)
                                    self.zoom_scale()
                                break
                        # ^ End Health bar

                        self.oldlasthealth = self.unit_health

                # v Stamina bar
                if self.old_last_stamina != self.stamina:
                    stamina_list = (self.stamina75, self.stamina50, self.stamina25, self.stamina5, -1)
                    for index, stamina in enumerate(stamina_list):
                        if self.stamina >= stamina:
                            if self.last_stamina_state != abs(4 - index):
                                # if index != 3:
                                self.image_original3.blit(self.stamina_image_list[index + 6], self.stamina_image_rect)
                                self.zoom_scale()
                                self.block_original.blit(self.stamina_image_list[index + 6], self.stamina_block_rect)
                                self.block.blit(self.block_original, self.corner_image_rect)
                                self.last_stamina_state = abs(4 - index)
                            break

                    self.old_last_stamina = self.stamina
                # ^ End stamina bar

            if self.state in (98, 99) and (self.base_pos[0] <= 0 or self.base_pos[0] >= 999 or
                                           self.base_pos[1] <= 0 or self.base_pos[1] >= 999):  # remove when unit move pass map border
                self.state = 100  # enter dead state
                self.battle.flee_troopnumber[self.team] += self.troop_number  # add number of troop retreat from battle
                self.troop_number = 0
                self.battle.battle_camera.remove(self)

            self.enemy_front = []  # reset collide
            self.enemy_side = []
            self.friend_front = []
            self.same_front = []
            self.full_merge = []
            self.collide_penalty = False

        else:  # dead
            if self.state != 100:  # enter dead state
                self.state = 100  # enter dead state
                self.image_original3.blit(self.health_image_list[5], self.health_image_rect)  # blit white hp bar
                self.block_original.blit(self.health_image_rect[5], self.health_block_rect)
                self.zoom_scale()
                self.last_health_state = 0
                self.skill_cooldown = {}  # remove all cooldown
                self.skill_effect = {}  # remove all skill effects

                self.block.blit(self.block_original, self.corner_image_rect)
                self.red_border = True  # to prevent red border appear when dead

                self.unit.dead_change = True

                if self in self.battle.battle_camera:
                    self.battle.battle_camera.change_layer(sprite=self, new_layer=1)
                self.battle.all_subunit_list.remove(self)
                self.unit.subunit_sprite.remove(self)

                for subunit in self.unit.subunit_list.flat:  # remove from index array
                    if subunit == self.game_id:
                        self.unit.subunit_list = np.where(self.unit.subunit_list == self.game_id, 0, self.unit.subunit_list)
                        break

                self.change_leader("destroyed")

                self.battle.event_log.add_log([0, str(self.board_pos) + " " + str(self.name)
                                               + " in " + self.unit.leader[0].name
                                               + "'s unit is destroyed"], [3])  # add log to say this subunit is destroyed in subunit tab

    def combat_pathfind(self):
        # v Pathfinding
        self.combat_move_queue = []
        movearray = self.battle.subunit_pos_array.copy()
        intbasetarget = (int(self.close_target.base_pos[0]), int(self.close_target.base_pos[1]))
        for y in self.close_target.pos_range[0]:
            for x in self.close_target.pos_range[1]:
                movearray[x][y] = 100  # reset path in the enemy sprite position

        intbasepos = (int(self.base_pos[0]), int(self.base_pos[1]))
        for y in self.pos_range[0]:
            for x in self.pos_range[1]:
                movearray[x][y] = 100  # reset path for sub-unit sprite position

        startpoint = (min([max(0, intbasepos[0] - 5), max(0, intbasetarget[0] - 5)]),  # start point of new smaller array
                      min([max(0, intbasepos[1] - 5), max(0, intbasetarget[1] - 5)]))
        endpoint = (max([min(999, intbasepos[0] + 5), min(999, intbasetarget[0] + 5)]),  # end point of new array
                    max([min(999, intbasepos[1] + 5), min(999, intbasetarget[1] + 5)]))

        movearray = movearray[startpoint[1]:endpoint[1]]  # cut 1000x1000 array into smaller one by row
        movearray = [thisarray[startpoint[0]:endpoint[0]] for thisarray in movearray]  # cut by column

        # if len(movearray) < 100 and len(movearray[0]) < 100: # if too big then skip combat pathfinding
        grid = Grid(matrix=movearray)
        grid.cleanup()

        start = grid.node(intbasepos[0] - startpoint[0], intbasepos[1] - startpoint[1])  # start point
        end = grid.node(intbasetarget[0] - startpoint[0], intbasetarget[1] - startpoint[1])  # end point

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)
        path = [(thispath[0] + startpoint[0], thispath[1] + startpoint[1]) for thispath in path]  # remake pos into actual map pos

        path = path[4:]  # remove some starting path that may clip with friendly sub-unit sprite

        self.combat_move_queue = path  # add path into combat movement queue
        if len(self.combat_move_queue) < 1:  # simply try walk to target anyway if pathfinder return empty
            self.combat_move_queue = [self.close_target.base_pos]
        # print("operations:", runs, "path length:", len(path))
        # print(grid.grid_str(path=path, start=start, end=end))
        # print(self.combat_move_queue)
        # print(self.base_pos, self.close_target.base_pos, self.game_id, startpoint, intbasepos[0] - startpoint[0], intbasepos[1] - startpoint[1])
        # ^ End path finding

    def add_trait(self):
        """Add trait to base stat"""
        trait_header = self.stat_list.trait_list_header

        for trait in self.trait.values():  # add trait modifier to base stat
            self.base_attack *= trait[trait_header['Melee Attack Effect']]
            self.base_melee_def *= trait[trait_header['Melee Defence Effect']]
            self.base_range_def *= trait[trait_header['Ranged Defence Effect']]
            self.base_armour += trait[trait_header['Armour Bonus']]
            self.base_speed *= trait[trait_header['Speed Effect']]
            self.base_accuracy *= trait[trait_header['Accuracy Effect']]
            self.base_range *= trait[trait_header['Range Effect']]
            self.base_reload *= trait[trait_header['Reload Effect']]
            self.base_charge *= trait[trait_header['Charge Effect']]
            self.base_charge_def += trait[trait_header['Charge Defence Bonus']]
            self.base_hp_regen += trait[trait_header['HP Regeneration Bonus']]
            self.base_stamina_regen += trait[trait_header['Stamina Regeneration Bonus']]
            self.base_morale += trait[trait_header['Morale Bonus']]
            self.base_discipline += trait[trait_header['Discipline Bonus']]
            self.crit_effect += trait[trait_header['Critical Bonus']]
            self.elem_res[0] += (trait[trait_header['Fire Resistance']] / 100)  # percentage, 1 mean perfect resistance, 0 mean none
            self.elem_res[1] += (trait[trait_header['Water Resistance']] / 100)
            self.elem_res[2] += (trait[trait_header['Air Resistance']] / 100)
            self.elem_res[3] += (trait[trait_header['Earth Resistance']] / 100)
            self.magic_res += (trait[trait_header['Magic Resistance']] / 100)
            self.heat_res += (trait[trait_header['Heat Resistance']] / 100)
            self.cold_res += (trait[trait_header['Cold Resistance']] / 100)
            self.elem_res[4] += (trait[trait_header['Poison Resistance']] / 100)
            self.mental += trait[trait_header['Mental Bonus']]
            if trait[trait_header['Enemy Status']] != [0]:
                for effect in trait[trait_header['Enemy Status']]:
                    self.base_inflict_status[effect] = trait[trait_header['Buff Range']]
            # self.base_elem_melee =
            # self.base_elem_range =

        if 3 in self.trait:  # Varied training
            self.base_attack *= (random.randint(70, 120) / 100)
            self.base_melee_def *= (random.randint(70, 120) / 100)
            self.base_range_def *= (random.randint(70, 120) / 100)
            self.base_speed *= (random.randint(70, 120) / 100)
            self.base_accuracy *= (random.randint(70, 120) / 100)
            self.base_reload *= (random.randint(70, 120) / 100)
            self.base_charge *= (random.randint(70, 120) / 100)
            self.base_charge_def *= (random.randint(70, 120) / 100)
            self.base_morale += random.randint(-15, 10)
            self.base_discipline += random.randint(-20, 0)
            self.mental += random.randint(-20, 10)

        # v Change trait variable
        if 16 in self.trait:
            self.arcshot = True  # can shoot in arc
        if 17 in self.trait:
            self.agileaim = True  # gain bonus accuracy when shoot while moving
        if 18 in self.trait:
            self.shootmove = True  # can shoot and move at same time
        if 29 in self.trait:
            self.ignore_chargedef = True  # ignore charge defence completely
        if 30 in self.trait:
            self.ignore_def = True  # ignore defence completely
        if 34 in self.trait:
            self.full_def = True  # full effective defence for all side
        if 33 in self.trait:
            self.backstab = True  # bonus on rear attack
        if 47 in self.trait:
            self.flanker = True  # bonus on flank attack
        if 55 in self.trait:
            self.oblivious = True  # more penalty on flank/rear defend
        if 73 in self.trait:
            self.no_range_penal = True  # no range penalty
        if 74 in self.trait:
            self.long_range_acc = True  # less range penalty
        if 111 in self.trait:
            self.unbreakable = True  # always unbreakable
            self.temp_unbreakable = True
        if 149 in self.trait:  # Impetuous
            self.base_auth_penalty += 0.5
        # ^ End change trait variable
        # ^^ End add trait to stat

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.unit
            del self.leader
            del self.who_last_select
            del self.attack_target
            del self.melee_target
            del self.close_target
            if self in self.battle.combat_path_queue:
                self.battle.combat_path_queue.remove(self)
