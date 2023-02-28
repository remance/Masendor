import math
import os
import random
from pathlib import Path

import pygame
import pygame.freetype

from gamescript.common import utility
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

rotation_list = (90, -90)
rotation_name = ("l_side", "r_side")
rotation_dict = {key: rotation_name[index] for index, key in enumerate(rotation_list)}

infinity = float("inf")

weapon_set = ("Main_", "Sub_")

"""Command dict Guide
Key:
name = action name that will be used to find animation, name with "Action" will find attack action of weapon for animation name
main_weapon = animation use one with common main weapon action name regardless of input
move attack = indicate using move attack animation
melee attack = indicate animation performing melee attack for spawning damage sprite in frame that can spawn it
range attack = indicate animation performing range attack for spawning bullet sprite when finish
repeat = keep repeating this animation until canceled, should only be used for action that can be controlled like walk
movable = can move during action
controllable = can perform controllable action during action like walk or attack 
forced move = subunit must move to provided pos during action regardless of input
next action = action that will be performed after the current one finish
uninterruptible = action can not be interrupt unless top_interrupt_animation is True
move loop = action involve repeating movement that can be cancel when movement change like walk to run
charge = indicate charging action
less mass = subunit has mass is divided during animation based on value provide
walk, run, flee, indicate movement type for easy checking
weapon = weapon index of action for easy checking
"""

skill_command_action_0 = {"name": "Skill 0"}
skill_command_action_1 = {"name": "Skill 1"}
skill_command_action_2 = {"name": "Skill 2"}
skill_command_action_3 = {"name": "Skill 3"}

walk_command_action = {"name": "Walk", "movable": True, "main_weapon": True, "repeat": True, "walk": True}
run_command_action = {"name": "Run", "movable": True, "main_weapon": True, "repeat": True,
                      "use momentum": True, "run": True}
flee_command_action = {"name": "Flee", "movable": True, "repeat": True, "flee": True}

melee_attack_command_action = ({"name": "Action 0", "melee attack": True, "weapon": 0},
                               {"name": "Action 1", "melee attack": True, "weapon": 1})
range_attack_command_action = ({"name": "Action 0", "range attack": True, "weapon": 0},
                               {"name": "Action 1", "range attack": True, "weapon": 1})

melee_hold_command_action = ({"name": "Action 0", "melee attack": True, "hold": True, "weapon": 0},
                             {"name": "Action 1", "melee attack": True, "hold": True, "weapon": 1})
range_hold_command_action = ({"name": "Action 0", "range attack": True, "hold": True, "weapon": 0},
                             {"name": "Action 1", "range attack": True, "hold": True, "weapon": 1})

range_walk_command_action = ({"name": "Action 0", "range attack": True, "walk": True, "movable": True, "weapon": 0},
                             {"name": "Action 1", "range attack": True, "walk": True, "movable": True, "weapon": 1})

range_run_command_action = ({"name": "Action 0", "range attack": True, "run": True, "movable": True, "weapon": 0},
                            {"name": "Action 1", "range attack": True, "run": True, "movable": True, "weapon": 1})

charge_command_action = ({"name": "Charge 0", "movable": True, "repeat": True,
                          "use momentum": True, "charge": True, "weapon": 0},
                         {"name": "Charge 1", "movable": True, "repeat": True,
                          "use momentum": True, "charge": True, "weapon": 1})

heavy_damaged_command_action = {"name": "HeavyDamaged", "uncontrollable": True, "movable": True,
                                "forced move": True, "less mass": 1.5, "damaged": True}
damaged_command_action = {"name": "Damaged", "uncontrollable": True, "movable": True,
                          "forced move": True, "less mass": 1.2, "damaged": True}
knockdown_command_action = {"name": "Knockdown", "uncontrollable": True, "movable": True, "forced move": True,
                            "less mass": 2, "uninterruptible": True,
                            "next action": {"name": "Standup", "uncontrollable": True, "damaged": True}}

die_command_action = {"name": "Die", "uninterruptible": True, "uncontrollable": True}


class Subunit(pygame.sprite.Sprite):
    empty_method = utility.empty_method

    battle = None
    base_map = None  # base map
    feature_map = None  # feature map
    height_map = None  # height map
    troop_data = None
    leader_data = None
    effect_list = None
    troop_sprite_list = None
    leader_sprite_list = None
    status_list = None
    animation_sprite_pool = None
    sound_effect_pool = None
    team_colour = None

    set_rotate = utility.set_rotate

    DiagonalMovement = DiagonalMovement
    Grid = Grid
    AStarFinder = AStarFinder

    # Import from common.subunit
    add_leader_buff = empty_method
    add_mount_stat = empty_method
    add_original_trait = empty_method
    add_weapon_stat = empty_method
    add_weapon_trait = empty_method
    ai_combat = empty_method
    ai_leader = empty_method
    ai_move = empty_method
    ai_retreat = empty_method
    ai_subunit = empty_method
    apply_effect = empty_method
    apply_map_status = empty_method
    apply_status_to_nearby = empty_method
    attack = empty_method
    cal_loss = empty_method
    cal_temperature = empty_method
    change_follow_order = empty_method
    change_formation = empty_method
    check_element_effect = empty_method
    check_element_threshold = empty_method
    check_skill_usage = empty_method
    check_special_effect = empty_method
    check_weapon_cooldown = empty_method
    create_subunit_sprite = empty_method
    create_troop_sprite = empty_method
    die = empty_method
    enter_battle = empty_method
    find_formation_size = empty_method
    find_retreat_target = empty_method
    health_stamina_logic = empty_method
    make_front_pos = empty_method
    morale_logic = empty_method
    move_logic = empty_method
    pick_animation = empty_method
    play_animation = empty_method
    process_trait_skill = empty_method
    rotate_logic = empty_method
    skill_command_input = empty_method
    status_update = empty_method
    swap_weapon = empty_method
    troop_loss = empty_method
    use_skill = empty_method

    script_dir = os.path.split(os.path.abspath(__file__))[0]
    for entry in os.scandir(Path(script_dir + "/common/subunit/")):  # load and replace modules from common.unit
        if entry.is_file():
            if ".py" in entry.name:
                file_name = entry.name[:-3]
            elif ".pyc" in entry.name:
                file_name = entry.name[:-4]
            exec(f"from gamescript.common.subunit import " + file_name)
            exec(f"" + file_name + " = " + file_name + "." + file_name)

    weapon_set = weapon_set

    skill_command_action_0 = skill_command_action_0
    skill_command_action_1 = skill_command_action_1
    skill_command_action_2 = skill_command_action_2
    skill_command_action_3 = skill_command_action_3

    walk_command_action = walk_command_action
    run_command_action = run_command_action
    flee_command_action = flee_command_action

    melee_attack_command_action = melee_attack_command_action
    range_attack_command_action = range_attack_command_action

    melee_hold_command_action = melee_hold_command_action
    range_hold_command_action = range_hold_command_action

    range_walk_command_action = range_walk_command_action
    range_run_command_action = range_run_command_action

    charge_command_action = charge_command_action

    heavy_damaged_command_action = heavy_damaged_command_action
    damaged_command_action = damaged_command_action
    knockdown_command_action = knockdown_command_action

    die_command_action = die_command_action

    all_formation_list = {}
    hitbox_image_list = {}

    # static variable
    default_animation_play_time = 0.1
    knock_down_sound_distance = 4
    knock_down_sound_shake = 1
    heavy_dmg_sound_distance = 2
    heavy_dmg_sound_shake = 0
    dmg_sound_distance = 1
    dmg_sound_shake = 0

    def __init__(self, troop_id, game_id, pos_id, team, start_pos, start_angle, start_hp, start_stamina,
                 leader_subunit, coa):
        """
        Subunit object represent a group of troop or leader
        Subunit has three different stage of stat;
        first: original stat (e.g., original_melee_attack), this is their stat before calculating equipment, trait, and other effect
        second: troop base stat (e.g., base_melee_attack), this is their stat after calculating equipment and trait
        third: stat with all effect (e.g., melee_attack), this is their stat after calculating terrain, weather, and status effect
        :param troop_id: ID of the troop or leader in data
        :param game_id: ID of the subunit as object
        :param pos_id: ID in map pos data
        :param team: Team index that this subunit belongs to
        :param start_angle: Starting angle
        :param start_hp: Starting health or troop number percentage
        :param start_stamina: Starting maximum stamina percentage
        :param coa: Coat of arms image, used as shadow and flag
        """
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.get_feature = self.feature_map.get_feature
        self.get_height = self.height_map.get_height

        self.not_broken = True
        self.move = False  # currently moving
        self.charging = False
        self.attack_subunit = None  # target for attacking
        self.melee_target = None  # current target of melee combat
        self.player_manual_control = False  # subunit controlled by player
        self.formation_add_change = False  # subordinate die in last update, reset formation, this is to avoid high workload when multiple die at once
        self.unit_add_change = False
        self.retreat_start = False
        self.taking_damage_angle = None

        self.hitbox = None

        self.sprite_troop_size = 1
        self.subunit_type = 1
        self.animation_play_time = self.default_animation_play_time
        self.animation_pool = {}  # list of animation sprite this subunit can play with its action
        self.current_animation = {}  # list of animation frames playing
        self.animation_queue = []  # list of animation queue
        self.show_frame = 0  # current animation frame
        self.max_show_frame = 0
        self.frame_timer = 0
        self.interrupt_animation = False
        self.top_interrupt_animation = False  # interrupt animation regardless of property
        self.current_action = {}  # action being performed
        self.command_action = {}  # next action to be performed
        self.idle_action = {}  # action that is performed when subunit is idle such as hold spear wall when skill active

        self.near_ally = []
        self.near_enemy = []
        self.nearest_enemy = []
        self.nearest_ally = []

        self.game_id = game_id  # ID of this subunit
        self.pos_id = pos_id
        self.team = team
        self.coa = coa

        self.alive_troop_follower = []  # list of alive troop subordinate subunits
        self.troop_follower_size = 0
        self.alive_leader_follower = []  # list of alive leader subordinate subunits
        self.leader_follower_size = 0
        self.leader = leader_subunit  # leader of the sub-subunit if there is one
        self.unit_leader = None  # leader at the top hierarchy in the unit
        self.is_unit_leader = False
        self.tactic = "attack"  # tactic for unit leader

        self.feature_mod = "Infantry"  # the terrain feature that will be used on this subunit
        self.move_speed = 0  # speed of current movement

        self.weapon_cooldown = {0: 0, 1: 0}  # subunit can attack with weapon only when cooldown reach attack speed
        self.flank_bonus = 1  # combat bonus when flanking
        self.morale_dmg_bonus = 0
        self.stamina_dmg_bonus = 0  # extra stamina melee_dmg
        self.original_hp_regen = 0  # health regeneration modifier, will not resurrect dead troop by default
        self.original_stamina_regen = 4  # stamina regeneration modifier
        self.original_morale_regen = 2  # morale regeneration modifier
        self.available_skill = []  # list of skills that subunit can currently use
        self.status_effect = {}  # current status effect
        self.status_duration = {}  # current status duration
        self.skill_effect = {}  # activate skill effect
        self.skill_duration = {}  # current active skill duration
        self.skill_cooldown = {}

        self.move_skill = []
        self.melee_skill = []
        self.range_skill = []
        self.enemy_near_skill = []
        self.damaged_skill = []
        self.retreat_skill = []
        self.idle_skill = []
        self.unit_melee_skill = []
        self.unit_range_skill = []
        self.troop_melee_skill = []
        self.move_far_skill = []

        self.available_move_skill = []
        self.available_melee_skill = []
        self.available_range_skill = []
        self.available_enemy_near_skill = []
        self.available_damaged_skill = []
        self.available_retreat_skill = []
        self.available_idle_skill = []
        self.available_unit_melee_skill = []
        self.available_troop_melee_skill = []
        self.available_troop_range_skill = []
        self.available_move_far_skill = []

        self.countup_timer = 0  # timer that count up to specific threshold to start event like charge attack timing
        self.countup_trigger_time = 0  # time that indicate when trigger happen
        self.hold_timer = 0  # how long animation holding so far
        self.release_timer = 0  # time when hold release

        self.attack_pos = None
        self.alive = True
        self.in_melee_combat_timer = 0
        self.timer = random.random()  # may need to use random.random()
        self.momentum = 0.1  # charging momentum
        self.max_melee_attack_range = 0
        self.melee_distance_zone = 1
        self.default_sprite_size = 1
        self.manual_shoot = False
        self.take_melee_dmg = 0
        self.take_range_dmg = 0
        self.take_aoe_dmg = 0

        self.terrain = 0
        self.feature = 0
        self.height = 0

        self.screen_scale = self.battle.screen_scale

        self.map_corner = self.battle.map_corner

        self.base_pos = pygame.Vector2(start_pos)  # true position of subunit in battle
        self.pos = pygame.Vector2((self.base_pos[0] * self.screen_scale[0] * 5,
                                   self.base_pos[1] * self.screen_scale[1] * 5))
        self.offset_pos = self.pos  # offset_pos after consider center offset for animation for showing on screen

        self.base_target = self.base_pos  # base_target pos to move
        self.command_target = self.base_pos  # command target pos
        self.follow_target = self.base_pos  # target pos based on formation position
        self.forced_target = self.base_pos  # target pos for animation that force moving

        self.front_pos = (0, 0)  # pos of this subunit for finding height of map at the front
        self.front_height = 0

        self.move_path = (self.base_pos, )

        # Set up special effect variable, first main item is for effect from troop/trait, second main item is for weapon
        # first sub item is permanent effect from trait, second sub item from temporary status or skill
        self.special_effect = {status_name["Name"]: [[False, False], [False, False]]
                               for status_name in self.troop_data.special_effect_list.values() if
                               status_name["Name"] != "Name"}

        # Setup troop original stat before applying trait, gear and other stuffs
        skill = []  # keep only troop and weapon skills in here, leader skills are kept in Leader object
        self.troop_id = troop_id  # ID of preset used for this subunit

        self.name = "None"
        self.is_leader = False
        if type(self.troop_id) is not str:  # normal troop
            self.troop_id = int(self.troop_id)
            sprite_list = self.troop_sprite_list
            stat = self.troop_data.troop_list[self.troop_id].copy()
            lore = self.troop_data.troop_lore[self.troop_id].copy()
            self.grade = stat["Grade"]  # training level/class grade
            grade_stat = self.troop_data.grade_list[self.grade]

            training_scale = (stat["Melee Attack Scale"], stat["Defence Scale"], stat["Ranged Attack Scale"])

            self.magazine_count = {index: {0: 1 + stat["Ammunition Modifier"], 1: 1 + stat["Ammunition Modifier"]}
                                   for index in range(0, 2)}  # Number of magazine, as mod number
            self.original_morale = stat["Morale"] + grade_stat["Morale Bonus"]  # morale with grade bonus
            self.original_discipline = stat["Discipline"] + grade_stat[
                "Discipline Bonus"]  # discipline with grade bonus
            self.original_mental = stat["Mental"] + grade_stat[
                "Mental Bonus"]  # mental resistance from morale melee_dmg and mental status effect
            self.troop_class = stat["Troop Class"]

        else:  # leader subunit
            self.is_leader = True
            sprite_list = self.leader_sprite_list
            stat = self.leader_data.leader_list[troop_id].copy()
            lore = self.leader_data.leader_lore[troop_id].copy()
            self.grade = 12  # leader grade by default
            grade_stat = self.troop_data.grade_list[self.grade]

            training_scale = (stat["Melee Speciality"], stat["Melee Speciality"], stat["Range Speciality"])

            self.magazine_count = {0: {0: 2, 1: 2}, 1: {0: 2, 1: 2}}  # leader gets double ammunition
            self.original_morale = 100 + grade_stat["Morale Bonus"]  # morale with grade bonus
            self.original_discipline = 100 + grade_stat[
                "Discipline Bonus"]  # discipline with grade bonus
            self.original_mental = 50 + grade_stat[
                "Mental Bonus"]  # mental resistance from morale melee_dmg and mental status effect

            self.special_effect["Shoot While Moving"][0][0] = True  # allow shoot while moving for hero

            self.troop_class = "Leader"

            self.leader_authority = stat["Charisma"]
            self.melee_command = stat["Melee Speciality"]
            self.range_command = stat["Range Speciality"]
            self.cav_command = stat["Cavalry Speciality"]
            self.leader_command_buff = (self.melee_command, self.range_command, self.cav_command)
            self.social = self.leader_data.leader_class[stat["Social Class"]]

            self.formation_list = ["Cluster"] + stat["Formation"]
            self.troop_formation_preset = []
            self.troop_formation = "Cluster"
            self.troop_formation_phase = "Melee Phase"
            self.troop_formation_style = "Cavalry Flank"
            self.troop_formation_density = "Tight"
            self.troop_formation_position = "Behind"
            self.troop_follow_order = "Stay Formation"

            self.unit_formation = "Cluster"
            self.unit_formation_preset = []
            self.unit_formation_phase = self.troop_formation_phase
            self.unit_formation_style = self.troop_formation_style
            self.unit_formation_density = self.troop_formation_density
            self.unit_formation_position = self.troop_formation_position
            self.unit_follow_order = self.troop_follow_order
            self.unit_type = "melee inf"  # type of unit indicate troop composition, melee inf, range inf, melee cav, range cav", "artillery"

            self.formation_consider_flank = False  # has both infantry and cavalry, consider flank placment style
            self.troop_distance_list = {}
            self.troop_pos_list = {}
            self.unit_consider_flank = False
            self.unit_distance_list = {}
            self.unit_pos_list = {}

            if self.troop_id in self.leader_data.images:  # Put leader image into leader slot
                self.portrait = self.leader_data.images[self.troop_id].copy()
            else:  # Use Unknown leader image if there is none in list
                self.portrait = self.leader_data.images["other"].copy()
                font = pygame.font.SysFont("timesnewroman", 50)
                text_image = font.render(self.troop_id, True, pygame.Color("white"))
                text_rect = text_image.get_rect(center=(self.portrait.get_width() / 2,
                                                        self.portrait.get_height() / 1.3))
                self.portrait.blit(text_image, text_rect)

        self.name = lore[0]  # name according to the preset
        self.race = stat["Race"]  # creature race
        race_stat = self.troop_data.race_list[stat["Race"]]
        self.race_name = race_stat["Name"]
        self.grade_name = grade_stat["Name"]

        self.charge_skill = stat["Charge Skill"]  # for easier reference to check what charge skill this subunit has
        skill = stat["Skill"]  # skill list according to the preset

        # Default element stat
        element_dict = {key.split(" ")[0]: 0 for key in race_stat if
                        " Resistance" in key}  # get only resistance that exist in race data
        self.element_status_check = element_dict.copy()  # element threshold count
        self.original_element_resistance = element_dict.copy()

        self.original_heat_resistance = 0  # resistance to heat temperature
        self.original_cold_resistance = 0  # Resistance to cold temperature
        self.temperature_count = 0  # temperature threshold count

        # initiate equipment stat
        self.weight = 0
        self.original_weapon_dmg = {index: {0: element_dict.copy(), 1: element_dict.copy()} for index in range(0, 2)}
        self.weapon_penetrate = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.weapon_weight = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.range_dmg = {index: {0: element_dict.copy(), 1: element_dict.copy()} for index in range(0, 2)}
        self.original_shoot_range = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.original_melee_range = {0: {}, 1: {}}
        self.original_melee_def_range = {0: {}, 1: {}}
        self.original_weapon_speed = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}

        self.magazine_size = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}  # can shoot how many times before have to reload
        self.ammo_now = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}  # ammunition count in the current magazine
        self.equipped_weapon = 0
        self.swap_weapon_list = (1, 0)  # for swapping to other set

        # Get troop stat

        attribute_stat = race_stat
        if type(troop_id) is str and "h" in troop_id:  # use leader stat for hero (leader) subunit
            attribute_stat = stat

        max_scale = sum(training_scale)
        if max_scale != 0:
            training_scale = [item / max_scale for item in
                              training_scale]  # convert to proportion of whatever max number
        else:
            training_scale = [0.333333 for _ in training_scale]

        self.subunit_type = 0
        if training_scale[2] > training_scale[0]:  # range training higher than melee, change type to range infantry
            self.subunit_type = 1

        self.strength = attribute_stat["Strength"]
        self.dexterity = attribute_stat["Dexterity"]
        self.agility = attribute_stat["Agility"]
        self.constitution = attribute_stat["Constitution"]
        self.intelligence = attribute_stat["Intelligence"]
        self.wisdom = attribute_stat["Wisdom"]

        self.original_melee_attack = ((self.strength * 0.4) + (self.dexterity * 0.3) + (self.wisdom * 0.2)) + \
                                     (grade_stat["Training Score"] * training_scale[0])

        self.original_melee_def = ((self.dexterity * 0.2) + (self.agility * 0.3) + (self.constitution * 0.3) +
                                   (self.wisdom * 0.2)) + (grade_stat["Training Score"] *
                                                           ((training_scale[0] + training_scale[1]) / 2))

        self.original_melee_dodge = ((self.dexterity * 0.1) + (self.agility * 0.3) + (self.wisdom * 0.1)) + \
                                    (grade_stat["Training Score"] * training_scale[1])

        self.original_range_def = ((self.dexterity * 0.4) + (self.agility * 0.2) + (self.constitution * 0.3) +
                                   (self.wisdom * 0.1)) + (grade_stat["Training Score"] *
                                                           ((training_scale[1] + training_scale[2]) / 2))

        self.original_range_dodge = ((self.dexterity * 0.2) + (self.agility * 0.2) + (self.wisdom * 0.1)) + \
                                    (grade_stat["Training Score"] * training_scale[1])

        self.original_accuracy = ((self.strength * 0.1) + (self.dexterity * 0.6) + (self.wisdom * 0.3)) + \
                                 (grade_stat["Training Score"] * training_scale[2]) / 4

        self.original_sight = ((self.dexterity * 0.8) + (self.wisdom * 0.2)) + (grade_stat["Training Score"] *
                                                                                training_scale[2])

        self.original_reload = ((self.strength * 0.1) + (self.dexterity * 0.4) + (self.agility * 0.4) +
                                (self.wisdom * 0.1)) + (grade_stat["Training Score"] * training_scale[2])

        self.original_charge = ((self.strength * 0.3) + (self.agility * 0.3) + (self.dexterity * 0.3) +
                                (self.wisdom * 0.2)) + (grade_stat["Training Score"] * training_scale[0])

        self.original_charge_def = ((self.dexterity * 0.4) + (self.agility * 0.1) + (self.constitution * 0.3) +
                                    (self.wisdom * 0.2)) + (grade_stat["Training Score"] *
                                                            ((training_scale[0] + training_scale[1]) / 2))

        self.original_speed = self.agility / 5  # get replaced with mount agi and speed bonus

        self.shot_per_shoot = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}

        self.original_crit_effect = 1  # critical extra modifier

        self.trait = {"Original": stat["Trait"] + race_stat["Trait"] +
                                  self.troop_data.grade_list[self.grade]["Trait"],
                      "Weapon": {0: {0: [], 1: []}, 1: {0: [], 1: []}}}  # trait from preset, race and grade
        self.trait_ally_status = {"Original": {}, "Weapon": {}, "Final": {}}
        self.trait_enemy_status = {"Original": {}, "Weapon": {}, "Final": {}}

        self.armour_gear = stat["Armour"]  # armour equipment
        self.armour_id = 0
        if self.armour_gear:
            self.armour_id = self.armour_gear[0]
            self.weight += self.troop_data.armour_list[self.armour_id]["Weight"]  # Add weight from both armour
            armour_stat = self.troop_data.armour_list[self.armour_id]
            armour_grade_mod = self.troop_data.equipment_grade_list[self.armour_gear[1]]["Modifier"]
            for element in self.original_element_resistance:  # resistance from race and armour
                self.original_element_resistance[element] = race_stat[element + " Resistance"]
                self.original_element_resistance[element] += (armour_stat[element + " Resistance"] * armour_grade_mod)
            self.trait["Original"] += self.troop_data.armour_list[self.armour_id][
                "Trait"]  # add armour trait to subunit

        self.original_skill = skill.copy()  # Skill that the subunit processes
        if "" in self.original_skill:
            self.original_skill.remove("")

        self.health = ((self.strength * 0.2) + (self.constitution * 0.8)) * (grade_stat[
            "Health Effect"] / 100) * (start_hp / 100)  # Health of troop
        self.stamina = ((self.strength * 0.2) + (self.constitution * 0.8)) * (grade_stat["Stamina Effect"] / 100) * (
                start_stamina / 100)  # starting stamina with grade

        self.original_mana = 0
        if "Mana" in stat:
            self.original_mana = stat["Mana"]  # Resource for magic skill

        # Add equipment stat
        self.primary_main_weapon = stat["Primary Main Weapon"]
        if not self.primary_main_weapon:  # replace empty with standard unarmed
            self.primary_main_weapon = (1, 3)
        self.primary_sub_weapon = stat["Primary Sub Weapon"]
        if not self.primary_sub_weapon:  # replace empty with standard unarmed
            self.primary_sub_weapon = (1, 3)
        self.secondary_main_weapon = stat["Secondary Main Weapon"]
        if not self.secondary_main_weapon:  # replace empty with standard unarmed
            self.secondary_main_weapon = (1, 3)
        self.secondary_sub_weapon = stat["Secondary Sub Weapon"]
        if not self.secondary_sub_weapon:  # replace empty with standard unarmed
            self.secondary_sub_weapon = (1, 3)
        self.melee_weapon_set = {}
        self.range_weapon_set = {}
        self.power_weapon = {}
        self.block_weapon = {}
        self.charge_block_weapon = {}
        self.timing_weapon = {}
        self.timing_start_weapon = {}
        self.timing_end_weapon = {}
        self.equipped_power_weapon = ()
        self.equipped_block_weapon = ()
        self.equipped_charge_block_weapon = ()
        self.equipped_timing_weapon = ()
        self.equipped_timing_start_weapon = {}
        self.equipped_timing_end_weapon = {}
        self.weapon_type = {}
        self.weapon_set = ((self.primary_main_weapon, self.primary_sub_weapon),
                           (self.secondary_main_weapon, self.secondary_sub_weapon))

        self.weapon_id = ((self.primary_main_weapon[0], self.primary_sub_weapon[0]),
                          (self.secondary_main_weapon[0], self.secondary_sub_weapon[0]))
        self.weapon_data = ((self.troop_data.weapon_list[self.primary_main_weapon[0]],
                             self.troop_data.weapon_list[self.primary_sub_weapon[0]]),
                            (self.troop_data.weapon_list[self.secondary_main_weapon[0]],
                             self.troop_data.weapon_list[self.secondary_sub_weapon[0]]))
        self.equipped_weapon_data = self.weapon_data[self.equipped_weapon]
        self.weapon_name = ((self.troop_data.weapon_list[self.primary_main_weapon[0]]["Name"],
                             self.troop_data.weapon_list[self.primary_sub_weapon[0]]["Name"]),
                            (self.troop_data.weapon_list[self.secondary_main_weapon[0]]["Name"],
                             self.troop_data.weapon_list[self.secondary_sub_weapon[0]]["Name"]))

        self.animation_race_name = self.race_name
        self.troop_size = race_stat["Size"]

        self.mount_gear = stat["Mount"]
        self.mount_race_name = "None"
        self.mount_armour_id = 0
        if self.mount_gear:
            self.mount = self.troop_data.mount_list[self.mount_gear[0]]  # stat of mount this subunit use
            self.mount_race_name = self.troop_data.race_list[self.mount["Race"]]["Name"]
            self.mount_grade = self.troop_data.mount_grade_list[self.mount_gear[1]]
            self.mount_armour_id = self.mount_gear[2]
            self.mount_armour = self.troop_data.mount_armour_list[self.mount_armour_id]
            self.weight += self.mount_armour["Weight"]  # Add weight from mount armour
            self.animation_race_name += "&" + self.mount_race_name

            if self.mount_gear[0] != 1:  # have a mount, add mount stat with its grade to subunit stat
                self.add_mount_stat()

        self.body_weapon_stat = self.troop_data.weapon_list[1]
        self.body_weapon_damage = element_dict.copy()  # weapon use when charge with no weapon, use unarmed as stat and will not be affected by status, skill or anything else
        for key in self.body_weapon_damage:  # add strength as damage bonus
            self.body_weapon_damage[key] = ((self.body_weapon_damage[key] * self.body_weapon_stat["Damage Balance"]) +
                                            self.body_weapon_damage[key] * (self.strength / 100),
                                            self.body_weapon_damage[key] +
                                            self.body_weapon_damage[key] * (self.strength / 100))
        # add troop size as pure bonus
        self.body_weapon_penetrate = self.troop_data.weapon_list[1]["Armour Penetration"] + self.troop_size

        self.troop_mass = self.troop_size

        self.knock_down_sound_distance = self.knock_down_sound_distance * self.troop_mass
        self.knock_down_sound_shake = self.knock_down_sound_shake * self.troop_mass
        self.heavy_dmg_sound_distance = self.heavy_dmg_sound_distance * self.troop_mass
        self.dmg_sound_distance = self.dmg_sound_distance * self.troop_mass
        self.hit_volume_mod = self.troop_mass / 50

        self.command_buff = 1
        self.leader_social_buff = 0
        self.authority = 0
        self.original_hidden = 1000 / self.troop_mass  # hidden based on size, use size after add mount

        self.trait["Original"] = tuple(
            set([trait for trait in self.trait["Original"] if trait != 0]))  # remove empty and duplicate traits
        self.trait["Original"] = {x: self.troop_data.trait_list[x] for x in self.trait["Original"] if
                                  x in self.troop_data.trait_list}  # replace trait index with data

        for index, status_head in enumerate(("Status", "Enemy Status")):
            trait_status_dict = (self.trait_ally_status, self.trait_enemy_status)[index]
            for trait in self.trait["Original"].values():
                for status in trait[status_head]:
                    if status not in trait_status_dict["Original"]:
                        trait_status_dict["Original"][status] = trait["Area Of Effect"]
                    elif trait_status_dict["Original"][status] < trait["Area Of Effect"]:  # replace aoe that larger
                        trait_status_dict["Original"][status] = trait["Area Of Effect"]

        self.add_original_trait()

        if self.leader:
            if self.is_leader:
                self.leader.alive_leader_follower.append(self)
            else:
                self.leader.alive_troop_follower.append(self)

        self.original_skill = [skill for skill in self.original_skill if
                               (type(skill) is str or (skill in self.troop_data.skill_list and
                                                       self.troop_data.skill_list[skill]["Troop Type"] == 0 or
                                                       self.troop_data.skill_list[skill]["Troop Type"] == self.subunit_type))]

        if self.subunit_type == 2:  # cavalry has half weight penalty
            self.weight = self.weight / 2

        self.original_speed = (self.original_speed * ((100 - self.weight) / 100)) + grade_stat[
            "Speed Bonus"]  # finalise base speed with weight and grade bonus
        self.acceleration = self.original_speed  # determine how long it takes to reach full speed when run

        # Stat after applying trait and gear
        self.base_melee_attack = self.original_melee_attack
        self.base_melee_def = self.original_melee_def
        self.base_range_def = self.original_range_def
        self.base_melee_dodge = self.original_melee_dodge - self.weight
        self.base_range_dodge = self.original_range_dodge - self.weight

        self.base_element_resistance = self.original_element_resistance.copy()

        self.base_speed = self.original_speed
        self.base_accuracy = self.original_accuracy
        self.base_sight = self.original_sight
        self.base_hidden = self.original_hidden
        self.base_reload = self.original_reload
        self.base_charge = self.original_charge
        self.base_charge_def = self.original_charge_def
        self.skill = self.original_skill.copy()
        self.input_skill = self.skill.copy()  # skill dict without charge skill

        self.leader_skill = {x: self.leader_data.skill_list[x] for x in self.skill if x in self.leader_data.skill_list}
        if not self.leader:  # no higher leader, count as commander tier
            for key, value in self.leader_skill.items():  # replace leader skill with commander skill version
                for key2, value2 in self.leader_data.commander_skill_list.items():
                    if key in value2["Replace"]:
                        old_action = self.leader_skill[key]["Action"]
                        self.leader_skill[key] = value2
                        self.leader_skill[key]["Action"] = old_action  # get action from normal leader skill

        self.base_mana = self.original_mana
        self.base_morale = self.original_morale
        self.base_discipline = self.original_discipline
        self.base_hp_regen = self.original_hp_regen
        self.base_stamina_regen = self.original_stamina_regen
        self.base_morale_regen = self.original_morale_regen
        self.base_mental = self.original_mental
        self.base_heat_resistance = self.original_heat_resistance
        self.base_cold_resistance = self.original_cold_resistance
        self.base_crit_effect = self.original_crit_effect

        self.add_weapon_stat()
        self.action_list = {}  # get added in change_equipment

        self.last_health_state = 0  # state start at full
        self.last_stamina_state = 0

        self.max_stamina = self.stamina
        self.stamina75 = self.stamina * 0.75
        self.stamina50 = self.stamina * 0.5
        self.stamina25 = self.stamina * 0.25
        self.stamina5 = self.stamina * 0.05
        self.stamina_list = (self.stamina75, self.stamina50, self.stamina25, self.stamina5, -1)

        self.max_health = self.health  # health percentage
        self.max_health10 = self.max_health * 0.1
        self.max_health20 = self.max_health * 0.2
        self.max_health50 = self.max_health * 0.5

        self.description = lore[1]  # subunit description for inspect ui

        self.max_morale = self.base_morale

        # Final stat after receiving modifier effect from various sources, reset every time status is updated
        self.melee_attack = self.base_melee_attack
        self.melee_def = self.base_melee_def
        self.range_def = self.base_range_def
        self.melee_dodge = self.base_melee_dodge
        self.range_dodge = self.base_range_dodge
        self.element_resistance = self.base_element_resistance.copy()
        self.speed = self.base_speed
        self.accuracy = self.base_accuracy
        self.reload = self.base_reload
        self.morale = self.base_morale
        self.discipline = self.base_discipline
        self.charge = self.base_charge
        self.charge_power = self.charge * self.speed / 2 * self.troop_mass
        self.charge_def = self.base_charge_def
        self.charge_def_power = self.charge_def * self.troop_mass
        self.hp_regen = self.base_hp_regen
        self.stamina_regen = self.base_stamina_regen
        self.morale_regen = self.base_morale_regen
        self.heat_resistance = self.base_heat_resistance
        self.cold_resistance = self.base_cold_resistance
        self.mental = self.base_mental
        self.crit_effect = self.base_crit_effect

        self.weapon_dmg = self.original_weapon_dmg[self.equipped_weapon].copy()
        self.weapon_speed = self.original_weapon_speed[self.equipped_weapon].copy()
        self.shoot_range = self.original_shoot_range[self.equipped_weapon].copy()
        self.melee_range = self.original_melee_range[self.equipped_weapon]
        self.melee_def_range = self.original_melee_def_range[self.equipped_weapon]
        self.max_melee_range = self.melee_range[0]
        self.charge_melee_range = self.max_melee_range * 10
        self.melee_charge_range = {0: 0, 1: 0}

        self.morale_state = 1  # turn into percentage

        self.run_speed = 1
        self.walk_speed = 1

        if self.mental < 0:  # cannot be negative
            self.mental = 0
        elif self.mental > 200:  # cannot exceed 200
            self.mental = 200

        self.mental = (200 - self.mental) / 100  # convert to percentage

        self.angle = start_angle
        self.new_angle = self.angle
        self.radians_angle = math.radians(360 - self.angle)  # radians for apply angle to position
        self.sprite_direction = rotation_dict[min(rotation_list,
                                                  key=lambda x: abs(
                                                      x - self.angle))]  # find closest in list of rotation for sprite direction

        self.sprite_id = str(stat["Sprite ID"])
        self.weapon_version = ((sprite_list[self.sprite_id]["p1_primary_main_weapon"],
                                sprite_list[self.sprite_id]["p1_primary_sub_weapon"]),
                               (sprite_list[self.sprite_id]["p1_secondary_main_weapon"],
                                sprite_list[self.sprite_id]["p1_secondary_sub_weapon"]))

        self.image = pygame.Surface((0, 0))  # create dummy image for now

        self.melee_distance_zone = self.troop_size * 5
        self.stay_distance_zone = self.melee_distance_zone + 10

        # Save some special effect that unlikely to change as variable to reduce workload
        self.shoot_while_moving = self.check_special_effect("Shoot While Moving")
        self.impetuous = self.check_special_effect("Impetuous")
        self.night_vision = self.check_special_effect("Night Vision")
        self.day_blindness = self.check_special_effect("Day Blindness")

        # Create hitbox sprite
        self.hitbox_front_distance = self.troop_size
        if self.team not in self.hitbox_image_list:
            self.hitbox_image_list[self.team] = {"troop": {}, "leader": {}}
        if self.is_leader:
            if (self.troop_size * 5, self.troop_size * 5) not in self.hitbox_image_list[self.team]["leader"]:
                self.hitbox_image = pygame.Surface((self.troop_size * 5, self.troop_size * 5), pygame.SRCALPHA)
                pygame.draw.circle(self.hitbox_image, (120, 128, 0, 150),
                                   (self.hitbox_image.get_width() / 2, self.hitbox_image.get_height() / 2),
                                   self.hitbox_image.get_width() / 2)

                pygame.draw.circle(self.hitbox_image,
                                   (self.team_colour[self.team][0], self.team_colour[self.team][1],
                                    self.team_colour[self.team][2], 150),
                                   (self.hitbox_image.get_width() / 2, self.hitbox_image.get_height() / 2),
                                   self.hitbox_image.get_width() / 2.4)
            else:
                self.hitbox_image = self.hitbox_image_list[self.team]["leader"][(self.troop_size * 5, self.troop_size * 5)]
        else:
            if (self.troop_size * 5, self.troop_size * 5) not in self.hitbox_image_list[self.team]["troop"]:
                self.hitbox_image = pygame.Surface((self.troop_size * 5, self.troop_size * 5), pygame.SRCALPHA)
                pygame.draw.circle(self.hitbox_image, (0, 0, 0, 150),
                                   (self.hitbox_image.get_width() / 2, self.hitbox_image.get_height() / 2),
                                   self.hitbox_image.get_width() / 2)

                pygame.draw.circle(self.hitbox_image,
                                   (self.team_colour[self.team][0], self.team_colour[self.team][1],
                                    self.team_colour[self.team][2], 150),
                                   (self.hitbox_image.get_width() / 2, self.hitbox_image.get_height() / 2),
                                   self.hitbox_image.get_width() / 2.4)
            else:
                self.hitbox_image = self.hitbox_image_list[self.team]["troop"][
                    (self.troop_size * 5, self.troop_size * 5)]

        self.rect = self.image.get_rect(center=self.offset_pos)  # for blit into screen

    def update(self, dt):
        if self.health:  # only run these when not dead
            if dt:  # only run these when game not pause
                self.timer += dt

                if self.formation_add_change:
                    self.formation_add_change = False
                    if self.alive_troop_follower:
                        self.change_formation("troop")

                if self.unit_add_change:
                    self.unit_add_change = False
                    if self.alive_leader_follower:
                        self.change_formation("unit")

                self.check_weapon_cooldown(dt)

                if self.in_melee_combat_timer > 0:
                    self.in_melee_combat_timer -= dt
                    if self.in_melee_combat_timer < 0:
                        self.in_melee_combat_timer = 0

                if self.take_melee_dmg > 0:
                    self.take_melee_dmg -= dt
                    if self.take_melee_dmg < 0:
                        self.take_melee_dmg = 0
                if self.take_range_dmg > 0:
                    self.take_range_dmg -= dt
                    if self.take_range_dmg < 0:
                        self.take_range_dmg = 0
                if self.take_aoe_dmg > 0:
                    self.take_aoe_dmg -= dt
                    if self.take_aoe_dmg < 0:
                        self.take_aoe_dmg = 0

                if self.timer > 1:  # Update status and skill use around every 1 second
                    self.status_update()

                    if self not in self.battle.troop_ai_logic_queue:
                        self.battle.troop_ai_logic_queue.append(self)

                    self.timer -= 1

                self.taking_damage_angle = None

                if not self.player_manual_control:
                    if self.not_broken:
                        if "uncontrollable" not in self.current_action and "uncontrollable" not in self.command_action:
                            self.ai_combat()
                            self.ai_move()
                    else:
                        self.ai_retreat()

                self.check_skill_usage()

                if self.angle != self.new_angle:  # Rotate Function
                    self.rotate_logic(dt)

                self.move_logic(dt)  # Move function

                if self.retreat_start and (self.map_corner[0] <= self.base_pos[0] or self.base_pos[0] <= 0 or
                                           self.map_corner[1] <= self.base_pos[1] or self.base_pos[1] <= 0):
                    self.alive = False  # # remove troop that pass map border, enter dead state
                    self.health = 0
                    self.die("flee")

                self.morale_logic(dt)

                self.health_stamina_logic(dt)

                self.move = False  # reset move check

                # Animation and sprite system

                #     if 0 < self.countup_timer < self.countup_trigger_time:
                #         self.countup_timer += dt
                # elif self.countup_timer > 0:
                #     self.countup_timer = 0
                #     self.countup_trigger_time = 0

                hold_check = False
                if "hold" in self.current_action and \
                        "hold" in self.current_animation[self.show_frame]["frame_property"] and \
                        "hold" in self.action_list[self.current_action["weapon"]]["Properties"]:
                    hold_check = True
                    self.hold_timer += dt
                elif self.hold_timer > 0:  # no longer holding, reset timer
                    self.hold_timer = 0

                done, frame_start = self.play_animation(dt, hold_check)

                if self.charging and "charge" not in self.current_action:  # no longer charge
                    self.charging = False

                if frame_start:
                    if "melee attack" in self.current_action and \
                            self.current_animation[self.show_frame]["dmg_sprite"]:
                        # perform melee attack when frame that produce dmg effect starts
                        self.attack(self.current_animation[self.show_frame]["dmg_sprite"])
                    elif self.charging is False and self.momentum == 1:
                        # add charge damage effect
                        self.charging = True
                        self.attack("charge")

                # Pick new animation, condition to stop animation: get interrupt,
                # low level animation got replace with more important one, finish playing, skill animation and its effect end
                if self.top_interrupt_animation or \
                        (self.interrupt_animation and "uninterruptible" not in self.current_action) or \
                        (((not self.current_action and self.command_action) or done or
                          (self.idle_action and self.idle_action != self.command_action))):
                    if done:
                        if "range attack" in self.current_action:  # shoot bullet only when animation finish
                            self.attack("range")
                        elif "skill" in self.current_action:  # spawn skill effect and sound
                            self.use_skill(self.current_action["skill"])

                    if "next action" in self.current_action:  # play next action first instead of command
                        self.current_action = self.current_action["next action"]
                    elif "damaged" in self.current_action and self.available_damaged_skill and \
                            not self.command_action:  # use skill after playing damaged animation
                        self.current_action = {}  # idle first to check for skill next update
                        self.command_action = {"skill": self.available_damaged_skill[0]}
                    else:
                        self.current_action = self.command_action  # continue next action when animation finish
                        self.command_action = self.idle_action

                    if self.interrupt_animation:
                        self.interrupt_animation = False
                        self.release_timer = 0  # reset any release timer

                    self.top_interrupt_animation = False

                    self.show_frame = 0
                    self.frame_timer = 0
                    self.pick_animation()

                    self.animation_play_time = self.default_animation_play_time

                    self.rect = self.image.get_rect(center=self.offset_pos)

        else:  # dead
            if self.alive:  # enter dead state
                self.alive = False  # enter dead state
                self.die("dead")
            if self.show_frame < self.max_show_frame:
                self.play_animation(dt, False)
