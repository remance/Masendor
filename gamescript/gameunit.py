import math
import random

import numpy as np
import pygame
import pygame.freetype
from gamescript import gamelongscript
from pygame.transform import scale


class Directionarrow(pygame.sprite.Sprite):  # TODO make it work so it can be implemented again
    def __init__(self, who):
        """Layer must be called before sprite_init"""
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.who = who
        self.pos = self.who.pos
        self.who.directionarrow = self
        self.lengthgap = self.who.image.get_height() / 2
        self.length = self.who.pos.distance_to(self.who.base_target) + self.lengthgap
        self.previouslength = self.length
        self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        # self.image_original = self.image.copy()
        # pygame.draw.line(self.image, (0, 0, 0), (self.image.get_width()/2, 0),(self.image.get_width()/2,self.image.get_height()), 5)
        self.image = pygame.transform.rotate(self.image, self.who.angle)
        self.rect = self.image.get_rect(midbottom=self.who.front_pos)

    def update(self, zoom):
        self.length = self.who.pos.distance_to(self.who.base_target) + self.lengthgap
        distance = self.who.front_pos.distance_to(self.who.base_target) + self.lengthgap
        if self.length != self.previouslength and distance > 2 and self.who.state != 0:
            self.pos = self.who.pos
            self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
            self.image.fill((0, 0, 0))
            self.image = pygame.transform.rotate(self.image, self.who.angle)
            self.rect = self.image.get_rect(midbottom=self.who.front_pos)
            self.previouslength = self.length
        elif distance < 2 or self.who.state in (0, 10, 11, 100):
            self.who.directionarrow = False
            self.kill()


class Troopnumber(pygame.sprite.Sprite):
    def __init__(self, who):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.who = who
        self.textcolour = pygame.Color("blue")
        if self.who.team == 2:
            self.textcolour = pygame.Color("red")
        self.pos = self.who.truenumber_pos
        self.number = self.who.troopnumber
        self.zoom = 0

        self.font = pygame.font.SysFont("timesnewroman", int(12 * self.heightadjust))

        self.image = self.render(str(self.number), self.font, self.textcolour)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, *args, **kwargs) -> None:
        if self.pos != self.who.truenumber_pos:  # new position
            self.pos = self.who.truenumber_pos
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.zoom != args[2]:  # zoom argument
            self.zoom = int(args[2])
            zoom = (11 - self.zoom) / 2
            if zoom < 1:
                zoom = 1
            newfontsize = int(60 / zoom * self.heightadjust)
            self.font = pygame.font.SysFont("timesnewroman", newfontsize)
            self.image = self.render(str(self.number), self.font, self.textcolour)
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.number != self.who.troopnumber:  # new troop number
            self.number = self.who.troopnumber
            self.image = self.render(str(self.number), self.font, self.textcolour)
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.who.state == 100:
            self.kill()
            self.delete()

    def circlepoints(self, r):
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

    def render(self, text, font, gfcolor=pygame.Color("black"), ocolor=(255, 255, 255), opx=2):
        """Render text with background border"""
        textsurface = font.render(text, True, gfcolor).convert_alpha()
        w = textsurface.get_width() + 2 * opx
        h = font.get_height()

        osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
        osurf.fill((0, 0, 0, 0))

        surf = osurf.copy()

        osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

        for dx, dy in self.circlepoints(opx):
            surf.blit(osurf, (dx + opx, dy + opx))

        surf.blit(textsurface, (opx, opx))

        return surf

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.who


class Unitarmy(pygame.sprite.Sprite):
    images = []
    status_list = None  # status effect list
    maxzoom = 10  # max zoom allow
    gamebattle = None
    rotationxy = gamelongscript.rotationxy
    die = gamelongscript.die  # die script
    setrotate = gamelongscript.setrotate
    formchangetimer = 10
    imgsize = None

    def __init__(self, startposition, gameid, squadlist, colour, control, coa, commander, startangle, starthp=100, startstamina=100, team=0):
        """Although parentunit in code, this is referred as subunit ingame"""
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icon = None  # for linking with army selection ui, got linked when icon created in gameui.Armyicon
        self.teamcommander = None  # commander leader
        self.startwhere = []
        self.subunit_sprite_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
        self.subunit_sprite = []
        self.leader = []
        self.leadersubunit = None  # subunit that general is in, get added in leader first update
        self.near_target = {}  # list dict of nearby enemy parentunit, sorted by distance
        self.gameid = gameid  # id of parentunit for reference in many function
        self.control = control  # player control or not
        self.starthp = starthp  # starting hp percentage
        self.startstamina = startstamina  # starting stamina percentage
        self.armysubunit = squadlist  # subunit array
        self.colour = colour  # box colour according to team
        self.commander = commander  # commander parentunit if true

        self.zoom = 10  # start with closest zoom
        self.lastzoom = 1  # zoom level without calculate with 11 - zoom for scale

        self.base_width_box, self.base_height_box = len(self.armysubunit[0]) * (self.imgsize[0] + 10) / 20, len(self.armysubunit) * (
                    self.imgsize[1] + 2) / 20

        self.base_pos = pygame.Vector2(startposition)  # base_pos is for true pos that is used for ingame calculation
        self.last_base_pos = self.base_pos
        self.base_attack_pos = 0  # position of attack base_target
        self.angle = startangle  # start at this angle
        if self.angle == 360:  # 360 is 0 angle at the start, not doing this cause angle glitch when game start
            self.angle = 0
        self.new_angle = self.angle
        self.radians_angle = math.radians(360 - startangle)  # radians for apply angle to position (allsidepos and subunit)
        frontpos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
        self.front_pos = self.rotationxy(self.base_pos, frontpos, self.radians_angle)
        self.movement_queue = []
        self.base_target = self.front_pos
        self.command_target = self.front_pos
        numberpos = (self.base_pos[0] - self.base_width_box,
                     (self.base_pos[1] + self.base_height_box))  # find position for number text
        self.number_pos = self.rotationxy(self.base_pos, numberpos, self.radians_angle)
        self.change_pos_scale()

        # v Setup default beheviour check # TODO add volley, divide behaviour ui into 3 types: combat, shoot, other (move)
        self.nextrotate = False
        self.selected = False  # for checking if it currently selected or not
        self.justselected = False  # for light up subunit when click
        self.zoom_change = False
        self.revert = False
        self.moverotate = False  # for checking if the movement require rotation first or not
        self.rotatecal = 0  # for calculate how much angle to rotate to the base_target
        self.rotatecheck = 0  # for checking if the new angle rotate pass the base_target angle or not
        self.justsplit = False  # subunit just got split
        self.leader_change = False
        self.directionarrow = False
        self.rotateonly = False  # Order parentunit to rotate to base_target direction
        self.charging = False  # For subunit charge skill activation
        self.forced_melee = False  # Force parentunit to melee attack
        self.attack_place = False  # attack position instead of enemy
        self.forcedmarch = False
        self.changefaction = False  # For initiating change faction function
        self.runtoggle = 0  # 0 = double right click to run, 1 = only one right click will make parentunit run
        self.shoothow = 0  # 0 = both arc and non-arc shot, 1 = arc shot only, 2 = forbid arc shot
        self.attackmode = 0  # frontline attack, 1 = formation attack, 2 = free for all attack,
        self.hold = 0  # 0 = not hold, 1 = skirmish/scout/avoid, 2 = hold
        self.fireatwill = 0  # 0 = fire at will, 1 = no fire
        self.retreat_start = False
        self.retreat_way = None
        self.collide = False  # for checking if subunit collide if yes stop moving
        self.range_combat_check = False
        self.attack_target = None  # attack base_target, can be either int or parentunit object
        self.got_killed = False  # for checking if die() was performed when subunit die yet
        # ^ End behaviour check

        # v setup default starting value
        self.troopnumber = 0  # sum
        self.stamina = 0  # average from all subunit
        self.morale = 0  # average from all subunit
        self.ammo = 0  # total magazine_left left of the whole parentunit
        self.oldammo = 0  # previous number of magazine_left for magazine_left bar checking
        self.minrange = 0  # minimum shoot range of all subunit inside this parentunit
        self.maxrange = 0  # maximum shoot range of all subunit inside this parentunit
        self.use_min_range = 0  # use min or max range for walk/run (range) command
        self.skill_cond = 0  # skill condition for stamina reservation
        self.state = 0  # see gameui.py topbar for name of each state
        self.command_state = self.state
        self.deadchange = False  # for checking when subunit dead and run related code
        self.timer = random.random()
        self.state_delay = 3  # some state has delay before can change state, default at 3 seconds
        self.rotatespeed = 1
        # ^ End default starting value

        # check if can split unit
        self.can_split_row = False
        if np.array_split(self.armysubunit, 2)[0].size > 10 and np.array_split(self.armysubunit, 2)[1].size > 10:
            self.can_split_row = True

        self.can_split_col = False
        if np.array_split(self.armysubunit, 2, axis=1)[0].size > 10 and np.array_split(self.armysubunit, 2, axis=1)[1].size > 10:
            self.can_split_col = True

        self.auth_penalty = 0  # authority penalty
        self.tactic_effect = {}
        self.coa = coa  # coat of arm image
        teamposlist = (self.gamebattle.team0poslist, self.gamebattle.team1poslist, self.gamebattle.team2poslist)
        self.gamebattle.allunitlist.append(self)
        self.gamebattle.allunitindex.append(self.gameid)

        self.team = team  # team
        self.ally_pos_list = teamposlist[self.team]
        if self.team == 1:
            self.enemy_pos_list = teamposlist[2]
        elif self.team == 2:
            self.enemy_pos_list = teamposlist[1]

        self.subunit_position_list = []
        self.frontline = {0: [], 1: [], 2: [], 3: []}  # frontline keep list of subunit at the front of each side in combat, same list index as above
        self.frontline_object = {0: [], 1: [], 2: [], 3: []}  # same as above but save object instead of index order:front, left, right, rear

        # v Set up subunit position list for drawing
        width, height = 0, 0
        subunitnum = 0  # Number of subunit based on the position in row and column
        for subunit in self.armysubunit.flat:
            width += self.imgsize[0]
            self.subunit_position_list.append((width, height))
            subunitnum += 1
            if subunitnum >= len(self.armysubunit[0]):  # Reach the last subunit in the row, go to the next one
                width = 0
                height += self.imgsize[1]
                subunitnum = 0
        # ^ End subunit position list

    def change_pos_scale(self):
        """Change position variable to new camera scale"""
        self.truenumber_pos = self.number_pos * (11 - self.zoom)

    def setup_army(self, gamestart=True):
        """Grab stat from all subunit in the parentunit"""
        self.troopnumber = 0
        self.stamina = 0
        self.morale = 0
        allspeed = []  # list of subunit spped, use to get the slowest one
        self.ammo = 0
        howmany = 0
        allshootrange = []  # list of shoot range, use to get the shortest and longest one

        # v Grab subunit stat
        notbroken = False
        for subunit in self.subunit_sprite:
            if subunit.state != 100:  # only get stat from alive subunit
                self.troopnumber += subunit.troopnumber
                self.stamina += subunit.stamina
                self.morale += subunit.morale
                allspeed.append(subunit.speed)
                self.ammo += subunit.magazine_left
                if subunit.shootrange > 0:
                    allshootrange.append(subunit.shootrange)
                subunit.skill_cond = self.skill_cond
                howmany += 1
                if subunit.state != 99:  # check if unit completely broken
                    notbroken = True
        self.troopnumber = int(self.troopnumber)  # convert to int to prevent float decimal

        if notbroken is False:
            self.state = 99  # completely broken
            self.can_split_row = False  # can not split unit
            self.can_split_col = False
        # ^ End grab subunit stat

        # v calculate stat for parentunit related calculation
        if self.troopnumber > 0:
            self.stamina = int(self.stamina / howmany)  # Average stamina of all subunit
            self.morale = int(self.morale / howmany)  # Average moorale of all subunit
            self.speed = min(allspeed)  # use slowest subunit
            self.walkspeed, self.runspeed = self.speed / 20, self.speed / 15
            if self.state in (1, 3, 5):
                self.rotatespeed = round(self.walkspeed * 50 / (len(self.armysubunit[0]) * len(
                    self.armysubunit)))  # rotate speed is based on move speed and parentunit block size (not subunit total number)
            else:
                self.rotatespeed = round(self.runspeed * 50 / (len(self.armysubunit[0]) * len(self.armysubunit)))

            if self.rotatespeed > 20:
                self.rotatespeed = 20  # state 10 melee combat rotate is auto placement
            if self.rotatespeed < 1:  # no less than speed 1, it will be too slow or can't rotate with speed 0
                self.rotatespeed = 1

            if len(allshootrange) > 0:
                self.maxrange = max(allshootrange)  # Max shoot range of all subunit
                self.minrange = min(allshootrange)  # Min shoot range of all subunit
            if gamestart is False:  # Only do once when game start
                self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.stamina, round(self.stamina * 0.75), round(
                    self.stamina * 0.50), round(self.stamina * 0.25)
                self.ammolist = (round(self.ammo * 0.75), round(self.ammo * 0.50), round(self.ammo * 0.25), 0, -1)
                self.last_health_state, self.last_stamina_state = 4, 4
                self.maxmorale = self.morale
                self.maxhealth, self.health75, self.health50, self.health25, = self.troopnumber, round(self.troopnumber * 0.75), round(
                    self.troopnumber * 0.50), round(self.troopnumber * 0.25)
            self.moralestate = round((self.morale * 100) / self.maxmorale)
            self.staminastate = round((self.stamina * 100) / self.maxstamina)
        # ^ End cal stat

    def setup_frontline(self):
        """Setup frontline array"""

        # v check if complelely empty side row/col, then delete and re-adjust array
        stoploop = False
        while stoploop is False:  # loop until no longer find completely empty row/col
            stoploop = True
            whoarray = self.armysubunit
            fullwhoarray = [whoarray, np.fliplr(whoarray.swapaxes(0, 1)), np.rot90(whoarray),
                            np.fliplr([whoarray])[0]]  # rotate the array based on the side
            whoarray = [whoarray[0], fullwhoarray[1][0], fullwhoarray[2][0], fullwhoarray[3][0]]
            for index, whofrontline in enumerate(whoarray):
                if any(subunit != 0 for subunit in whofrontline) is False: # has completely empty outer row or column, remove them
                    if index == 0:  # front side
                        self.armysubunit = self.armysubunit[1:]
                        for subunit in self.subunit_sprite:
                            subunit.unitposition = (subunit.unitposition[0], subunit.unitposition[1] - (self.imgsize[1] / 8))
                    elif index == 1:  # left side
                        self.armysubunit = np.delete(self.armysubunit, 0, 1)
                        for subunit in self.subunit_sprite:
                            subunit.unitposition = (subunit.unitposition[0] - (self.imgsize[0] / 8), subunit.unitposition[1])
                    elif index == 2:  # right side
                        self.armysubunit = np.delete(self.armysubunit, -1, 1)
                    elif index == 3:  # rear side
                        self.armysubunit = np.delete(self.armysubunit, -1, 0)

                    if len(self.armysubunit) > 0: # still has row left
                        oldwidthbox, oldheightbox = self.base_width_box, self.base_height_box
                        self.base_width_box, self.base_height_box = len(self.armysubunit[0]) * (self.imgsize[0] + 10) / 20, \
                                                                    len(self.armysubunit) * (self.imgsize[1] + 2) / 20

                        numberpos = (self.base_pos[0] - self.base_width_box,
                                     (self.base_pos[1] + self.base_height_box))  # find position for number text
                        self.number_pos = self.rotationxy(self.base_pos, numberpos, self.radians_angle)
                        self.change_pos_scale()

                        oldwidthbox = oldwidthbox - self.base_width_box
                        oldheightbox = oldheightbox - self.base_height_box
                        if index == 0:  # front
                            newpos = (self.base_pos[0], self.base_pos[1] + oldheightbox)
                        elif index == 1:  # left
                            newpos = (self.base_pos[0] + oldwidthbox, self.base_pos[1])
                        elif index == 2:  # right
                            newpos = (self.base_pos[0] - oldwidthbox, self.base_pos[1])
                        else:  # rear
                            newpos = (self.base_pos[0], self.base_pos[1] - oldheightbox)
                        self.base_pos = self.rotationxy(self.base_pos, newpos, self.radians_angle)
                        self.last_base_pos = self.base_pos

                        frontpos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
                        self.front_pos = self.rotationxy(self.base_pos, frontpos, self.radians_angle)
                    stoploop = False
        # ^ End check completely empty row

        gotanother = True  # keep finding another subunit while true

        for index, whofrontline in enumerate(whoarray):
            newwhofrontline = whofrontline.copy()
            dead = np.where((newwhofrontline == 0) | (newwhofrontline == 1))  # replace the dead in frontline with other subunit in the same column
            for deadsquad in dead[0]:
                run = 0
                while gotanother:
                    if fullwhoarray[index][run, deadsquad] not in (0, 1):
                        newwhofrontline[deadsquad] = fullwhoarray[index][run, deadsquad]
                        gotanother = False
                    else:
                        run += 1
                        if len(fullwhoarray[index]) == run:
                            newwhofrontline[deadsquad] = 0
                            gotanother = False
                gotanother = True  # reset for another loop
            emptyarray = newwhofrontline
            newwhofrontline = emptyarray.copy()

            self.frontline[index] = newwhofrontline

        self.frontline_object = self.frontline.copy()  # frontline array as object instead of index
        for arrayindex, whofrontline in enumerate(list(self.frontline.values())):
            self.frontline_object[arrayindex] = self.frontline_object[arrayindex].tolist()
            for index, stuff in enumerate(whofrontline):
                for subunit in self.subunit_sprite:
                    if subunit.gameid == stuff:
                        self.frontline_object[arrayindex][index] = subunit
                        break

        for subunit in self.subunit_sprite:  # assign frontline variable to subunit for only front side
            subunit.frontline = False
            if subunit in self.frontline_object[0]:
                subunit.frontline = True

        self.auth_penalty = 0
        for subunit in self.subunit_sprite:
            if subunit.state != 100:
                self.auth_penalty += subunit.auth_penalty  # add authority penalty of all alive subunit

    # def useskill(self,whichskill):
    #     #charge skill
    #     skillstat = self.skill[list(self.skill)[0]].copy()
    #     if whichskill == 0:
    #         self.skill_effect[self.chargeskill] = skillstat
    #         if skillstat[26] != 0:
    #             self.status_effect[self.chargeskill] = skillstat[26]
    #         self.skill_cooldown[self.chargeskill] = skillstat[4]
    #     # other skill
    #     else:
    #         if skillstat[1] == 1:
    #             self.skill[whichskill]
    #         self.skill_cooldown[whichskill] = skillstat[4]
    # self.skill_cooldown[whichskill] =

    def set_subunit_target(self, target = "rotate", resetpath = False):
        """generate all four side, hitbox and subunit positions
        target parameter can be "rotate" for simply rotate whole unit but not move or tuple/vector2 for target position to move
        resetpath argument True will reset sub-unit command queue"""
        if target == "rotate":  # rotate unit before moving
            unit_topleft = pygame.Vector2(self.base_pos[0] - self.base_width_box,  # get the top left corner of sprite to generate subunit position
                                         self.base_pos[1] - self.base_height_box)

            for subunit in self.subunit_sprite:  # generate position of each subunit
                if subunit.state != 99 or (subunit.state == 99 and self.retreat_start):
                    newtarget = unit_topleft + subunit.unitposition
                    if resetpath:
                        subunit.command_target.append(pygame.Vector2(
                            self.rotationxy(self.base_pos, newtarget, self.radians_angle)))
                    else:
                        subunit.command_target = pygame.Vector2(
                            self.rotationxy(self.base_pos, newtarget, self.radians_angle))  # rotate according to sprite current rotation
                        subunit.new_angle = self.new_angle

        else:  # moving unit to specific target position
            unit_topleft = pygame.Vector2(target[0] - self.base_width_box,
                                         target[1])  # get the top left corner of sprite to generate subunit position

            for subunit in self.subunit_sprite:  # generate position of each subunit
                if subunit.state != 99 or (subunit.state == 99 and self.retreat_start):
                    subunit.new_angle = self.new_angle
                    newtarget = unit_topleft + subunit.unitposition
                    if resetpath:
                        subunit.command_target.append(pygame.Vector2(
                            self.rotationxy(target, newtarget, self.radians_angle)))
                    else:
                        subunit.command_target = pygame.Vector2(
                            self.rotationxy(target, newtarget, self.radians_angle))  # rotate according to sprite current rotation

    def authrecal(self):
        """recalculate authority from all alive leaders"""
        self.authority = int(
            (self.leader[0].authority / 2) + (self.leader[1].authority / 4) + (self.leader[2].authority / 4) + (self.leader[3].authority / 10))
        self.leader_social = self.leader[0].social
        if self.authority > 0:
            bigarmysize = self.armysubunit > 0
            bigarmysize = bigarmysize.sum()
            if bigarmysize > 20:  # army size larger than 20 will reduce main leader authority
                self.authority = int((self.teamcommander.authority / 2) +
                                     (self.leader[0].authority / 2 * (100 - bigarmysize) / 100) + self.leader[1].authority / 2 + self.leader[
                                         2].authority / 2 +
                                     self.leader[3].authority / 4)
            else:
                self.authority = int(self.authority + (self.teamcommander.authority / 2))

    def startset(self, squadgroup):
        """Setup various variables at the start of battle or when new unit spawn/split"""
        self.setup_army(False)
        self.setup_frontline()
        self.oldarmyhealth, self.oldarmystamina = self.troopnumber, self.stamina
        self.spritearray = self.armysubunit
        self.leader_social = self.leader[0].social

        # v assign team leader commander to every parentunit in team if this is commander parentunit
        if self.commander:
            whicharmy = self.gamebattle.team1unit
            if self.team == 2:  # team2
                whicharmy = self.gamebattle.team2unit
            for army in whicharmy:
                army.teamcommander = self.leader[0]
        # ^ End assign commander

        self.authrecal()
        self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                            (self.leader[0].cavcommand - 5) * 0.1]  # parentunit leader command buff

        for subunit in squadgroup:
            self.spritearray = np.where(self.spritearray == subunit.gameid, subunit, self.spritearray)

        parentunittopleft = pygame.Vector2(self.base_pos[0] - self.base_width_box,
                                           # get the top left corner of sprite to generate subunit position
                                           self.base_pos[1] - self.base_height_box)
        for subunit in self.subunit_sprite:  # generate start position of each subunit
            subunit.base_pos = parentunittopleft + subunit.unitposition
            subunit.base_pos = pygame.Vector2(self.rotationxy(self.base_pos, subunit.base_pos, self.radians_angle))
            subunit.pos = subunit.base_pos * subunit.zoom
            subunit.rect.center = subunit.pos
            subunit.base_target = subunit.base_pos
            subunit.command_target = subunit.base_pos  # rotate according to sprite current rotation
            subunit.make_front_pos()

        self.change_pos_scale()

    def update(self, weather, squadgroup, dt, zoom, mousepos, mouseup):
        # v Camera zoom change
        if self.lastzoom != zoom:
            if self.lastzoom != zoom:  # camera zoom is changed
                self.lastzoom = zoom
                self.zoom_change = True
                self.zoom = 11 - zoom  # save scale
                self.change_pos_scale()  # update parentunit sprite according to new scale
        # ^ End zoom

        # v Setup frontline again when any subunit die
        if self.deadchange:
            self.setup_frontline()

            for subunit in self.subunit_sprite:
                subunit.base_morale -= (30 * subunit.mental)
            self.deadchange = False
        # ^ End setup frontline when subunit die

        # v remove when troop number reach 0
        if len(self.armysubunit) < 1:
            self.stamina, self.morale, self.speed = 0, 0, 0

            leaderlist = [leader for leader in self.leader]  # create temp list to remove leader
            for leader in leaderlist:  # leader retreat
                if leader.state < 90:  # Leaders flee when parentunit destroyed
                    leader.state = 96
                    leader.gone()

            self.state = 100
        # ^ End remove

        if self.state != 100:
            self.ally_pos_list[self.gameid] = self.base_pos  # update current position to team position list

            if self.justselected:  # add highlight to subunit in selected unit
                for subunit in self.subunit_sprite:
                    subunit.zoomscale()
                self.justselected = False

            elif self.selected and self.gamebattle.last_selected != self:  # no longer selected
                self.selected = False
                for subunit in self.subunit_sprite:  # remove highlight
                    subunit.image_original = subunit.image_original2.copy()
                    subunit.rotate()
                    subunit.selected = False

            if dt > 0:  # Set timer for complex calculation that cannot happen every loop as it drop too much fps
                self.timer += dt
                self.gamebattle.teamtroopnumber[self.team] += self.troopnumber
                if self.timer >= 1:
                    self.setup_army()

                    # v Find near enemy base_target
                    self.near_target = {}  # Near base_target is enemy that is nearest
                    for n, thisside in self.enemy_pos_list.items():
                        self.near_target[n] = pygame.Vector2(thisside).distance_to(self.base_pos)
                    self.near_target = {k: v for k, v in sorted(self.near_target.items(), key=lambda item: item[1])}  # sort to the closest one
                    for n in self.enemy_pos_list:
                        self.near_target[n] = self.enemy_pos_list[n]  # change back near base_target list value to vector with sorted order
                    # ^ End find near base_target

                    # v Check if any subunit still fighting, if not change to idle state
                    if self.state == 10:
                        stopfight = True
                        for subunit in self.subunit_sprite:
                            if subunit.state == 10:
                                stopfight = False
                                break
                        if stopfight:
                            self.state = 0
                    # ^ End check fighting

                    self.timer -= 1  # reset timer, not reset to 0 because higher speed can cause inconsistency in update timing

                # v Recal stat involve leader if one die
                if self.leader_change:
                    self.authrecal()
                    self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                                        (self.leader[0].cavcommand - 5) * 0.1]
                    self.leader_change = False
                # ^ End recal stat when leader die

                if self.range_combat_check:
                    self.state = 11  # can only shoot if range_combat_check is true

                # v skirmishing
                if self.hold == 1 and self.state not in (97, 98, 99):
                    minrange = self.minrange  # run away from enemy that reach minimum range
                    if minrange < 50:
                        minrange = 50  # for in case minrange is 0 (melee troop only)
                    if list(self.near_target.values())[0].distance_to(self.base_pos) <= minrange:  # if there is any enemy in minimum range
                        self.state = 96  # retreating
                        basetarget = self.base_pos - ((list(self.near_target.values())[0] - self.base_pos) / 5)  # generate base_target to run away

                        if basetarget[0] < 1:  # can't run away when reach corner of map same for below if elif
                            basetarget[0] = 1
                        elif basetarget[0] > 998:
                            basetarget[0] = 998
                        if basetarget[1] < 1:
                            basetarget[1] = 1
                        elif basetarget[1] > 998:
                            basetarget[1] = 998

                        self.processcommand(basetarget, True, True)  # set base_target position to run away
                # ^ End skirmishing

                # v Chase base_target and rotate accordingly
                if self.state in (3, 4, 5, 6, 10) and self.command_state in (3, 4, 5, 6) and self.attack_target is not None and self.hold == 0:
                    if self.attack_target.state != 100:
                        if self.collide is False:
                            self.state = self.command_state  # resume attack command
                            self.set_target(self.attack_target.leadersubunit.base_pos)  # set base_target to cloest enemy's side
                            self.base_attack_pos = self.base_target
                            self.new_angle = self.setrotate()  # keep rotating while chasing
                    else:  # enemy dead stop chasing
                        self.attack_target = None
                        self.base_attack_pos = 0
                        self.processcommand(self.front_pos, othercommand=1)
                # ^ End chase

                # v Morale/authority state function
                if self.authority <= 0:  # disobey
                    self.state = 95
                    if random.randint(0, 100) == 100 and self.leader[0].state < 90:  # chance to recover
                        self.leader[0].authority += 20
                        self.authrecal()

                if self.morale <= 10:  # Retreat state when morale lower than 10
                    if self.state not in (98, 99):
                        self.state = 98
                    if self.retreat_start is False:
                        self.retreat_start = True

                elif self.state == 98 and self.morale >= 50:  # quit retreat when morale reach increasing limit
                    self.state = 0  # become idle, not resume previous command
                    self.retreat_start = False
                    self.retreat_way = None
                    self.processcommand(self.base_pos, False, False, othercommand=1)

                if self.retreat_start and self.state != 96:
                    if self.retreat_way is None:  # not yet start retreat or previous retreat way got blocked
                        retreatside = (
                            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[0] if subunit != 0) + 2,
                            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[1] if subunit != 0) + 1,
                            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[2] if subunit != 0) + 1,
                            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[3] if subunit != 0))

                        thisindex = retreatside.index(min(retreatside))  # find side with least subunit fighting to retreat, rear always prioritised
                        if thisindex == 0:  # front
                            self.retreat_way = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find position to retreat
                        elif thisindex == 1:  # left
                            self.retreat_way = (self.base_pos[0] - self.base_width_box, self.base_pos[1])  # find position to retreat
                        elif thisindex == 2:  # right
                            self.retreat_way = (self.base_pos[0] + self.base_width_box, self.base_pos[1])  # find position to retreat
                        else:  # rear
                            self.retreat_way = (self.base_pos[0], (self.base_pos[1] + self.base_height_box))  # find rear position to retreat
                        self.retreat_way = [self.rotationxy(self.base_pos, self.retreat_way, self.radians_angle), thisindex]
                        basetarget = self.base_pos + ((self.retreat_way[0] - self.base_pos) * 1000)

                        self.processretreat(basetarget)
                        # if random.randint(0, 100) > 99:  # change side via surrender or betrayal
                        #     if self.team == 1:
                        #         self.gamebattle.allunitindex = self.switchfaction(self.gamebattle.team1unit, self.gamebattle.team2unit,
                        #                                                         self.gamebattle.team1poslist, self.gamebattle.allunitindex,
                        #                                                         self.gamebattle.enactment)
                        #     else:
                        #         self.gamebattle.allunitindex = self.switchfaction(self.gamebattle.team2unit, self.gamebattle.team1unit,
                        #                                                         self.gamebattle.team2poslist, self.gamebattle.allunitindex,
                        #                                                         self.gamebattle.enactment)
                        #     self.gamebattle.eventlog.addlog([0, str(self.leader[0].name) + "'s parentunit surrender"], [0, 1])
                        #     self.gamebattle.setuparmyicon()
                # ^ End retreat function

                # v Rotate Function
                if self.angle != self.new_angle and self.state != 10 and self.stamina > 0 and self.collide is False:
                    self.rotatecal = abs(self.new_angle - self.angle)  # amount of angle left to rotate
                    self.rotatecheck = 360 - self.rotatecal  # rotate distance used for preventing angle calculation bug (pygame rotate related)
                    self.moverotate = True
                    self.radians_angle = math.radians(360 - self.angle)  # for subunit rotate
                    if self.angle < 0:  # negative angle (rotate to left side)
                        self.radians_angle = math.radians(-self.angle)

                    # vv Rotate logic to continuously rotate based on angle and shortest length
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
                    # ^^ End rotate tiny

                    self.set_subunit_target()  # generate new pos related to side

                elif self.moverotate and self.angle == self.new_angle:  # Finish
                    self.moverotate = False
                    if self.rotateonly is False:  # continue moving to base_target after finish rotate
                        self.set_subunit_target(self.base_target)
                    else:
                        self.state = 0  # idle state
                        self.command_state = self.state
                        self.rotateonly = False  # reset rotate only condition
                # ^ End rotate function

                if self.state not in (0, 95) and self.front_pos.distance_to(self.command_target) < 1:  # reach destination and not in combat
                    nothalt = False  # check if any subunit in combat
                    for subunit in self.subunit_sprite:
                        if subunit.state == 10:
                            nothalt = True
                        if subunit.unit_leader and subunit.state != 10:
                            nothalt = False
                            break
                    if nothalt is False:
                        self.retreat_start = False  # reset retreat
                        self.revert = False  # reset revert order
                        self.processcommand(self.base_target, othercommand=1)  # reset command base_target state will become 0 idle

                # v Perform range attack, can only enter range attack state after finishing rotate
                shootrange = self.maxrange
                if self.use_min_range == 0:  # use minimum range to shoot
                    shootrange = self.minrange

                if self.state in (5, 6) and self.moverotate is False and (
                        (self.attack_target is not None and self.base_pos.distance_to(self.attack_target.base_pos) <= shootrange)
                        or self.base_pos.distance_to(self.base_attack_pos) <= shootrange):  # in shoot range
                    self.set_target(self.front_pos)
                    self.range_combat_check = True  # set range combat check to start shooting
                elif self.state == 11 and self.attack_target is not None and self.base_pos.distance_to(self.attack_target.base_pos) > shootrange \
                        and self.hold == 0 and self.collide is False:  # chase base_target if it go out of range and hold condition not hold
                    self.state = self.command_state  # set state to attack command state
                    self.range_combat_check = False  # stop range combat check
                    self.set_target(self.attack_target.base_pos)  # move to new base_target
                    self.new_angle = self.setrotate()  # also keep rotate to base_target
                # ^ End range attack state

        else:  # dead parentunit
            # v parentunit just got killed
            if self.got_killed is False:
                if self.team == 1:
                    self.die(self.gamebattle)
                else:
                    self.die(self.gamebattle)

                self.gamebattle.setup_uniticon()  # reset army icon (remove dead one)
                self.gamebattle.eventlog.addlog([0, str(self.leader[0].name) + "'s parentunit is destroyed"],
                                              [0, 1])  # put destroyed event in war and army log

                self.kill()
                for subunit in self.subunit_sprite:
                    subunit.kill()
            # ^ End got killed

    def set_target(self, pos):
        """set new base_target, scale base_target from base_target according to zoom scale"""
        self.base_target = pygame.Vector2(pos)  # Set new base base_target
        self.set_subunit_target(self.base_target)

    def revertmove(self):
        """Only subunit will rotate to move, not the entire unit"""
        self.new_angle = self.angle
        self.moverotate = False  # will not rotate to move
        self.revert = True
        newangle = self.setrotate()
        for subunit in self.subunit_sprite:
            subunit.new_angle = newangle

    def processcommand(self, targetpoint, runcommand=False, revertmove=False, enemy=None, othercommand=0):
        """Process input order into state and subunit base_target action
        othercommand parameter 0 is default command, 1 is natural pause, 2 is order pause"""
        if othercommand == 0:  # move or attack command
            self.state = 1

            if self.attack_place or (enemy is not None and (self.team != enemy.team)):  # attack
                if self.ammo <= 0 or self.forced_melee:  # no magazine_left to shoot or forced attack command
                    self.state = 3  # move to melee
                elif self.ammo > 0:  # have magazine_left to shoot
                    self.state = 5  # Move to range attack
                if self.attack_place:  # attack specific location
                    self.set_target(targetpoint)
                    # if self.magazine_left > 0:
                    self.base_attack_pos = targetpoint
                else:
                    self.attack_target = enemy
                    self.base_attack_pos = enemy.base_pos
                    self.set_target(self.base_attack_pos)

            else:
                self.set_target(targetpoint)

            if runcommand or self.runtoggle == 1:
                self.state += 1  # run state

            self.command_state = self.state

            self.range_combat_check = False
            self.command_target = self.base_target
            self.new_angle = self.setrotate()

            if revertmove:  # revert subunit without rotate, cannot run in this state
                self.revertmove()
                # if runcommand or self.runtoggle:
                #     self.state -= 1

            if self.charging:  # change order when attacking will cause authority penalty
                self.leader[0].authority -= self.auth_penalty
                self.authrecal()

        elif othercommand in (1, 2) and self.state != 10:  # Pause all action command except combat
            if self.charging and othercommand == 2:  # halt order instead of auto halt
                self.leader[0].authority -= self.auth_penalty  # decrease authority of the first leader for stop charge
                self.authrecal()  # recal authority

            self.state = 0  # go into idle state
            self.command_state = self.state  # reset command state
            self.set_target(self.front_pos)  # set base_target at self
            self.command_target = self.base_target  # reset command base_target
            self.range_combat_check = False  # reset range combat check
            self.new_angle = self.setrotate()  # set rotation base_target

    def processretreat(self, pos):
        self.state = 96  # controlled retreat state (not same as 98)
        self.command_state = self.state  # command retreat
        self.leader[0].authority -= self.auth_penalty  # retreat reduce main leader authority
        if self.charging:  # change order when attacking will cause authority penalty
            self.leader[0].authority -= self.auth_penalty
        self.authrecal()
        self.retreat_start = True  # start retreat process
        self.set_target(pos)
        self.revertmove()
        self.command_target = self.base_target

    def command(self, pos, mouse_right, double_mouse_right, target, keystate, othercommand=0):
        """othercommand is special type of command such as stop all action, raise flag, decimation, duel and so on"""
        if self.control and self.state not in (95, 97, 98, 99):
            self.revert = False
            self.retreat_start = False  # reset retreat
            self.rotateonly = False
            self.forced_melee = False
            self.attack_target = None
            self.base_attack_pos = 0
            self.attack_place = False
            self.range_combat_check = False

            # register user keyboard
            if keystate is not None and keystate[pygame.K_LCTRL]:
                self.forced_melee = True
            if keystate is not None and keystate[pygame.K_LALT]:
                self.attack_place = True

            if self.state != 100:
                if mouse_right and 1 <= pos[0] < 998 and 1 <= pos[1] < 998:
                    if self.state in (10, 96) and target is None:
                        self.processretreat(pos)  # retreat
                    else:
                        for subunit in self.subunit_sprite:
                            subunit.attacking = True
                        # if self.state == 10:
                        if keystate is not None and keystate[pygame.K_LSHIFT]:
                            self.rotateonly = True
                        if keystate is not None and keystate[pygame.K_z]:
                            self.revert = True
                        self.processcommand(pos, double_mouse_right, self.revert, target)
                elif othercommand != 0:
                    self.processcommand(pos, double_mouse_right, self.revert, target, othercommand)

    def switchfaction(self, oldgroup, newgroup, oldposlist, enactment):
        """Change army group and gameid when change side"""
        self.colour = (144, 167, 255)  # team1 colour
        self.control = True  # TODO need to change later when player can choose team

        if self.team == 2:
            self.team = 1  # change to team 1
        else:  # originally team 1, new team would be 2
            self.team = 2  # change to team 2
            self.colour = (255, 114, 114)  # team2 colour
            if enactment is False:
                self.control = False

        oldgroup.remove(self)  # remove from old team group
        newgroup.append(self)  # add to new team group
        oldposlist.pop(self.gameid)  # remove from old pos list
        self.gameid = newgameid  # change game id
        # self.changescale() # reset scale to the current zoom
        self.icon.changeimage(changeside=True)  # change army icon to new team

    def placement(self, mouse_pos, mouse_right, mouse_rightdown, double_mouse_right):
        if double_mouse_right:  # move unit to new pos
            self.base_pos = mouse_pos
            self.last_base_pos = self.base_pos

        elif mouse_right or mouse_rightdown:  # rotate unit
            self.angle = self.setrotate(mouse_pos)
            self.new_angle = self.angle
            self.radians_angle = math.radians(360 - self.angle)  # for subunit rotate
            if self.angle < 0:  # negative angle (rotate to left side)
                self.radians_angle = math.radians(-self.angle)

        frontpos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
        self.front_pos = self.rotationxy(self.base_pos, frontpos, self.radians_angle)
        numberpos = (self.base_pos[0] - self.base_width_box,
                     (self.base_pos[1] + self.base_height_box))  # find position for number text
        self.number_pos = self.rotationxy(self.base_pos, numberpos, self.radians_angle)
        self.change_pos_scale()

        self.base_target = self.base_pos
        self.command_target = self.base_target  # reset command base_target
        unit_topleft = pygame.Vector2(self.base_pos[0] - self.base_width_box,
                                      # get the top left corner of sprite to generate subunit position
                                      self.base_pos[1] - self.base_height_box)

        for subunit in self.subunit_sprite:  # generate position of each subunit
            newtarget = unit_topleft + subunit.unitposition
            subunit.base_pos = pygame.Vector2(
                subunit.rotationxy(self.base_pos, newtarget, self.radians_angle))  # rotate according to sprite current rotation
            subunit.pos = subunit.base_pos * subunit.zoom  # pos is for showing on screen
            subunit.angle = self.angle
            subunit.rotate()

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.icon
            del self.teamcommander
            del self.startwhere
            del self.subunit_sprite
            del self.near_target
            del self.leader
            del self.frontline_object
            del self.attack_target
            del self.leadersubunit
