import math
import random

import pygame
import pygame.freetype
from gamescript.common import utility, animation
from gamescript.common.subunit import common_subunit_combat, common_subunit_movement, \
    common_subunit_update, common_subunit_setup, common_subunit_zoom

rotation_list = common_subunit_movement.rotation_list
rotation_name = common_subunit_movement.rotation_name
rotation_dict = common_subunit_movement.rotation_dict

infinity = float("inf")


def change_subunit_genre(self):
    """
    Change genre method to subunit class
    :param self: Game object
    """
    import importlib

    subunit_combat = importlib.import_module("gamescript." + self.genre + ".subunit.subunit_combat")
    subunit_setup = importlib.import_module("gamescript." + self.genre + ".subunit.subunit_setup")
    subunit_movement = importlib.import_module("gamescript." + self.genre + ".subunit.subunit_movement")
    subunit_update = importlib.import_module("gamescript." + self.genre + ".subunit.subunit_update")

    Subunit.add_weapon_stat = subunit_setup.add_weapon_stat
    Subunit.add_mount_stat = subunit_setup.add_mount_stat
    Subunit.add_trait = subunit_setup.add_trait
    Subunit.find_shooting_target = subunit_combat.find_shooting_target
    Subunit.attack_logic = subunit_combat.attack_logic
    Subunit.dmg_cal = subunit_combat.dmg_cal
    Subunit.change_leader = subunit_combat.change_leader
    Subunit.die = subunit_combat.die
    Subunit.rotate_logic = subunit_movement.rotate_logic
    Subunit.move_logic = subunit_movement.move_logic
    Subunit.player_interact = subunit_update.player_interact
    Subunit.status_update = subunit_update.status_update
    Subunit.state_reset_logic = subunit_update.state_reset_logic
    Subunit.morale_logic = subunit_update.morale_logic
    Subunit.check_skill_condition = subunit_update.check_skill_condition
    Subunit.skill_check_logic = subunit_update.skill_check_logic
    Subunit.pick_animation = subunit_update.pick_animation
    Subunit.health_stamina_logic = subunit_update.health_stamina_logic
    Subunit.swap_weapon = subunit_update.swap_weapon
    Subunit.charge_logic = subunit_update.charge_logic
    Subunit.zoom_scale = common_subunit_zoom.zoom_scale
    Subunit.change_pos_scale = common_subunit_zoom.change_pos_scale


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
    use_skill = common_subunit_combat.use_skill
    rotate = common_subunit_movement.rotate
    combat_pathfind = common_subunit_movement.combat_pathfind
    find_close_target = common_subunit_movement.find_close_target
    make_front_pos = common_subunit_update.make_front_pos
    make_pos_range = common_subunit_update.make_pos_range
    threshold_count = common_subunit_update.threshold_count
    temperature_cal = common_subunit_update.temperature_cal
    find_nearby_subunit = common_subunit_update.find_nearby_subunit
    apply_map_status = common_subunit_update.apply_map_status
    status_to_friend = common_subunit_update.status_to_friend
    start_set = common_subunit_setup.start_set
    process_trait_skill = common_subunit_setup.process_trait_skill
    create_inspect_sprite = common_subunit_setup.create_inspect_sprite

    # methods that change based on genre
    def add_weapon_stat(self): pass
    def add_mount_stat(self): pass
    def add_trait(self): pass
    def find_shooting_target(self): pass
    def attack_logic(self): pass
    def dmg_cal(self): pass
    def change_leader(self): pass
    def die(self): pass
    def rotate_logic(self): pass
    def move_logic(self): pass
    def player_interact(self): pass
    def status_update(self): pass
    def state_reset_logic(self): pass
    def morale_logic(self): pass
    def health_stamina_logic(self): pass
    def swap_weapon(self): pass
    def charge_logic(self): pass
    def check_skill_condition(self): pass
    def skill_check_logic(self): pass
    def pick_animation(self): pass

    def __init__(self, troop_id, game_id, unit, start_pos, start_hp, start_stamina, unit_scale):
        """
        Subunit object represent a group of troop or leader
        Subunit has three different stage of stat;
        first: original stat (e.g., original_melee_attack), this is their stat before calculating equipment, trait, and other effect
        second: base stat (e.g., base_melee_attack), this is their stat after calculating equipment and trait
        third: stat itself (e.g., melee_attack), this is their stat after calculating terrain, weather, and status effect
        :param troop_id: ID of the troop in data, can be 'h' for game mode that directly use leader character
        :param game_id: ID of the subunit as object
        :param unit: Unit that this subunit belongs to
        :param start_pos: Starting pos of the subunit that will be used for sprite blit
        :param start_hp: Starting health or troop number percentage
        :param start_stamina: Starting maximum stamina percentage
        :param unit_scale: Scale of troop number
        """
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.get_feature = self.feature_map.get_feature
        self.get_height = self.height_map.get_height

        self.leader = None  # Leader in the sub-subunit if there is one, got add in leader start_set
        self.board_pos = None  # Used for event log position of subunit (Assigned in battle subunit setup)
        self.walk = False  # currently walking
        self.run = False  # currently running
        self.frontline = False  # on front line of unit or not
        self.unit_leader = False  # contain the general or not, making it leader subunit
        self.attack_target = None  # target for attacking
        self.melee_target = None  # current target of melee combat
        self.close_target = None  # closet target to move to in melee
        self.attacking = False  # For checking if unit in attacking state or not for using charge skill

        self.current_animation = {}  # list of animation frames playing
        self.animation_queue = []  # list of animation queue
        self.show_frame = 0  # current animation frame
        self.animation_timer = 0
        self.current_action = ()  # for genre that use specific action instead of state
        self.command_action = ()  # next action to be performed
        self.idle_action = ()  # action that is performed when subunit is idle such as hold spearwall when skill active

        self.enemy_front = []  # list of front collide sprite
        self.enemy_side = []  # list of side collide sprite
        self.friend_front = []  # list of friendly front collide sprite
        self.same_front = []  # list of same unit front collide sprite
        self.full_merge = []  # list of sprite that collide and almost overlap with this sprite
        self.collide_penalty = False
        self.movement_queue = []
        self.combat_move_queue = []  # movement during melee combat

        self.game_id = game_id  # ID of this
        self.unit = unit  # reference to the parent uit of this subunit
        self.team = self.unit.team

        self.red_border = False  # red corner to indicate taking melee_dmg in inspect ui
        self.state = 0  # Current subunit state, similar to unit state
        self.timer = random.random()  # may need to use random.random()
        self.move_timer = 0  # timer for moving to front position before attacking nearest enemy
        self.charge_momentum = 1  # charging momentum to reach target before choosing the nearest enemy
        self.zoom = 1
        self.last_zoom = 0
        self.skill_cond = 0
        self.broken_limit = 0  # morale require for unit to stop broken state, will increase everytime broken state stop
        self.ammo_now = 0  # ammunition count in the current magazine
        self.interrupt_animation = False
        self.use_animation_sprite = False

        # v Setup troop original stat before applying trait, gear and other stuffs
        if type(troop_id) == int or "h" not in troop_id:
            self.troop_id = int(troop_id)  # ID of preset used for this subunit
            stat = self.troop_data.troop_list[self.troop_id].copy()
            self.grade = stat["Grade"]  # training level/class grade
            grade_stat = self.troop_data.grade_list[self.grade]
            self.original_melee_attack = stat["Melee Attack"] + grade_stat[
                "Melee Attack Bonus"]  # melee attack with grade bonus
            self.original_melee_def = stat["Melee Defence"] + grade_stat[
                "Defence Bonus"]  # melee defence with grade bonus
            self.original_range_def = stat["Ranged Defence"] + grade_stat[
                "Defence Bonus"]  # range defence with grade bonus
            self.original_accuracy = stat["Accuracy"] + grade_stat["Accuracy Bonus"]
            self.original_sight = stat["Sight"]  # sight range
            self.magazine_left = {0: {0: stat["Ammunition Modifier"], 1: stat["Ammunition Modifier"]},
                                  1: {0: stat["Ammunition Modifier"], 1: stat["Ammunition Modifier"]}}  # ammunition, for now as mod number
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
                "Melee Attack Bonus"]  # melee attack with grade bonus
            self.original_melee_def = (stat["Melee Command"] * stat["Combat"]) + grade_stat[
                "Defence Bonus"]  # melee defence with grade bonus
            self.original_range_def = (stat["Range Command"] * stat["Combat"]) + grade_stat[
                "Defence Bonus"]  # range defence with grade bonus
            self.original_accuracy = (stat["Range Command"] * stat["Combat"]) + grade_stat["Accuracy Bonus"]
            self.original_sight = (stat["Range Command"] * stat["Combat"])  # sight range
            self.magazine_left = {0: {0: 2, 1: 2},
                                  1: {0: 2, 1: 2}}  # leader gets double ammunition
            self.original_reload = (stat["Range Command"] * stat["Combat"]) + grade_stat["Reload Bonus"]
            self.original_charge = 100
            self.original_charge_def = 100
            self.charge_skill = 25  # use leading charge by default for leader
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
        self.original_armour = self.troop_data.race_list[stat["Race"]]["Armour"]
        self.base_armour = self.armour_data.armour_list[self.armour_gear[0]]["Armour"] \
                           * self.armour_data.quality[self.armour_gear[1]]  # armour stat is calculated from based armour * quality

        self.original_skill = skill.copy()  # Skill that the subunit processes
        if "" in self.original_skill:
            self.original_skill.remove("")
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
        self.melee_dmg = {0: {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}, 1: {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}}
        self.melee_penetrate = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.range_dmg = {0: {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}, 1: {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}}
        self.range_penetrate = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.base_range = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.weapon_speed = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.magazine_size = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}  # can shoot how many times before have to reload
        self.arrow_speed = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.weapon_skill = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.equipped_weapon = 0

        self.original_speed = self.troop_data.race_list[stat["Race"]]["Speed"] * \
                              self.troop_data.race_list[stat["Race"]]["Size"]  # use speed of race multiply by race size
        self.feature_mod = "Infantry"  # the starting column in terrain bonus of infantry
        self.authority = 100  # default start at 100

        # vv Elemental stat
        self.original_elem_melee = 0  # start with physical element for melee weapon
        self.original_elem_range = 0  # start with physical for range weapon
        self.elem_count = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}  # Elemental threshold count fire, water, air, earth, poison
        self.temp_count = 0  # Temperature threshold count
        self.elem_res = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}  # fire, water, air, earth, poison in this order
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

        self.trait = self.original_trait
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
        self.troop_skill = self.original_skill.copy()
        self.base_mana = self.original_mana
        self.base_morale = self.original_morale
        self.base_discipline = self.original_discipline
        self.base_hp_regen = self.original_hp_regen
        self.base_stamina_regen = self.original_stamina_regen
        self.base_morale_regen= self.original_morale_regen
        self.base_elem_melee = self.original_elem_melee
        self.base_elem_range = self.original_elem_range

        self.add_weapon_stat()
        self.action_list = {}  # got added in change_equipment

        if stat["Mount"][0] != 1:  # have a mount, add mount stat with its grade to subunit stat
            self.add_mount_stat()
            race_id = [key for key, value in self.troop_data.race_list.items() if self.mount["Race"] in value["Name"]][0]
            if self.troop_data.race_list[race_id]["Size"] > self.size:  # replace size if mount is larger
                self.size = self.troop_data.race_list[self.mount["Race"]]["Size"]

        self.swap_weapon()

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

        self.unit_position = (start_pos[0] / 10, start_pos[1] / 10)  # position in unit sprite
        try:
            unit_top_left = pygame.Vector2(self.unit.base_pos[0] - self.unit.base_width_box / 2,
                                           self.unit.base_pos[
                                               1] - self.unit.base_height_box / 2)  # get top left corner position of unit to calculate true pos
            self.base_pos = pygame.Vector2(unit_top_left[0] + self.unit_position[0],
                                           unit_top_left[1] + self.unit_position[1])  # true position of subunit in map
            self.last_pos = self.base_pos

            self.angle = self.unit.angle
            self.new_angle = self.unit.angle
            self.radians_angle = math.radians(360 - self.angle)  # radians for apply angle to position
            self.sprite_direction = rotation_dict[min(rotation_list,
                                                      key=lambda x: abs(
                                                          x - self.angle))]  # find closest in list of rotation for sprite direction
            self.attack_pos = self.unit.base_attack_pos

            self.base_target = self.base_pos  # base_target to move
            self.command_target = self.base_pos  # actual base_target outside of combat
            self.pos = (self.base_pos[0] * self.screen_scale[0] * self.zoom,
                        self.base_pos[1] * self.screen_scale[1] * self.zoom)  # pos is for showing on screen

            self.image_height = (self.image.get_height() - 1) / 20  # get real half height of circle sprite

            self.front_pos = self.make_front_pos()

            self.rect = self.image.get_rect(center=self.pos)
        except AttributeError:  # for subunit with dummy unit
            pass

    def update(self, weather, dt, zoom, combat_timer, mouse_pos, mouse_left_up):
        recreate_rect = False
        if self.last_zoom != zoom:  # camera zoom is changed
            self.last_zoom = zoom
            self.zoom = zoom  # save scale
            self.zoom_scale()  # update unit sprite according to new scale
            recreate_rect = True

        if self.unit_health > 0:  # only run these when not dead
            self.player_interact(mouse_pos, mouse_left_up)

            if dt > 0:  # only run these when self not pause
                self.timer += dt

                self.walk = False  # reset walk
                self.run = False  # reset run

                parent_state = self.unit.state

                if self.timer > 1:  # Update status and skill use around every 1 second
                    self.status_update(weather=weather)

                    self.charge_logic(parent_state)

                    self.timer -= 1

                self.state_reset_logic(parent_state)

                parent_state, collide_list = self.attack_logic(dt, combat_timer, parent_state)

                if self.angle != self.new_angle:  # Rotate Function
                    self.rotate_logic(dt)

                self.move_logic(dt, parent_state, collide_list)  # Move function

                self.available_skill = []
                self.skill_check_logic()

                self.morale_logic(dt, parent_state)

                self.health_stamina_logic(dt)

            if self.state in (98, 99) and (self.base_pos[0] <= 1 or self.base_pos[0] >= 999 or
                                           self.base_pos[1] <= 1 or self.base_pos[1] >= 999):  # remove when unit move pass map border
                self.state = 100  # enter dead state
                self.battle.flee_troop_number[self.team] += self.troop_number  # add number of troop retreat from battle
                self.troop_number = 0
                self.battle.battle_camera.remove(self)
            done = self.play_animation(0.15, dt, replace_image=self.use_animation_sprite)
            # pick new animation if interrupt or playing idle action or finish playing current animation and not repeat
            if ((self.interrupt_animation and "uninterruptible" not in self.current_action) or
                (self.idle_action != self.command_action and not self.command_action)) or \
                    (done and "repeat" not in self.current_action):
                self.interrupt_animation = False
                self.current_action = self.command_action  # continue next action when animation finish
                self.pick_animation()
                self.command_action = ()
                if not self.idle_action:
                    self.command_action = self.idle_action
            if recreate_rect:
                self.rect = self.image.get_rect(center=self.pos)

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

    def delete(self, local=False):
        """delete reference when method is called"""
        del self.unit
        del self.leader
        del self.attack_target
        del self.melee_target
        del self.close_target
        if self in self.battle.combat_path_queue:
            self.battle.combat_path_queue.remove(self)
        if local:
            print(locals())


class EditorSubunit(Subunit):
    def __init__(self, troop_id, game_id, unit, start_pos, start_hp, start_stamina, unit_scale):
        """Create subunit object used for editor only"""
        Subunit.__init__(self, troop_id, game_id, unit, start_pos, start_hp, start_stamina, unit_scale)
        self.pos = start_pos
        self.inspect_pos = (self.pos[0] - (self.image.get_width() / 2), self.pos[1] - (self.image.get_height() / 2))
        self.image = self.block
        self.inspect_image_original = self.block_original
        self.commander = True
        self.rect = self.image.get_rect(center=self.pos)
