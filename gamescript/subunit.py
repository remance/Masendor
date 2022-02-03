import math
import random

import pygame
import pygame.freetype
from gamescript.common import utility, animation
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pygame.transform import scale

rotation_xy = utility.rotation_xy


def change_subunit_genre(genre):
    """Change game genre and add appropriate method to subunit class"""
    if genre == "tactical":
        from gamescript.tactical.subunit import fight, spawn, movement, refresh
    elif genre == "arcade":
        from gamescript.arcade.subunit import fight, spawn, movement, refresh

    Subunit.add_weapon_stat = spawn.add_weapon_stat
    Subunit.add_mount_stat = spawn.add_mount_stat
    Subunit.add_trait = spawn.add_trait
    Subunit.create_sprite = spawn.create_sprite
    Subunit.attack_logic = fight.attack_logic
    Subunit.dmg_cal = fight.dmg_cal
    Subunit.change_leader = fight.change_leader
    Subunit.die = fight.die
    Subunit.rotate = movement.rotate
    Subunit.rotate_logic = movement.rotate_logic
    Subunit.move_logic = movement.move_logic
    Subunit.player_interact = refresh.player_interact
    Subunit.status_update = refresh.status_update
    Subunit.morale_logic = refresh.morale_logic
    Subunit.health_stamina_logic = refresh.health_stamina_logic
    Subunit.charge_logic = refresh.charge_logic


class Subunit(pygame.sprite.Sprite):
    unit_ui_images = []
    battle = None
    base_map = None  # base map
    feature_map = None  # feature map
    height_map = None  # height map
    weapon_list = None
    armour_list = None
    stat_list = None
    status_list = None
    generic_animation_pool = None
    max_zoom = 10  # max zoom allow
    screen_scale = (1, 1)

    play_animation = animation.play_animation
    set_rotate = utility.set_rotate

    # method that change based on genre
    add_weapon_stat = None
    add_mount_stat = None
    add_trait = None
    create_sprite = None
    attack_logic = None
    dmg_cal = None
    change_leader = None
    die = None
    rotate = None
    rotate_logic = None
    move_logic = None
    player_interact = None
    status_update = None
    morale_logic = None
    health_stamina_logic = None
    charge_logic = None

    def __init__(self, troop_id, game_id, unit, start_pos, start_hp, start_stamina, unit_scale, genre, purpose="battle"):
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.get_feature = self.feature_map.get_feature
        self.get_height = self.height_map.get_height

        self.who_last_select = None
        self.leader = None  # Leader in the sub-subunit if there is one, got add in leader start_set
        self.board_pos = None  # Used for event log position of subunit (Assigned in battle subunit setup)
        self.walk = False  # currently walking
        self.run = False  # currently running
        self.frontline = False  # on front line of unit or not
        self.unit_leader = False  # contain the general or not, making it leader subunit
        self.attack_target = None
        self.melee_target = None  # current target of melee combat
        self.close_target = None  # closet target to move to in melee
        self.attacking = False  # For checking if unit in attacking state or not for using charge skill

        self.current_animation = {}  # list of animation frames playing
        self.animation_queue = []  # list of animation queue
        self.current_frame = 0

        self.enemy_front = []  # list of front collide sprite
        self.enemy_side = []  # list of side collide sprite
        self.friend_front = []  # list of friendly front collide sprite
        self.same_front = []  # list of same unit front collide sprite
        self.full_merge = []  # list of sprite that collide and almost overlap with this sprite
        self.collide_penalty = False

        self.game_id = game_id  # ID of this
        self.troop_id = int(troop_id)  # ID of preset used for this subunit
        self.unit = unit  # reference to the parent uit of this subunit
        self.team = self.unit.team

        self.red_border = False  # red corner to indicate taking melee_dmg in inspect ui
        self.state = 0  # Current subunit state, similar to unit state
        self.timer = random.random()  # may need to use random.random()
        self.move_timer = 0  # timer for moving to front position before attacking nearest enemy
        self.charge_momentum = 1  # charging momentum to reach target before choosing the nearest enemy
        self.ammo_now = 0
        self.zoom = 1
        self.last_zoom = 10
        self.skill_cond = 0
        self.broken_limit = 0  # morale require for unit to stop broken state, will increase everytime broken state stop

        # v Setup troop original stat before applying trait, gear and other stuffs
        stat = self.stat_list.troop_list[self.troop_id].copy()
        self.name = stat["Name"]  # name according to the preset
        self.grade = stat["Grade"]  # training level/class grade
        self.race = stat["Race"]  # creature race
        self.original_trait = stat["Trait"]  # trait list from preset
        self.original_trait = self.original_trait + self.stat_list.grade_list[self.grade]["Trait"]  # add trait from grade
        skill = stat["Skill"]  # skill list according to the preset
        self.skill_cooldown = {}
        self.cost = stat["Cost"]
        grade_stat = self.stat_list.grade_list[self.grade]
        self.grade_name = grade_stat["Name"]
        self.original_melee_attack = stat["Melee Attack"] + grade_stat["Melee Attack Bonus"]  # base melee melee_attack with grade bonus
        self.original_melee_def = stat["Melee Defence"] + grade_stat["Defence Bonus"]  # base melee defence with grade bonus
        self.original_range_def = stat["Ranged Defence"] + grade_stat["Defence Bonus"]  # base range defence with grade bonus
        self.armour_gear = stat["Armour"]  # armour equipment
        self.original_armour = 0  # TODO change when has race or something
        self.base_armour = self.armour_list.armour_list[self.armour_gear[0]]["Armour"] \
                           * self.armour_list.quality[self.armour_gear[1]]  # armour stat is calculated from based armour * quality
        self.original_accuracy = stat["Accuracy"] + grade_stat["Accuracy Bonus"]
        self.original_sight = stat["Sight"]  # base sight range
        self.magazine_left = stat["Ammunition"]  # amount of ammunition
        self.original_reload = stat["Reload"] + grade_stat["Reload Bonus"]
        self.original_charge = stat["Charge"]
        self.original_charge_def = 50  # All infantry subunit has default 50 charge defence
        self.charge_skill = stat["Charge Skill"]  # For easier reference to check what charge skill this subunit has
        self.original_skill = [self.charge_skill] + skill  # Add charge skill as first item in the list
        self.troop_health = stat["Health"] * grade_stat["Health Effect"]  # Health of each troop
        self.stamina = stat["Stamina"] * grade_stat["Stamina Effect"] * (start_stamina / 100)  # starting stamina with grade
        self.original_mana = stat["Mana"]  # Resource for magic skill

        # vv Equipment stat
        self.primary_main_weapon = stat["Primary Main Weapon"]
        self.primary_sub_weapon = stat["Primary Sub Weapon"]
        self.secondary_main_weapon = stat["Secondary Main Weapon"]
        self.secondary_sub_weapon = stat["Secondary Sub Weapon"]

        self.mount = self.stat_list.mount_list[stat["Mount"][0]]  # mount this subunit use
        self.mount_grade = self.stat_list.mount_grade_list[stat["Mount"][1]]
        self.mount_armour = self.stat_list.mount_armour_list[stat["Mount"][2]]

        self.weight = 0
        self.melee_dmg = [0, 0]
        self.melee_penetrate = 0
        self.range_dmg = [0, 0]
        self.range_penetrate = 0
        self.base_range = 0
        self.weapon_speed = 0
        self.magazine_size = 0

        self.original_morale = stat["Morale"] + grade_stat["Morale Bonus"]  # morale with grade bonus
        self.original_discipline = stat["Discipline"] + grade_stat["Discipline Bonus"]  # discipline with grade bonus
        self.mental = stat["Mental"] + grade_stat["Mental Bonus"]  # mental resistance from morale melee_dmg and mental status effect
        self.troop_number = stat["Troop"] * unit_scale[self.team - 1] * start_hp / 100  # number of starting troop, team -1 to become list index
        self.original_speed = 50  # All infantry has base speed at 50
        self.subunit_type = stat["Troop Class"] - 1  # 0 is melee infantry and 1 is range for command buff
        self.feature_mod = 1  # the starting column in terrain bonus of infantry
        self.authority = 100  # default start at 100

        # vv Elemental stat
        self.original_elem_melee = 0  # start with physical element for melee weapon
        self.original_elem_range = 0  # start with physical for range weapon
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
        self.corner_atk = False  # Check if subunit can melee_attack corner enemy or not
        self.flank_bonus = 1  # Combat bonus when flanking
        self.base_auth_penalty = 0.1  # penalty to authority when bad event happen
        self.bonus_morale_dmg = 0  # extra morale melee_dmg
        self.bonus_stamina_dmg = 0  # extra stamina melee_dmg
        self.auth_penalty = 0.1  # authority penalty for certain activities/order
        self.original_hp_regen = 0  # hp regeneration modifier, will not resurrect dead troop by default
        self.original_stamina_regen = 2  # stamina regeneration modifier
        self.original_morale_regen = 2  # morale regeneration modifier
        self.available_skill = []
        self.status_effect = {}  # list of current status effect
        self.skill_effect = {}  # list of activate skill effect
        self.base_inflict_status = {}  # list of status that this subunit will inflict to enemy when melee_attack
        self.special_status = []

        # vv Set up trait variable

        self.arc_shot = False
        self.anti_inf = False
        self.anti_cav = False
        self.shoot_move = False
        self.agile_aim = False
        self.no_range_penal = False
        self.long_range_acc = False
        self.ignore_charge_def = False
        self.ignore_def = False
        self.full_def = False
        self.temp_full_def = False
        self.backstab = False
        self.oblivious = False
        self.flanker = False
        self.unbreakable = False
        self.temp_unbreakable = False
        self.station_place = False
        # ^^ End setup trait variable
        # ^ End setup stat

        # stat after applying trait and gear

        self.trait = self.original_trait.copy()
        self.base_melee_attack = self.original_melee_attack
        self.base_melee_def = self.original_melee_def
        self.base_range_def = self.original_range_def
        # armour stat is calculated from based armour * quality
        self.base_armour = self.original_armour + (self.armour_list.armour_list[self.armour_gear[0]]["Armour"]
                                                   * self.armour_list.quality[self.armour_gear[1]])
        self.base_speed = self.original_speed
        self.base_accuracy = self.original_accuracy
        self.base_sight = self.original_sight
        self.base_reload = self.original_reload
        self.base_charge = self.original_charge
        self.base_charge_def = self.original_charge_def
        self.skill = self.original_skill.copy()
        self.base_mana = self.original_mana
        self.base_morale = self.original_morale
        self.base_discipline = self.original_discipline
        self.base_hp_regen = self.original_hp_regen
        self.base_stamina_regen = self.original_stamina_regen
        self.base_morale_regen= self.original_morale_regen
        self.base_elem_melee = self.original_elem_melee
        self.base_elem_range = self.original_elem_range

        if genre == "tactical":
            self.add_weapon_stat()
            if stat["Mount"][0] != 1:  # have a mount, add mount stat with its grade to subunit stat
                self.add_mount_stat()

            self.last_health_state = 4  # state start at full
            self.last_stamina_state = 4

            self.max_stamina = self.stamina
            self.stamina75 = self.stamina * 0.75
            self.stamina50 = self.stamina * 0.5
            self.stamina25 = self.stamina * 0.25
            self.stamina5 = self.stamina * 0.05

            self.unit_health = self.troop_health * self.troop_number  # Total health of subunit from all troop
            self.old_unit_health = self.unit_health
            self.max_health = self.unit_health  # health percentage
            self.health_list = (self.unit_health * 0.75, self.unit_health * 0.5, self.unit_health * 0.25, 0)

            self.old_last_health, self.old_last_stamina = self.unit_health, self.stamina  # save previous health and stamina in previous update
            self.max_troop = self.troop_number  # max number of troop at the start

            sprite_dict = self.create_sprite()
            self.image = sprite_dict["image"]
            self.image_original = sprite_dict["original"]
            self.image_original2 = sprite_dict["original2"]
            self.image_original3 = sprite_dict["original3"]
            self.block = sprite_dict["block"]
            self.block_original = sprite_dict["block_original"]
            self.selected_image = sprite_dict["selected"]
            self.selected_image_rect = sprite_dict["selected_rect"]
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

        self.trait += self.armour_list.armour_list[self.armour_gear[0]]["Trait"]  # Apply armour trait to subunit

        self.trait = list(set([trait for trait in self.trait if trait != 0]))  # remove empty and duplicate traits
        if len(self.trait) > 0:
            self.trait = {x: self.stat_list.trait_list[x] for x in self.trait if
                          x in self.stat_list.trait_list}  # Any trait not available in ruleset will be ignored
            self.add_trait()

        self.skill = {x: self.stat_list.skill_list[x].copy() for x in self.skill if
                      x != 0 and x in self.stat_list.skill_list}  # grab skill stat into dict
        for skill in list(self.skill.keys()):  # remove skill if class mismatch
            skill_troop_cond = self.skill[skill]["Troop Type"]
            if skill_troop_cond != 0 and self.subunit_type != skill_troop_cond:
                self.skill.pop(skill)

        # v Weight calculation
        self.weight += self.armour_list.armour_list[self.armour_gear[0]]["Weight"] + self.mount_armour["Weight"]  # Weight from both melee and range weapon and armour
        if self.subunit_type == 2:  # cavalry has half weight penalty
            self.weight = self.weight / 2
        # ^ End weight cal

        self.base_speed = (self.base_speed * ((100 - self.weight) / 100)) + grade_stat["Speed Bonus"]  # finalise base speed with weight and grade bonus
        self.size = stat["Size"]
        self.battle.start_troop_number[self.team] += self.troop_number  # add troop number to counter how many troop join battle
        self.description = stat["Description"]  # subunit description for inspect ui
        # if self.hidden

        # vv Stat variable after receive modifier effect from various sources, used for activity and effect calculation
        self.max_morale = self.base_morale
        self.melee_attack = self.base_melee_attack
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
        self.morale_regen = self.base_morale_regen
        self.inflict_status = self.base_inflict_status
        self.elem_melee = self.base_elem_melee
        self.elem_range = self.base_elem_range
        # ^^ End stat for status effect

        self.morale_state = self.base_morale / self.max_morale  # turn into percentage
        self.stamina_state = (self.stamina * 100) / self.max_stamina  # turn into percentage
        self.stamina_state_cal = self.stamina_state / 100  # for using as modifier on stat

        if self.mental < 0:  # cannot be negative
            self.mental = 0
        elif self.mental > 200:  # cannot exceed 100
            self.mental = 200
        self.mental_text = self.mental - 100
        self.mental = (200 - self.mental) / 100  # convert to percentage

        self.corner_atk = False  # cannot melee_attack corner enemy by default
        self.temp_full_def = False

        if purpose == "battle":
            self.battle.all_subunit_list.append(self)
            if self.team == 1:  # add sprite to team subunit group for collision
                group_collide = self.battle.team1_subunit
            elif self.team == 2:
                group_collide = self.battle.team2_subunit
            group_collide.add(self)

            self.angle = self.unit.angle
            self.new_angle = self.unit.angle
            self.radians_angle = math.radians(360 - self.angle)  # radians for apply angle to position
            self.parent_angle = self.unit.angle  # angle subunit will face when not moving

            # v position related
            self.unit_position = (start_pos[0] / 10, start_pos[1] / 10)  # position in unit sprite
            unit_top_left = pygame.Vector2(self.unit.base_pos[0] - self.unit.base_width_box / 2,
                                           self.unit.base_pos[
                                               1] - self.unit.base_height_box / 2)  # get top left corner position of unit to calculate true pos
            self.base_pos = pygame.Vector2(unit_top_left[0] + self.unit_position[0],
                                           unit_top_left[1] + self.unit_position[1])  # true position of subunit in map
            self.last_pos = self.base_pos
            self.attack_pos = self.unit.base_attack_pos

            self.movement_queue = []
            self.combat_move_queue = []
            self.base_target = self.base_pos  # base_target to move
            self.command_target = self.base_pos  # actual base_target outside of combat
            self.pos = (self.base_pos[0] * self.screen_scale[0] * self.zoom, self.base_pos[1] * self.screen_scale[1] * self.zoom)  # pos is for showing on screen

            self.image_height = (self.image.get_height() - 1) / 20  # get real half height of circle sprite

            self.front_pos = (self.base_pos[0], (self.base_pos[1] - self.image_height))  # generate front side position
            self.front_pos = rotation_xy(self.base_pos, self.front_pos, self.radians_angle)  # rotate the new front side according to sprite rotation

            self.terrain, self.feature = self.get_feature(self.base_pos, self.base_map)  # get new terrain and feature at each subunit position
            self.height = self.height_map.get_height(self.base_pos)  # current terrain height
            self.front_height = self.height_map.get_height(self.front_pos)  # terrain height at front position
            # ^ End position related
        elif purpose == "edit":
            self.image = self.block
            self.pos = start_pos
            self.inspect_pos = (self.pos[0] - (self.image.get_width() / 2), self.pos[1] - (self.image.get_height() / 2))
            self.image_original = self.block_original
            self.coa = self.unit.coa
            self.commander = True

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
        self.pos = (self.base_pos[0] * self.screen_scale[0] * self.zoom, self.base_pos[1] * self.screen_scale[1] * self.zoom)
        self.rect.center = self.pos

    def use_skill(self, which_skill):
        if which_skill == 0:  # charge skill need to separate since charge power will be used only for charge skill
            skill_stat = self.skill[list(self.skill)[0]].copy()  # get skill stat
            self.skill_effect[self.charge_skill] = skill_stat  # add stat to skill effect
            self.skill_cooldown[self.charge_skill] = skill_stat["Cooldown"]  # add skill cooldown
        else:  # other skill
            skill_stat = self.skill[which_skill].copy()  # get skill stat
            self.skill_effect[which_skill] = skill_stat  # add stat to skill effect
            self.skill_cooldown[which_skill] = skill_stat["Cooldown"]  # add skill cooldown
        self.stamina -= skill_stat["Stamina Cost"]
        # self.skill_cooldown[which_skill] =

    # def receiveskill(self,which_skill):

    def check_skill_condition(self):
        """Check which skill can be used, cooldown, condition state, discipline, stamina are checked. charge skill is excepted from this check"""
        if self.skill_cond == 1 and self.stamina_state < 50:  # reserve 50% stamina, don't use any skill
            self.available_skill = []
        elif self.skill_cond == 2 and self.stamina_state < 25:  # reserve 25% stamina, don't use any skill
            self.available_skill = []
        else:  # check all skill
            self.available_skill = [skill for skill in self.skill if skill not in self.skill_cooldown.keys()
                                    and self.state in self.skill[skill]["Condition"] and self.discipline >= self.skill[skill][
                                        "Discipline Requirement"]
                                    and self.stamina > self.skill[skill]["Stamina Cost"] and skill != self.charge_skill]

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
        """Find close enemy subunit to move to fight"""
        close_list = {subunit: subunit.base_pos.distance_to(self.base_pos) for subunit in subunit_list}
        close_list = dict(sorted(close_list.items(), key=lambda item: item[1]))
        max_random = 3
        if len(close_list) < 4:
            max_random = len(close_list) - 1
            if max_random < 0:
                max_random = 0
        close_target = None
        if len(close_list) > 0:
            close_target = list(close_list.keys())[random.randint(0, max_random)]
            # if close_target.base_pos.distance_to(self.base_pos) < 20: # in case can't find close target
        return close_target

    def find_shooting_target(self, unit_state):
        """get nearby enemy base_target from list if not targeting anything yet"""
        self.attack_pos = list(self.unit.near_target.values())[0]  # replace attack_pos with enemy unit pos
        self.attack_target = list(self.unit.near_target.keys())[0]  # replace attack_target with enemy unit id
        if self.shoot_range >= self.attack_pos.distance_to(self.base_pos):
            self.state = 11
            if unit_state in (1, 3, 5):  # Walk and shoot
                self.state = 12
            elif unit_state in (2, 4, 6):  # Run and shoot
                self.state = 13

    def make_front_pos(self):
        """create new pos for front side of sprite"""
        self.front_pos = (self.base_pos[0], (self.base_pos[1] - self.image_height))

        self.front_pos = rotation_xy(self.base_pos, self.front_pos, self.radians_angle)

    def make_pos_range(self):
        """create range of sprite pos for pathfinding"""
        self.pos_range = (range(int(max(0, self.base_pos[0] - (self.image_height - 1))), int(min(1000, self.base_pos[0] + self.image_height))),
                          range(int(max(0, self.base_pos[1] - (self.image_height - 1))), int(min(1000, self.base_pos[1] + self.image_height))))

    def start_set(self, zoom):
        """run once when self start or subunit just get created"""
        self.zoom = zoom
        self.make_front_pos()
        self.make_pos_range()
        self.zoom_scale()
        self.find_nearby_subunit()
        self.status_update()
        self.terrain, self.feature = self.get_feature(self.base_pos, self.base_map)
        self.height = self.height_map.get_height(self.base_pos)

    def update(self, weather, new_dt, zoom, combat_timer, mouse_pos, mouse_left_up):
        if self.last_zoom != zoom:  # camera zoom is changed
            self.last_zoom = zoom
            self.zoom = zoom  # save scale
            self.zoom_scale()  # update unit sprite according to new scale

        if self.unit_health > 0:  # only run these when not dead
            self.player_interact(mouse_pos, mouse_left_up)

            dt = new_dt
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

                    if len(self.available_skill) > 0 and random.randint(0, 10) >= 6:  # random chance to use random available skill
                        self.use_skill(self.available_skill[random.randint(0, len(self.available_skill) - 1)])

                    self.charge_logic(parent_state)

                    self.timer -= 1

                parent_state, collide_list = self.attack_logic(dt, combat_timer, parent_state)

                if self.angle != self.new_angle:  # Rotate Function
                    self.rotate_logic(dt)

                self.move_logic(dt, parent_state, collide_list)  # Move function

                self.morale_logic(dt, parent_state)

                self.health_stamina_logic(dt)

                # self.play_animation(self.image, position, speed, play_list)

            if self.state in (98, 99) and (self.base_pos[0] <= 0 or self.base_pos[0] >= 999 or
                                           self.base_pos[1] <= 0 or self.base_pos[1] >= 999):  # remove when unit move pass map border
                self.state = 100  # enter dead state
                self.battle.flee_troop_number[self.team] += self.troop_number  # add number of troop retreat from battle
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
                self.die()

    def combat_pathfind(self):
        # v Pathfinding
        self.combat_move_queue = []
        move_array = self.battle.subunit_pos_array.copy()
        int_base_target = (int(self.close_target.base_pos[0]), int(self.close_target.base_pos[1]))
        for y in self.close_target.pos_range[0]:
            for x in self.close_target.pos_range[1]:
                move_array[x][y] = 100  # reset path in the enemy sprite position

        int_base_pos = (int(self.base_pos[0]), int(self.base_pos[1]))
        for y in self.pos_range[0]:
            for x in self.pos_range[1]:
                move_array[x][y] = 100  # reset path for subunit sprite position

        start_point = (min([max(0, int_base_pos[0] - 5), max(0, int_base_target[0] - 5)]),  # start point of new smaller array
                      min([max(0, int_base_pos[1] - 5), max(0, int_base_target[1] - 5)]))
        end_point = (max([min(999, int_base_pos[0] + 5), min(999, int_base_target[0] + 5)]),  # end point of new array
                    max([min(999, int_base_pos[1] + 5), min(999, int_base_target[1] + 5)]))

        move_array = move_array[start_point[1]:end_point[1]]  # cut 1000x1000 array into smaller one by row
        move_array = [this_array[start_point[0]:end_point[0]] for this_array in move_array]  # cut by column

        # if len(move_array) < 100 and len(move_array[0]) < 100: # if too big then skip combat pathfinding
        grid = Grid(matrix=move_array)
        grid.cleanup()

        start = grid.node(int_base_pos[0] - start_point[0], int_base_pos[1] - start_point[1])  # start point
        end = grid.node(int_base_target[0] - start_point[0], int_base_target[1] - start_point[1])  # end point

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)
        path = [(this_path[0] + start_point[0], this_path[1] + start_point[1]) for this_path in path]  # remake pos into actual map pos

        path = path[4:]  # remove some starting path that may clip with friendly subunit sprite

        self.combat_move_queue = path  # add path into combat movement queue
        if len(self.combat_move_queue) < 1:  # simply try walk to target anyway if pathfinder return empty
            self.combat_move_queue = [self.close_target.base_pos]
        # ^ End path finding


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
