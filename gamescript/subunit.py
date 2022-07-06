import math
import os
import random

import pygame
import pygame.freetype
from gamescript.common import utility, animation

rotation_list = (90, 120, 45, 0, -90, -45, -120, 180, -180)
rotation_name = ("l_side", "l_sidedown", "l_sideup", "front", "r_side", "r_sideup", "r_sidedown", "back", "back")
rotation_dict = {key: rotation_name[index] for index, key in enumerate(rotation_list)}

infinity = float("inf")


class Subunit(pygame.sprite.Sprite):
    empty_method = utility.empty_method

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
    reset_animation = animation.reset_animation
    set_rotate = utility.set_rotate

    # Import from common.subunit
    add_mount_stat = empty_method
    add_original_trait = empty_method
    add_weapon_trait = empty_method
    add_weapon_stat = empty_method
    apply_map_status = empty_method
    apply_status_to_friend = empty_method
    combat_pathfind = empty_method
    create_inspect_sprite = empty_method
    die = empty_method
    dmg_cal = empty_method
    element_effect_count = empty_method
    element_threshold_count = empty_method
    find_close_target = empty_method
    find_nearby_subunit = empty_method
    hit_register = empty_method
    loss_cal = empty_method
    make_front_pos = empty_method
    make_pos_range = empty_method
    make_sprite = empty_method
    process_trait_skill = empty_method
    rotate = empty_method
    special_effect_check = empty_method
    start_set = empty_method
    status_update = empty_method
    swap_weapon = empty_method
    temperature_cal = empty_method
    troop_loss = empty_method
    use_skill = empty_method
    zoom_scale = empty_method

    # Import from *genre*.subunit
    charge_logic = empty_method
    combat_logic = empty_method
    fatigue = empty_method
    find_shooting_target = empty_method
    gone_leader_process = empty_method
    health_stamina_logic = empty_method
    morale_logic = empty_method
    move_logic = empty_method
    pick_animation = empty_method
    player_interact = empty_method
    rotate_logic = empty_method
    skill_check_logic = empty_method
    state_reset_logic = empty_method

    script_dir = os.path.split(os.path.abspath(__file__))[0]
    for entry in os.scandir(script_dir + "\\common\\subunit\\"):  # load and replace modules from common.unit
        if entry.is_file() and ".py" in entry.name:
            file_name = entry.name[:-3]
            exec(f"from gamescript.common.subunit import " + file_name)
            exec(f"" + file_name + " = " + file_name + "." + file_name)

    # genre specific variables
    dmg_include_leader = True
    stat_use_troop_number = True

    def __init__(self, troop_id, game_id, unit, start_pos, start_hp, start_stamina, unit_scale, animation_pool=None):
        """
        Subunit object represent a group of troop or leader
        Subunit has three different stage of stat;
        first: original stat (e.g., original_melee_attack), this is their stat before calculating equipment, trait, and other effect
        second: troop base stat (e.g., base_melee_attack), this is their stat after calculating equipment and trait
        third: stat with all effect (e.g., melee_attack), this is their stat after calculating terrain, weather, and status effect
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

        self.leader = None  # leader in the sub-subunit if there is one, got add in leader start_set
        self.board_pos = None  # used for event log position of subunit (Assigned in battle subunit setup)
        self.walk = False  # currently walking
        self.run = False  # currently running
        self.frontline = False  # on front line of unit or not
        self.unit_leader = False  # contain the general or not, making it leader subunit
        self.attack_target = None  # target for attacking
        self.melee_target = None  # current target of melee combat
        self.close_target = None  # closet target to move to in melee
        self.attacking = False  # for checking if unit in attacking state or not for using charge skill
        self.control = True  # subunit will obey command input

        self.animation_pool = {}  # list of animation sprite this subunit can play with its action
        self.current_animation = {}  # list of animation frames playing
        self.animation_queue = []  # list of animation queue
        self.show_frame = 0  # current animation frame
        self.animation_timer = 0
        self.current_action = ()  # for genre that use specific action instead of state
        self.command_action = ()  # next action to be performed
        self.idle_action = ()  # action that is performed when subunit is idle such as hold spear wall when skill active

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
        self.state = 0  # current subunit state, similar to unit state
        self.timer = random.random()  # may need to use random.random()
        self.move_timer = 0  # timer for moving to front position before attacking nearest enemy
        self.charge_momentum = 1  # charging momentum to reach target before choosing the nearest enemy
        self.zoom = 1
        self.last_zoom = 0
        self.skill_cond = 0
        self.broken_limit = 0  # morale require for unit to stop broken state, will increase everytime broken state stop
        self.interrupt_animation = False
        self.use_animation_sprite = False

        # Default element stat
        element_dict = {"Physical": 0, "Fire": 0, "Water": 0, "Air": 0, "Earth": 0, "Poison": 0, "Magic": 0}
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
        self.original_range = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.original_weapon_speed = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}

        self.magazine_size = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}  # can shoot how many times before have to reload
        self.ammo_now = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}  # ammunition count in the current magazine
        self.arrow_speed = {0: {0: 0, 1: 0}, 1: {0: 0, 1: 0}}
        self.weapon_skill = {0: {0: [], 1: []}, 1: {0: [], 1: []}}
        self.equipped_weapon = 0

        # Setup troop original stat before applying trait, gear and other stuffs
        skill = []  # keep only troop and weapon skills in here, leader skills are kept in Leader object
        self.troop_number = 1  # number of troops inside the subunit
        if type(troop_id) == int or "h" not in troop_id:
            self.troop_id = int(troop_id)  # ID of preset used for this subunit
            stat = self.troop_data.troop_list[self.troop_id].copy()
            self.grade = stat["Grade"]  # training level/class grade
            grade_stat = self.troop_data.grade_list[self.grade]
            skill = stat["Skill"]  # skill list according to the preset
            self.original_melee_attack = stat["Melee Attack"] + grade_stat[
                "Melee Attack Bonus"]  # melee attack with grade bonus
            self.original_melee_def = stat["Melee Defence"] + grade_stat[
                "Defence Bonus"]  # melee defence with grade bonus
            self.original_range_def = stat["Ranged Defence"] + grade_stat[
                "Defence Bonus"]  # range defence with grade bonus
            self.original_accuracy = stat["Accuracy"] + grade_stat["Accuracy Bonus"]
            self.original_sight = stat["Sight"]  # sight range
            self.magazine_count = {index: {0: stat["Ammunition Modifier"], 1: stat["Ammunition Modifier"]}
                                   for index in range(0, 2)}  # Number of magazine, as mod number
            self.original_reload = stat["Reload"] + grade_stat["Reload Bonus"]
            self.original_charge = stat["Charge"]
            self.original_charge_def = 50  # all infantry subunit has default 50 charge defence
            self.charge_skill = stat["Charge Skill"]  # for easier reference to check what charge skill this subunit has
            self.original_morale = stat["Morale"] + grade_stat["Morale Bonus"]  # morale with grade bonus
            self.original_discipline = stat["Discipline"] + grade_stat["Discipline Bonus"]  # discipline with grade bonus
            self.original_mental = stat["Mental"] + grade_stat[
                "Mental Bonus"]  # mental resistance from morale melee_dmg and mental status effect
            if self.stat_use_troop_number:
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
            self.magazine_count = {0: {0: 2, 1: 2}, 1: {0: 2, 1: 2}}  # leader gets double ammunition
            self.original_reload = (stat["Range Command"] * stat["Combat"]) + grade_stat["Reload Bonus"]
            self.original_charge = 100
            self.original_charge_def = 100
            self.charge_skill = 25  # use leading charge by default for leader
            self.original_morale = 100 + grade_stat["Morale Bonus"]  # morale with grade bonus
            self.original_discipline = 100 + grade_stat[
                "Discipline Bonus"]  # discipline with grade bonus
            self.original_mental = 50 + grade_stat[
                "Mental Bonus"]  # mental resistance from morale melee_dmg and mental status effect
            self.stamina = 10000 * grade_stat["Stamina Effect"] * (
                        start_stamina / 100)  # starting stamina with grade
            self.subunit_type = 0
            if self.original_accuracy > self.original_melee_attack:  # range leader
                self.subunit_type = 1

        self.name = stat["Name"]  # name according to the preset
        self.race = stat["Race"]  # creature race
        self.race_name = self.troop_data.race_list[stat["Race"]]["Name"]

        self.trait = {"Original": stat["Trait"] + self.troop_data.race_list[stat["Race"]]["Trait"] + \
                      self.troop_data.grade_list[self.grade]["Trait"], "Weapon": {0: {0: [], 1: []}, 1: {0: [], 1: []}}}  # trait from preset, race and grade

        self.skill_cooldown = {}
        self.grade_name = grade_stat["Name"]
        self.armour_gear = stat["Armour"]  # armour equipment
        for element in self.original_element_resistance:  # resistance from race
            self.original_element_resistance[element] = self.troop_data.race_list[stat["Race"]][element + " Resistance"]

        self.original_skill = skill.copy()  # Skill that the subunit processes
        if "" in self.original_skill:
            self.original_skill.remove("")
        self.troop_health = stat["Health"] * grade_stat["Health Effect"]  # Health of each troop
        self.original_mana = 0
        if "Mana" in stat:
            self.original_mana = stat["Mana"]  # Resource for magic skill

        # Add equipment stat
        self.primary_main_weapon = stat["Primary Main Weapon"]
        self.primary_sub_weapon = stat["Primary Sub Weapon"]
        self.secondary_main_weapon = stat["Secondary Main Weapon"]
        self.secondary_sub_weapon = stat["Secondary Sub Weapon"]
        self.melee_weapon_set = []
        self.range_weapon_set = []

        self.weapon_name = ((self.weapon_data.weapon_list[self.primary_main_weapon[0]]["Name"],
                             self.weapon_data.weapon_list[self.primary_sub_weapon[0]]["Name"]),
                            (self.weapon_data.weapon_list[self.secondary_main_weapon[0]]["Name"],
                             self.weapon_data.weapon_list[self.secondary_sub_weapon[0]]["Name"]))

        self.mount = self.troop_data.mount_list[stat["Mount"][0]]  # mount this subunit use
        self.mount_grade = self.troop_data.mount_grade_list[stat["Mount"][1]]
        self.mount_armour = self.troop_data.mount_armour_list[stat["Mount"][2]]

        self.size = self.troop_data.race_list[stat["Race"]]["Size"]

        self.original_speed = self.troop_data.race_list[stat["Race"]]["Speed"]  # use speed of race
        self.original_inflict_status = {}  # status that this subunit will inflict to enemy when melee_attack
        self.feature_mod = "Infantry"  # the terrain feature that will be used on this subunit
        self.authority = 100  # default start at 100

        # Other stats
        self.weapon_cooldown = {0: 0, 1: 0}  # subunit can attack with weapon only when cooldown reach attack speed
        self.crit_effect = 1  # critical extra modifier
        self.corner_atk = False  # check if subunit can melee_attack corner enemy or not
        self.flank_bonus = 1  # combat bonus when flanking
        self.base_auth_penalty = 0.1  # penalty to authority when bad event happen
        self.bonus_morale_dmg = 0  # extra morale melee_dmg
        self.bonus_stamina_dmg = 0  # extra stamina melee_dmg
        self.auth_penalty = 0.1  # authority penalty for certain activities/order
        self.original_hp_regen = 0  # health regeneration modifier, will not resurrect dead troop by default
        self.original_stamina_regen = 2  # stamina regeneration modifier
        self.original_morale_regen = 2  # morale regeneration modifier
        self.available_skill = []  # list of skills that subunit can currently use
        self.status_effect = {}  # current status effect
        self.skill_effect = {}  # activate skill effect
        self.base_inflict_status = {}  # status that this subunit will inflict to enemy when melee_attack

        # Set up special effect variable, first item is permanent or from trait, second item from status or skill
        self.special_effect = {status_name["Name"]: [[False, False], [False, False]]  # first item is for effect from troop/trait, second item is for weapon
                               for status_name in self.troop_data.special_effect_list.values() if status_name["Name"] != "Name"}

        if stat["Mount"][0] != 1:  # have a mount, add mount stat with its grade to subunit stat
            self.add_mount_stat()

        self.trait["Original"] += self.armour_data.armour_list[self.armour_gear[0]][
            "Trait"]  # add armour trait to subunit

        self.trait["Original"] = list(
            set([trait for trait in self.trait["Original"] if trait != 0]))  # remove empty and duplicate traits
        self.trait["Original"] = {x: self.troop_data.trait_list[x] for x in self.trait["Original"] if
                                  x in self.troop_data.trait_list}  # replace trait index with data

        self.add_original_trait()

        # Stat after applying trait and gear
        self.base_melee_attack = self.original_melee_attack
        self.base_melee_def = self.original_melee_def
        self.base_range_def = self.original_range_def

        self.base_element_resistance = self.original_element_resistance.copy()

        self.base_speed = self.original_speed
        self.base_accuracy = self.original_accuracy
        self.base_sight = self.original_sight
        self.base_reload = self.original_reload
        self.base_charge = self.original_charge
        self.base_charge_def = self.original_charge_def
        self.skill = self.original_skill.copy()
        self.troop_skill = self.original_skill.copy()
        self.troop_skill = [skill for skill in self.troop_skill if skill != 0 and
                            (type(skill) == str or (self.troop_data.skill_list[skill]["Troop Type"] == 0 or
                             self.troop_data.skill_list[skill]["Troop Type"] == self.subunit_type + 1))]  # keep matched
        self.base_mana = self.original_mana
        self.base_morale = self.original_morale
        self.base_discipline = self.original_discipline
        self.base_hp_regen = self.original_hp_regen
        self.base_stamina_regen = self.original_stamina_regen
        self.base_morale_regen = self.original_morale_regen
        self.base_heat_resistance = self.original_heat_resistance
        self.base_cold_resistance = self.original_cold_resistance
        self.base_mental = self.original_mental

        self.add_weapon_stat()
        self.action_list = {}  # get added in change_equipment

        self.swap_weapon()
        self.last_health_state = 4  # state start at full
        self.last_stamina_state = 4

        self.max_stamina = self.stamina
        self.stamina75 = self.stamina * 0.75
        self.stamina50 = self.stamina * 0.5
        self.stamina25 = self.stamina * 0.25
        self.stamina5 = self.stamina * 0.05

        self.subunit_health = self.troop_health * self.troop_number  # Total health of subunit from all troop
        self.old_subunit_health = self.subunit_health
        self.max_health = self.subunit_health  # health percentage
        self.health_list = (self.subunit_health * 0.75, self.subunit_health * 0.5, self.subunit_health * 0.25, 0)

        self.old_last_health, self.old_last_stamina = self.subunit_health, self.stamina  # save previous health and stamina in previous update
        self.max_troop = self.troop_number  # max number of troop at the start

        # v Weight calculation
        self.weight += self.armour_data.armour_list[self.armour_gear[0]]["Weight"] + self.mount_armour["Weight"]  # Weight from both melee and range weapon and armour
        if self.subunit_type == 2:  # cavalry has half weight penalty
            self.weight = self.weight / 2
        # ^ End weight cal

        self.base_speed = (self.base_speed * ((100 - self.weight) / 100)) + grade_stat["Speed Bonus"]  # finalise base speed with weight and grade bonus
        self.description = stat["Description"]  # subunit description for inspect ui
        # if self.hidden

        # vv Stat variable after receive modifier effect from various sources, used for activity and effect calculation
        self.max_morale = self.base_morale
        self.melee_attack = self.base_melee_attack
        self.melee_def = self.base_melee_def
        self.range_def = self.base_range_def
        self.element_resistance = self.base_element_resistance.copy()
        self.speed = self.base_speed
        self.accuracy = self.base_accuracy
        self.reload = self.base_reload
        self.morale = self.base_morale
        self.discipline = self.base_discipline
        self.charge = self.base_charge
        self.charge_def = self.base_charge_def
        self.auth_penalty = self.base_auth_penalty
        self.hp_regen = self.base_hp_regen
        self.stamina_regen = self.base_stamina_regen
        self.morale_regen = self.base_morale_regen
        self.heat_resistance = self.base_heat_resistance
        self.cold_resistance = self.base_cold_resistance
        self.mental = self.base_mental

        self.inflict_status = self.base_inflict_status
        self.weapon_dmg = self.original_weapon_dmg[self.equipped_weapon].copy()
        self.weapon_speed = self.original_weapon_speed[self.equipped_weapon].copy()
        self.shoot_range = self.original_range[self.equipped_weapon].copy()
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

    def update(self, weather, dt, zoom, mouse_pos, mouse_left_up):
        if self.subunit_health > 0:  # only run these when not dead
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

                parent_state, collide_list = self.combat_logic(dt, parent_state)

                if self.angle != self.new_angle:  # Rotate Function
                    self.rotate_logic(dt)

                self.move_logic(dt, parent_state, collide_list)  # Move function

                self.available_skill = []
                self.skill_check_logic()

                self.morale_logic(dt, parent_state)

                self.health_stamina_logic(dt)

                if self.state in (98, 99) and (self.base_pos[0] <= 0 or self.base_pos[0] >= 1000 or
                                               self.base_pos[1] <= 0 or self.base_pos[1] >= 1000):  # remove when unit move pass map border
                    self.state = 100  # enter dead state
                    self.battle.flee_troop_number[self.team] += self.troop_number  # add number of troop retreat from battle
                    self.troop_loss(self.troop_number)
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

        recreate_rect = False
        if self.last_zoom != zoom:  # camera zoom is changed
            self.last_zoom = zoom
            self.zoom = zoom  # save scale
            self.zoom_scale()  # update unit sprite according to new scale
            recreate_rect = True

        # animation and sprite system

        done = self.play_animation(0.15, dt, replace_image=self.use_animation_sprite)
        # Pick new animation, condition to stop animation: get interrupt,
        # low level animation got replace with more important one, finish playing, skill animation and its effect end
        if self.state != 100 and \
                ((self.interrupt_animation and "uninterruptible" not in self.current_action) or
                 (not self.current_action and self.command_action) or
                 (done and "repeat" not in self.current_action) or
                 (len(self.current_action) > 1 and type(self.current_action[-1]) == int and self.current_action[-1] not in self.skill_effect) or
                 (self.idle_action and self.idle_action != self.command_action)):
            self.reset_animation()
            self.interrupt_animation = False
            self.current_action = self.command_action  # continue next action when animation finish
            self.pick_animation()
            self.command_action = self.idle_action
        if recreate_rect:
            self.rect = self.image.get_rect(center=self.pos)


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
