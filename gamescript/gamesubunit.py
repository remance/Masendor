import random
import numpy as np
import pygame
import pygame.freetype
import math
from pygame.transform import scale
from gamescript import rangeattack, gamelongscript

class Subunit(pygame.sprite.Sprite):
    images = []
    maingame = None
    gamemap = None # base map
    gamemapfeature = None # feature map
    gamemapheight = None # height map
    dmgcal = gamelongscript.dmgcal
    weapon_list = None
    armour_list = None
    stat_list = None
    create_troop_stat = gamelongscript.create_troop_stat
    rotationxy = gamelongscript.rotationxy
    setrotate = gamelongscript.setrotate
    changeleader = gamelongscript.changeleader
    maxzoom = 10 # max zoom allow
    # use same position as subunit front index 0 = front, 1 = left, 2 = rear, 3 = right

    def __init__(self, unitid, gameid, parentunit, position, starthp, startstamina, unitscale):
        """Although subunit in code, this is referred as sub-subunit ingame"""
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.wholastselect = None
        self.mouse_over = False
        self.leader = None # Leader in the sub-subunit if there is one, got add in leader gamestart
        self.board_pos = None  # Used for event log position of subunit (Assigned in maingame subunit setup)
        self.walk = False # currently walking
        self.run = False # currently running
        self.frontline = False # on front line of unit or not
        self.unit_leader = False # contain the general or not, making it leader subunit
        self.attack_target = None
        self.melee_target = None # current target of melee combat
        self.close_target = None # clost target to move to in melee
        self.parentunit = parentunit # reference to the parent battlion of this subunit

        self.enemy_front = [] # list of front collide sprite
        self.enemy_side = [] # list of side collide sprite
        self.friend_front = [] # list of friendly front collide sprite
        self.team = self.parentunit.team
        if self.team == 1: # add sprite to team subunit group for collision
            groupcollide = self.maingame.team1subunit
        elif self.team == 2:
            groupcollide = self.maingame.team2subunit
        groupcollide.add(self)

        self.status_list = self.parentunit.status_list

        self.gameid = gameid # ID of this subunit
        self.unitid = int(unitid) # ID of preset used for this subunit

        self.angle = self.parentunit.angle
        self.new_angle = self.parentunit.angle
        self.radians_angle = math.radians(360 - self.angle)  # radians for apply angle to position (allsidepos and subunit)
        self.parent_angle = self.parentunit.angle # angle subunit will face when not moving or

        self.red_corner = False  # red corner to indicate taking damage in inspect ui
        self.state = 0 # Current subunit state, similar to parentunit state
        self.timer = 0 # may need to use random.random()
        self.movetimer = 0 # timer for moving to front position before attacking nearest enemy
        self.charge_momentum = 1 # charging momentum to reach target before choosing nearest enemy
        self.magazine_now = 0
        self.zoom = 1
        self.lastzoom = 10
        self.brokenlimit = 0  # morale require for parentunit to stop broken state, will increase everytime broken state stop

        self.getfeature = self.gamemapfeature.getfeature
        self.getheight = self.gamemapheight.getheight

        #v Setup troop stat
        self.create_troop_stat(self.team, self.stat_list.unit_list[self.unitid].copy(), unitscale, starthp, startstamina)

        self.crit_effect = 1 # default critical effect
        self.front_dmg_effect = 1 # default frontal damage
        self.side_dmg_effect = 1 # default side damage

        self.corner_atk = False # cannot attack corner enemy by default
        self.temp_fulldef = False

        self.auth_penalty = self.base_auth_penalty
        self.hpregen = self.base_hpregen
        self.staminaregen = self.base_staminaregen
        self.inflictstatus = self.base_inflictstatus
        self.elemmelee = self.base_elemmelee
        self.elemrange = self.base_elemrange
        #^ End setup stat

        #v Subunit block team colour
        image = self.images[0].copy()  # Subunit block blue colour for team1 for shown in inspect ui
        if self.team == 2:
            image = self.images[13].copy()

        self.image = pygame.Surface((image.get_width()+10, image.get_height()+10), pygame.SRCALPHA) # subunit sprite image
        pygame.draw.circle(self.image, self.parentunit.colour, (self.image.get_width() / 2, self.image.get_height() / 2), image.get_width() / 2)

        if self.unit_type == 2: # cavalry draw line on block
            pygame.draw.line(image, (0, 0, 0), (0, 0), (image.get_width(), image.get_height()), 2)
            radian = 45 * 0.0174532925 # top left
            start = (self.image.get_width()/3 * math.cos(radian), self.image.get_width()/3 * math.sin(radian)) # draw line from 45 degree in circle
            radian = 225 * 0.0174532925 # bottom right
            end = (self.image.get_width() * -math.cos(radian), self.image.get_width() * -math.sin(radian)) # drow line to 225 degree in circle
            pygame.draw.line(self.image, (0, 0, 0), start, end, 2)

        self.imageblock = image.copy() # image shown in inspect ui as square instead of circle

        self.selectedimage = pygame.Surface((image.get_width(), image.get_height()), pygame.SRCALPHA)
        pygame.draw.circle(self.selectedimage, (255, 255, 255, 150), (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2)
        pygame.draw.circle(self.selectedimage, (0, 0, 0, 255), (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2, 1)
        self.selectedimage_original, self.selectedimage_original2 = self.selectedimage.copy(), self.selectedimage.copy()
        self.selectedimagerect = self.selectedimage.get_rect(topleft=(0,0))
        #^ End subunit block team colour

        #v health circle image setup
        self.healthimage = self.images[1]
        self.healthimagerect = self.healthimage.get_rect(center=self.image.get_rect().center) # for battle sprite
        self.healthimageblockrect = self.healthimage.get_rect(center=self.imageblock.get_rect().center) # for ui sprite
        self.image.blit(self.healthimage, self.healthimagerect)
        self.imageblock.blit(self.healthimage, self.healthimageblockrect)
        #^ End health circle

        #v stamina circle image setup
        self.staminaimage = self.images[6]
        self.staminaimagerect = self.staminaimage.get_rect(center=self.image.get_rect().center) # for battle sprite
        self.staminaimageblockrect = self.staminaimage.get_rect(center=self.imageblock.get_rect().center) # for ui sprite
        self.image.blit(self.staminaimage, self.staminaimagerect)
        self.imageblock.blit(self.staminaimage, self.staminaimageblockrect)
        #^ End stamina circle

        #v weapon class icon in middle circle
        if self.unitclass == 0: # melee weapon image as main
            image1 = self.weapon_list.imgs[self.weapon_list.weapon_list[self.meleeweapon[0]][-3]] # image on subunit sprite
        else: # range weapon image
            image1 = self.weapon_list.imgs[self.weapon_list.weapon_list[self.rangeweapon[0]][-3]]
        image1rect = image1.get_rect(center=self.image.get_rect().center)
        self.image.blit(image1, image1rect)

        image1rect = image1.get_rect(center=self.imageblock.get_rect().center)
        self.imageblock.blit(image1, image1rect)
        self.imageblock_original = self.imageblock.copy()

        self.cornerimagerect = self.images[11].get_rect(center=self.imageblock.get_rect().center) # red corner when take dmg shown in image block
        #^ End weapon icon

        self.image_original =  self.image.copy()  # original for rotate
        self.image_original2 =  self.image.copy() # original2 for saving original notclicked
        self.image_original3 = self.image.copy() # original3 for saving original zoom level

        #v position related
        self.armypos = (position[0]/10, position[1]/10) # position in parentunit sprite
        battaliontopleft = pygame.Vector2(self.parentunit.base_pos[0] - self.parentunit.base_width_box / 2,
                                          self.parentunit.base_pos[1] - self.parentunit.base_height_box / 2) # get topleft corner position of parentunit to calculate true pos
        self.base_pos = pygame.Vector2(battaliontopleft[0] + self.armypos[0], battaliontopleft[1] + self.armypos[1]) # true position of subunit in map
        self.lastpos = self.base_pos

        self.movement_queue = []
        self.combat_move_queue = []
        self.base_target = self.base_pos # base_target to move
        self.command_target = self.base_pos # actual base_target outside of combat
        self.pos = self.base_pos * self.zoom  # pos is for showing on screen

        #v Generate front side position
        self.imageheight = (image.get_height() - 1) / 20 # get real half height of circle sprite

        #v rotate the new front side according to sprite rotation
        self.front_pos = (self.base_pos[0], (self.base_pos[1] - self.imageheight))
        self.front_pos = self.rotationxy(self.base_pos, self.front_pos, self.radians_angle)

        self.attack_pos = self.parentunit.base_attack_pos
        self.terrain, self.feature = self.getfeature(self.base_pos, self.gamemap)  # get new terrain and feature at each subunit position
        self.height = self.gamemapheight.getheight(self.base_pos)  # Current terrain height
        self.front_height = self.gamemapheight.getheight(self.front_pos) # terrain height at front position
        #^ End position related

        self.rect = self.image.get_rect(center=self.pos)

    def zoomscale(self):
        """camera zoom change and rescale the sprite and position scale"""
        self.image_original = self.image_original3.copy() # reset image for new scale
        scalewidth = self.image_original.get_width() * self.zoom / self.maxzoom
        scaleheight = self.image_original.get_height() * self.zoom / self.maxzoom
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.image_original = self.image.copy()
        self.image_original2 = self.image.copy()

        if self.parentunit.selected and self.state != 100:
            self.selectedimage_original = pygame.transform.scale(self.selectedimage_original2, (int(self.dim[0]), int(self.dim[1])))

        self.change_pos_scale()
        self.rotate()
        self.mask = pygame.mask.from_surface(self.image)  # make new mask for collision

    def change_pos_scale(self):
        """Change position variable to new camera scale"""
        self.pos = self.base_pos * self.zoom
        self.rect = self.image.get_rect(center=self.pos)

    def useskill(self, whichskill):
        if whichskill == 0:  # charge skill need to seperate since charge power will be used only for charge skill
            skillstat = self.skill[list(self.skill)[0]].copy() # get skill stat
            self.skill_effect[self.chargeskill] = skillstat # add stat to skill effect
            self.skill_cooldown[self.chargeskill] = skillstat[4] # add skill cooldown
        else:  # other skill
            skillstat = self.skill[whichskill].copy() # get skill stat
            self.skill_effect[whichskill] = skillstat # add stat to skill effect
            self.skill_cooldown[whichskill] = skillstat[4] # add skill cooldown
        self.stamina -= skillstat[9]
        # self.skill_cooldown[whichskill] =

    # def receiveskill(self,whichskill):

    def check_skill_condition(self):
        """Check which skill can be used, cooldown, condition state, discipline, stamina are checked. charge skill is excepted from this check"""
        if self.skill_cond == 1 and self.staminastate < 50: # reserve 50% stamina, don't use any skill
            self.available_skill = []
        elif self.skill_cond == 2 and self.staminastate < 25: # reserve 25% stamina, don't use any skill
            self.available_skill = []
        else: # check all skill
            self.available_skill = [skill for skill in self.skill if skill not in self.skill_cooldown.keys()
                                    and self.state in self.skill[skill][6] and self.discipline >= self.skill[skill][8]
                                    and self.stamina > self.skill[skill][9] and skill != self.chargeskill]

    def find_nearby_subunit(self):
        """Find nearby friendly squads in the same parentunit for applying buff"""
        self.nearby_subunit_list = []
        corner_subunit = []
        for rowindex, rowlist in enumerate(self.parentunit.armysubunit.tolist()):
            if self.gameid in rowlist:
                if rowlist.index(self.gameid) - 1 != -1:  #get subunit from left if not at first column
                    self.nearby_subunit_list.append(self.parentunit.spritearray[rowindex][rowlist.index(self.gameid) - 1]) # index 0
                else: # not exist
                    self.nearby_subunit_list.append(0) # add number 0 instead

                if rowlist.index(self.gameid) + 1 != len(rowlist):  #get subunit from right if not at last column
                    self.nearby_subunit_list.append(self.parentunit.spritearray[rowindex][rowlist.index(self.gameid) + 1]) # index 1
                else: # not exist
                    self.nearby_subunit_list.append(0) # add number 0 instead

                if rowindex != 0:  #get top subunit
                    self.nearby_subunit_list.append(self.parentunit.spritearray[rowindex - 1][rowlist.index(self.gameid)]) # index 2
                    if rowlist.index(self.gameid) - 1 != -1:  # get top left subunit
                        corner_subunit.append(self.parentunit.spritearray[rowindex - 1][rowlist.index(self.gameid) - 1]) # index 3
                    else: # not exist
                        corner_subunit.append(0) # add number 0 instead
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  # get top right
                        corner_subunit.append(self.parentunit.spritearray[rowindex - 1][rowlist.index(self.gameid) + 1]) # index 4
                    else: # not exist
                        corner_subunit.append(0) # add number 0 instead
                else: # not exist
                    self.nearby_subunit_list.append(0) # add number 0 instead

                if rowindex != len(self.parentunit.spritearray) - 1:  # get bottom subunit
                    self.nearby_subunit_list.append(self.parentunit.spritearray[rowindex + 1][rowlist.index(self.gameid)]) # index 5
                    if rowlist.index(self.gameid) - 1 != -1:  # get bottom left subunit
                        corner_subunit.append(self.parentunit.spritearray[rowindex + 1][rowlist.index(self.gameid) - 1]) # index 6
                    else: # not exist
                        corner_subunit.append(0) # add number 0 instead
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  # get bottom  right subunit
                        corner_subunit.append(self.parentunit.spritearray[rowindex + 1][rowlist.index(self.gameid) + 1]) # index 7
                    else: # not exist
                        corner_subunit.append(0) # add number 0 instead
                else: # not exist
                    self.nearby_subunit_list.append(0) # add number 0 instead
        self.nearby_subunit_list = self.nearby_subunit_list + corner_subunit

    def status_to_friend(self, aoe, id, statuslist):
        """apply status effect to nearby subunit depending on aoe stat"""
        if aoe in (2, 3):
            if aoe > 1: # only direct nearby friendly subunit
                for subunit in self.nearby_subunit_list[0:4]:
                    if subunit != 0 and subunit.state != 100: # only apply to exist and alive squads
                        subunit.statuseffect[id] = statuslist # apply status effect
            if aoe > 2: # all nearby including corner friendly subunit
                for subunit in self.nearby_subunit_list[4:]:
                    if subunit != 0 and subunit.state != 100: # only apply to exist and alive squads
                        subunit.statuseffect[id] = statuslist # apply status effect
        elif aoe == 4: # apply to whole parentunit
            for subunit in self.parentunit.spritearray.flat:
                if subunit.state != 100: # only apply to alive squads
                    subunit.status_effect[id] = statuslist # apply status effect

    def threshold_count(self, elem, t1status, t2status):
        """apply elemental status effect when reach elemental threshold"""
        if elem > 50:
            self.status_effect[t1status] = self.status_list[t1status].copy() # apply tier 1 status
            if elem > 100:
                self.status_effect[t2status] = self.status_list[t2status].copy() # apply tier 2 status
                del self.status_effect[t1status] # remove tier 1 status
                elem = 0 # reset elemental count
        return elem

    def find_close_target(self):
        """Find close enemy sub-unit to move to fight"""
        closelist = {subunit: subunit.base_pos.distance_to(self.base_pos) for subunit in
                     self.melee_target.parentunit.subunit_sprite}
        closelist = dict(sorted(closelist.items(), key=lambda item: item[1]))
        maxrandom = 3
        if len(closelist) < 4:
            maxrandom = len(closelist) - 1
            if maxrandom < 0:
                maxrandom = 0
        if len(closelist) > 0:
            closetarget = list(closelist.keys())[random.randint(0, maxrandom)]
            # if close_target.base_pos.distance_to(self.base_pos) < 20: # in case can't find close target
            self.close_target = closetarget

    def statusupdate(self, thisweather=None):
        """calculate stat from stamina, morale state, skill, status, terrain"""

        if self.red_corner:  # have red corner reset image
            self.imageblock.blit(self.imageblock_original, self.cornerimagerect)
            self.red_corner = False

        #v reset stat to default and apply morale, stamina, command buff to stat
        if self.maxstamina > 100: # Max stamina gradually decrease over time - (self.timer * 0.05)
            self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.maxstamina-(self.timer*0.05), round(self.maxstamina * 0.75), round(
                self.maxstamina * 0.5), round(self.maxstamina * 0.25)
        self.morale = self.base_morale
        self.authority = self.parentunit.authority # parentunit total authoirty
        self.commandbuff = self.parentunit.commandbuff[self.unit_type] * 100 # command buff from main leader according to this subunit subunit type
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

        self.crit_effect = 1 # default critical effect
        self.front_dmg_effect = 1 # default frontal damage
        self.side_dmg_effect = 1 # default side damage

        self.corner_atk = False # cannot attack corner enemy by default
        self.temp_fulldef = False

        self.auth_penalty = self.base_auth_penalty
        self.hpregen = self.base_hpregen
        self.staminaregen = self.base_staminaregen
        self.inflictstatus = self.base_inflictstatus
        self.elemmelee = self.base_elemmelee
        self.elemrange = self.base_elemrange
        #^ End default stat

        if self.height > 100: #  apply height to range for height that is higher than 100 #TODO redo height range cal to use enemy base_target height as well
            self.shootrange = self.shootrange + (self.height / 10)

        #v Apply status effect from trait
        if len(self.trait) > 1:
            for trait in self.trait.values():
                if trait[18] != [0]:
                    for effect in trait[18]: #aplly status effect from trait
                        self.status_effect[effect] = self.status_list[effect].copy()
                        if trait[1] > 1:  # status buff range to nearby friend
                            self.status_to_friend(trait[1], effect, self.status_list[effect].copy())
        #^ End trait

        #v apply effect from weather"""
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
            if weather.elem[0] != 0: # Weather can cause elemental effect such as wet
                self.elem_count[weather.elem[0]] += ((weather.elem[1] * (100 - self.elem_res[weather.elem[0]]) / 100))
            weathertemperature = weather.temperature
        #^ End weather

        #v Map feature modifier to stat
        map_feature_mod = self.gamemapfeature.featuremod[self.feature]
        if map_feature_mod[self.featuremod] != 1: # speed/charge
            speedmod = map_feature_mod[self.featuremod] # get the speed mod appropiate to subunit type
            self.speed *= speedmod
            self.charge *= speedmod

        if map_feature_mod[self.featuremod + 1] != 1: # melee attack
            # combatmod = self.parentunit.gamemapfeature.featuremod[self.parentunit.feature][self.featuremod + 1]
            self.attack *= map_feature_mod[self.featuremod + 1] # get the attack mod appropiate to subunit type

        if map_feature_mod[self.featuremod + 2] != 1: # melee/charge defense
            combatmod = map_feature_mod[self.featuremod + 2] # get the defence mod appropiate to subunit type
            self.meleedef *= combatmod
            self.chargedef *= combatmod

        self.rangedef += map_feature_mod[7] # range defense bonus from terrain bonus
        self.accuracy -= (map_feature_mod[7]/2) # range def bonus block subunit sight as well so less accuracy
        self.discipline += map_feature_mod[9]  # discipline defense bonus from terrain bonus

        if map_feature_mod[11] != [0]: # Some terrain feature can also cause status effect such as swimming in water
            if 1 in map_feature_mod[11]: # Shallow water type terrain
                self.status_effect[31] = self.status_list[31].copy()  # wet
            if 5 in map_feature_mod[11]: # Deep water type terrain
                self.status_effect[93] = self.status_list[93].copy()  # drench

                if self.weight > 60 or self.stamina <= 0: # weight too much or tired will cause drowning
                    self.status_effect[102] = self.status_list[102].copy() # Drowning

                elif self.weight > 30:  # Medium weight subunit has trouble travel through water and will sink and progressively lose troops
                    self.status_effect[101] = self.status_list[101].copy() # Sinking

                elif self.weight < 30:  # Light weight subunit has no trouble travel through water
                    self.status_effect[104] = self.status_list[104].copy() # Swiming

            if 2 in map_feature_mod[11]:  # Rot type terrain
                self.status_effect[54] = self.status_list[54].copy()

            if 3 in map_feature_mod[11]:  # Poison type terrain
                self.elem_count[4] += ((100 - self.elem_res[5]) / 100)
        # self.hidden += self.parentunit.gamemapfeature[self.parentunit.feature][6]
        #^ End map feature

        #v Temperature mod function from terrain and weather
        tempreach = map_feature_mod[10] + weathertemperature # temperature the subunit will change to based on current terrain feature and weather
        for status in self.status_effect.values():
            tempreach += status[19] # add more from status effect
        if tempreach < 0: # cold temperature
            tempreach = tempreach * (100 - self.cold_res) / 100 # lowest temperature the subunit will change based on cold resist
        else: # hot temperature
            tempreach = tempreach * (100 - self.heat_res) / 100 # highest temperature the subunit will change based on heat resist

        if self.temp_count != tempreach: # move temp_count toward tempreach
            if tempreach > 0:
                if self.temp_count < tempreach:
                    self.temp_count += (100 - self.heat_res) / 100 * self.timer # increase subunit temperature, rate depends on heat resistance (negative make rate faster)
            elif tempreach < 0:
                if self.temp_count > tempreach:
                    self.temp_count -= (100 - self.cold_res) / 100 * self.timer # reduce subunit temperature, rate depends on cold resistance
            else: # tempreach is 0, subunit temp revert back to 0
                if self.temp_count > 0:
                    self.temp_count -= (1 + self.heat_res) / 100 * self.timer # revert faster with higher resist
                else:
                    self.temp_count += (1 + self.cold_res) / 100 * self.timer
        #^ End temperature

        #v Apply effect from skill
        if len(self.skill_effect) > 0:
            for status in self.skill_effect:  # apply elemental effect to dmg if skill has element
                calstatus = self.skill_effect[status]
                if calstatus[1] == 0 and calstatus[31] != 0: # melee elemental effect
                    self.elemmelee = int(calstatus[31])
                elif calstatus[1] == 1 and calstatus[31] != 0: # range elemental effect
                    self.elemrange = int(calstatus[31])
                self.attack = self.attack * calstatus[10]
                self.meleedef = self.meleedef * calstatus[11]
                self.rangedef = self.rangedef * calstatus[12]
                self.speed = self.speed * calstatus[13]
                self.accuracy = self.accuracy * calstatus[14]
                self.shootrange = self.shootrange * calstatus[15]
                self.reload = self.reload / calstatus[16] # different than other modifier the higher mod reduce reload time (decrease stat)
                self.charge = self.charge * calstatus[17]
                self.chargedef = self.chargedef + calstatus[18]
                self.hpregen += calstatus[19]
                self.staminaregen += calstatus[20]
                self.morale = self.morale + (calstatus[21] * self.mental)
                self.discipline = self.discipline + calstatus[22]
                # self.sight += calstatus[18]
                # self.hidden += calstatus[19]
                self.crit_effect = round(self.crit_effect * calstatus[23], 0)
                self.front_dmg_effect = round(self.front_dmg_effect * calstatus[24], 0)
                if calstatus[2] in (2, 3) and calstatus[24] != 100:
                    self.side_dmg_effect = round(self.side_dmg_effect * calstatus[24], 0)
                    if calstatus[2] == 3: self.corner_atk = True # if aoe 3 mean it can attack nearby enemy squads in corner

                #v Apply status to friendly if there is one in skill effect
                if calstatus[27] != [0]:
                    for effect in calstatus[27]:
                        self.status_effect[effect] = self.status_list[effect].copy()
                        if self.status_effect[effect][2] > 1:
                            self.status_to_friend(self.status_effect[effect][2], effect, self.status_list)
                        # if status[2] > 1:
                        #     self.parentunit.armysubunit
                        # if status[2] > 2:
                #^ End apply status to

                self.bonus_morale_dmg += calstatus[28]
                self.bonus_stamina_dmg += calstatus[29]
                if calstatus[30] != [0]: # Apply inflict status effect to enemy from skill to inflict list
                    for effect in calstatus[30]:
                        if effect != [0]: self.inflictstatus[effect] = calstatus[2]
            if self.chargeskill in self.skill_effect:
                self.auth_penalty += 0.5 # higher authority penalty when attacking (retreat while attacking)
        #^ End skill effect

        #v Elemental effect
        if self.elem_count != [0, 0, 0, 0, 0]: # Apply effect if elem threshold reach 50 or 100
            self.elem_count[0] = self.threshold_count(self.elem_count[0], 28, 92)
            self.elem_count[1] = self.threshold_count(self.elem_count[1], 31, 93)
            self.elem_count[2] = self.threshold_count(self.elem_count[2], 30, 94)
            self.elem_count[3] = self.threshold_count(self.elem_count[3], 23, 35)
            self.elem_count[4] = self.threshold_count(self.elem_count[4], 26, 27)
            self.elem_count = [elem - self.timer if elem > 0 else elem for elem in self.elem_count]
        #^ End elemental effect

        #v Temperature effect
        if self.temp_count > 50: # Hot
            self.status_effect[96] = self.status_list[96].copy()
            if self.temp_count > 100: # Extremely hot
                self.status_effect[97] = self.status_list[97].copy()
                del self.status_effect[96]
        if self.temp_count < -50: # Cold
            self.status_effect[95] = self.status_list[95].copy()
            if self.temp_count < -100: # Extremely cold
                self.status_effect[29] = self.status_list[29].copy()
                del self.status_effect[95]
        #^ End temperature effect related function

        #v Apply effect and modifer from status effect
        # """special status: 0 no control, 1 hostile to all, 2 no retreat, 3 no terrain effect, 4 no attack, 5 no skill, 6 no spell, 7 no exp gain,
        # 7 immune to bad mind, 8 immune to bad body, 9 immune to all effect, 10 immortal""" Not implemented yet
        if len(self.status_effect) > 0:
            for status in self.status_effect:
                calstatus = self.status_list[status]
                self.attack = self.attack * calstatus[4]
                self.meleedef = self.meleedef * calstatus[5]
                self.rangedef = self.rangedef * calstatus[6]
                self.armour = self.armour * calstatus[7]
                self.speed = self.speed * calstatus[8]
                self.accuracy = self.accuracy * calstatus[9]
                self.reload = self.reload / calstatus[10]
                self.charge = self.charge * calstatus[11]
                self.chargedef += calstatus[12]
                self.hpregen += calstatus[13]
                self.staminaregen += calstatus[14]
                self.morale = self.morale + (calstatus[15] * self.mental)
                self.discipline += calstatus[16]
                # self.sight += status[18]
                # self.hidden += status[19]
                if status == 91: # All round defense status
                    self.temp_fulldef = True
        #^ End status effect

        moralestate = self.morale
        if moralestate > 300: # morale more than 300 give no more benefit
            moralestate = 300
        self.moralestate = round((moralestate / self.maxmorale), 0)  # for using as modifer to stat
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        self.staminastatecal = self.staminastate / 100  # for using as modifer to stat
        self.discipline = (self.discipline * self.moralestate * self.staminastatecal) + self.parentunit.leader_social[
            self.grade + 1] + (self.authority / 10)  # use morale, stamina, leader social vs grade and authority
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

        #v Rounding up, add discipline to stat and forbid negative int stat
        # self.discipline = round(self.discipline, 0)
        disciplinecal = self.discipline / 200
        self.attack = round(self.attack + (self.attack * disciplinecal), 0)
        self.meleedef = round(self.meleedef + (self.meleedef * disciplinecal), 0)
        self.rangedef = round(self.rangedef + (self.rangedef * disciplinecal), 0)
        self.armour = round(self.armour, 0)
        self.speed = round(self.speed + (self.speed * disciplinecal/2), 0)
        self.accuracy = round(self.accuracy, 0)
        self.reload = round(self.reload, 0)
        self.chargedef = round(self.chargedef + (self.chargedef * disciplinecal), 0)
        self.charge = round(self.charge + (self.charge * disciplinecal), 0)

        if self.ammo == 0 and self.magazine_now == 0:
            self.shootrange = 0
        if self.attack < 0: self.attack = 0
        if self.meleedef < 0: self.meleedef = 0
        if self.rangedef < 0: self.rangedef = 0
        if self.armour < 0: self.armour = 0
        elif self.armour > 100: self.armour = 100 # Armour cannot be higher than 100 since it is percentage reduction
        if self.speed < 0: self.speed = 0
        if self.accuracy < 0: self.accuracy = 0
        if self.reload < 0: self.reload = 0
        if self.charge < 0: self.charge = 0
        if self.chargedef < 0: self.chargedef = 0
        if self.discipline < 0: self.discipline = 0
        #^ End rounding up

        self.rotatespeed = self.parentunit.rotatespeed * 2 # rotate speed for subunit only use for self rotate not subunit rotate related
        if self.state == 99:
            self.rotatespeed = self.speed

        #v cooldown, active and effect timer function
        self.skill_cooldown = {key: val - self.timer for key, val in self.skill_cooldown.items()} # cooldown decrease overtime
        self.skill_cooldown = {key: val for key, val in self.skill_cooldown.items() if val > 0} # remove cooldown if time reach 0
        for a, b in self.skill_effect.items(): # Can't use dict comprehension here since value include all other skill stat
            b[3] -= self.timer
        self.skill_effect = {key: val for key, val in self.skill_effect.items() if val[3] > 0 and self.state in val[5]} # remove effect if time reach 0 or restriction state is not met
        for a, b in self.status_effect.items():
            b[3] -= self.timer
        self.status_effect = {key: val for key, val in self.status_effect.items() if val[3] > 0}
        #^ End timer effectrangedamage

    def findshootingtarget(self, parentstate):
        # get nearby enemy base_target from list if not targeting anything yet
        self.attack_pos = list(self.parentunit.near_target.values())[0]  # replace attack_target with enemy pos
        self.attack_target = list(self.parentunit.near_target.keys())[0]  # replace attack_target with enemy id
        if self.shootrange >= self.attack_pos.distance_to(self.base_pos):
            self.state = 11
            if parentstate in (1, 3, 5):  # Walk and shoot
                self.state = 12
            elif parentstate in (2, 4, 6):  # Run and shoot
                self.state = 13

    def makefrontsidepos(self):
        """create new pos for front side of sprite"""
        self.front_pos = (self.base_pos[0], (self.base_pos[1] - self.imageheight))

        self.front_pos = self.rotationxy(self.base_pos, self.front_pos, self.radians_angle)

    def makeposrange(self):
        """create range of sprite pos for pathfinding"""
        self.posrange = (range(int(max(0, self.base_pos[0] - (self.imageheight - 1))), int(min(1000, self.base_pos[0] + self.imageheight))),
                         range(int(max(0, self.base_pos[1] - (self.imageheight - 1))), int(min(1000, self.base_pos[1] + self.imageheight))))

    def gamestart(self, zoom):
        """run once when game start or subunit just get created"""
        self.zoom = zoom
        self.makefrontsidepos()
        self.makeposrange()
        self.zoomscale()
        self.find_nearby_subunit()
        self.statusupdate()

    def update(self, weather, newdt, zoom, combattimer, mousepos, mouseup):
        if self.lastzoom != zoom: # camera zoom is changed
            self.lastzoom = zoom
            self.zoomchange = True
            self.zoom = zoom # save scale
            self.zoomscale() # update parentunit sprite according to new scale

        if self.state != 100:

            # v Mouse collision detection
            if self.rect.collidepoint(mousepos):
                self.maingame.last_mouseover = self.parentunit  # last mouse over on this parentunit
                if mouseup and self.maingame.uiclick is False:
                    self.maingame.last_selected = self.parentunit  # become last selected parentunit
                    if self.parentunit.selected is False:
                        self.parentunit.justselected = True
                        self.parentunit.selected = True
                    self.wholastselect = self.gameid
                    self.maingame.clickany = True
            # ^ End mouse detect

            #v Health bar
            if self.oldlasthealth != self.unit_health:
                healthlist = (self.health75, self.health50, self.health25, 0)
                for index, health in enumerate(healthlist):
                    if self.unit_health > health:
                        if self.last_health_state != abs(4 - index):
                            self.image_original3.blit(self.images[index+1], self.healthimagerect)
                            self.imageblock_original.blit(self.images[index+1], self.healthimageblockrect)
                            self.imageblock.blit(self.imageblock_original, self.cornerimagerect)
                            self.last_health_state = abs(4 - index)
                            self.zoomscale()
                        break
            #^ End hp bar

            #v Stamina bar
            if self.old_last_stamina != self.stamina:
                staminalist = (self.maxstamina, self.stamina75, self.stamina50, self.stamina25, 0)
                for index, stamina in enumerate(staminalist):
                    if self.stamina >= stamina:
                        if self.last_stamina_state != abs(4 - index):
                            # if index != 3:
                            self.image_original3.blit(self.images[index + 6], self.staminaimagerect)
                            self.zoomscale()
                            self.imageblock_original.blit(self.images[index + 6], self.staminaimageblockrect)
                            self.imageblock.blit(self.imageblock_original, self.cornerimagerect)
                            self.last_stamina_state = abs(4 - index)
                        break

                self.old_last_stamina = self.stamina
            #^ End stamina bar

            dt = newdt
            if dt > 0: # only run these when game not pause
                self.timer += dt

                self.walk = False  # reset walk
                self.run = False  # reset run

                parentstate = self.parentunit.state
                if parentstate in (1, 2, 3, 4):
                    self.attacking = True
                elif self.attacking and parentstate not in (1, 2, 3, 4, 10):  # cancel charge when no longer move to melee or in combat
                    self.attacking = False
                if self.state not in (95, 97, 98, 99) and parentstate in (0, 1, 2, 3, 4, 5, 6, 95, 96, 97, 98, 99):
                    self.state = parentstate # Enforce parentunit state to subunit when moving and breaking
                    if 9 in self.status_effect: # fight to the death
                        self.state = 10

                self.attack_target = self.parentunit.attack_target
                self.attack_pos = self.parentunit.base_attack_pos
                # if self.attack_target is not None:
                #     self.attack_pos = self.attack_target.leadersubunit.base_pos

                if self.timer > 1: # Update status and skill use around every 1 second
                    self.statusupdate(weather)
                    self.available_skill = []

                    if self.skill_cond != 3: # any skill condition behaviour beside 3 (forbid skill) will check available skill to use
                        self.check_skill_condition()

                    if parentstate == 4 and self.attacking and self.parentunit.moverotate is False and self.chargeskill not in self.skill_cooldown \
                            and self.base_pos.distance_to(self.base_target) < 100: # charge skill only when running to melee
                        self.charge_momentum += self.timer # TODO charge change target bug
                        if self.charge_momentum >= 10:
                            self.useskill(0)  # Use charge skill
                            self.parentunit.charging = True
                            self.charge_momentum = 10

                    elif parentstate != 4 and self.charge_momentum > 1:  # reset charge momentum if charge skill not active
                        self.charge_momentum -= self.timer * 2
                        if self.charge_momentum < 1:
                            self.parentunit.charging = False
                            self.charge_momentum = 1

                    skillchance = random.randint(0, 10) # random chance to use random available skill
                    if len(self.available_skill) > 0 and skillchance >= 6:
                        self.useskill(self.available_skill[random.randint(0, len(self.available_skill) - 1)])
                    self.timer -= 1

                # if parentstate not in (96,97,98,99) and self.state != 99:
                if self.enemy_front != [] or self.enemy_side != []: # Check if in combat or not with collision
                    collidelist = self.enemy_front + self.enemy_side
                    for subunit in collidelist:
                        if subunit.team != self.team:
                            if self.state not in (96, 98, 99):
                                self.state = 10
                                self.melee_target = subunit
                                if self.enemy_front == []:  # no enemy in front try rotate to enemy at side
                                    # self.base_target = self.melee_target.base_pos
                                    self.new_angle = self.setrotate(self.melee_target.base_pos)
                            else:  # no way to retreat, Fight to the death
                                if self.enemy_front != [] and self.enemy_side != []: # if both front and any side got attacked
                                    self.state = 10
                                    if 9 not in self.status_effect:
                                        self.status_effect[9] = self.status_list[9].copy() # fight to the death status
                            if parentstate not in (96,98,99):
                                parentstate = 10
                                self.parentunit.state = 10
                            if self.melee_target is not None:
                                self.parentunit.attack_target = self.melee_target.parentunit
                            break

                elif parentstate == 10: # no collide enemy while parent unit in fight state
                    if self.attacking and self.parentunit.collide:
                        if self.charge_momentum == 1 and (self.frontline or self.parentunit.attackmode == 2) and self.parentunit.attackmode != 1: # attack to nearest target instead
                            if self.melee_target is None and self.parentunit.attack_target is not None:
                                self.melee_target = self.parentunit.attack_target.subunit_sprite[0]
                            if self.close_target is None: # movement queue is empty regenerate new one
                                self.find_close_target() # find new close target

                                if self.close_target is not None: # found target to fight
                                    if self not in self.maingame.combatpathqueue:
                                        self.maingame.combatpathqueue.append(self)

                                else: # no target to fight move back to command pos first)
                                    self.base_target = self.attack_target.base_pos
                                    self.new_angle = self.setrotate()

                            if self.melee_target.parentunit.state != 100:
                                if self.movetimer == 0:
                                    self.movetimer = 0.1 # recalculate again in 10 seconds if not in fight
                                    # if len(self.friend_front) != 0 and len(self.enemy_front) == 0: # collide with friend try move to base_target first before enemy
                                        # self.combat_move_queue = [] # clean queue since the old one no longer without collide
                                else:
                                    self.movetimer += dt
                                    if len(self.enemy_front) != 0 or len(self.enemy_side) != 0: # in fight, stop timer
                                        self.movetimer = 0

                                    elif self.movetimer > 10 or len(self.combat_move_queue) == 0: # # time up, or no path. reset path
                                        self.movetimer = 0
                                        self.close_target = None
                                        if self in self.maingame.combatpathqueue:
                                            self.maingame.combatpathqueue.remove(self)

                                    elif len(self.combat_move_queue) > 0: # no collide move to enemy
                                        self.base_target = pygame.Vector2(self.combat_move_queue[0])
                                        self.new_angle = self.setrotate()

                            else: # whole targeted enemy unit destroyed, reset target and state
                                self.melee_target = None
                                self.close_target = None
                                if self in self.maingame.combatpathqueue:
                                    self.maingame.combatpathqueue.remove(self)

                                self.attack_target = None
                                self.base_target = self.command_target
                                self.new_angle = self.setrotate()
                                self.new_angle = self.parentunit.angle
                                self.state = 0

                        elif self.charge_momentum > 1: # gradually reduce charge momentum during combat
                            self.charge_momentum -= dt
                            if self.charge_momentum < 1:
                                self.charge_momentum = 1

                    elif self.attacking is False:  # not in fight anymore, rotate and move back to original position
                        self.melee_target = None
                        self.close_target = None
                        if self in self.maingame.combatpathqueue:
                            self.maingame.combatpathqueue.remove(self)

                        self.attack_target = None
                        self.base_target = self.command_target
                        self.new_angle = self.parentunit.angle
                        self.state = 0

                    if self.state != 10 and self.ammo > 0 and self.parentunit.fireatwill == 0 and (
                            self.arcshot or self.frontline) and self.charge_momentum == 1:  # Help range attack when parentunit in melee combat if has arcshot or frontline
                        self.state = 11
                        if self.parentunit.near_target != {} and (self.attack_target is None or self.attack_pos == 0):
                            self.findshootingtarget(parentstate)

                #^ End melee check

                else: # range attack
                    self.melee_target = None
                    self.close_target = None
                    if self in self.maingame.combatpathqueue:
                        self.maingame.combatpathqueue.remove(self)
                    self.attack_target = None
                    self.combat_move_queue = []

                    #v Range attack function
                    if parentstate == 11: # Unit in range attack state
                        self.state = 0 # Default state at idle
                        if (self.ammo > 0 or self.magazine_now > 0) and self.attack_pos != 0 \
                                and self.shootrange >= self.attack_pos.distance_to(self.parentunit.base_pos): # can shoot if have ammo and in shoot range
                            self.state = 11 # range combat state

                    elif self.ammo > 0 and self.parentunit.fireatwill == 0 and (self.state == 0 or (parentstate in (1, 2, 3, 4, 5, 6)
                                                                                                    and self.shootmove)):  # Fire at will, auto pick closest enemy
                        if self.parentunit.near_target != {} and self.attack_target is None:
                            self.findshootingtarget(parentstate)

                if self.state in (11, 12, 13) and self.ammo > 0 and self.magazine_now == 0: # reloading ammo
                    self.reloadtime += dt
                    if self.reloadtime >= self.reload:
                        self.magazine_now = self.magazinesize
                        self.ammo -= 1
                        self.reloadtime = 0
                    self.stamina = self.stamina - (dt * 5) # use stamina while reloading
                #^ End range attack function

                #v Combat action related
                if combattimer >= 0.5: # combat is calculated every 0.5 second in game time
                    if self.state == 10: # if melee combat (engaging anyone on any side)
                        collidelist = [subunit for subunit in self.enemy_front if subunit.team != self.team]
                        for subunit in collidelist:
                            anglecheck = abs(self.angle - subunit.angle)  # calculate which side arrow hit the subunit
                            if anglecheck >= 135:  # front
                                hitside = 0
                            elif anglecheck >= 45:  # side
                                hitside = 1
                            else: # rear
                                hitside = 2
                            self.dmgcal(subunit, 0, hitside, self.maingame.gameunitstat.status_list, combattimer)
                            self.stamina = self.stamina - (combattimer * 5)

                    elif self.state in (11, 12, 13): # range combat
                        if type(self.attack_target) == int: # For fire at will, which attacktarge is int
                            allunitindex = self.maingame.allunitindex
                            if self.attack_target in allunitindex: # if the attack base_target still alive (if dead it would not be in index list)
                                self.attack_target = self.maingame.allunitlist[allunitindex.index(self.attack_target)] # change attack_target index into sprite
                            else: # enemy dead
                                self.attack_pos = 0 # reset attack_pos to 0
                                self.attack_target = None # reset attack_target to 0

                                for target in list(self.parentunit.near_target.values()): # find other nearby base_target to shoot
                                    if target in allunitindex: # check if base_target alive
                                        self.attack_pos = target[1]
                                        self.attack_target = target[1]
                                        self.attack_target = self.maingame.allunitlist[allunitindex.index(self.attack_target)]
                                        break # found new base_target break loop

                        if self.magazine_now > 0 and self.shootrange > 0 and ((self.attack_target is not None and self.attack_target.state != 100) or
                                                                              (self.attack_target is None and self.attack_pos != 0)) \
                                            and (self.arcshot or (self.arcshot is False and self.parentunit.shoothow != 1)):
                            # can shoot if reload finish and base_target existed and not dead. Non arcshot cannot shoot if forbidded
                            rangeattack.Rangearrow(self, self.base_pos.distance_to(self.attack_pos), self.shootrange, self.zoom) # Shoot at enemy
                            self.magazine_now -= 1 # use 1 ammo in magazine
                        elif self.attack_target is not None and self.attack_target.state == 100: # if base_target die when it about to shoot
                            self.parentunit.range_combat_check, self.parentunit.attack_target = False, 0 # reset range combat check and base_target

                #^ End combat related

                if parentstate != 10 and self.charge_momentum == 1: # reset base_target every update to command base_target outside of combat
                    if self.base_target != self.command_target:
                        print('test1')
                        self.base_target = self.command_target
                        if parentstate == 0:
                            self.new_angle = self.setrotate()
                            # self.new_angle = self.parentunit.angle
                    elif self.base_pos == self.base_target and self.angle != self.parentunit.angle:
                        print('testtse')
                        self.new_angle = self.setrotate()
                        self.new_angle = self.parentunit.angle
                # elif self.state != 10 and self.frontline: # set base_target to enemy base_pos
                #     if self.attack_target is not None:
                #         pass
                    # self.base_target = self.attack_target.base_pos
                    # self.new_angle = self.setrotate()

                # v Rotate Function
                if self.angle != self.new_angle:
                    print(self.new_angle, self.angle)
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
                            if self.rotatecheck <= 0: self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                        else:
                            self.angle += rotatetiny
                            if self.angle > self.new_angle: self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                    elif self.new_angle < self.angle:  # rotate to angle less than the current one
                        if self.rotatecal > 180:  # rotate with the smallest angle direction
                            self.angle += rotatetiny
                            self.rotatecheck -= rotatetiny
                            if self.rotatecheck <= 0: self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                        else:
                            self.angle -= rotatetiny
                            if self.angle < self.new_angle: self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
                    self.rotate()  # rotate sprite to new angle
                    self.makefrontsidepos()  # generate new pos related to side
                    self.mask = pygame.mask.from_surface(self.image) # make new mask
                # ^ End rotate

                revertmove = False
                if parentstate == 0 or self.parentunit.revert or (self.angle != self.parentunit.angle and self.parentunit.moverotate is False):
                    revertmove = True # revert move check for in case subunit still need to rotate before moving

                #v Move function to given base_target position
                if (revertmove is False or self.angle == self.new_angle) and (self.base_pos != self.base_target or self.charge_momentum > 1): # cannot move if still need to rotate

                    #v Can move if front not collided
                    if self.stamina > 0 and ((self.parentunit.collide is False or parentstate == 99) or ((self.frontline or self.parentunit.attackmode == 2) and self.parentunit.attackmode != 1) or self.charge_momentum > 1) \
                            and len(self.enemy_front) == 0 and (len(self.friend_front) == 0 or self.state == 99 or (parentstate == 0 and self.charge_momentum == 1)):
                        if self.charge_momentum > 1 and self.base_pos == self.base_target:
                            newtarget = self.front_pos - self.base_pos
                            self.base_target = self.base_target + newtarget
                            # self.command_target = self.base_target
                        move = self.base_target - self.base_pos
                        move_length = move.length()  # convert length

                        if move_length > 0:  # movement length longer than 0.1, not reach base_target yet
                            move.normalize_ip()

                            if parentstate in (1, 3, 5, 7):  # walking
                                speed = self.parentunit.walkspeed #use walk speed
                                self.walk = True
                            elif parentstate in (10, 99) or self.charge_momentum > 1: # run with its own speed instead of uniformed run
                                speed = self.speed / 15 # use its own speed when broken
                                self.run = True
                            else:  # self.state in (2, 4, 6, 10, 96, 98, 99), running
                                speed = self.parentunit.runspeed # use run speed
                                self.run = True
                            move = move * speed * dt
                            newmove_length = move.length()
                            newpos = self.base_pos + move

                            if  self.state in (98, 99) or (self.state not in (98, 99) and (newpos[0] > 0 and newpos[0] < 999 and newpos[1] > 0 and newpos[1] < 999)):  # cannot go pass map unless in retreat
                                if newmove_length <= move_length:  # move normally according to move speed
                                    self.base_pos = newpos
                                    self.pos = self.base_pos * self.zoom
                                    self.rect.center = list(int(v) for v in self.pos)  # list rect so the sprite gradually move to position
                                    if self.walk:
                                        self.stamina = self.stamina - (dt * 3)
                                    elif self.run:
                                        self.stamina = self.stamina - (dt * 5)

                                else:  # move length pass the base_target destination, set movement to stop exactly at base_target
                                    move = self.base_target - self.base_pos  # simply change move to whatever remaining distance
                                    self.base_pos += move  # adjust base position according to movement
                                    self.pos = self.base_pos * self.zoom
                                    self.rect.center = self.pos  # no need to do list
                                if len(self.combat_move_queue) > 0 and self.base_pos.distance_to(pygame.Vector2(self.combat_move_queue[0])) < 0.1: #:  # reach the current queue point, remove from queue
                                    self.combat_move_queue = self.combat_move_queue[1:]

                                self.makefrontsidepos()
                                self.makeposrange()

                                if self.unit_leader and newmove_length > 0: #parentstate != 10 and self.parentunit.moving is False and self.parentunit.moverotate is False:
                                    if self.parentunit.moverotate is False:
                                        self.parentunit.base_pos += move
                                    frontpos = (self.parentunit.base_pos[0], (self.parentunit.base_pos[1] - self.parentunit.base_height_box))  # find front position
                                    self.parentunit.front_pos = self.rotationxy(self.parentunit.base_pos, frontpos, self.parentunit.radians_angle)

                                    numberpos = (self.parentunit.base_pos[0] - self.parentunit.base_width_box, (self.parentunit.base_pos[1] + self.parentunit.base_height_box))
                                    self.parentunit.number_pos = self.rotationxy(self.parentunit.base_pos, numberpos, self.parentunit.radians_angle)
                                    self.parentunit.truenumber_pos = self.parentunit.number_pos * (11 - self.parentunit.zoom) # find new position for troop number text

                        else:  # Stopping subunit when reach base_target
                            self.state = 0  # idle

                        # if self.lastpos != self.base_pos:
                        self.terrain, self.feature = self.getfeature(self.base_pos, self.gamemap)  # get new terrain and feature at each subunit position
                        self.height = self.gamemapheight.getheight(self.base_pos)  # get new height
                        self.front_height = self.gamemapheight.getheight(self.front_pos)
                        self.mask = pygame.mask.from_surface(self.image) # make new mask
                        self.lastpos = self.base_pos
                    # ^ End move function

                #v Morale check
                if self.base_morale < self.maxmorale:
                    if self.morale <= 10: # Enter retreat state when morale reach 0
                        if self.state not in (98, 99):
                            self.state = 98 # retreat state
                            self.brokenlimit += random.randint(10, 20)

                            self.moraleregen -= 0.3 # morale regen slower per broken state
                            if self.brokenlimit > 50:  # begin checking broken state
                                if self.brokenlimit > 100:
                                    self.brokenlimit = 100
                                if random.randint(self.brokenlimit, 100) > 80:  # check whether unit enter broken state or not
                                    self.state = 99  # Broken state
                                    self.changeleader(type="broken")

                                    cornerlist = [[0, self.base_pos[1]], [1000, self.base_pos[1]], [self.base_pos[0], 0], [self.base_pos[0], 1000]]
                                    whichcorner = [self.base_pos.distance_to(cornerlist[0]), self.base_pos.distance_to(cornerlist[1]),
                                                   self.base_pos.distance_to(cornerlist[2]), self.base_pos.distance_to(cornerlist[3])] # find closest map corner to run to
                                    foundcorner = whichcorner.index(min(whichcorner))
                                    self.base_target = pygame.Vector2(cornerlist[foundcorner])
                                    self.command_target = self.base_target
                                    self.new_angle = self.setrotate()

                            for subunit in self.parentunit.subunit_sprite:
                                subunit.base_morale -= (15 * subunit.mental) # reduce morale of other subunit, creating panic when seeing friend panic and may cause mass panic
                        if self.morale < 0:
                            self.morale = 0 # morale cannot be lower than 0

                elif self.base_morale > self.maxmorale:
                    self.base_morale -= dt # gradually reduce morale that exceed the starting max amount

                if self.state not in (95, 99) and parentstate not in (10, 99):  # If not missing main leader can replenish morale
                    self.base_morale += (dt * self.staminastatecal * self.moraleregen)  # Morale replenish based on stamina

                if self.state == 95:  # disobey state, morale gradually decrease until recover
                    self.base_morale -= dt * self.mental

                if self.state == 98:
                    if parentstate not in (98, 99):
                        self.unit_health -= (dt * 100)  # Unit begin to desert if retreating but parentunit not retreat/broken
                        if self.moralestate > 0.2:
                            self.state = 0  # Reset state to 0 when exit retreat state

                if self.base_morale < 0:  # morale cannot be negative
                    self.base_morale = 0
                elif self.base_morale > 200:  # morale cannot be higher than 200
                    self.base_morale = 200
                #^ End morale check

                if self.oldlasthealth != self.unit_health:
                    self.troopnumber = self.unit_health / self.troophealth  # Calculate how many troop left based on current hp
                    if self.troopnumber.is_integer() is False:  # always round up if there is decimal
                        self.troopnumber = int(self.troopnumber + 1)
                    self.oldlasthealth = self.unit_health

                #v Hp and stamina regen
                if self.stamina < self.maxstamina:
                    if self.stamina <= 0:  # Collapse and cannot act
                        self.stamina = 0
                        self.status_effect[105] = self.status_list[105].copy() # receive collapse status
                    self.stamina = self.stamina + (dt * self.staminaregen) # regen
                elif self.stamina > self.maxstamina: # stamina cannot exceed the max stamina
                    self.stamina = self.maxstamina

                if self.hpregen > 0 and self.unit_health % self.troophealth != 0:  ## hp regen cannot ressurect troop only heal to max hp
                    alivehp = self.troopnumber * self.troophealth  ## Max hp possible for the number of alive subunit
                    self.unit_health += self.hpregen * dt # regen hp back based on time and regen stat
                    if self.unit_health > alivehp: self.unit_health = alivehp # Cannot exceed health of alive subunit (exceed mean resurrection)
                elif self.hpregen < 0:  ## negative regen can kill
                    self.unit_health += self.hpregen * dt # use the same as positive regen (negative regen number * dt will reduce hp)
                    self.troopnumber = self.unit_health / self.troophealth  # Recal number of troop again in case some die from negative regen
                    if round(self.troopnumber) < self.troopnumber: # no method to always round up number so I need to do this manually
                        self.troopnumber = int(self.troopnumber + 1)
                    else:
                        self.troopnumber = int(self.troopnumber)

                if self.unit_health < 0: self.unit_health = 0 # can't have negative hp
                elif self.unit_health > self.maxhealth: self.unit_health = self.maxhealth # hp can't exceed max hp (would increase number of troop)
                #^ End regen

            if self.state in (98, 99) and (self.base_pos[0] <= 0 or self.base_pos[0] >= 999 or self.base_pos[1] <= 0 or self.base_pos[1] >= 999): # remove when unit move pass map border
                self.state = 100  # enter dead state
                self.troopnumber = 0
                self.maingame.battlecamera.remove(self)

            if self.troopnumber <= 0:  # enter dead state
                self.state = 100 # enter dead state
                self.image_original3.blit(self.images[5], self.healthimagerect) # blit white hp bar
                self.imageblock_original.blit(self.images[5], self.healthimageblockrect)
                self.zoomscale()
                self.last_health_state = 0
                self.skill_cooldown = {} # remove all cooldown
                self.skill_effect = {} # remove all skill effects

                self.imageblock.blit(self.imageblock_original, self.cornerimagerect)
                self.red_corner = True # to prevent red border appear when dead

                self.parentunit.deadchange = True

                if self in self.maingame.battlecamera:
                    self.maingame.battlecamera.change_layer(sprite=self, new_layer=1)
                self.maingame.allsubunitlist.remove(self)
                self.parentunit.subunit_sprite.remove(self)

                for subunit in self.parentunit.armysubunit.flat: # remove from index array
                    if subunit == self.gameid:
                        self.parentunit.armysubunit = np.where(self.parentunit.armysubunit == self.gameid, 0, self.parentunit.armysubunit)
                        break

                self.changeleader(type="die")

                self.maingame.eventlog.addlog([0, str(self.board_pos) + " " + str(self.name)
                                               + " in " + self.parentunit.leader[0].name
                                               + "'s parentunit is destroyed"], [3]) # add log to say this subunit is destroyed in subunit tab

            self.enemy_front = [] # reset collide
            self.enemy_side = [] # reset collide
            self.friend_front = []

    def rotate(self):
        """rotate subunit image may use when subunit can change direction independently from parentunit"""
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        if self.parentunit.selected and self.state != 100:
            self.selectedimage = pygame.transform.rotate(self.selectedimage_original, self.angle)
            self.image.blit(self.selectedimage, self.selectedimagerect)
        self.rect = self.image.get_rect(center=self.pos)

    # def command(self, mouse_pos, mouse_up, mouse_right, squadlastselect):
    #     """For inspect ui clicking"""
    #     self.wholastselect = squadlastselect
    #     if self.rect.collidepoint(mouse_pos[0]):
    #         self.mouse_over = True
    #         self.whomouseover = self.gameid
    #         if mouse_up:
    #             self.parentunit.selected = True
    #             self.parentunit.justselected = True
    #             self.wholastselect = self.gameid

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
            if self in self.maingame.combatpathqueue:
                self.maingame.combatpathqueue.remove(self)


