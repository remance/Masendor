import math
import random
import time

import numpy as np
import pygame
import pygame.freetype
from PIL import Image, ImageFilter
from gamescript import commonscript
from gamescript.arcade import rangeattack, longscript
from pygame.transform import scale

infinity = float("inf")

rotationxy = commonscript.rotationxy

def create_troop_stat(self, stat, starthp, troop_type):
    if troop_type == "troop":
        stat_header = self.stat_list.troop_list_header
    elif troop_type == "leader":
        stat_header = self.stat_list.leader_list_header

    weapon_header = self.weapon_list.weapon_list_header
    armour_header = self.armour_list.armour_list_header
    grade_header = self.stat_list.grade_list_header
    mount_header = self.stat_list.mount_list_header
    mount_grade_header = self.stat_list.mount_grade_list_header
    trait_header = self.stat_list.trait_list_header

    self.name = stat[0]  # name according to the preset
    skill = stat[stat_header["Skill"]]  # skill list according to the preset
    self.troop_skill = {x: self.stat_list.skill_list[x].copy() for x in skill if
                        x != 0 and x in self.stat_list.skill_list}  # grab skill stat into dict
    self.skill = self.troop_skill  # saving troop skill for when swap weapon
    self.base_trait = stat[stat_header["Trait"]]  # trait list from preset
    self.troop_health = stat[stat_header["Health"]]

    self.armourgear = stat[stat_header["Armour"]]  # armour equipement
    self.prime_armour = self.armour_list.armour_list[self.armourgear[0]][1] \
                        * self.armour_list.quality[self.armourgear[1]]  # armour stat is calculate from based armour * quality
    self.skill_cooldown = {}

    self.prime_speed = 50  # All infantry has prime speed at 50
    self.featuremod = 1  # the starting column in unit_terrainbonus of infantry
    self.authority = self.leader.authority  # default start at 100

    # vv Mount stat
    self.subunit_type = 1
    self.mount = self.stat_list.mount_list[stat[stat_header["Mount"]][0]]  # mount this subunit use
    self.mountgrade = self.stat_list.mount_grade_list[stat[stat_header["Mount"]][1]]
    self.mountarmour = self.stat_list.mount_armour_list[stat[stat_header["Mount"]][2]]
    self.prime_chargedef = 50  # All infantry subunit has default 50 charge defence
    if stat[stat_header["Mount"]][0] != 1:  # have mount, add mount stat with its grade to subunit stat
        self.prime_chargedef = 25  # charge defence only 25 for cav
        self.prime_speed = (self.mount[mount_header['Speed']] + self.mountgrade[mount_grade_header['Speed Bonus']])  # use mount prime speed instead
        self.base_trait = self.base_trait + self.mount[mount_header['Trait']]  # Apply mount trait to subunit
        self.subunit_type = 2  # If subunit has mount, count as cav for command buff
        self.featuremod = 4  # the starting column in unit_terrainbonus of cavalry
    # ^^ End mount stat

    if self.leader is False:  # normal troop only
        self.grade = stat[stat_header["Grade"]]  # training level/class grade
        self.race = stat[stat_header["Race"]]  # creature race
        self.base_trait = self.base_trait + self.stat_list.grade_list[self.grade][grade_header["Trait"]]  # add trait from grade
        self.cost = stat[stat_header["Cost"]]
        gradestat = self.stat_list.grade_list[self.grade]
        self.prime_attack = stat[stat_header["Melee Attack"]] + \
                            gradestat[grade_header["Melee Attack Bonus"]]  # prime melee attack with grade bonus
        self.prime_meleedef = stat[stat_header["Melee Defence"]] + \
                              gradestat[grade_header["Defence Bonus"]]  # prime melee defence with grade bonus
        self.prime_rangedef = stat[stat_header["Ranged Defence"]] + \
                              gradestat[grade_header["Defence Bonus"]]  # prime range defence with grade bonus
        self.prime_accuracy = stat[stat_header["Accuracy"]] + gradestat[grade_header["Accuracy Bonus"]]
        self.base_sight = stat[stat_header["Sight"]]  # prime sight range
        self.magazine_left = stat[stat_header["Ammunition"]]  # amount of ammunition
        self.prime_reload = stat[stat_header["Reload"]] + gradestat[grade_header["Reload Bonus"]]
        self.prime_charge = stat[stat_header["Charge"]]
        self.troop_health = self.troop_health * gradestat[grade_header["Health Effect"]]  # Health of each troop
        self.prime_morale = stat[stat_header["Morale"]] + gradestat[grade_header["Morale Bonus"]]  # morale with grade bonus
        self.prime_discipline = stat[stat_header["Discipline"]] + gradestat[grade_header["Discipline Bonus"]]  # discilpline with grade bonus
        self.prime_mental = stat[stat_header["Mental"]] + gradestat[
            grade_header["Mental Bonus"]]  # mental resistance from morale melee_dmg and mental status effect

        if self.subunit_type != 2:
            self.subunit_type = stat[stat_header["Troop Class"]] - 1  # 0 is melee infantry and 1 is range for command buff

    else:  # leader subunit only
        self.base_sight = 50
        commandstat = self.leader.meleecommand
        if self.subunit_type == 2:
            commandstat = self.leader.cavcommand
        self.prime_attack = stat[stat_header["Combat"]] * commandstat  # prime melee attack with command bonus
        self.prime_meleedef = stat[stat_header["Melee Defence"]] * commandstat  # prime melee defence with command bonus
        self.prime_rangedef = stat[stat_header["Ranged Defence"]] * commandstat  # prime range defence with command bonus
        self.prime_charge = stat[stat_header["Combat"]] * commandstat
        self.prime_accuracy = stat[stat_header["Combat"]] * self.leader.rangecommand
        self.prime_reload = stat[stat_header["Combat"]] * self.leader.rangecommand

        self.prime_morale = 100
        self.prime_discipline = 100
        self.prime_mental = 100

    if stat[stat_header["Mount"]][0] != 1:  # have mount, add mount stat with its grade to subunit stat
        self.troop_health += (self.mount[mount_header['Health Bonus']] * self.mountgrade[mount_grade_header['Health Effect']]) + \
                             self.mountarmour[1]  # Add mount health to the troop health
        self.prime_charge += (self.mount[mount_header['Charge Bonus']] +
                              self.mountgrade[mount_grade_header['Charge Bonus']])  # Add charge power of mount to troop
        self.prime_morale += self.mountgrade[mount_grade_header['Morale Bonus']]
        self.prime_discipline += self.mountgrade[mount_grade_header['Discipline Bonus']]

    self.size = stat[stat_header["Size"]]

    self.description = stat[-1]  # subunit description for inspect ui
    # if self.hidden

    self.prime_crit_effect = 1  # critical extra modifier

    # vv Elemental stat
    self.prime_elem_main = 0  # start with physical element for melee weapon
    self.prime_elem_sub = 0  # start with physical for range weapon
    self.elem_count = [0, 0, 0, 0, 0]  # Elemental threshold count in this order fire,water,air,earth,poison
    self.temp_count = 0  # Temperature threshold count
    fire_res = 0  # resistance to fire, will be combine into list
    water_res = 0  # resistance to water, will be combine into list
    air_res = 0  # resistance to air, will be combine into list
    earth_res = 0  # resistance to earth, will be combine into list
    self.base_magic_res = 0  # Resistance to any magic
    self.base_heat_res = 0  # Resistance to heat temperature
    self.base_cold_res = 0  # Resistance to cold temperature
    poison_res = 0  # resistance to poison, will be combine into list
    self.base_elem_res = [fire_res, water_res, air_res, earth_res, poison_res]  # list of elemental resistance
    # ^^ End elemental

    self.front_dmg_effect = 1  # Some skill affect only frontal combat melee_dmg
    self.side_dmg_effect = 1  # Some skill affect melee_dmg for side combat as well (AOE)
    self.corner_atk = False  # Check if subunit can attack corner enemy or not
    self.flankbonus = 1  # Combat bonus when flanking
    self.base_auth_penalty = 0.1  # penalty to authority when bad event happen
    self.bonus_morale_dmg = 0  # extra morale melee_dmg
    self.auth_penalty = 0.1  # authority penalty for certain activities/order
    self.base_hpregen = 0  # hp regeneration modifier, will not resurrect dead troop by default
    self.moraleregen = 2  # morale regeneration modifier
    self.status_effect = {}  # list of current status effect
    self.skill_effect = {}  # list of activate skill effect
    self.prime_inflictstatus = {}  # list of status that this subunit will inflict to enemy when attack
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

    if len(self.base_trait) > 0:
        self.base_trait = {x: self.stat_list.trait_list[x] for x in self.trait if
                           x in self.stat_list.trait_list}  # Any trait not available in ruleset will be ignored
        for trait in self.base_trait.values():  # add trait modifier to prime stat
            self.prime_attack *= trait[trait_header['Melee Attack Effect']]
            self.prime_meleedef *= trait[trait_header['Melee Defence Effect']]
            self.prime_rangedef *= trait[trait_header['Ranged Defence Effect']]
            self.prime_armour += trait[trait_header['Armour Bonus']]
            self.prime_speed *= trait[trait_header['Speed Effect']]
            self.prime_accuracy *= trait[trait_header['Accuracy Effect']]
            self.prime_range *= trait[trait_header['Range Effect']]
            self.prime_reload *= trait[trait_header['Reload Effect']]
            self.prime_charge *= trait[trait_header['Charge Effect']]
            self.prime_chargedef += trait[trait_header['Charge Defence Bonus']]
            self.prime_hpregen += trait[trait_header['HP Regeneration Bonus']]
            self.prime_morale += trait[trait_header['Morale Bonus']]
            self.prime_crit_effect += trait[trait_header['Critical Bonus']]
            self.prime_discipline += trait[trait_header['Discipline Bonus']]
            self.elem_res[0] += (trait[trait_header['Fire Resistance']] / 100)  # percentage, 1 mean perfect resistance, 0 mean none
            self.elem_res[1] += (trait[trait_header['Water Resistance']] / 100)
            self.elem_res[2] += (trait[trait_header['Air Resistance']] / 100)
            self.elem_res[3] += (trait[trait_header['Earth Resistance']] / 100)
            self.magic_res += (trait[trait_header['Magic Resistance']] / 100)
            self.heat_res += (trait[trait_header['Heat Resistance']] / 100)
            self.cold_res += (trait[trait_header['Cold Resistance']] / 100)
            self.elem_res[4] += (trait[trait_header['Poison Resistance']] / 100)
            self.prime_mental += trait[trait_header['Mental Bonus']]
            if trait[trait_header['Enemy Status']] != [0]:
                for effect in trait[trait_header['Enemy Status']]:
                    self.prime_inflictstatus[effect] = trait[trait_header['Buff Range']]
            if trait[trait_header['Element']] != 0:  # attack elemental effect
                self.prime_elem_main = trait[trait_header['Element']]
                self.prime_elem_sub = trait[trait_header['Element']]

        if 3 in self.trait:  # Varied training
            self.prime_attack *= (random.randint(70, 120) / 100)
            self.prime_meleedef *= (random.randint(70, 120) / 100)
            self.prime_rangedef *= (random.randint(70, 120) / 100)
            self.prime_speed *= (random.randint(70, 120) / 100)
            self.prime_accuracy *= (random.randint(70, 120) / 100)
            self.prime_reload *= (random.randint(70, 120) / 100)
            self.prime_charge *= (random.randint(70, 120) / 100)
            self.prime_chargedef *= (random.randint(70, 120) / 100)
            self.prime_morale += random.randint(-15, 10)
            self.prime_discipline += random.randint(-20, 0)
            self.prime_mental += random.randint(-20, 10)

    # vv Weapon stat
    self.primary_weapon = [stat[stat_header["Primary Main Weapon"]], stat[stat_header["Secondary Main Weapon"]]]
    self.secondary_weapon = [stat[stat_header["Primary Sub Weapon"]], stat[stat_header["Secondary Sub Weapon"]]]
    self.melee_weapon = []
    self.range_weapon = []
    if self.weapon_list.weapon_list[self.primary_weapon[0]][weapon_header["Range"]] > 0:  # ranged weapon if range more than 0
        self.range_weapon += self.primary_weapon
    else:
        self.melee_weapon += self.primary_weapon

    if self.weapon_list.weapon_list[self.secondary_weapon[0]][weapon_header["Range"]] > 0:  # ranged weapon if range more than 0
        self.range_weapon += self.secondary_weapon
    else:
        self.melee_weapon += self.secondary_weapon

    if self.weapon_list.weapon_list[self.secondary_main_weapon[0]][weapon_header["Range"]] > 0:  # ranged weapon if range more than 0
        self.range_weapon += self.secondary_main_weapon

    self.prime_trait = list(set([trait for trait in self.trait if trait != 0]))
    self.swap_weapon(self.primary_weapon)
    # ^^ End weapon stat

    # v Weight calculation
    self.weight = self.weapon_list.weapon_list[self.primary_weapon[0][0]][weapon_header["Weight"]] + \
                  self.weapon_list.weapon_list[self.primary_weapon[1][0]][weapon_header["Weight"]] + \
                  self.weapon_list.weapon_list[self.secondary_weapon[0][0]][weapon_header["Weight"]] + \
                  self.weapon_list.weapon_list[self.secondary_weapon[1][0]][weapon_header["Weight"]] + \
                  self.armour_list.armour_list[self.armourgear[0]][armour_header["Weight"]] + \
                  self.mountarmour[2]  # Weight from both melee and range weapon and armour
    if self.subunit_type == 2:  # cavalry has half weight penalty
        self.weight = self.weight / 2
    # ^ End weight cal

    self.prime_speed = (self.base_speed * ((100 - self.weight) / 100)) + gradestat[
        grade_header["Speed Bonus"]]  # finalise base speed with weight and grade bonus

    # self.loyalty
    self.last_health_state = 4  # state start at full

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

    self.troop_health = self.troop_health * starthp / 100
    self.max_health = self.troop_health  # health percentage

    self.oldlasthealth = self.troop_health  # save previous health in previous update
    self.moralestate = self.base_morale / self.max_morale  # turn into percentage

    self.corner_atk = False  # cannot attack corner enemy by default
    self.temp_fulldef = False

    self.auth_penalty = self.base_auth_penalty
    self.hpregen = self.base_hpregen
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

    setrotate = longscript.setrotate
    create_troop_stat = create_troop_stat
    zoom = 4

    def __init__(self, troopid, gameid, parentunit, position, starthp):
        """Although subunit in code, this is referred as sub-subunit ingame"""
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.wholastselect = None
        self.leader = False
        self.walk = False  # currently walking
        self.run = False  # currently running
        self.frontline = False  # on front line of unit or not
        self.unit_leader = False  # contain the general or not, making it leader subunit
        self.attack_target = None
        self.melee_target = None  # current target of melee combat
        self.close_target = None  # clost target to move to in melee
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
        self.troopid = troopid
        troop_type = "troop"
        if self.troopid == "h":  # leader subunit
            troop_type = "leader"
            self.troopid = self.parentunit.leader.gameid
            self.leader = self.parentunit.leader

        self.angle = self.parentunit.angle
        self.new_angle = self.parentunit.angle
        self.radians_angle = math.radians(360 - self.angle)  # radians for apply angle to position (allsidepos and subunit)
        self.parent_angle = self.parentunit.angle  # angle subunit will face when not moving or

        self.state = 0  # Current subunit state, similar to parentunit state
        self.timer = random.random()  # may need to use random.random()
        self.movetimer = 0  # timer for moving to front position before attacking nearest enemy
        self.charge_momentum = 1  # charging momentum to reach target before choosing nearest enemy
        self.ammo_now = 0
        self.reload_time = 0  # Unit can only refill magazine when reload_time is equal or more than reload stat
        self.current_animation = "idle"

        self.getfeature = self.gamemapfeature.getfeature
        self.getheight = self.gamemapheight.getheight

        # v Setup troop stat
        stat = self.stat_list.leader_list[self.troopid].copy()

        self.create_troop_stat(stat, starthp, troop_type)
        self.gamebattle.start_troopnumber[self.team] += 1  # add troop number to counter how many troop join battle
        # ^ End setup stat

        # v Subunit sprite
        image = self.images[0].copy()  # Subunit block blue colour for team1 for shown in inspect ui
        if self.team == 2:
            image = self.images[13].copy()  # red colour

        self.image = pygame.Surface((image.get_width() + 10, image.get_height() + 10), pygame.SRCALPHA)  # subunit sprite image
        pygame.draw.circle(self.image, self.parentunit.colour, (self.image.get_width() / 2, self.image.get_height() / 2), image.get_width() / 2)
        # ^ End subunit sprite

        scalewidth = self.image.get_width()
        scaleheight = self.image.get_height()
        dim = pygame.Vector2(scalewidth, scaleheight)
        self.far_image = pygame.transform.scale(self.far_image, (int(dim[0]), int(dim[1])))
        self.far_selectedimage = pygame.transform.scale(self.far_selectedimage, (int(dim[0]), int(dim[1])))

        self.sprite_size = self.size * 55  # default size of generic body sprite for collision calculation TODO grab size from race
        if troop_type == "leader":  # check custom sprite size
            data = pygame.image.tostring(self.image, "RGBa")  # convert image to string data for filtering effect
            img = Image.frombytes("RGBa", (100, 100), data)  # use PIL to get image data
            image_data = np.asarray(img)
            image_data_bw = image_data[:,:,3]
            non_empty_columns = np.where(image_data_bw.max(axis=0) > 0)[0]
            non_empty_rows = np.where(image_data_bw.max(axis=1) > 0)[0]
            cropBox = (min(non_empty_rows), max(non_empty_rows),
                       min(non_empty_columns), max(non_empty_columns))
            image_data_new = image_data[cropBox[0]:cropBox[
                                                       1] + 1, cropBox[2]:cropBox[3] + 1, :]
            img = Image.fromarray(image_data_new)
            img = img.tobytes()
            img = pygame.image.fromstring(img, (1000, 1000), "RGBa")  # convert image back to a pygame surface
            self.sprite_size = int(img.get_width() * img.get_height() / 2)  # size of unique leader body sprite
            del img

        self.image_original = self.image.copy()  # original for rotate

        # v position related
        self.unitposition = (position[0] / 10, position[1] / 10)  # position in parentunit sprite
        battaliontopleft = pygame.Vector2(self.parentunit.base_pos[0] - self.parentunit.base_width_box / 2,
                                          self.parentunit.base_pos[
                                              1] - self.parentunit.base_height_box / 2)  # get topleft corner position of parentunit to calculate true pos
        self.base_pos = pygame.Vector2(battaliontopleft[0] + self.unitposition[0],
                                       battaliontopleft[1] + self.unitposition[1])  # true position of subunit in map
        self.last_pos = self.base_pos
        self.pos = self.base_pos * self.zoom  # pos is for showing on screen

        self.skill_queue = []
        self.base_target = self.base_pos  # base_target to move
        self.command_target = self.base_pos  # actual base_target outside of combat

        self.imageheight = (image.get_height() - 1) / 20  # get real half height of circle sprite

        self.front_pos = (self.base_pos[0], (self.base_pos[1] - self.imageheight))  # generate front side position
        self.front_pos = rotationxy(self.base_pos, self.front_pos, self.radians_angle)  # rotate the new front side according to sprite rotation

        self.attack_pos = self.parentunit.base_attack_pos
        self.terrain, self.feature = self.getfeature(self.base_pos, self.gamemap)  # get new terrain and feature at each subunit position
        self.height = self.gamemapheight.getheight(self.base_pos)  # current terrain height
        self.front_height = self.gamemapheight.getheight(self.front_pos)  # terrain height at front position
        # ^ End position related

        self.rect = self.image.get_rect(center=self.pos)

    def useskill(self, whichskill):
        skill = self.skill[whichskill].copy()  # get skill stat
        if skill not in self.skill_cooldown.keys() and \
                self.state in self.skill[skill][self.skill_condition] and \
                self.discipline >= self.skill[skill][self.skill_discipline_req] and \
                self.stamina > self.skill[skill][self.skill_stamina_cost]:
            self.skill_effect[whichskill] = skill  # add stat to skill effect
            self.skill_cooldown[whichskill] = skill[self.skill_cd]  # add skill cooldown
        # animation_queue

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
        """calculate stat morale state, skill, status, terrain"""

        if self.red_border and self.parentunit.selected:  # have red border (taking melee_dmg) on inspect ui, reset image
            self.imageblock.blit(self.imageblock_original, self.corner_image_rect)
            self.red_border = False

        # v reset stat to default

        self.morale = self.base_morale
        self.authority = self.parentunit.authority  # parentunit total authoirty
        self.discipline = self.base_discipline
        self.commandbuff = 1
        if self.leader is False:  # command buff from leader according to this subunit subunit type
            self.commandbuff = self.parentunit.commandbuff[
                                   self.subunit_type] * 100
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

        self.temp_fulldef = False

        self.auth_penalty = self.base_auth_penalty
        self.hpregen = self.base_hpregen
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

                if self.weight > 60:  # weight too much or tired will cause drowning
                    self.status_effect[102] = self.status_list[102].copy()  # Drowning

                elif self.weight > 30:  # Medium weight subunit has trouble travel through water and will sink and progressively lose troops
                    self.status_effect[101] = self.status_list[101].copy()  # Sinking

                elif self.weight < 30:  # Light weight subunit has no trouble travel through water
                    self.status_effect[104] = self.status_list[104].copy()  # Swiming

            if 2 in map_feature_mod[11]:  # Rot type terrain
                self.status_effect[54] = self.status_list[54].copy()

            if 3 in map_feature_mod[11]:  # Poison type terrain
                self.elem_count[4] += ((100 - self.elem_res[5]) / 100)
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

        self.discipline = (self.discipline * self.moralestate) + self.parentunit.leader_social[
            self.grade + 1] + (self.authority / 10)  # use morale, stamina, leader social vs grade (+1 to skip class name) and authority

        self.attack = (self.attack * (self.moralestate + 0.1)) + self.commandbuff  # use morale and command buff
        self.meleedef = (self.meleedef * (
                self.moralestate + 0.1)) + self.commandbuff  # use morale and command buff
        self.rangedef = (self.rangedef * (self.moralestate + 0.1)) + (
                self.commandbuff / 2)  # use morale and half command buff
        self.accuracy = self.accuracy + self.commandbuff  # use command buff
        self.chargedef = (self.chargedef * (self.moralestate + 0.1)) + self.commandbuff  # use morale and command buff
        heightdiff = (self.height / self.front_height) ** 2  # walking down hill increase speed while walking up hill reduce speed
        self.speed = self.speed * heightdiff
        self.charge = (self.charge + self.speed) * (
                self.moralestate + 0.1) + self.commandbuff  # use morale and command buff

        fullmergelen = len(self.fullmerge) + 1
        if fullmergelen > 1:  # reduce discipline if there are overlap sub-unit
            self.discipline = self.discipline / fullmergelen

        disciplinecal = self.discipline / 200
        if self.leader:
            disciplinecal = 1
        elif disciplinecal > 1:
            disciplinecal = 1
        self.attack = self.attack + (self.attack * disciplinecal)
        self.meleedef = self.meleedef + (self.meleedef * disciplinecal)
        self.rangedef = self.rangedef + (self.rangedef * disciplinecal)
        self.speed = self.speed + (self.speed * disciplinecal / 2)
        self.chargedef = self.chargedef + (self.chargedef * disciplinecal)

        # v Rounding up and forbid negative int stat
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
        # ^ End rounding up

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

        self.front_pos = rotationxy(self.base_pos, self.front_pos, self.radians_angle)

    def make_pos_range(self):
        """create range of sprite pos for pathfinding"""
        self.posrange = (range(int(max(0, self.base_pos[0] - (self.imageheight - 1))), int(min(1000, self.base_pos[0] + self.imageheight))),
                         range(int(max(0, self.base_pos[1] - (self.imageheight - 1))), int(min(1000, self.base_pos[1] + self.imageheight))))

    def gamestart(self):
        """run once when game start or subunit just get created"""
        self.make_pos_range()
        self.find_nearby_subunit()
        self.statusupdate()
        self.terrain, self.feature = self.getfeature(self.base_pos, self.gamemap)
        self.height = self.gamemapheight.getheight(self.base_pos)

    def update(self, weather, newdt, combattimer, mousepos, mouseup):
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
                    if 9 in self.status_effect:  # fight to the death
                        self.state = 10

                if self.timer > 1:  # Update status and skill use around every 1 second
                    self.statusupdate(weather)

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
                                self.state = 10
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

                            else:  # no target to fight move back to command pos first)
                                self.base_target = self.attack_target.base_pos
                                self.new_angle = self.setrotate()

                    elif self.attacking is False:  # not in fight anymore, rotate and move back to original position
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
                            rangeattack.RangeArrow(self, self.base_pos.distance_to(self.attack_pos), self.shootrange)  # Shoot
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
                        if self.state in (96, 98, 99):  # chance to escape
                            if random.randint(0, len(collidelist) + 2) < 2:
                                enemycollide_check = False
                        elif self.chargeskill in self.skill_effect and random.randint(0, 1) == 0:  # chance to charge through
                            enemycollide_check = False

                    if nocolide_check and enemycollide_check is False and \
                            len(self.same_front) == 0 and len(self.friend_front) == 0:
                        if self.chargeskill in self.skill_effect and self.base_pos == self.base_target and parentstate == 10:
                            new_target = self.front_pos - self.base_pos  # keep charging pass original target until momentum run out
                            self.base_target = self.base_target + new_target
                            self.command_target = self.base_target

                        move = self.base_target - self.base_pos
                        move_length = move.length()  # convert length

                        if move_length > 0:  # movement length longer than 0.1, not reach base_target yet
                            move.normalize_ip()

                            if self.parentunit.leader.run is False:  # walking
                                speed = self.parentunit.walkspeed  # use walk speed
                                self.walk = True
                            else:  # running
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

                                else:  # move length pass the base_target destination, set movement to stop exactly at base_target
                                    move = self.base_target - self.base_pos  # simply change move to whatever remaining distance
                                    self.base_pos += move  # adjust base position according to movement
                                    self.pos = self.base_pos
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
                            self.base_morale += (dt * self.moraleregen)  # Morale replenish

                        if self.base_morale < 0:  # morale cannot be negative
                            self.base_morale = 0

                    elif self.base_morale > self.max_morale:
                        self.base_morale -= dt  # gradually reduce morale that exceed the starting max amount

                    if self.state == 95:  # disobey state, morale gradually decrease until recover
                        self.base_morale -= dt * self.mental

                    elif self.state == 98:
                        if parentstate not in (98, 99):
                            self.troop_health -= (dt * 100)  # Unit begin to desert if retreating but parentunit not retreat/broken
                            if self.moralestate > 0.2:
                                self.state = 0  # Reset state to 0 when exit retreat state
                # ^ End morale check

                # v Hp regen
                if self.troop_health != infinity:
                    if self.hpregen > 0 and self.troop_health % self.troop_health != 0:  # hp regen cannot ressurect troop only heal to max hp
                        self.troop_health += self.hpregen * dt  # regen hp back based on time and regen stat
                    elif self.hpregen < 0:  # negative regen can kill
                        self.troop += self.hpregen * dt  # use the same as positive regen (negative regen number * dt will reduce hp)
                        wound = random.randint(0, 1)  # chance to be wounded instead of dead
                        if wound == 1:
                            self.gamebattle.wound_troopnumber[self.team] += 1
                        else:
                            self.gamebattle.death_troopnumber[self.team] += 1

                    if self.troop_health > self.max_health:
                        self.troop_health = self.max_health  # hp can't exceed max hp (would increase number of troop)
                    elif self.troop_health <= 0:  # enter dead state
                        self.troop_health = 0
                        self.state = 100  # enter dead state
                        self.last_health_state = 0
                        self.skill_cooldown = {}  # remove all cooldown
                        self.skill_effect = {}  # remove all skill effects

                        self.parentunit.deadchange = True

                        if self in self.gamebattle.battlecamera:
                            self.gamebattle.battlecamera.change_layer(sprite=self, new_layer=1)
                        self.gamebattle.allsubunitlist.remove(self)
                        self.parentunit.subunit_sprite.remove(self)

                        wound = random.randint(0, 1)  # chance to be wounded instead of dead
                        if wound == 1:
                            self.gamebattle.wound_troopnumber[self.team] += 1
                        else:
                            self.gamebattle.death_troopnumber[self.team] += 1

                        for subunit in self.parentunit.armysubunit.flat:  # remove from index array
                            if subunit == self.gameid:
                                self.parentunit.armysubunit = np.where(self.parentunit.armysubunit == self.gameid, 0, self.parentunit.armysubunit)
                                break

                    self.oldlasthealth = self.troop_health

            if self.state in (98, 99) and (self.base_pos[0] <= 0 or self.base_pos[0] >= 999 or
                                           self.base_pos[1] <= 0 or self.base_pos[1] >= 999):  # remove when unit move pass map border
                self.state = 100  # enter dead state
                self.gamebattle.flee_troopnumber[self.team] += 1  # add number of troop retreat from battle
                self.gamebattle.battlecamera.remove(self)

            self.enemy_front = []  # reset collide
            self.enemy_side = []
            self.friend_front = []
            self.same_front = []
            self.fullmerge = []
            self.collide_penalty = False

    def rotate(self):
        """rotate subunit image may use when subunit can change direction independently from parentunit"""
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def swap_weapon(self, newweapon):
        """self.weapon_skill assigned as class variable in longscript.py load data"""
        weapon_header = self.weapon_list.weapon_list_header
        trait_header = self.stat_list.trait_list_header

        if self.equiped_weapon != newweapon:
            self.equiped_weapon = newweapon
            self.trait = self.prime_trait
            self.elem_res = self.baes_elem_res

            self.main_weapon_dmg = (self.weapon_list.weapon_list[self.equiped_weapon[0][0]][weapon_header["Minimum Damage"]] *
                                    self.weapon_list.quality[self.equiped_weapon[0][1]],
                                    self.weapon_list.weapon_list[self.equiped_weapon[0][0]][weapon_header["Maximum Damage"]] *
                                    self.weapon_list.quality[self.equiped_weapon[0][1]])
            self.sub_weapon_dmg = (self.weapon_list.weapon_list[self.equiped_weapon[1][0]][weapon_header["Minimum Damage"]] *
                                   self.weapon_list.quality[self.equiped_weapon[1][1]],
                                   self.weapon_list.weapon_list[self.equiped_weapon[0]][weapon_header["Maximum Damage"]] *
                                   self.weapon_list.quality[self.equiped_weapon[1][1]])

            self.main_weapon_penetrate = self.weapon_list.weapon_list[self.equiped_weapon[0][0]][weapon_header["Armour Penetration"]] * \
                                         self.weapon_list.quality[self.equiped_weapon[0][1]]
            self.sub_weapon_penetrate = self.weapon_list.weapon_list[self.equiped_weapon[1][0]][weapon_header["Armour Penetration"]] * \
                                        self.weapon_list.quality[self.equiped_weapon[1][1]]

            self.main_weapon_speed = self.weapon_list.weapon_list[self.equiped_weapon[0][0]][weapon_header["Speed"]]
            self.sub_weapon_speed = self.weapon_list.weapon_list[self.equiped_weapon[1][1]][weapon_header["Speed"]]

            self.main_weapon_magazine_size = self.weapon_list.weapon_list[self.equiped_weapon[0][0]][
                weapon_header["Magazine"]]  # shoot how many before reload
            self.sub_weapon_magazine_size = self.weapon_list.weapon_list[self.equiped_weapon[1][0]][weapon_header["Magazine"]]

            self.main_weapon_base_range = self.weapon_list.weapon_list[self.equiped_weapon[0][0]][weapon_header["Range"]] * \
                                          self.weapon_list.quality[self.equiped_weapon[0][1]]  # weapon range depend on weapon range stat and quality
            self.sub_weapon_base_range = self.weapon_list.weapon_list[self.equiped_weapon[1][0]][weapon_header["Range"]] * \
                                         self.weapon_list.quality[self.equiped_weapon[1][1]]  # weapon range depend on weapon range stat and quality

            self.main_weapon_arrowspeed = self.weapon_list.weapon_list[self.equiped_weapon[0][0]][weapon_header["Travel Speed"]]
            self.sub_weapon_arrowspeed = self.weapon_list.weapon_list[self.equiped_weapon[1][0]][weapon_header["Travel Speed"]]

            self.weapon1_trait = self.equiped_weapon[0][weapon_header["Trait"]]
            self.weapon2_trait = self.equiped_weapon[1][weapon_header["Trait"]]

            self.trait = self.weapon1_trait + self.weapon2_trait

            self.base_attack = self.prime_attack
            self.base_meleedef = self.prime_meleedf
            self.base_rangedef = self.prime_rangedf
            self.base_armour = self.prime_armour
            self.base_speed = self.prime_speed
            self.base_accuracy = self.prime_accuracy
            self.base_range = self.prime_range
            self.base_reload = self.prime_reload
            self.base_charge = self.prime_charge
            self.base_chargedef = self.prime_chargedef
            self.base_hpregen = self.prime_hpregen
            self.base_morale = self.prime_morale
            self.crit_effect = self.prime_crit_effect
            self.base_discipline = self.prime_discipline
            self.elem_res = self.base_elem_res
            self.magic_res = self.base_magic_res
            self.heat_res = self.base_heat_res
            self.cold_res = self.base_cold_res
            self.mental = self.prime_mental
            self.base_elem_main = self.prime_elem_main
            self.base_elem_sub = self.prime_elem_sub

            self.base_inflictstatus = self.prime_inflictstatus

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
                    self.base_morale += trait[trait_header['Morale Bonus']]
                    self.crit_effect += trait[trait_header['Critical Bonus']]
                    self.base_discipline += trait[trait_header['Discipline Bonus']]
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
                            self.base_inflictstatus[effect] = trait[trait_header['Buff Range']]

                self.weapon1_trait = {x: self.stat_list.trait_list[x] for x in self.weapon1_trait if
                                      x in self.stat_list.trait_list}
                for trait in self.weapon1_trait:
                    if trait[trait_header['Element']] != 0:  # melee elemental effect
                        self.base_elem_main = trait[trait_header['Element']]
                self.weapon2_trait = {x: self.stat_list.trait_list[x] for x in self.weapon2_trait if
                                      x in self.stat_list.trait_list}
                for trait in self.weapon2_trait:
                    if trait[trait_header['Element']] != 0:  # melee elemental effect
                        self.base_elem_sub = trait[trait_header['Element']]

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

            if self.mental < 0:  # cannot be negative
                self.mental = 0
            elif self.mental > 200:  # cannot exceed 100
                self.mental = 200
            self.mentaltext = self.mental - 100
            self.mental = (200 - self.mental) / 100  # convert to percentage

            self.trait = {**self.base_trait, **self.trait}

            self.skill = [self.primary_main_weapon[self.weapon_skill] + self.secondary_main_weapon[self.weapon_skill] + \
                          self.primary_sub_weapon[self.weapon_skill] + self.secondary_sub_weapon[self.weapon_skill]]
            self.skill += self.troop_skill
            for skill in list(self.skill.keys()):  # remove skill if class mismatch
                skill_troop_cond = self.skill[skill][self.skill_trooptype]
                if skill_troop_cond != 0 or (self.subunit_type == 2 and skill_troop_cond != 2) or (self.subunit_type != 2 and skill_troop_cond == 2):
                    self.skill.pop(skill)

    def animation(self, frms, spd_ms):
        """Credit to cenk"""
        self.event
        self.frames = frms
        self.speed_ms = spd_ms / 1000
        self.start_frame = 0
        self.end_frame = len(self.frames) - 1
        self.first_time = time.time()
        self.show_frame = 0

    def blit(self, pen, crd):
        if time.time() - self.first_time >= self.speed_ms:
            self.show_frame = self.show_frame + 1
            self.first_time = time.time()
        if self.show_frame > self.end_frame:
            self.show_frame = self.start_frame
        # pen mean to window and is abbreivation of "pencere"
        pen.blit(self.frames[self.show_frame], crd)

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
