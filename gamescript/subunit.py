import math
import random
import time

import pygame
import pygame.freetype
from gamescript.common import utility, animation
from gamescript.common.subunit import common_fight, common_movement, common_refresh
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pygame.transform import scale

rotation_list = common_movement.rotation_list
rotation_name = common_movement.rotation_name
rotation_dict = common_movement.rotation_dict

infinity = float("inf")


def change_subunit_genre(genre):
    """Change game genre and add appropriate method to subunit class"""
    if genre == "tactical":
        from gamescript.tactical.subunit import fight, spawn, movement, refresh
    elif genre == "arcade":
        from gamescript.arcade.subunit import fight, spawn, movement, refresh

    Subunit.add_weapon_stat = spawn.add_weapon_stat
    Subunit.add_mount_stat = spawn.add_mount_stat
    Subunit.add_trait = spawn.add_trait
    Subunit.attack_logic = fight.attack_logic
    Subunit.dmg_cal = fight.dmg_cal
    Subunit.change_leader = fight.change_leader
    Subunit.die = fight.die
    Subunit.rotate_logic = movement.rotate_logic
    Subunit.move_logic = movement.move_logic
    Subunit.player_interact = refresh.player_interact
    Subunit.status_update = refresh.status_update
    Subunit.morale_logic = refresh.morale_logic
    Subunit.pick_animation = refresh.pick_animation
    Subunit.health_stamina_logic = refresh.health_stamina_logic
    Subunit.charge_logic = refresh.charge_logic


class Subunit(pygame.sprite.Sprite):
    unit_ui_images = []
    battle = None
    base_map = None  # base map
    feature_map = None  # feature map
    height_map = None  # height map
    weapon_data = None
    armour_data = None
    troop_data = None
    leader_data = None
    status_list = None
    animation_sprite_pool = None
    max_zoom = 10  # max zoom allow
    screen_scale = (1, 1)
    subunit_state = None
    generic_action_data = None

    play_animation = animation.play_animation
    set_rotate = utility.set_rotate
    use_skill = common_fight.use_skill
    rotate = common_movement.rotate
    check_skill_condition = common_fight.check_skill_condition
    make_front_pos = common_refresh.make_front_pos

    # method that change based on genre
    add_weapon_stat = None
    add_mount_stat = None
    add_trait = None
    attack_logic = None
    dmg_cal = None
    change_leader = None
    die = None
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
        self.show_frame = 0
        self.animation_timer = 0

        self.enemy_front = []  # list of front collide sprite
        self.enemy_side = []  # list of side collide sprite
        self.friend_front = []  # list of friendly front collide sprite
        self.same_front = []  # list of same unit front collide sprite
        self.full_merge = []  # list of sprite that collide and almost overlap with this sprite
        self.collide_penalty = False

        self.game_id = game_id  # ID of this
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
        if type(troop_id) == int or "h" not in troop_id:
            self.troop_id = int(troop_id)  # ID of preset used for this subunit
            stat = self.troop_data.troop_list[self.troop_id].copy()
            self.grade = stat["Grade"]  # training level/class grade
            grade_stat = self.troop_data.grade_list[self.grade]
            self.original_melee_attack = stat["Melee Attack"] + grade_stat[
                "Melee Attack Bonus"]  # base melee melee_attack with grade bonus
            self.original_melee_def = stat["Melee Defence"] + grade_stat[
                "Defence Bonus"]  # base melee defence with grade bonus
            self.original_range_def = stat["Ranged Defence"] + grade_stat[
                "Defence Bonus"]  # base range defence with grade bonus
            self.original_accuracy = stat["Accuracy"] + grade_stat["Accuracy Bonus"]
            self.original_sight = stat["Sight"]  # base sight range
            self.magazine_left = stat["Ammunition"]  # amount of ammunition
            self.original_reload = stat["Reload"] + grade_stat["Reload Bonus"]
            self.original_charge = stat["Charge"]
            self.original_charge_def = 50  # All infantry subunit has default 50 charge defence
            self.charge_skill = stat["Charge Skill"]  # For easier reference to check what charge skill this subunit has
            self.original_morale = stat["Morale"] + grade_stat["Morale Bonus"]  # morale with grade bonus
            self.original_discipline = stat["Discipline"] + grade_stat["Discipline Bonus"]  # discipline with grade bonus
            self.mental = stat["Mental"] + grade_stat[
                "Mental Bonus"]  # mental resistance from morale melee_dmg and mental status effect
            self.troop_number = stat["Troop"] * unit_scale[
                self.team] * start_hp / 100  # number of starting troop, team -1 to become list index
            self.stamina = stat["Stamina"] * grade_stat["Stamina Effect"] * (
                        start_stamina / 100)  # starting stamina with grade
            self.subunit_type = stat["Troop Class"] - 1  # 0 is melee infantry and 1 is range for command buff

        else:  # leader character, for game mode that replace subunit with leader
            self.troop_id = troop_id
            stat = self.leader_data.leader_list[int(troop_id.replace("h", ""))].copy()
            self.grade = 12  # leader grade by default
            grade_stat = self.troop_data.grade_list[self.grade]
            self.original_melee_attack = (stat["Melee Command"] * stat["Combat"]) + grade_stat[
                "Melee Attack Bonus"]  # base melee melee_attack with grade bonus
            self.original_melee_def = (stat["Melee Command"] * stat["Combat"]) + grade_stat[
                "Defence Bonus"]  # base melee defence with grade bonus
            self.original_range_def = (stat["Range Command"] * stat["Combat"]) + grade_stat[
                "Defence Bonus"]  # base range defence with grade bonus
            self.original_accuracy = (stat["Range Command"] * stat["Combat"]) + grade_stat["Accuracy Bonus"]
            self.original_sight = (stat["Range Command"] * stat["Combat"])  # base sight range
            self.magazine_left = infinity  # amount of ammunition
            self.original_reload = (stat["Range Command"] * stat["Combat"]) + grade_stat["Reload Bonus"]
            self.original_charge = 100
            self.original_charge_def = 100
            self.charge_skill = 21  # use normal charge by default
            self.original_morale = 100 + grade_stat["Morale Bonus"]  # morale with grade bonus
            self.original_discipline = 100 + grade_stat[
                "Discipline Bonus"]  # discipline with grade bonus
            self.mental = 50 + grade_stat[
                "Mental Bonus"]  # mental resistance from morale melee_dmg and mental status effect
            self.troop_number = 1
            self.stamina = 10000 * grade_stat["Stamina Effect"] * (
                        start_stamina / 100)  # starting stamina with grade
            self.subunit_type = 0
            if self.original_accuracy > self.original_melee_attack:  # range leader
                self.subunit_type = 1

        self.name = stat["Name"]  # name according to the preset
        self.race = stat["Race"]  # creature race
        self.race_name = self.troop_data.race_list[stat["Race"]]["Name"]
        self.original_trait = stat["Trait"]  # trait list from preset
        self.original_trait = self.original_trait + self.troop_data.grade_list[self.grade]["Trait"]  # add trait from grade
        skill = stat["Skill"]  # skill list according to the preset
        self.skill_cooldown = {}
        self.grade_name = grade_stat["Name"]
        self.armour_gear = stat["Armour"]  # armour equipment
        self.original_armour = 0  # TODO change when has race or something
        self.base_armour = self.armour_data.armour_list[self.armour_gear[0]]["Armour"] \
                           * self.armour_data.quality[self.armour_gear[1]]  # armour stat is calculated from based armour * quality

        self.original_skill = [self.charge_skill] + skill  # Add charge skill as first item in the list
        self.troop_health = stat["Health"] * grade_stat["Health Effect"]  # Health of each troop
        self.original_mana = 0
        if "Mana" in stat:
            self.original_mana = stat["Mana"]  # Resource for magic skill

        # vv Equipment stat
        self.primary_main_weapon = stat["Primary Main Weapon"]
        self.primary_sub_weapon = stat["Primary Sub Weapon"]
        self.secondary_main_weapon = stat["Secondary Main Weapon"]
        self.secondary_sub_weapon = stat["Secondary Sub Weapon"]

        self.weapon_name = ((self.weapon_data.weapon_list[self.primary_main_weapon[0]]["Name"],
                             self.weapon_data.weapon_list[self.primary_sub_weapon[0]]["Name"]),
                            (self.weapon_data.weapon_list[self.secondary_main_weapon[0]]["Name"],
                             self.weapon_data.weapon_list[self.secondary_sub_weapon[0]]["Name"]))

        self.mount = self.troop_data.mount_list[stat["Mount"][0]]  # mount this subunit use
        self.mount_grade = self.troop_data.mount_grade_list[stat["Mount"][1]]
        self.mount_armour = self.troop_data.mount_armour_list[stat["Mount"][2]]

        self.size = self.troop_data.race_list[stat["Race"]]["Size"]
        self.weight = 0
        self.melee_dmg = [0, 0]
        self.melee_penetrate = 0
        self.range_dmg = [0, 0]
        self.range_penetrate = 0
        self.base_range = 0
        self.weapon_speed = 0
        self.magazine_size = 0
        self.equipped_weapon = 0

        self.original_speed = 50  # All infantry has base speed at 50
        self.feature_mod = "Infantry"  # the starting column in terrain bonus of infantry
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
        self.base_armour = self.original_armour + (self.armour_data.armour_list[self.armour_gear[0]]["Armour"]
                                                   * self.armour_data.quality[self.armour_gear[1]])
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

        self.add_weapon_stat()
        self.action_list = {key: value for key, value in self.generic_action_data.items() if key in self.weapon_name[0] or key in self.weapon_name[1]}

        if stat["Mount"][0] != 1:  # have a mount, add mount stat with its grade to subunit stat
            self.add_mount_stat()
            race_id = [key for key, value in self.troop_data.race_list.items() if self.mount["Race"] in value["Name"]][0]
            if self.troop_data.race_list[race_id]["Size"] > self.size:  # replace size if mount is larger
                self.size = self.troop_data.race_list[self.mount["Race"]]["Size"]

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

        self.trait += self.armour_data.armour_list[self.armour_gear[0]]["Trait"]  # Apply armour trait to subunit

        self.trait = list(set([trait for trait in self.trait if trait != 0]))  # remove empty and duplicate traits
        if len(self.trait) > 0:
            self.trait = {x: self.troop_data.trait_list[x] for x in self.trait if
                          x in self.troop_data.trait_list}  # Any trait not available in ruleset will be ignored
            self.add_trait()

        self.skill = {x: self.troop_data.skill_list[x].copy() for x in self.skill if
                      x != 0 and x in self.troop_data.skill_list}  # grab skill stat into dict
        for skill in list(self.skill.keys()):  # remove skill if class mismatch
            skill_troop_cond = self.skill[skill]["Troop Type"]
            if skill_troop_cond != 0 and self.subunit_type != skill_troop_cond:
                self.skill.pop(skill)

        # v Weight calculation
        self.weight += self.armour_data.armour_list[self.armour_gear[0]]["Weight"] + self.mount_armour["Weight"]  # Weight from both melee and range weapon and armour
        if self.subunit_type == 2:  # cavalry has half weight penalty
            self.weight = self.weight / 2
        # ^ End weight cal

        self.base_speed = (self.base_speed * ((100 - self.weight) / 100)) + grade_stat["Speed Bonus"]  # finalise base speed with weight and grade bonus
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

        # sprite for inspection or far view
        sprite_dict = self.create_inspect_sprite()
        self.inspect_image = sprite_dict["image"]
        self.image = self.inspect_image.copy()
        self.inspect_image_original = sprite_dict["original"]
        self.inspect_image_original2 = sprite_dict["original2"]
        self.inspect_image_original3 = sprite_dict["original3"]
        self.block = sprite_dict["block"]
        self.block_original = sprite_dict["block_original"]
        self.selected_inspect_image = sprite_dict["selected"]
        self.selected_inspect_image_rect = sprite_dict["selected_rect"]
        self.selected_inspect_image_original = sprite_dict["selected_original"]
        self.selected_inspect_image_original2 = sprite_dict["selected_original2"]
        self.far_image = sprite_dict["far"]
        self.far_selected_image = sprite_dict["far_selected"]
        self.health_image_rect = sprite_dict["health_rect"]
        self.health_block_rect = sprite_dict["health_block_rect"]
        self.stamina_image_rect = sprite_dict["stamina_rect"]
        self.stamina_block_rect = sprite_dict["stamina_block_rect"]
        self.corner_image_rect = sprite_dict["corner_rect"]
        self.health_image_list = sprite_dict["health_list"]
        self.stamina_image_list = sprite_dict["stamina_list"]

        if purpose == "battle":
            self.angle = self.unit.angle
            self.new_angle = self.unit.angle
            self.radians_angle = math.radians(360 - self.angle)  # radians for apply angle to position
            self.sprite_direction = rotation_dict[min(rotation_list,
                                                      key=lambda x: abs(x - self.angle))]  # find closest in list of rotation for sprite direction
            self.parent_angle = self.unit.angle  # angle subunit will face when not moving

            # position related
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

            self.front_pos = self.make_front_pos()

            try:
                self.terrain, self.feature = self.get_feature(self.base_pos, self.base_map)  # get new terrain and feature at each subunit position
                self.height = self.height_map.get_height(self.base_pos)  # current terrain height
                self.front_height = self.height_map.get_height(self.front_pos)  # terrain height at front position
            except AttributeError:
                pass

        elif purpose == "edit":
            self.image = self.block
            self.pos = start_pos
            self.inspect_pos = (self.pos[0] - (self.image.get_width() / 2), self.pos[1] - (self.image.get_height() / 2))
            self.inspect_image_original = self.block_original
            self.coa = self.unit.coa
            self.commander = True

        self.rect = self.image.get_rect(center=self.pos)

    def zoom_scale(self):
        """camera zoom change and rescale the sprite and position scale, sprite closer zoom will be scale in the play animation function instead"""
        if self.zoom != self.max_zoom:
            if self.zoom > 1:
                self.inspect_image_original = self.inspect_image_original3.copy()  # reset image for new scale
                dim = pygame.Vector2(self.inspect_image_original.get_width() * self.zoom / self.max_zoom, self.inspect_image_original.get_height() * self.zoom / self.max_zoom)
                self.image = pygame.transform.scale(self.inspect_image_original, (int(dim[0]), int(dim[1])))
                if self.unit.selected and self.state != 100:
                    self.selected_inspect_image_original = pygame.transform.scale(self.selected_inspect_image_original2, (int(dim[0]), int(dim[1])))
            else:  # furthest zoom
                self.inspect_image_original = self.far_image.copy()
                self.image = self.inspect_image_original.copy()
                if self.unit.selected and self.state != 100:
                    self.selected_inspect_image_original = self.far_selected_image.copy()
            self.inspect_image_original = self.image.copy()
            self.inspect_image_original2 = self.image.copy()
            self.rotate()
        self.change_pos_scale()

    def change_pos_scale(self):
        """Change position variable to new camera scale"""
        self.pos = (self.base_pos[0] * self.screen_scale[0] * self.zoom, self.base_pos[1] * self.screen_scale[1] * self.zoom)
        self.rect.center = self.pos

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

    def make_pos_range(self):
        """create range of sprite pos for pathfinding"""
        self.pos_range = (range(int(max(0, self.base_pos[0] - (self.image_height - 1))), int(min(1000, self.base_pos[0] + self.image_height))),
                          range(int(max(0, self.base_pos[1] - (self.image_height - 1))), int(min(1000, self.base_pos[1] + self.image_height))))

    def start_set(self, zoom):
        """run once when battle start or subunit just get created"""
        self.zoom = zoom
        self.front_pos = self.make_front_pos()
        self.make_pos_range()
        self.zoom_scale()
        self.find_nearby_subunit()
        self.terrain, self.feature = self.get_feature(self.base_pos, self.base_map)
        self.height = self.height_map.get_height(self.base_pos)
        self.front_height = self.height_map.get_height(self.front_pos)  # terrain height at front position
        self.grade_social_effect = self.unit.leader_social[self.grade_name]
        self.status_update()

        self.battle.alive_subunit_list.append(self)
        if self.team == 1:  # add sprite to team subunit group for collision
            group_collide = self.battle.team1_subunit
        elif self.team == 2:
            group_collide = self.battle.team2_subunit
        group_collide.add(self)

        self.sprite_pool = self.animation_sprite_pool[self.troop_id]  # grab only animation sprite that the subunit can use

        self.pick_animation()

        # self.idle_animation = self.sprite_pool["Human_Default/" + str(self.equiped_weapon)]
        # self.walk_animation = None
        # self.run_animation = None
        # self.action1_animation = None
        # self.action2_animation = None
        # self.die_animation = None

    def create_inspect_sprite(self):
        # v Subunit image sprite in inspect ui and far zoom
        ui_image = self.unit_ui_images["ui_squad_player.png"].copy()  # Subunit block blue colour for team1 for shown in inspect ui
        if self.team == 2:
            ui_image = self.unit_ui_images["ui_squad_enemy.png"].copy()  # red colour

        image = pygame.Surface((ui_image.get_width() + 10, ui_image.get_height() + 10), pygame.SRCALPHA)  # subunit sprite image
        pygame.draw.circle(image, self.unit.colour, (image.get_width() / 2, image.get_height() / 2), ui_image.get_width() / 2)

        if self.subunit_type == 2:  # cavalry draw line on block
            pygame.draw.line(ui_image, (0, 0, 0), (0, 0), (ui_image.get_width(), ui_image.get_height()), 2)
            radian = 45 * 0.0174532925  # top left
            start = (
                image.get_width() / 3 * math.cos(radian),
                image.get_width() / 3 * math.sin(radian))  # draw line from 45 degree in circle
            radian = 225 * 0.0174532925  # bottom right
            end = (image.get_width() * -math.cos(radian), image.get_width() * -math.sin(radian))  # draw line to 225 degree in circle
            pygame.draw.line(image, (0, 0, 0), start, end, 2)

        selected_image = pygame.Surface((ui_image.get_width(), ui_image.get_height()), pygame.SRCALPHA)
        pygame.draw.circle(selected_image, (255, 255, 255, 150), (ui_image.get_width() / 2, ui_image.get_height() / 2), ui_image.get_width() / 2)
        pygame.draw.circle(selected_image, (0, 0, 0, 255), (ui_image.get_width() / 2, ui_image.get_height() / 2), ui_image.get_width() / 2, 1)
        selected_image_original = selected_image.copy()
        selected_image_original2 = selected_image.copy()
        selected_image_rect = selected_image.get_rect(topleft=(0, 0))

        far_image = image.copy()
        pygame.draw.circle(far_image, (0, 0, 0), (far_image.get_width() / 2, far_image.get_height() / 2),
                           far_image.get_width() / 2, 4)
        far_selected_image = selected_image.copy()
        pygame.draw.circle(far_selected_image, (0, 0, 0), (far_selected_image.get_width() / 2, far_selected_image.get_height() / 2),
                           far_selected_image.get_width() / 2, 4)

        dim = pygame.Vector2(image.get_width() * 1 / self.max_zoom, image.get_height() * 1 / self.max_zoom)
        far_image = pygame.transform.scale(far_image, (int(dim[0]), int(dim[1])))
        far_selected_image = pygame.transform.scale(far_selected_image, (int(dim[0]), int(dim[1])))

        block = ui_image.copy()  # image shown in inspect ui as square instead of circle
        # ^ End subunit base sprite

        # v health and stamina related
        health_image_list = [self.unit_ui_images["ui_health_circle_100.png"], self.unit_ui_images["ui_health_circle_75.png"],
                             self.unit_ui_images["ui_health_circle_50.png"], self.unit_ui_images["ui_health_circle_25.png"],
                             self.unit_ui_images["ui_health_circle_0.png"]]
        stamina_image_list = [self.unit_ui_images["ui_stamina_circle_100.png"], self.unit_ui_images["ui_stamina_circle_75.png"],
                              self.unit_ui_images["ui_stamina_circle_50.png"], self.unit_ui_images["ui_stamina_circle_25.png"],
                              self.unit_ui_images["ui_stamina_circle_0.png"]]

        health_image = self.unit_ui_images["ui_health_circle_100.png"]
        health_image_rect = health_image.get_rect(center=image.get_rect().center)  # for battle sprite
        health_block_rect = health_image.get_rect(center=block.get_rect().center)  # for ui sprite
        image.blit(health_image, health_image_rect)
        block.blit(health_image, health_block_rect)

        stamina_image = self.unit_ui_images["ui_stamina_circle_100.png"]
        stamina_image_rect = stamina_image.get_rect(center=image.get_rect().center)  # for battle sprite
        stamina_block_rect = stamina_image.get_rect(center=block.get_rect().center)  # for ui sprite
        image.blit(stamina_image, stamina_image_rect)
        block.blit(stamina_image, stamina_block_rect)
        # ^ End health and stamina

        # v weapon class icon in middle circle
        image1 = self.weapon_data.images[self.weapon_data.weapon_list[self.primary_main_weapon[0]]["ImageID"]]  # image on subunit sprite
        image_rect = image1.get_rect(center=image.get_rect().center)
        if self.unit_leader:  # add crown image first
            image2 = self.weapon_data.images[-1]
            image.blit(image2, image_rect)
        image.blit(image1, image_rect)

        image_rect = image1.get_rect(center=block.get_rect().center)
        block.blit(image1, image_rect)
        block_original = block.copy()

        corner_image_rect = self.unit_ui_images["ui_squad_combat.png"].get_rect(
            center=block.get_rect().center)  # red corner when take melee_dmg shown in image block
        # ^ End weapon icon

        inspect_image_original = image.copy()  # original for rotate
        inspect_image_original2 = image.copy()  # original2 for saving original not clicked
        inspect_image_original3 = image.copy()  # original3 for saving original zoom level

        return {"image": image, "original": inspect_image_original, "original2": inspect_image_original2, "original3": inspect_image_original3,
                "block": block, "block_original": block_original, "selected": selected_image, "selected_rect": selected_image_rect,
                "selected_original": selected_image_original, "selected_original2": selected_image_original2,
                "far": far_image, "far_selected": far_selected_image, "health_rect": health_image_rect, "health_block_rect": health_block_rect,
                "stamina_rect": stamina_image_rect, "stamina_block_rect": stamina_block_rect,
                "corner_rect": corner_image_rect, "health_list": health_image_list, "stamina_list": stamina_image_list}

    def update(self, weather, dt, zoom, combat_timer, mouse_pos, mouse_left_up):
        recreate_rect = False
        if self.last_zoom != zoom:  # camera zoom is changed
            self.last_zoom = zoom
            self.zoom = zoom  # save scale
            self.zoom_scale()  # update unit sprite according to new scale
            recreate_rect = True

        if self.zoom == self.max_zoom:  # TODO add weapon specific action condition
            done = self.play_animation(0.5, dt)
            if done and self.state != 100:
                self.pick_animation()
            if recreate_rect:
                self.rect = self.image.get_rect(center=self.pos)

        if self.unit_health > 0:  # only run these when not dead
            self.player_interact(mouse_pos, mouse_left_up)

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
        """delete reference when function is called"""
        del self.unit
        del self.leader
        del self.who_last_select
        del self.attack_target
        del self.melee_target
        del self.close_target
        if self in self.battle.combat_path_queue:
            self.battle.combat_path_queue.remove(self)
        if local:
            print(locals())
