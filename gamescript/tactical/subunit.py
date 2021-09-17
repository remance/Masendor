import math
import random

import numpy as np
import pygame
import pygame.freetype
from gamescript import commonscript
from gamescript.tactical import rangeattack, longscript
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pygame.transform import scale

infinity = float("inf")


def create_troop_stat(self, stat, starthp, startstamina, unitscale):
    stat_header = self.stat_list.troop_list_header
    weapon_header = self.weapon_list.weapon_list_header
    armour_header = self.armour_list.armour_list_header
    grade_header = self.stat_list.grade_list_header
    mount_header = self.stat_list.mount_list_header
    mount_grade_header = self.stat_list.mount_grade_list_header
    trait_header = self.stat_list.trait_list_header

    self.name = stat[0]  # name according to the preset
    self.grade = stat[stat_header["Grade"]]  # training level/class grade
    self.race = stat[stat_header["Race"]]  # creature race
    self.trait = stat[stat_header["Trait"]]  # trait list from preset
    self.trait = self.trait + self.stat_list.grade_list[self.grade][grade_header["Trait"]]  # add trait from grade
    skill = stat[stat_header["Skill"]]  # skill list according to the preset
    self.skill_cooldown = {}
    self.cost = stat[stat_header["Cost"]]
    gradestat = self.stat_list.grade_list[self.grade]
    self.base_attack = stat[stat_header["Melee Attack"]] + \
                       gradestat[grade_header["Melee Attack Bonus"]]  # base melee attack with grade bonus
    self.base_meleedef = stat[stat_header["Melee Defence"]] + \
                         gradestat[grade_header["Defence Bonus"]]  # base melee defence with grade bonus
    self.base_rangedef = stat[stat_header["Ranged Defence"]] + \
                         gradestat[grade_header["Defence Bonus"]]  # base range defence with grade bonus
    self.armourgear = stat[stat_header["Armour"]]  # armour equipement
    self.base_armour = self.armour_list.armour_list[self.armourgear[0]][1] \
                       * self.armour_list.quality[self.armourgear[1]]  # armour stat is calculate from based armour * quality
    self.base_accuracy = stat[stat_header["Accuracy"]] + gradestat[grade_header["Accuracy Bonus"]]
    self.base_sight = stat[stat_header["Sight"]]  # base sight range
    self.magazine_left = stat[stat_header["Ammunition"]]  # amount of ammunition
    self.base_reload = stat[stat_header["Reload"]] + gradestat[grade_header["Reload Bonus"]]
    self.base_charge = stat[stat_header["Charge"]]
    self.base_chargedef = 50  # All infantry subunit has default 50 charge defence
    self.chargeskill = stat[stat_header["Charge Skill"]]  # For easier reference to check what charge skill this subunit has
    self.skill = [self.chargeskill] + skill  # Add charge skill as first item in the list
    self.troop_health = stat[stat_header["Health"]] * gradestat[grade_header["Health Effect"]]  # Health of each troop
    self.stamina = stat[stat_header["Stamina"]] * gradestat[grade_header["Stamina Effect"]] * (startstamina / 100)  # starting stamina with grade
    self.mana = stat[stat_header["Mana"]]  # Resource for magic skill

    # vv Weapon stat
    self.primary_main_weapon = stat[stat_header["Primary Main Weapon"]]
    self.primary_sub_weapon = stat[stat_header["Primary Sub Weapon"]]
    self.secondary_main_weapon = stat[stat_header["Secondary Main Weapon"]]
    self.secondary_sub_weapon = stat[stat_header["Secondary Sub Weapon"]]

    self.melee_dmg = [0, 0]
    self.melee_penetrate = 0
    self.range_dmg = [0, 0]
    self.range_penetrate = 0
    self.meleespeed = 0
    self.magazine_size = 0
    weapon_reload = 0
    base_range = []
    arrowspeed = []

    # vvv Combine weapon stat
    self.weight = 0
    for index, weapon in enumerate([self.primary_main_weapon, self.primary_sub_weapon, self.secondary_main_weapon, self.secondary_sub_weapon]):
        if self.weapon_list.weapon_list[weapon[0]][weapon_header["Range"]] == 0:  # melee weapon if range 0
            self.melee_dmg[0] += self.weapon_list.weapon_list[weapon[0]][weapon_header["Minimum Damage"]] * \
                                 self.weapon_list.quality[weapon[1]] / (index + 1)
            self.melee_dmg[1] += self.weapon_list.weapon_list[weapon[0]][weapon_header["Maximum Damage"]] * \
                                 self.weapon_list.quality[weapon[1]] / (index + 1)

            self.melee_penetrate += self.weapon_list.weapon_list[weapon[0]][weapon_header["Armour Penetration"]] * \
                                    self.weapon_list.quality[weapon[1]] / (index + 1)
            self.meleespeed += self.weapon_list.weapon_list[weapon[0]][weapon_header["Speed"]] / (index + 1)
        else:
            self.range_dmg[0] += self.weapon_list.weapon_list[weapon[0]][weapon_header["Minimum Damage"]] * \
                                 self.weapon_list.quality[weapon[1]]
            self.range_dmg[1] += self.weapon_list.weapon_list[weapon[0]][weapon_header["Maximum Damage"]] * \
                                 self.weapon_list.quality[weapon[1]]

            self.range_penetrate += self.weapon_list.weapon_list[weapon[0]][weapon_header["Armour Penetration"]] * \
                                    self.weapon_list.quality[weapon[1]] / (index + 1)
            self.magazine_size += self.weapon_list.weapon_list[weapon[0]][
                weapon_header["Magazine"]]  # can shoot how many time before have to reload
            weapon_reload += self.weapon_list.weapon_list[weapon[0]][weapon_header["Speed"]] * (index + 1)
            base_range.append(self.weapon_list.weapon_list[weapon[0]][weapon_header["Range"]] * self.weapon_list.quality[weapon[1]])
            arrowspeed.append(self.weapon_list.weapon_list[weapon[0]][weapon_header["Travel Speed"]])  # travel speed of range attack
        self.base_meleedef += self.weapon_list.weapon_list[weapon[0]][weapon_header["Defense"]] / (index + 1)
        self.base_rangedef += self.weapon_list.weapon_list[weapon[0]][weapon_header["Defense"]] / (index + 1)
        self.skill += self.weapon_list.weapon_list[weapon[0]][weapon_header['Skill']]
        self.trait += self.weapon_list.weapon_list[weapon[0]][weapon_header['Trait']]

        self.weight += self.weapon_list.weapon_list[weapon[0]][weapon_header["Weight"]]

    self.meleespeed = int(self.meleespeed)
    self.skill = {x: self.stat_list.skill_list[x].copy() for x in self.skill if
                  x != 0 and x in self.stat_list.skill_list}  # grab skill stat into dict
    if base_range != []:
        self.base_range = np.mean(base_range)  # use average range
    else:
        self.base_range = 0
    if arrowspeed != []:
        self.arrowspeed = np.mean(arrowspeed)  # use average range
    else:
        self.arrowspeed = 0
    # ^^^ End combine
    if self.melee_penetrate < 0:
        self.melee_penetrate = 0  # melee melee_penetrate cannot be lower than 0
    if self.range_penetrate < 0:
        self.range_penetrate = 0

    # ^^ End weapon stat

    self.base_morale = stat[stat_header["Morale"]] + gradestat[grade_header["Morale Bonus"]]  # morale with grade bonus
    self.base_discipline = stat[stat_header["Discipline"]] + gradestat[grade_header["Discipline Bonus"]]  # discilpline with grade bonus
    self.mental = stat[stat_header["Mental"]] + gradestat[
        grade_header["Mental Bonus"]]  # mental resistance from morale melee_dmg and mental status effect
    self.troop_number = stat[stat_header["Troop"]] * unitscale[
        self.team - 1] * starthp / 100  # number of starting troop, team -1 to become list index
    self.base_speed = 50  # All infantry has base speed at 50
    self.subunit_type = stat[stat_header["Troop Class"]] - 1  # 0 is melee infantry and 1 is range for command buff
    self.featuremod = 1  # the starting column in unit_terrainbonus of infantry
    self.authority = 100  # default start at 100

    # vv Mount stat
    self.mount = self.stat_list.mount_list[stat[stat_header["Mount"]][0]]  # mount this subunit use
    self.mountgrade = self.stat_list.mount_grade_list[stat[stat_header["Mount"]][1]]
    self.mountarmour = self.stat_list.mount_armour_list[stat[stat_header["Mount"]][2]]
    if stat[stat_header["Mount"]][0] != 1:  # have mount, add mount stat with its grade to subunit stat
        self.base_chargedef = 25  # charge defence only 25 for cav
        self.base_speed = (self.mount[mount_header['Speed']] + self.mountgrade[mount_grade_header['Speed Bonus']])  # use mount base speed instead
        self.troop_health += (self.mount[mount_header['Health Bonus']] * self.mountgrade[mount_grade_header['Health Effect']]) + \
                             self.mountarmour[1]  # Add mount health to the troop health
        self.base_charge += (self.mount[mount_header['Charge Bonus']] +
                             self.mountgrade[mount_grade_header['Charge Bonus']])  # Add charge power of mount to troop
        self.base_morale += self.mountgrade[mount_grade_header['Morale Bonus']]
        self.base_discipline += self.mountgrade[mount_grade_header['Discipline Bonus']]
        self.stamina += self.mount[mount_header['Stamina Bonus']]
        self.trait += self.mount[mount_header['Trait']]  # Apply mount trait to subunit
        self.subunit_type = 2  # If subunit has mount, count as cav for command buff
        self.featuremod = 4  # the starting column in unit_terrainbonus of cavalry
    # ^^ End mount stat

    # v Weight calculation
    self.weight += self.armour_list.armour_list[self.armourgear[0]][armour_header["Weight"]] + \
                   self.mountarmour[2]  # Weight from both melee and range weapon and armour
    if self.subunit_type == 2:  # cavalry has half weight penalty
        self.weight = self.weight / 2
    # ^ End weight cal

    self.trait += self.armour_list.armour_list[self.armourgear[0]][armour_header["Trait"]]  # Apply armour trait to subunit
    self.base_speed = (self.base_speed * ((100 - self.weight) / 100)) + gradestat[
        grade_header["Speed Bonus"]]  # finalise base speed with weight and grade bonus
    self.size = stat[stat_header["Size"]]
    self.description = stat[-1]  # subunit description for inspect ui
    # if self.hidden

    # vv Elemental stat
    self.base_elem_melee = 0  # start with physical element for melee weapon
    self.base_elem_range = 0  # start with physical for range weapon
    self.elem_count = [0, 0, 0, 0, 0]  # Elemental threshold count in this order fire,water,air,earth,poison
    self.temp_count = 0  # Temperature threshold count
    fire_res = 0  # resistance to fire, will be combine into list
    water_res = 0  # resistance to water, will be combine into list
    air_res = 0  # resistance to air, will be combine into list
    earth_res = 0  # resistance to earth, will be combine into list
    self.magic_res = 0  # Resistance to any magic
    self.heat_res = 0  # Resistance to heat temperature
    self.cold_res = 0  # Resistance to cold temperature
    poison_res = 0  # resistance to poison, will be combine into list
    # ^^ End elemental

    self.reload_time = 0  # Unit can only refill magazine when reload_time is equal or more than reload stat
    self.crit_effect = 1  # critical extra modifier
    self.front_dmg_effect = 1  # Some skill affect only frontal combat melee_dmg
    self.side_dmg_effect = 1  # Some skill affect melee_dmg for side combat as well (AOE)
    self.corner_atk = False  # Check if subunit can attack corner enemy or not
    self.flankbonus = 1  # Combat bonus when flanking
    self.base_auth_penalty = 0.1  # penalty to authority when bad event happen
    self.bonus_morale_dmg = 0  # extra morale melee_dmg
    self.bonus_stamina_dmg = 0  # extra stamina melee_dmg
    self.auth_penalty = 0.1  # authority penalty for certain activities/order
    self.base_hpregen = 0  # hp regeneration modifier, will not resurrect dead troop by default
    self.base_staminaregen = 2  # stamina regeneration modifier
    self.moraleregen = 2  # morale regeneration modifier
    self.status_effect = {}  # list of current status effect
    self.skill_effect = {}  # list of activate skill effect
    self.base_inflictstatus = {}  # list of status that this subunit will inflict to enemy when attack
    self.specialstatus = []

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
    self.fulldef = False
    self.temp_fulldef = False
    self.backstab = False
    self.oblivious = False
    self.flanker = False
    self.unbreakable = False
    self.temp_unbraekable = False
    self.stationplace = False
    # ^^ End setup trait variable

    # vv Add trait to base stat
    self.trait = list(set([trait for trait in self.trait if trait != 0]))
    if len(self.trait) > 0:
        self.trait = {x: self.stat_list.trait_list[x] for x in self.trait if
                      x in self.stat_list.trait_list}  # Any trait not available in ruleset will be ignored
        for trait in self.trait.values():  # add trait modifier to base stat
            self.base_attack *= trait[trait_header['Melee Attack Effect']]
            self.base_meleedef *= trait[trait_header['Melee Defence Effect']]
            self.base_rangedef *= trait[trait_header['Ranged Defence Effect']]
            self.base_armour += trait[trait_header['Armour Bonus']]
            self.base_speed *= trait[trait_header['Speed Effect']]
            self.base_accuracy *= trait[trait_header['Accuracy Effect']]
            self.base_range *= trait[trait_header['Range Effect']]
            self.base_reload *= trait[trait_header['Reload Effect']]
            self.base_charge *= trait[trait_header['Charge Effect']]
            self.base_chargedef += trait[trait_header['Charge Defence Bonus']]
            self.base_hpregen += trait[trait_header['HP Regeneration Bonus']]
            self.base_staminaregen += trait[trait_header['Stamina Regeneration Bonus']]
            self.base_morale += trait[trait_header['Morale Bonus']]
            self.base_discipline += trait[trait_header['Discipline Bonus']]
            self.crit_effect += trait[trait_header['Critical Bonus']]
            fire_res += (trait[trait_header['Fire Resistance']] / 100)  # percentage, 1 mean perfect resistance, 0 mean none
            water_res += (trait[trait_header['Water Resistance']] / 100)
            air_res += (trait[trait_header['Air Resistance']] / 100)
            earth_res += (trait[trait_header['Earth Resistance']] / 100)
            self.magic_res += (trait[trait_header['Magic Resistance']] / 100)
            self.heat_res += (trait[trait_header['Heat Resistance']] / 100)
            self.cold_res += (trait[trait_header['Cold Resistance']] / 100)
            poison_res += (trait[trait_header['Poison Resistance']] / 100)
            self.mental += trait[trait_header['Mental Bonus']]
            if trait[trait_header['Enemy Status']] != [0]:
                for effect in trait[trait_header['Enemy Status']]:
                    self.base_inflictstatus[effect] = trait[trait_header['Buff Range']]
            # self.base_elem_melee =
            # self.base_elem_range =

        if 3 in self.trait:  # Varied training
            self.base_attack *= (random.randint(70, 120) / 100)
            self.base_meleedef *= (random.randint(70, 120) / 100)
            self.base_rangedef *= (random.randint(70, 120) / 100)
            self.base_speed *= (random.randint(70, 120) / 100)
            self.base_accuracy *= (random.randint(70, 120) / 100)
            self.base_reload *= (random.randint(70, 120) / 100)
            self.base_charge *= (random.randint(70, 120) / 100)
            self.base_chargedef *= (random.randint(70, 120) / 100)
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
            self.fulldef = True  # full effective defence for all side
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
            self.temp_unbraekable = True
        if 149 in self.trait:  # Impetuous
            self.base_auth_penalty += 0.5
        # ^ End change trait variable
    # ^^ End add trait to stat

    for skill in list(self.skill.keys()):  # remove skill if class mismatch
        skill_troop_cond = self.skill[skill][self.skill_trooptype]
        if skill_troop_cond == 0 or (self.subunit_type == 2 and skill_troop_cond == 2) or (self.subunit_type != 2 and skill_troop_cond != 2):
            pass
        else:
            self.skill.pop(skill)

    # self.loyalty
    self.elem_res = (fire_res, water_res, air_res, earth_res, poison_res)  # list of elemental resistance
    self.max_stamina = self.stamina
    self.stamina75 = self.stamina * 0.75
    self.stamina50 = self.stamina * 0.5
    self.stamina25 = self.stamina * 0.25
    self.stamina5 = self.stamina * 0.05
    self.unit_health = self.troop_health * self.troop_number  # Total health of subunit from all troop
    self.last_health_state = 4  # state start at full
    self.last_stamina_state = 4

    self.base_reload = weapon_reload + ((50 - self.base_reload) * weapon_reload / 100)  # final reload speed from weapon and skill

    # vv Stat variable after receive modifier effect from various sources, used for activity and effect calculation
    self.max_morale = self.base_morale
    self.attack = self.base_attack
    self.meleedef = self.base_meleedef
    self.rangedef = self.base_rangedef
    self.armour = self.base_armour
    self.speed = self.base_speed
    self.accuracy = self.base_accuracy
    self.reload = self.base_reload
    self.morale = self.base_morale
    self.discipline = self.base_discipline
    self.shootrange = self.base_range
    self.charge = self.base_charge
    self.chargedef = self.base_chargedef
    # ^^ End stat for status effect

    if self.mental < 0:  # cannot be negative
        self.mental = 0
    elif self.mental > 200:  # cannot exceed 100
        self.mental = 200
    self.mentaltext = self.mental - 100
    self.mental = (200 - self.mental) / 100  # convert to percentage

    self.max_health = self.unit_health  # health percentage
    self.health75 = self.unit_health * 0.75
    self.health50 = self.unit_health * 0.5
    self.health25 = self.unit_health * 0.25

    self.oldlasthealth, self.old_last_stamina = self.unit_health, self.stamina  # save previous health and stamina in previous update
    self.maxtroop = self.troop_number  # max number of troop at the start
    self.moralestate = self.base_morale / self.max_morale  # turn into percentage
    self.staminastate = (self.stamina * 100) / self.max_stamina  # turn into percentage
    self.staminastate_cal = self.staminastate / 100  # for using as modifer on stat

    self.corner_atk = False  # cannot attack corner enemy by default
    self.temp_fulldef = False

    self.auth_penalty = self.base_auth_penalty
    self.hpregen = self.base_hpregen
    self.staminaregen = self.base_staminaregen
    self.inflictstatus = self.base_inflictstatus
    self.elem_melee = self.base_elem_melee
    self.elem_range = self.base_elem_range


class Subunit(pygame.sprite.Sprite):
    images = []
    gamebattle = None
    gamemap = None  # base map
    gamemapfeature = None  # feature map
    gamemapheight = None  # height map
    dmgcal = longscript.dmgcal
    weapon_list = None
    armour_list = None
    stat_list = None
    rotationxy = commonscript.rotationxy
    setrotate = longscript.setrotate
    change_leader = longscript.change_leader
    maxzoom = 10  # max zoom allow
    create_troop_stat = create_troop_stat

    def __init__(self, troopid, gameid, parentunit, position, starthp, startstamina, unitscale):
        """Although subunit in code, this is referred as sub-subunit ingame"""
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.wholastselect = None
        self.leader = None  # Leader in the sub-subunit if there is one, got add in leader gamestart
        self.board_pos = None  # Used for event log position of subunit (Assigned in gamebattle subunit setup)
        self.walk = False  # currently walking
        self.run = False  # currently running
        self.frontline = False  # on front line of unit or not
        self.unit_leader = False  # contain the general or not, making it leader subunit
        self.attack_target = None
        self.melee_target = None  # current target of melee combat
        self.close_target = None  # clost target to move to in melee
        self.attacking = False  # For checking if parentunit in attacking state or not for using charge skill
        self.parentunit = parentunit  # reference to the parent battlion of this subunit

        self.enemy_front = []  # list of front collide sprite
        self.enemy_side = []  # list of side collide sprite
        self.friend_front = []  # list of friendly front collide sprite
        self.same_front = []  # list of same unit front collide sprite
        self.fullmerge = []  # list of sprite that collide and almost overlap with this sprite
        self.collide_penalty = False
        self.team = self.parentunit.team
        self.gamebattle.allsubunitlist.append(self)
        if self.team == 1:  # add sprite to team subunit group for collision
            groupcollide = self.gamebattle.team1subunit
        elif self.team == 2:
            groupcollide = self.gamebattle.team2subunit
        groupcollide.add(self)

        self.status_list = self.parentunit.status_list

        self.gameid = gameid  # ID of this
        self.troopid = int(troopid)  # ID of preset used for this subunit

        self.angle = self.parentunit.angle
        self.new_angle = self.parentunit.angle
        self.radians_angle = math.radians(360 - self.angle)  # radians for apply angle to position (allsidepos and subunit)
        self.parent_angle = self.parentunit.angle  # angle subunit will face when not moving or

        self.red_border = False  # red corner to indicate taking melee_dmg in inspect ui
        self.state = 0  # Current subunit state, similar to parentunit state
        self.timer = random.random()  # may need to use random.random()
        self.movetimer = 0  # timer for moving to front position before attacking nearest enemy
        self.charge_momentum = 1  # charging momentum to reach target before choosing nearest enemy
        self.ammo_now = 0
        self.zoom = 1
        self.lastzoom = 10
        self.skill_cond = 0
        self.brokenlimit = 0  # morale require for parentunit to stop broken state, will increase everytime broken state stop

        self.getfeature = self.gamemapfeature.getfeature
        self.getheight = self.gamemapheight.getheight

        # v Setup troop stat
        stat = self.stat_list.troop_list[self.troopid].copy()

        self.create_troop_stat(stat, starthp, startstamina, unitscale)
        self.gamebattle.start_troopnumber[self.team] += self.troop_number  # add troop number to counter how many troop join battle
        # ^ End setup stat

        # v Subunit image block
        image = self.images[0].copy()  # Subunit block blue colour for team1 for shown in inspect ui
        if self.team == 2:
            image = self.images[13].copy()  # red colour

        self.image = pygame.Surface((image.get_width() + 10, image.get_height() + 10), pygame.SRCALPHA)  # subunit sprite image
        pygame.draw.circle(self.image, self.parentunit.colour, (self.image.get_width() / 2, self.image.get_height() / 2), image.get_width() / 2)

        if self.subunit_type == 2:  # cavalry draw line on block
            pygame.draw.line(image, (0, 0, 0), (0, 0), (image.get_width(), image.get_height()), 2)
            radian = 45 * 0.0174532925  # top left
            start = (
                self.image.get_width() / 3 * math.cos(radian), self.image.get_width() / 3 * math.sin(radian))  # draw line from 45 degree in circle
            radian = 225 * 0.0174532925  # bottom right
            end = (self.image.get_width() * -math.cos(radian), self.image.get_width() * -math.sin(radian))  # drow line to 225 degree in circle
            pygame.draw.line(self.image, (0, 0, 0), start, end, 2)

        self.imageblock = image.copy()  # image shown in inspect ui as square instead of circle

        self.selectedimage = pygame.Surface((image.get_width(), image.get_height()), pygame.SRCALPHA)
        pygame.draw.circle(self.selectedimage, (255, 255, 255, 150), (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2)
        pygame.draw.circle(self.selectedimage, (0, 0, 0, 255), (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2, 1)
        self.selectedimage_original, self.selectedimage_original2 = self.selectedimage.copy(), self.selectedimage.copy()
        self.selectedimagerect = self.selectedimage.get_rect(topleft=(0, 0))
        # ^ End subunit block

        self.far_image = self.image.copy()
        pygame.draw.circle(self.far_image, (0, 0, 0), (self.far_image.get_width() / 2, self.far_image.get_height() / 2),
                           self.far_image.get_width() / 2, 4)
        self.far_selectedimage = self.selectedimage.copy()
        pygame.draw.circle(self.far_selectedimage, (0, 0, 0), (self.far_selectedimage.get_width() / 2, self.far_selectedimage.get_height() / 2),
                           self.far_selectedimage.get_width() / 2, 4)

        scalewidth = self.image.get_width() * 1 / self.maxzoom
        scaleheight = self.image.get_height() * 1 / self.maxzoom
        dim = pygame.Vector2(scalewidth, scaleheight)
        self.far_image = pygame.transform.scale(self.far_image, (int(dim[0]), int(dim[1])))
        self.far_selectedimage = pygame.transform.scale(self.far_selectedimage, (int(dim[0]), int(dim[1])))

        # v health circle image setup
        self.healthimage = self.images[1]
        self.health_image_rect = self.healthimage.get_rect(center=self.image.get_rect().center)  # for battle sprite
        self.health_imageblock_rect = self.healthimage.get_rect(center=self.imageblock.get_rect().center)  # for ui sprite
        self.image.blit(self.healthimage, self.health_image_rect)
        self.imageblock.blit(self.healthimage, self.health_imageblock_rect)
        # ^ End health circle

        # v stamina circle image setup
        self.staminaimage = self.images[6]
        self.stamina_image_rect = self.staminaimage.get_rect(center=self.image.get_rect().center)  # for battle sprite
        self.stamina_imageblock_rect = self.staminaimage.get_rect(center=self.imageblock.get_rect().center)  # for ui sprite
        self.image.blit(self.staminaimage, self.stamina_image_rect)
        self.imageblock.blit(self.staminaimage, self.stamina_imageblock_rect)
        # ^ End stamina circle

        # v weapon class icon in middle circle
        image1 = self.weapon_list.imgs[self.weapon_list.weapon_list[self.primary_main_weapon[0]][-3]]  # image on subunit sprite
        image1rect = image1.get_rect(center=self.image.get_rect().center)
        self.image.blit(image1, image1rect)

        image1rect = image1.get_rect(center=self.imageblock.get_rect().center)
        self.imageblock.blit(image1, image1rect)
        self.imageblock_original = self.imageblock.copy()

        self.corner_image_rect = self.images[11].get_rect(
            center=self.imageblock.get_rect().center)  # red corner when take melee_dmg shown in image block
        # ^ End weapon icon

        self.image_original = self.image.copy()  # original for rotate
        self.image_original2 = self.image.copy()  # original2 for saving original notclicked
        self.image_original3 = self.image.copy()  # original3 for saving original zoom level

        # v position related
        self.unitposition = (position[0] / 10, position[1] / 10)  # position in parentunit sprite
        battaliontopleft = pygame.Vector2(self.parentunit.base_pos[0] - self.parentunit.base_width_box / 2,
                                          self.parentunit.base_pos[
                                              1] - self.parentunit.base_height_box / 2)  # get topleft corner position of parentunit to calculate true pos
        self.base_pos = pygame.Vector2(battaliontopleft[0] + self.unitposition[0],
                                       battaliontopleft[1] + self.unitposition[1])  # true position of subunit in map
        self.last_pos = self.base_pos

        self.movement_queue = []
        self.combat_move_queue = []
        self.base_target = self.base_pos  # base_target to move
        self.command_target = self.base_pos  # actual base_target outside of combat
        self.pos = self.base_pos * self.zoom  # pos is for showing on screen

        self.imageheight = (image.get_height() - 1) / 20  # get real half height of circle sprite

        self.front_pos = (self.base_pos[0], (self.base_pos[1] - self.imageheight))  # generate front side position
        self.front_pos = self.rotationxy(self.base_pos, self.front_pos, self.radians_angle)  # rotate the new front side according to sprite rotation

        self.attack_pos = self.parentunit.base_attack_pos
        self.terrain, self.feature = self.getfeature(self.base_pos, self.gamemap)  # get new terrain and feature at each subunit position
        self.height = self.gamemapheight.getheight(self.base_pos)  # current terrain height
        self.front_height = self.gamemapheight.getheight(self.front_pos)  # terrain height at front position
        # ^ End position related

        self.rect = self.image.get_rect(center=self.pos)

    def zoomscale(self):
        """camera zoom change and rescale the sprite and position scale"""
        if self.zoom != 1:
            self.image_original = self.image_original3.copy()  # reset image for new scale
            scalewidth = self.image_original.get_width() * self.zoom / self.maxzoom
            scaleheight = self.image_original.get_height() * self.zoom / self.maxzoom
            dim = pygame.Vector2(scalewidth, scaleheight)
            self.image = pygame.transform.scale(self.image_original, (int(dim[0]), int(dim[1])))

            if self.parentunit.selected and self.state != 100:
                self.selectedimage_original = pygame.transform.scale(self.selectedimage_original2, (int(dim[0]), int(dim[1])))
        else:
            self.image_original = self.far_image.copy()
            self.image = self.image_original.copy()
            if self.parentunit.selected and self.state != 100:
                self.selectedimage_original = self.far_selectedimage.copy()
        self.image_original = self.image.copy()
        self.image_original2 = self.image.copy()
        self.change_pos_scale()
        self.rotate()

    def change_pos_scale(self):
        """Change position variable to new camera scale"""
        self.pos = self.base_pos * self.zoom
        self.rect = self.image.get_rect(center=self.pos)

    def useskill(self, whichskill):
        if whichskill == 0:  # charge skill need to seperate since charge power will be used only for charge skill
            skillstat = self.skill[list(self.skill)[0]].copy()  # get skill stat
            self.skill_effect[self.chargeskill] = skillstat  # add stat to skill effect
            self.skill_cooldown[self.chargeskill] = skillstat[self.skill_cd]  # add skill cooldown
        else:  # other skill
            skillstat = self.skill[whichskill].copy()  # get skill stat
            self.skill_effect[whichskill] = skillstat  # add stat to skill effect
            self.skill_cooldown[whichskill] = skillstat[self.skill_cd]  # add skill cooldown
        self.stamina -= skillstat[9]
        # self.skill_cooldown[whichskill] =

    # def receiveskill(self,whichskill):

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
                                    and self.stamina > self.skill[skill][self.skill_stamina_cost] and skill != self.chargeskill]

    def find_nearby_subunit(self):
        """Find nearby friendly squads in the same parentunit for applying buff"""
        self.nearby_subunit_list = []
        corner_subunit = []
        for rowindex, rowlist in enumerate(self.parentunit.armysubunit.tolist()):
            if self.gameid in rowlist:
                if rowlist.index(self.gameid) - 1 != -1:  # get subunit from left if not at first column
                    self.nearby_subunit_list.append(self.parentunit.spritearray[rowindex][rowlist.index(self.gameid) - 1])  # index 0
                else:  # not exist
                    self.nearby_subunit_list.append(0)  # add number 0 instead

                if rowlist.index(self.gameid) + 1 != len(rowlist):  # get subunit from right if not at last column
                    self.nearby_subunit_list.append(self.parentunit.spritearray[rowindex][rowlist.index(self.gameid) + 1])  # index 1
                else:  # not exist
                    self.nearby_subunit_list.append(0)  # add number 0 instead

                if rowindex != 0:  # get top subunit
                    self.nearby_subunit_list.append(self.parentunit.spritearray[rowindex - 1][rowlist.index(self.gameid)])  # index 2
                    if rowlist.index(self.gameid) - 1 != -1:  # get top left subunit
                        corner_subunit.append(self.parentunit.spritearray[rowindex - 1][rowlist.index(self.gameid) - 1])  # index 3
                    else:  # not exist
                        corner_subunit.append(0)  # add number 0 instead
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  # get top right
                        corner_subunit.append(self.parentunit.spritearray[rowindex - 1][rowlist.index(self.gameid) + 1])  # index 4
                    else:  # not exist
                        corner_subunit.append(0)  # add number 0 instead
                else:  # not exist
                    self.nearby_subunit_list.append(0)  # add number 0 instead

                if rowindex != len(self.parentunit.spritearray) - 1:  # get bottom subunit
                    self.nearby_subunit_list.append(self.parentunit.spritearray[rowindex + 1][rowlist.index(self.gameid)])  # index 5
                    if rowlist.index(self.gameid) - 1 != -1:  # get bottom left subunit
                        corner_subunit.append(self.parentunit.spritearray[rowindex + 1][rowlist.index(self.gameid) - 1])  # index 6
                    else:  # not exist
                        corner_subunit.append(0)  # add number 0 instead
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  # get bottom  right subunit
                        corner_subunit.append(self.parentunit.spritearray[rowindex + 1][rowlist.index(self.gameid) + 1])  # index 7
                    else:  # not exist
                        corner_subunit.append(0)  # add number 0 instead
                else:  # not exist
                    self.nearby_subunit_list.append(0)  # add number 0 instead
        self.nearby_subunit_list = self.nearby_subunit_list + corner_subunit

    def status_to_friend(self, aoe, statusid, statuslist):
        """apply status effect to nearby subunit depending on aoe stat"""
        if aoe in (2, 3):
            if aoe > 1:  # only direct nearby friendly subunit
                for subunit in self.nearby_subunit_list[0:4]:
                    if subunit != 0 and subunit.state != 100:  # only apply to exist and alive squads
                        subunit.statuseffect[statusid] = statuslist  # apply status effect
            if aoe > 2:  # all nearby including corner friendly subunit
                for subunit in self.nearby_subunit_list[4:]:
                    if subunit != 0 and subunit.state != 100:  # only apply to exist and alive squads
                        subunit.statuseffect[statusid] = statuslist  # apply status effect
        elif aoe == 4:  # apply to whole parentunit
            for subunit in self.parentunit.spritearray.flat:
                if subunit.state != 100:  # only apply to alive squads
                    subunit.status_effect[statusid] = statuslist  # apply status effect

    def threshold_count(self, elem, t1status, t2status):
        """apply elemental status effect when reach elemental threshold"""
        if elem > 50:
            self.status_effect[t1status] = self.status_list[t1status].copy()  # apply tier 1 status
            if elem > 100:
                self.status_effect[t2status] = self.status_list[t2status].copy()  # apply tier 2 status
                del self.status_effect[t1status]  # remove tier 1 status
                elem = 0  # reset elemental count
        return elem

    def find_close_target(self, subunitlist):
        """Find close enemy sub-unit to move to fight"""
        closelist = {subunit: subunit.base_pos.distance_to(self.base_pos) for subunit in subunitlist}
        closelist = dict(sorted(closelist.items(), key=lambda item: item[1]))
        maxrandom = 3
        if len(closelist) < 4:
            maxrandom = len(closelist) - 1
            if maxrandom < 0:
                maxrandom = 0
        if len(closelist) > 0:
            closetarget = list(closelist.keys())[random.randint(0, maxrandom)]
            # if close_target.base_pos.distance_to(self.base_pos) < 20: # in case can't find close target
        return closetarget

    def statusupdate(self, thisweather=None):
        """calculate stat from stamina, morale state, skill, status, terrain"""

        if self.red_border and self.parentunit.selected:  # have red border (taking melee_dmg) on inspect ui, reset image
            self.imageblock.blit(self.imageblock_original, self.corner_image_rect)
            self.red_border = False

        # v reset stat to default and apply morale, stamina, command buff to stat
        if self.max_stamina > 100:
            self.max_stamina = self.max_stamina - (self.timer * 0.05)  # Max stamina gradually decrease over time - (self.timer * 0.05)
            self.stamina75 = self.max_stamina * 0.75
            self.stamina50 = self.max_stamina * 0.5
            self.stamina25 = self.max_stamina * 0.25
            self.stamina5 = self.max_stamina * 0.05

        self.morale = self.base_morale
        self.authority = self.parentunit.authority  # parentunit total authoirty
        self.commandbuff = self.parentunit.commandbuff[
                               self.subunit_type] * 100  # command buff from gamestart leader according to this subunit subunit type
        self.discipline = self.base_discipline
        self.attack = self.base_attack
        self.meleedef = self.base_meleedef
        self.rangedef = self.base_rangedef
        self.accuracy = self.base_accuracy
        self.reload = self.base_reload
        self.chargedef = self.base_chargedef
        self.speed = self.base_speed
        self.charge = self.base_charge
        self.shootrange = self.base_range

        self.crit_effect = 1  # default critical effect
        self.front_dmg_effect = 1  # default frontal melee_dmg
        self.side_dmg_effect = 1  # default side melee_dmg

        self.corner_atk = False  # cannot attack corner enemy by default
        self.temp_fulldef = False

        self.auth_penalty = self.base_auth_penalty
        self.hpregen = self.base_hpregen
        self.staminaregen = self.base_staminaregen
        self.inflictstatus = self.base_inflictstatus
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
        weathertemperature = 0
        if thisweather is not None:
            weather = thisweather
            self.attack += weather.meleeatk_buff
            self.meleedef += weather.meleedef_buff
            self.rangedef += weather.rangedef_buff
            self.armour += weather.armour_buff
            self.speed += weather.speed_buff
            self.accuracy += weather.accuracy_buff
            self.reload += weather.reload_buff
            self.charge += weather.charge_buff
            self.chargedef += weather.chargedef_buff
            self.hpregen += weather.hpregen_buff
            self.staminaregen += weather.staminaregen_buff
            self.morale += (weather.morale_buff * self.mental)
            self.discipline += weather.discipline_buff
            if weather.elem[0] != 0:  # Weather can cause elemental effect such as wet
                self.elem_count[weather.elem[0]] += (weather.elem[1] * (100 - self.elem_res[weather.elem[0]]) / 100)
            weathertemperature = weather.temperature
        # ^ End weather

        # v Map feature modifier to stat
        map_feature_mod = self.gamemapfeature.featuremod[self.feature]
        if map_feature_mod[self.featuremod] != 1:  # speed/charge
            speedmod = map_feature_mod[self.featuremod]  # get the speed mod appropiate to subunit type
            self.speed *= speedmod
            self.charge *= speedmod

        if map_feature_mod[self.featuremod + 1] != 1:  # melee attack
            # combatmod = self.parentunit.gamemapfeature.featuremod[self.parentunit.feature][self.featuremod + 1]
            self.attack *= map_feature_mod[self.featuremod + 1]  # get the attack mod appropiate to subunit type

        if map_feature_mod[self.featuremod + 2] != 1:  # melee/charge defence
            combatmod = map_feature_mod[self.featuremod + 2]  # get the defence mod appropiate to subunit type
            self.meleedef *= combatmod
            self.chargedef *= combatmod

        self.rangedef += map_feature_mod[7]  # range defence bonus from terrain bonus
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
        # self.hidden += self.parentunit.gamemapfeature[self.parentunit.feature][6]
        tempreach = map_feature_mod[10] + weathertemperature  # temperature the subunit will change to based on current terrain feature and weather
        # ^ End map feature

        # v Apply effect from skill
        # For list of status and skill effect column index used in statusupdate see longscript.py load_game_data()
        if len(self.skill_effect) > 0:
            for status in self.skill_effect:  # apply elemental effect to melee_dmg if skill has element
                calstatus = self.skill_effect[status]
                if calstatus[self.skill_type] == 0 and calstatus[self.skill_element] != 0:  # melee elemental effect
                    self.elem_melee = calstatus[self.skill_element]
                elif calstatus[self.skill_type] == 1 and calstatus[self.skill_element] != 0:  # range elemental effect
                    self.elem_range = calstatus[self.skill_element]
                self.attack = self.attack * calstatus[self.skill_melee_attack]
                self.meleedef = self.meleedef * calstatus[self.skill_melee_defence]
                self.rangedef = self.rangedef * calstatus[self.skill_range_defence]
                self.speed = self.speed * calstatus[self.skill_speed]
                self.accuracy = self.accuracy * calstatus[self.skill_accuracy]
                self.shootrange = self.shootrange * calstatus[self.skill_range]
                self.reload = self.reload / calstatus[
                    self.skill_reload]  # different than other modifier the higher mod reduce reload time (decrease stat)
                self.charge = self.charge * calstatus[self.skill_charge]
                self.chargedef = self.chargedef + calstatus[self.skill_charge_defence]
                self.hpregen += calstatus[self.skill_hp_regen]
                self.staminaregen += calstatus[self.skill_stamina_regen]
                self.morale = self.morale + (calstatus[self.skill_morale] * self.mental)
                self.discipline = self.discipline + calstatus[self.skill_discipline]
                # self.sight += calstatus[self.skill_sight]
                # self.hidden += calstatus[self.skill_hide]
                self.crit_effect = self.crit_effect * calstatus[self.skill_critical]
                self.front_dmg_effect = self.front_dmg_effect * calstatus[self.skill_damage]
                if calstatus[self.skill_aoe] in (2, 3) and calstatus[self.skill_damage] != 100:
                    self.side_dmg_effect = self.side_dmg_effect * calstatus[self.skill_damage]
                    if calstatus[self.skill_aoe] == 3:
                        self.corner_atk = True  # if aoe 3 mean it can attack enemy on all side

                # v Apply status to friendly if there is one in skill effect
                if calstatus[self.skill_status] != [0]:
                    for effect in calstatus[self.skill_status]:
                        self.status_effect[effect] = self.status_list[effect].copy()
                        if self.status_effect[effect][2] > 1:
                            self.status_to_friend(self.status_effect[effect][2], effect, self.status_list)
                # ^ End apply status to

                self.bonus_morale_dmg += calstatus[self.skill_moraledmg]
                self.bonus_stamina_dmg += calstatus[self.skill_staminadmg]
                if calstatus[self.skill_enemy_status] != [0]:  # Apply inflict status effect to enemy from skill to inflict list
                    for effect in calstatus[self.skill_enemy_status]:
                        if effect != 0:
                            self.inflictstatus[effect] = calstatus[self.skill_aoe]
            if self.chargeskill in self.skill_effect:
                self.auth_penalty += 0.5  # higher authority penalty when attacking (retreat while attacking)
        # ^ End skill effect

        # v Apply effect and modifer from status effect
        # """special status: 0 no control, 1 hostile to all, 2 no retreat, 3 no terrain effect, 4 no attack, 5 no skill, 6 no spell, 7 no exp gain,
        # 7 immune to bad mind, 8 immune to bad body, 9 immune to all effect, 10 immortal""" Not implemented yet
        if len(self.status_effect) > 0:
            for status in self.status_effect:
                calstatus = self.status_list[status]
                self.attack = self.attack * calstatus[self.status_melee_attack]
                self.meleedef = self.meleedef * calstatus[self.status_melee_defence]
                self.rangedef = self.rangedef * calstatus[self.status_range_defence]
                self.armour = self.armour * calstatus[self.status_armour]
                self.speed = self.speed * calstatus[self.status_speed]
                self.accuracy = self.accuracy * calstatus[self.status_accuracy]
                self.reload = self.reload / calstatus[self.status_reload]
                self.charge = self.charge * calstatus[self.status_charge]
                self.chargedef += calstatus[self.status_charge_defence]
                self.hpregen += calstatus[self.status_hp_regen]
                self.staminaregen += calstatus[self.status_stamina_regen]
                self.morale = self.morale + (calstatus[self.status_morale] * self.mental)
                self.discipline += calstatus[self.status_discipline]
                # self.sight += calstatus[self.status_sight]
                # self.hidden += calstatus[self.status_hide]
                tempreach += calstatus[self.status_temperature]
                if status == 91:  # All round defence status
                    self.temp_fulldef = True
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

        self.discipline = (self.discipline * self.moralestate * self.staminastatecal) + self.parentunit.leader_social[
            self.grade + 1] + (self.authority / 10)  # use morale, stamina, leader social vs grade (+1 to skip class name) and authority
        self.attack = (self.attack * (self.moralestate + 0.1)) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff
        self.meleedef = (self.meleedef * (
                self.moralestate + 0.1)) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff
        self.rangedef = (self.rangedef * (self.moralestate + 0.1)) * self.staminastatecal + (
                self.commandbuff / 2)  # use morale, stamina and half command buff
        self.accuracy = self.accuracy * self.staminastatecal + self.commandbuff  # use stamina and command buff
        self.reload = self.reload * (2 - self.staminastatecal)  # the less stamina, the higher reload time
        self.chargedef = (self.chargedef * (
                self.moralestate + 0.1)) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff
        heightdiff = (self.height / self.front_height) ** 2  # walking down hill increase speed while walking up hill reduce speed
        self.speed = self.speed * self.staminastatecal * heightdiff  # use stamina
        self.charge = (self.charge + self.speed) * (
                self.moralestate + 0.1) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff

        fullmergelen = len(self.fullmerge) + 1
        if fullmergelen > 1:  # reduce discipline if there are overlap sub-unit
            self.discipline = self.discipline / fullmergelen

        # v Rounding up, add discipline to stat and forbid negative int stat
        disciplinecal = self.discipline / 200
        self.attack = self.attack + (self.attack * disciplinecal)
        self.meleedef = self.meleedef + (self.meleedef * disciplinecal)
        self.rangedef = self.rangedef + (self.rangedef * disciplinecal)
        # self.armour = self.armour
        self.speed = self.speed + (self.speed * disciplinecal / 2)
        # self.accuracy = self.accuracy
        # self.reload = self.reload
        self.chargedef = self.chargedef + (self.chargedef * disciplinecal)
        self.charge = self.charge + (self.charge * disciplinecal)

        if self.magazine_left == 0 and self.ammo_now == 0:
            self.shootrange = 0
        if self.attack < 0:  # seem like using if 0 is faster than max(0,)
            self.attack = 0
        if self.meleedef < 0:
            self.meleedef = 0
        if self.rangedef < 0:
            self.rangedef = 0
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
        if self.chargedef < 0:
            self.chargedef = 0
        if self.discipline < 0:
            self.discipline = 0
        # ^ End rounding up

        self.rotatespeed = self.parentunit.rotatespeed * 2  # rotate speed for subunit only use for self rotate not subunit rotate related
        if self.state in (0, 99):
            self.rotatespeed = self.speed

        # v cooldown, active and effect timer function
        self.skill_cooldown = {key: val - self.timer for key, val in self.skill_cooldown.items()}  # cooldown decrease overtime
        self.skill_cooldown = {key: val for key, val in self.skill_cooldown.items() if val > 0}  # remove cooldown if time reach 0
        for a, b in self.skill_effect.items():  # Can't use dict comprehension here since value include all other skill stat
            b[3] -= self.timer
        self.skill_effect = {key: val for key, val in self.skill_effect.items() if
                             val[3] > 0 and self.state in val[5]}  # remove effect if time reach 0 or restriction state is not met
        for a, b in self.status_effect.items():
            b[3] -= self.timer
        self.status_effect = {key: val for key, val in self.status_effect.items() if val[3] > 0}
        # ^ End timer effectrangedamage

    def find_shooting_target(self, parentstate):
        """get nearby enemy base_target from list if not targeting anything yet"""
        self.attack_pos = list(self.parentunit.near_target.values())[0]  # replace attack_pos with enemy unit pos
        self.attack_target = list(self.parentunit.near_target.keys())[0]  # replace attack_target with enemy unit id
        if self.shootrange >= self.attack_pos.distance_to(self.base_pos):
            self.state = 11
            if parentstate in (1, 3, 5):  # Walk and shoot
                self.state = 12
            elif parentstate in (2, 4, 6):  # Run and shoot
                self.state = 13

    def make_front_pos(self):
        """create new pos for front side of sprite"""
        self.front_pos = (self.base_pos[0], (self.base_pos[1] - self.imageheight))

        self.front_pos = self.rotationxy(self.base_pos, self.front_pos, self.radians_angle)

    def make_pos_range(self):
        """create range of sprite pos for pathfinding"""
        self.posrange = (range(int(max(0, self.base_pos[0] - (self.imageheight - 1))), int(min(1000, self.base_pos[0] + self.imageheight))),
                         range(int(max(0, self.base_pos[1] - (self.imageheight - 1))), int(min(1000, self.base_pos[1] + self.imageheight))))

    def gamestart(self, zoom):
        """run once when game start or subunit just get created"""
        self.zoom = zoom
        self.make_front_pos()
        self.make_pos_range()
        self.zoomscale()
        self.find_nearby_subunit()
        self.statusupdate()
        self.terrain, self.feature = self.getfeature(self.base_pos, self.gamemap)
        self.height = self.gamemapheight.getheight(self.base_pos)

    def update(self, weather, newdt, zoom, combattimer, mousepos, mouseup):
        if self.lastzoom != zoom:  # camera zoom is changed
            self.lastzoom = zoom
            self.zoomchange = True
            self.zoom = zoom  # save scale
            self.zoomscale()  # update parentunit sprite according to new scale

        if self.state != 100:  # only run these when not dead
            # v Mouse collision detection
            if self.gamebattle.gamestate == 1 or (self.gamebattle.gamestate == 2 and self.gamebattle.unit_build_slot not in self.gamebattle.battleui):
                if self.rect.collidepoint(mousepos):
                    self.gamebattle.last_mouseover = self.parentunit  # last mouse over on this parentunit
                    if mouseup and self.gamebattle.uiclick is False:
                        self.gamebattle.last_selected = self.parentunit  # become last selected parentunit
                        if self.parentunit.selected is False:
                            self.parentunit.justselected = True
                            self.parentunit.selected = True
                        self.wholastselect = self.gameid
                        self.gamebattle.clickany = True
            # ^ End mouse detect

            dt = newdt
            if dt > 0:  # only run these when game not pause
                self.timer += dt

                self.walk = False  # reset walk
                self.run = False  # reset run

                parentstate = self.parentunit.state
                if parentstate in (1, 2, 3, 4):
                    self.attacking = True
                elif self.attacking and parentstate not in (1, 2, 3, 4, 10):  # cancel charge when no longer move to melee or in combat
                    self.attacking = False
                if self.state not in (95, 97, 98, 99) and parentstate in (0, 1, 2, 3, 4, 5, 6, 95, 96, 97, 98, 99):
                    self.state = parentstate  # Enforce parentunit state to subunit when moving and breaking

                self.attack_target = self.parentunit.attack_target
                self.attack_pos = self.parentunit.base_attack_pos

                if self.timer > 1:  # Update status and skill use around every 1 second
                    self.statusupdate(weather)
                    self.available_skill = []

                    if self.skill_cond != 3:  # any skill condition behaviour beside 3 (forbid skill) will check available skill to use
                        self.check_skill_condition()

                    if self.state in (4, 13) and parentstate != 10 and self.attacking and self.parentunit.moverotate is False and \
                            self.base_pos.distance_to(self.base_target) < 50:  # charge skill only when running to melee

                        self.charge_momentum += self.timer * (self.speed / 50)
                        if self.charge_momentum >= 5:
                            self.useskill(0)  # Use charge skill
                            self.parentunit.charging = True
                            self.charge_momentum = 5

                    elif self.charge_momentum > 1:  # reset charge momentum if charge skill not active
                        self.charge_momentum -= self.timer * (self.speed / 50)
                        if self.charge_momentum <= 1:
                            self.parentunit.charging = False
                            self.charge_momentum = 1

                    skillchance = random.randint(0, 10)  # random chance to use random available skill
                    if len(self.available_skill) > 0 and skillchance >= 6:
                        self.useskill(self.available_skill[random.randint(0, len(self.available_skill) - 1)])
                    self.timer -= 1

                # if parentstate not in (96,97,98,99) and self.state != 99:
                collidelist = []
                if self.enemy_front != [] or self.enemy_side != []:  # Check if in combat or not with collision
                    collidelist = self.enemy_front + self.enemy_side
                    for subunit in collidelist:
                        if self.state not in (96, 98, 99):
                            self.state = 10
                            self.melee_target = subunit
                            if self.enemy_front == []:  # no enemy in front try rotate to enemy at side
                                # self.base_target = self.melee_target.base_pos
                                self.new_angle = self.setrotate(self.melee_target.base_pos)
                        else:  # no way to retreat, Fight to the death
                            if self.enemy_front != [] and self.enemy_side != []:  # if both front and any side got attacked
                                if 9 not in self.status_effect:
                                    self.status_effect[9] = self.status_list[9].copy()  # fight to the death status
                        if parentstate not in (10, 96, 98, 99):
                            parentstate = 10
                            self.parentunit.state = 10
                        if self.melee_target is not None:
                            self.parentunit.attack_target = self.melee_target.parentunit
                        break

                elif parentstate == 10:  # no collide enemy while parent unit in fight state
                    if self.attacking and self.parentunit.collide:
                        if self.charge_momentum == 1 and (
                                self.frontline or self.parentunit.attackmode == 2) and self.parentunit.attackmode != 1:  # attack to nearest target instead
                            if self.melee_target is None and self.parentunit.attack_target is not None:
                                self.melee_target = self.parentunit.attack_target.subunit_sprite[0]
                            if self.melee_target is not None:
                                if self.close_target is None:  # movement queue is empty regenerate new one
                                    self.close_target = self.find_close_target(self.melee_target.parentunit.subunit_sprite)  # find new close target

                                    if self.close_target is not None:  # found target to fight
                                        if self not in self.gamebattle.combatpathqueue:
                                            self.gamebattle.combatpathqueue.append(self)

                                    else:  # no target to fight move back to command pos first)
                                        self.base_target = self.attack_target.base_pos
                                        self.new_angle = self.setrotate()

                                if self.melee_target.parentunit.state != 100:
                                    if self.movetimer == 0:
                                        self.movetimer = 0.1  # recalculate again in 10 seconds if not in fight
                                        # if len(self.same_front) != 0 and len(self.enemy_front) == 0: # collide with friend try move to base_target first before enemy
                                        # self.combat_move_queue = [] # clean queue since the old one no longer without collide
                                    else:
                                        self.movetimer += dt
                                        if len(self.enemy_front) != 0 or len(self.enemy_side) != 0:  # in fight, stop timer
                                            self.movetimer = 0

                                        elif self.movetimer > 10 or len(self.combat_move_queue) == 0:  # # time up, or no path. reset path
                                            self.movetimer = 0
                                            self.close_target = None
                                            if self in self.gamebattle.combatpathqueue:
                                                self.gamebattle.combatpathqueue.remove(self)

                                        elif len(self.combat_move_queue) > 0:  # no collide move to enemy
                                            self.base_target = pygame.Vector2(self.combat_move_queue[0])
                                            self.new_angle = self.setrotate()

                                else:  # whole targeted enemy unit destroyed, reset target and state
                                    self.melee_target = None
                                    self.close_target = None
                                    if self in self.gamebattle.combatpathqueue:
                                        self.gamebattle.combatpathqueue.remove(self)

                                    self.attack_target = None
                                    self.base_target = self.command_target
                                    self.new_angle = self.setrotate()
                                    self.new_angle = self.parentunit.angle
                                    self.state = 0

                    elif self.attacking is False:  # not in fight anymore, rotate and move back to original position
                        self.melee_target = None
                        self.close_target = None
                        if self in self.gamebattle.combatpathqueue:
                            self.gamebattle.combatpathqueue.remove(self)

                        self.attack_target = None
                        self.base_target = self.command_target
                        self.new_angle = self.parentunit.angle
                        self.state = 0

                    if self.state != 10 and self.magazine_left > 0 and self.parentunit.fireatwill == 0 and (self.arcshot or self.frontline) and \
                            self.charge_momentum == 1:  # Range attack when parentunit in melee state with arcshot
                        self.state = 11
                        if self.parentunit.near_target != {} and (self.attack_target is None or self.attack_pos == 0):
                            self.find_shooting_target(parentstate)
                # ^ End melee check

                else:  # range attack
                    self.melee_target = None
                    self.close_target = None
                    if self in self.gamebattle.combatpathqueue:
                        self.gamebattle.combatpathqueue.remove(self)
                    self.attack_target = None
                    self.combat_move_queue = []

                    # v Range attack function
                    if parentstate == 11:  # Unit in range attack state
                        self.state = 0  # Default state at idle
                        if (self.magazine_left > 0 or self.ammo_now > 0) and self.attack_pos != 0 and \
                                self.shootrange >= self.attack_pos.distance_to(self.base_pos):
                            self.state = 11  # can shoot if have magazine_left and in shoot range, enter range combat state

                    elif self.magazine_left > 0 and self.parentunit.fireatwill == 0 and \
                            (self.state == 0 or (self.state not in (95, 96, 97, 98, 99) and
                                                 parentstate in (1, 2, 3, 4, 5, 6) and self.shootmove)):  # Fire at will
                        if self.parentunit.near_target != {} and self.attack_target is None:
                            self.find_shooting_target(parentstate)  # shoot nearest target

                if self.state in (11, 12, 13) and self.magazine_left > 0 and self.ammo_now == 0:  # reloading magazine_left
                    self.reload_time += dt
                    if self.reload_time >= self.reload:
                        self.ammo_now = self.magazine_size
                        self.magazine_left -= 1
                        self.reload_time = 0
                    self.stamina = self.stamina - (dt * 2)  # use stamina while reloading
                # ^ End range attack function

                # v Combat action related
                if combattimer >= 0.5:  # combat is calculated every 0.5 second in game time
                    if self.state == 10:  # if melee combat (engaging anyone on any side)
                        collidelist = [subunit for subunit in self.enemy_front]
                        for subunit in collidelist:
                            anglecheck = abs(self.angle - subunit.angle)  # calculate which side arrow hit the subunit
                            if anglecheck >= 135:  # front
                                hitside = 0
                            elif anglecheck >= 45:  # side
                                hitside = 1
                            else:  # rear
                                hitside = 2
                            self.dmgcal(subunit, 0, hitside, self.gamebattle.troop_data.status_list, combattimer)
                            self.stamina = self.stamina - (combattimer * 5)

                    elif self.state in (11, 12, 13):  # range combat
                        if type(self.attack_target) == int:  # For fire at will, which attacktarget is int
                            allunitindex = self.gamebattle.allunitindex
                            if self.attack_target in allunitindex:  # if the attack base_target still alive (if dead it would not be in index list)
                                self.attack_target = self.gamebattle.allunitlist[
                                    allunitindex.index(self.attack_target)]  # change attack_target index into sprite
                            else:  # enemy dead
                                self.attack_pos = 0  # reset attack_pos to 0
                                self.attack_target = None  # reset attack_target to 0

                                for target in list(self.parentunit.near_target.values()):  # find other nearby base_target to shoot
                                    if target in allunitindex:  # check if base_target alive
                                        self.attack_pos = target[1]
                                        self.attack_target = target[1]
                                        self.attack_target = self.gamebattle.allunitlist[allunitindex.index(self.attack_target)]
                                        break  # found new base_target break loop
                        elif self.attack_target is None:
                            self.attack_target = self.parentunit.attack_target

                        if self.ammo_now > 0 and ((self.attack_target is not None and self.attack_target.state != 100) or
                                                  (self.attack_target is None and self.attack_pos != 0)) \
                                and (self.arcshot or (self.arcshot is False and self.parentunit.shoothow != 1)):
                            # can shoot if reload finish and base_target existed and not dead. Non arcshot cannot shoot if forbidded
                            # TODO add line of sight for range attack
                            rangeattack.RangeArrow(self, self.base_pos.distance_to(self.attack_pos), self.shootrange, self.zoom)  # Shoot
                            self.ammo_now -= 1  # use 1 magazine_left in magazine
                        elif self.attack_target is not None and self.attack_target.state == 100:  # if base_target die when it about to shoot
                            self.parentunit.range_combat_check = False
                            self.parentunit.attack_target = 0  # reset range combat check and base_target
                # ^ End combat related

                if parentstate != 10:  # reset base_target every update to command base_target outside of combat
                    if self.base_target != self.command_target:
                        self.base_target = self.command_target
                        if parentstate == 0:
                            self.new_angle = self.setrotate()
                    elif self.base_pos == self.base_target and self.angle != self.parentunit.angle:  # reset angle
                        self.new_angle = self.setrotate()
                        self.new_angle = self.parentunit.angle

                # v Rotate Function
                if self.angle != self.new_angle:
                    self.rotatecal = abs(self.new_angle - self.angle)  # amount of angle left to rotate
                    self.rotatecheck = 360 - self.rotatecal  # rotate distance used for preventing angle calculation bug (pygame rotate related)
                    self.radians_angle = math.radians(360 - self.angle)  # for allside rotate
                    if self.angle < 0:  # negative angle (rotate to left side)
                        self.radians_angle = math.radians(-self.angle)

                    rotatetiny = self.rotatespeed * dt  # rotate little by little according to time
                    if self.new_angle > self.angle:  # rotate to angle more than the current one
                        if self.rotatecal > 180:  # rotate with the smallest angle direction
                            self.angle -= rotatetiny
                            self.rotatecheck -= rotatetiny
                            if self.rotatecheck <= 0:
                                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                        else:
                            self.angle += rotatetiny
                            if self.angle > self.new_angle:
                                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                    elif self.new_angle < self.angle:  # rotate to angle less than the current one
                        if self.rotatecal > 180:  # rotate with the smallest angle direction
                            self.angle += rotatetiny
                            self.rotatecheck -= rotatetiny
                            if self.rotatecheck <= 0:
                                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                        else:
                            self.angle -= rotatetiny
                            if self.angle < self.new_angle:
                                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                    self.rotate()  # rotate sprite to new angle
                    self.make_front_pos()  # generate new pos related to side
                    self.front_height = self.gamemapheight.getheight(self.front_pos)
                # ^ End rotate

                # v Move function to given base_target position
                revertmove = True  # revert move check for in case subunit still need to rotate before moving
                if parentstate == 0 or self.parentunit.revert or (self.angle != self.parentunit.angle and self.parentunit.moverotate is False):
                    revertmove = False

                if (self.base_pos != self.base_target or self.charge_momentum > 1) and \
                        (revertmove or self.angle == self.new_angle):  # cannot move if unit still need to rotate

                    nocolide_check = False  # can move if front of unit not collided
                    if (((self.parentunit.collide is False or self.frontline is False) or parentstate == 99)
                            or (parentstate == 10 and ((self.frontline or self.parentunit.attackmode == 2) and self.parentunit.attackmode != 1)
                                or self.charge_momentum > 1)):
                        nocolide_check = True

                    enemycollide_check = False  # for chance to move or charge through enemy
                    if len(collidelist) > 0:
                        enemycollide_check = True
                        if self.state in (96, 98, 99):  # escape
                            enemycollide_check = False
                            nocolide_check = True  # bypass collide
                        elif self.chargeskill in self.skill_effect and random.randint(0, 1) == 0:  # chance to charge through
                            enemycollide_check = False

                    if self.stamina > 0 and nocolide_check and enemycollide_check is False and \
                            (len(self.same_front) == 0 and len(self.friend_front) == 0 or self.state in (96, 98, 99)):
                        if self.chargeskill in self.skill_effect and self.base_pos == self.base_target and parentstate == 10:
                            new_target = self.front_pos - self.base_pos  # keep charging pass original target until momentum run out
                            self.base_target = self.base_target + new_target
                            self.command_target = self.base_target

                        move = self.base_target - self.base_pos
                        move_length = move.length()  # convert length

                        if move_length > 0:  # movement length longer than 0.1, not reach base_target yet
                            move.normalize_ip()

                            if parentstate in (1, 3, 5, 7):  # walking
                                speed = self.parentunit.walkspeed  # use walk speed
                                self.walk = True
                            elif parentstate in (10, 99):  # run with its own speed instead of uniformed run
                                speed = self.speed / 15  # use its own speed when broken
                                self.run = True
                            else:  # self.state in (2, 4, 6, 10, 96, 98, 99), running
                                speed = self.parentunit.runspeed  # use run speed
                                self.run = True
                            if self.chargeskill in self.skill_effect:  # speed gradually decrease with momentum during charge
                                speed = speed * self.charge_momentum / 8
                            if self.collide_penalty:  # reduce speed during moving through another unit
                                speed = speed / 2
                            move = move * speed * dt
                            newmove_length = move.length()
                            newpos = self.base_pos + move

                            if speed > 0 and (self.state in (98, 99) or (self.state not in (98, 99) and
                                                                         (0 < newpos[0] < 999 and 0 < newpos[1] < 999))):
                                # cannot go pass map unless in retreat state
                                if newmove_length <= move_length:  # move normally according to move speed
                                    self.base_pos = newpos
                                    self.pos = self.base_pos * self.zoom
                                    self.rect.center = list(int(v) for v in self.pos)  # list rect so the sprite gradually move to position
                                    if self.stamina != infinity:
                                        if self.walk:
                                            self.stamina = self.stamina - (dt * 2)
                                        elif self.run:
                                            self.stamina = self.stamina - (dt * 5)

                                else:  # move length pass the base_target destination, set movement to stop exactly at base_target
                                    move = self.base_target - self.base_pos  # simply change move to whatever remaining distance
                                    self.base_pos += move  # adjust base position according to movement
                                    self.pos = self.base_pos * self.zoom
                                    self.rect.center = self.pos  # no need to do list
                                if len(self.combat_move_queue) > 0 and self.base_pos.distance_to(
                                        pygame.Vector2(self.combat_move_queue[0])) < 0.1:  # reach the current queue point, remove from queue
                                    self.combat_move_queue = self.combat_move_queue[1:]

                                self.make_front_pos()
                                self.make_pos_range()

                                self.terrain, self.feature = self.getfeature(self.base_pos,
                                                                             self.gamemap)  # get new terrain and feature at each subunit position
                                self.height = self.gamemapheight.getheight(self.base_pos)  # get new height
                                self.front_height = self.gamemapheight.getheight(self.front_pos)
                                self.last_pos = self.base_pos

                                if self.unit_leader and newmove_length > 0:
                                    if self.parentunit.moverotate is False:
                                        self.parentunit.base_pos += move
                                    frontpos = (self.parentunit.base_pos[0],
                                                (self.parentunit.base_pos[1] - self.parentunit.base_height_box))  # find front position
                                    self.parentunit.front_pos = self.rotationxy(self.parentunit.base_pos, frontpos, self.parentunit.radians_angle)

                                    numberpos = (self.parentunit.base_pos[0] - self.parentunit.base_width_box,
                                                 (self.parentunit.base_pos[1] + self.parentunit.base_height_box))
                                    self.parentunit.number_pos = self.rotationxy(self.parentunit.base_pos, numberpos, self.parentunit.radians_angle)
                                    self.parentunit.truenumber_pos = self.parentunit.number_pos * (
                                            11 - self.parentunit.zoom)  # find new position for troop number text

                        else:  # Stopping subunit when reach base_target
                            self.state = 0  # idle
                    # ^ End move function

                # v Morale check
                if self.max_morale != infinity:
                    if self.base_morale < self.max_morale:
                        if self.morale <= 10:  # Enter retreat state when morale reach 0
                            if self.state not in (98, 99):
                                self.state = 98  # retreat state
                                maxrandom = 1 - (self.mental / 100)
                                if maxrandom < 0:
                                    maxrandom = 0
                                self.moraleregen -= random.uniform(0, maxrandom)  # morale regen slower per broken state
                                if self.moraleregen < 0:  # begin checking broken state
                                    self.state = 99  # Broken state
                                    self.change_leader("broken")

                                    cornerlist = [[0, self.base_pos[1]], [1000, self.base_pos[1]], [self.base_pos[0], 0], [self.base_pos[0], 1000]]
                                    whichcorner = [self.base_pos.distance_to(cornerlist[0]), self.base_pos.distance_to(cornerlist[1]),
                                                   self.base_pos.distance_to(cornerlist[2]),
                                                   self.base_pos.distance_to(cornerlist[3])]  # find closest map corner to run to
                                    foundcorner = whichcorner.index(min(whichcorner))
                                    self.base_target = pygame.Vector2(cornerlist[foundcorner])
                                    self.command_target = self.base_target
                                    self.new_angle = self.setrotate()

                                for subunit in self.parentunit.subunit_sprite:
                                    subunit.base_morale -= (
                                            15 * subunit.mental)  # reduce morale of other subunit, creating panic when seeing friend panic and may cause mass panic
                            if self.morale < 0:
                                self.morale = 0  # morale cannot be lower than 0

                        if self.state not in (95, 99) and parentstate not in (10, 99):  # If not missing gamestart leader can replenish morale
                            self.base_morale += (dt * self.staminastatecal * self.moraleregen)  # Morale replenish based on stamina

                        if self.base_morale < 0:  # morale cannot be negative
                            self.base_morale = 0

                    elif self.base_morale > self.max_morale:
                        self.base_morale -= dt  # gradually reduce morale that exceed the starting max amount

                    if self.state == 95:  # disobey state, morale gradually decrease until recover
                        self.base_morale -= dt * self.mental

                    elif self.state == 98:
                        if parentstate not in (98, 99):
                            self.unit_health -= (dt * 100)  # Unit begin to desert if retreating but parentunit not retreat/broken
                            if self.moralestate > 0.2:
                                self.state = 0  # Reset state to 0 when exit retreat state
                # ^ End morale check

                # v Hp and stamina regen
                if self.stamina != infinity:
                    if self.stamina < self.max_stamina:
                        if self.stamina <= 0:  # Collapse and cannot act
                            self.stamina = 0
                            self.status_effect[105] = self.status_list[105].copy()  # receive collapse status
                        self.stamina = self.stamina + (dt * self.staminaregen)  # regen
                    else:  # stamina cannot exceed the max stamina
                        self.stamina = self.max_stamina
                if self.unit_health != infinity:
                    if self.hpregen > 0 and self.unit_health % self.troop_health != 0:  # hp regen cannot ressurect troop only heal to max hp
                        alivehp = self.troop_number * self.troop_health  # max hp possible for the number of alive subunit
                        self.unit_health += self.hpregen * dt  # regen hp back based on time and regen stat
                        if self.unit_health > alivehp:
                            self.unit_health = alivehp  # Cannot exceed health of alive subunit (exceed mean resurrection)
                    elif self.hpregen < 0:  # negative regen can kill
                        self.unit_health += self.hpregen * dt  # use the same as positive regen (negative regen number * dt will reduce hp)
                        remain = self.unit_health / self.troop_health
                        if remain.is_integer() is False:  # always round up if there is decimal number
                            remain = int(remain) + 1
                        else:
                            remain = int(remain)
                        wound = random.randint(0, (self.troop_number - remain))  # chance to be wounded instead of dead
                        self.gamebattle.death_troopnumber[self.team] += self.troop_number - remain - wound
                        self.gamebattle.wound_troopnumber[self.team] += wound
                        self.troop_number = remain  # Recal number of troop again in case some die from negative regen

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
                        self.gamebattle.death_troopnumber[self.team] += self.troop_number - remain - wound
                        if self.state in (98, 99) and len(self.enemy_front) + len(
                                self.enemy_side) > 0:  # fleeing or broken got captured instead of wound
                            self.gamebattle.capture_troopnumber[self.team] += wound
                        else:
                            self.gamebattle.wound_troopnumber[self.team] += wound
                        self.troop_number = remain  # Recal number of troop again in case some die from negative regen

                        # v Health bar
                        healthlist = (self.health75, self.health50, self.health25, 0)
                        for index, health in enumerate(healthlist):
                            if self.unit_health > health:
                                if self.last_health_state != abs(4 - index):
                                    self.image_original3.blit(self.images[index + 1], self.health_image_rect)
                                    self.imageblock_original.blit(self.images[index + 1], self.health_imageblock_rect)
                                    self.imageblock.blit(self.imageblock_original, self.corner_image_rect)
                                    self.last_health_state = abs(4 - index)
                                    self.zoomscale()
                                break
                        # ^ End Health bar

                        self.oldlasthealth = self.unit_health

                # v Stamina bar
                if self.old_last_stamina != self.stamina:
                    staminalist = (self.stamina75, self.stamina50, self.stamina25, self.stamina5, -1)
                    for index, stamina in enumerate(staminalist):
                        if self.stamina >= stamina:
                            if self.last_stamina_state != abs(4 - index):
                                # if index != 3:
                                self.image_original3.blit(self.images[index + 6], self.stamina_image_rect)
                                self.zoomscale()
                                self.imageblock_original.blit(self.images[index + 6], self.stamina_imageblock_rect)
                                self.imageblock.blit(self.imageblock_original, self.corner_image_rect)
                                self.last_stamina_state = abs(4 - index)
                            break

                    self.old_last_stamina = self.stamina
                # ^ End stamina bar

            if self.state in (98, 99) and (self.base_pos[0] <= 0 or self.base_pos[0] >= 999 or
                                           self.base_pos[1] <= 0 or self.base_pos[1] >= 999):  # remove when unit move pass map border
                self.state = 100  # enter dead state
                self.gamebattle.flee_troopnumber[self.team] += self.troop_number  # add number of troop retreat from battle
                self.troop_number = 0
                self.gamebattle.battlecamera.remove(self)

            if self.troop_number <= 0:  # enter dead state
                self.state = 100  # enter dead state
                self.image_original3.blit(self.images[5], self.health_image_rect)  # blit white hp bar
                self.imageblock_original.blit(self.images[5], self.health_imageblock_rect)
                self.zoomscale()
                self.last_health_state = 0
                self.skill_cooldown = {}  # remove all cooldown
                self.skill_effect = {}  # remove all skill effects

                self.imageblock.blit(self.imageblock_original, self.corner_image_rect)
                self.red_border = True  # to prevent red border appear when dead

                self.parentunit.deadchange = True

                if self in self.gamebattle.battlecamera:
                    self.gamebattle.battlecamera.change_layer(sprite=self, new_layer=1)
                self.gamebattle.allsubunitlist.remove(self)
                self.parentunit.subunit_sprite.remove(self)

                for subunit in self.parentunit.armysubunit.flat:  # remove from index array
                    if subunit == self.gameid:
                        self.parentunit.armysubunit = np.where(self.parentunit.armysubunit == self.gameid, 0, self.parentunit.armysubunit)
                        break

                self.change_leader("die")

                self.gamebattle.eventlog.addlog([0, str(self.board_pos) + " " + str(self.name)
                                                 + " in " + self.parentunit.leader[0].name
                                                 + "'s parentunit is destroyed"], [3])  # add log to say this subunit is destroyed in subunit tab

            self.enemy_front = []  # reset collide
            self.enemy_side = []
            self.friend_front = []
            self.same_front = []
            self.fullmerge = []
            self.collide_penalty = False

    def rotate(self):
        """rotate subunit image may use when subunit can change direction independently from parentunit"""
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        if self.parentunit.selected and self.state != 100:
            self.selectedimage = pygame.transform.rotate(self.selectedimage_original, self.angle)
            self.image.blit(self.selectedimage, self.selectedimagerect)
        self.rect = self.image.get_rect(center=self.pos)

    def combat_pathfind(self):
        # v Pathfinding
        self.combat_move_queue = []
        movearray = self.gamebattle.subunitposarray.copy()
        intbasetarget = (int(self.close_target.base_pos[0]), int(self.close_target.base_pos[1]))
        for y in self.close_target.posrange[0]:
            for x in self.close_target.posrange[1]:
                movearray[x][y] = 100  # reset path in the enemy sprite position

        intbasepos = (int(self.base_pos[0]), int(self.base_pos[1]))
        for y in self.posrange[0]:
            for x in self.posrange[1]:
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
        # print(self.base_pos, self.close_target.base_pos, self.gameid, startpoint, intbasepos[0] - startpoint[0], intbasepos[1] - startpoint[1])
        # ^ End path finding

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.parentunit
            del self.leader
            del self.wholastselect
            del self.attack_target
            del self.melee_target
            del self.close_target
            if self in self.gamebattle.combatpathqueue:
                self.gamebattle.combatpathqueue.remove(self)
