import math
import random
import numpy as np
import pygame
import pygame.freetype
from pygame.transform import scale

from gamescript import gamelongscript

class Directionarrow(pygame.sprite.Sprite): #TODO make it work so it can be implemented again
    def __init__(self, who):
        """Layer must be called before sprite_init"""
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.who = who
        self.pos = self.who.pos
        self.who.directionarrow = self
        self.lengthgap = self.who.image.get_height() / 2
        self.length = self.who.pos.distance_to(self.who.basetarget) + self.lengthgap
        self.previouslength = self.length
        self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        # self.image_original = self.image.copy()
        # pygame.draw.line(self.image, (0, 0, 0), (self.image.get_width()/2, 0),(self.image.get_width()/2,self.image.get_height()), 5)
        self.image = pygame.transform.rotate(self.image, self.who.angle)
        self.rect = self.image.get_rect(midbottom=self.who.frontsidepos)

    def update(self, zoom):
        self.length = self.who.pos.distance_to(self.who.basetarget) + self.lengthgap
        distance = self.who.frontsidepos.distance_to(self.who.basetarget) + self.lengthgap
        if self.length != self.previouslength and distance > 2 and self.who.state != 0:
            self.pos = self.who.pos
            self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
            self.image.fill((0, 0, 0))
            self.image = pygame.transform.rotate(self.image, self.who.angle)
            self.rect = self.image.get_rect(midbottom=self.who.frontsidepos)
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

        self.font = pygame.font.SysFont("timesnewroman", int(12 * self.heightadjust))

        self.who = who
        self.textcolour = pygame.Color('blue')
        if self.who.team == 2:
            self.textcolour = pygame.Color('red')
        self.pos = self.who.truenumberpos
        self.number = self.who.troopnumber
        self.zoom = 1

        self.image = self.render(str(self.number), self.font, self.textcolour)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, *args, **kwargs) -> None:
        if self.pos != self.who.truenumberpos: # new position
            self.pos = self.who.truenumberpos
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.zoom != args[2]: # zoom argument
            self.zoom = int(args[2])
            zoom = (11 - self.zoom) / 2
            if zoom < 1:
                zoom = 1
            newfontsize = int(60 / zoom * self.heightadjust)
            self.font = pygame.font.SysFont("timesnewroman", newfontsize)
            self.image = self.render(str(self.number), self.font, self.textcolour)
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.number != self.who.troopnumber: # new troop number
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

    def render(self, text, font, gfcolor=pygame.Color('black'), ocolor=(255, 255, 255), opx=2):
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
    statuslist = None # status effect list
    maxzoom = 10 # max zoom allow
    maingame = None
    rotationxy = gamelongscript.rotationxy
    die = gamelongscript.die # die script
    setrotate = gamelongscript.setrotate
    formchangetimer = 10

    def __init__(self, startposition, gameid, squadlist, imgsize, colour, control, coa, commander, startangle, starthp=100, startstamina=100, team=0):
        """Although parentunit in code, this is referred as subunit ingame"""
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icon = None  ## for linking with army selection ui, got linked when icon created in gameui.Armyicon
        self.teamcommander = None # commander leader
        self.startwhere = []
        self.subunitspritearray = np.empty((8, 8), dtype=object) # array of subunit object(not index)
        self.subunitsprite = []
        self.leader = []
        self.leadersubunit = None # subunit that general is in, get added in leader first update
        self.neartarget = {} # list dict of nearby enemy parentunit, sorted by distance
        self.gameid = gameid # id of parentunit for reference in many function
        self.control = control # player control or not
        self.starthp = starthp # starting hp percentage
        self.startstamina = startstamina # starting stamina percentage
        self.armysubunit = squadlist # subunit array
        self.colour = colour # box colour according to team
        self.commander = commander # commander parentunit if true

        self.zoom = 10 # start with closest zoom
        self.lastzoom = 1 # zoom level without calculate with 11 - zoom for scale

        self.imgsize = imgsize
        self.basewidthbox, self.baseheightbox = len(self.armysubunit[0]) * (self.imgsize[0] + 10) / 20, len(self.armysubunit) * (self.imgsize[1] + 2) / 20

        self.basepos = pygame.Vector2(startposition)  # Basepos is for true pos that is used for ingame calculation
        self.lastbasepos = self.basepos
        self.baseattackpos = 0  # position of attack basetarget
        self.angle = startangle  # start at this angle
        if self.angle == 360: # 360 is 0 angle at the start, not doing this cause angle glitch when game start
            self.angle = 0
        self.newangle = self.angle
        self.radians_angle = math.radians(360 - startangle) # radians for apply angle to position (allsidepos and subunit)
        frontpos = (self.basepos[0], (self.basepos[1] - self.baseheightbox))  # find front position of unit
        self.frontpos = self.rotationxy(self.basepos, frontpos, self.radians_angle)
        self.set_target(self.frontpos)
        self.movementqueue = []
        self.basetarget = self.frontpos
        self.commandtarget = self.frontpos
        numberpos = (self.basepos[0] - self.basewidthbox,
                     (self.basepos[1] + self.baseheightbox))  # find position for number text
        self.numberpos = self.rotationxy(self.basepos, numberpos, self.radians_angle)
        self.changeposscale()

        #v Setup default beheviour check
        self.nextrotate = False
        self.selected = False # for checking if it currently selected or not
        self.justselected = False # for light up subunit when click
        self.zoomchange = False
        self.cansplitrow = False
        self.revert = False
        self.moverotate = False # for checking if the movement require rotation first or not
        self.rotatecal = 0 # for calculate how much angle to rotate to the basetarget
        self.rotatecheck = 0 # for checking if the new angle rotate pass the basetarget angle or not
        self.justsplit = False # subunit just got split
        self.leaderchange = False
        self.directionarrow = False
        self.rotateonly = False # Order parentunit to rotate to basetarget direction
        self.charging = False # For subunit charge skill activation
        self.forcedmelee = False # Force parentunit to melee attack
        self.attackplace = False # attack position instead of enemy
        self.forcedmarch = False
        self.changefaction = False # For initiating change faction function
        self.runtoggle = 0 # 0 = double right click to run, 1 = only one right click will make parentunit run
        self.shoothow = 0 # 0 = both arc and non-arc shot, 1 = arc shot only, 2 = forbid arc shot
        self.attackmode = 0 # frontline attack, 1 = formation attack, 2 = free for all attack,
        self.hold = 0  # 0 = not hold, 1 = skirmish/scout/avoid, 2 = hold
        self.fireatwill = 0  # 0 = fire at will, 1 = no fire
        self.retreatstart = False
        self.retreatway = None
        self.collide = False # for checking if subunit collide if yes stop moving
        self.rangecombatcheck = False
        self.attacktarget = None # attack basetarget, can be either int or parentunit object
        self.gotkilled = False # for checking if die() was performed when subunit die yet
        self.combatpreparestate = False # for initialise auto placement in melee combat
        self.gotcombatprepare = False # for checking if the enemy is the one doing auto placement or not
        self.stopcombatmove = False
        #^ End behaviour check

        #v setup default starting value
        self.troopnumber = 0 # sum
        self.stamina = 0 # average from all subunit
        self.morale = 0 # average from all subunit
        self.ammo = 0 # total ammo left of the whole parentunit
        self.oldammo = 0 # previous number of ammo for ammo bar checking
        self.minrange = 0 # minimum shoot range of all subunit inside this parentunit
        self.maxrange = 0 # maximum shoot range of all subunit inside this parentunit
        self.useminrange = 0 # use min or max range for walk/run (range) command
        self.useskillcond = 0 # skill condition for stamina reservation
        self.state = 0  # see gameui.py topbar for name of each state
        self.commandstate = self.state
        self.deadchange = False # for checking when subunit dead and run related code
        self.timer = random.random()
        self.statedelay = 3 # some state has delay before can change state, default at 3 seconds
        self.rotatespeed = 1
        self.brokenlimit = 0  # morale require for parentunit to stop broken state, will increase everytime broken state stop
        #^ End default starting value

        if np.array_split(self.armysubunit, 2)[0].size > 10 and np.array_split(self.armysubunit, 2)[1].size > 10: self.cansplitrow = True
        self.cansplitcol = False
        if np.array_split(self.armysubunit, 2, axis=1)[0].size > 10 and np.array_split(self.armysubunit, 2, axis=1)[1].size > 10: self.cansplitcol = True
        self.authpenalty = 0 # authority penalty
        self.tacticeffect = {}
        self.coa = coa # coat of arm image
        self.team = team # team

        self.squadpositionlist = []
        self.battleside = [None, None, None, None] # battleside with enemy object
        self.battlesideid = [0,0,0,0]  # index of battleside (enemy gameid fighting at the side of parentunit), list index: 0 = front 1 = left 2 =right 3 =rear
        self.frontline = {0: [], 1: [], 2: [], 3: []}  # frontline keep list of subunit at the front of each side in combat, same list index as above
        self.frontlineobject = {0: [], 1: [], 2: [], 3: []} # same as above but save object instead of index

        #v Set up subunit position list for drawing
        width, height = 0, 0
        squadnum = 0 # Number of subunit based on the position in row and column
        for squad in self.armysubunit.flat:
            width += self.imgsize[0]
            self.squadpositionlist.append((width, height))
            squadnum += 1
            if squadnum >= len(self.armysubunit[0]): # Reach the last subunit in the row, go to the next one
                width = 0
                height += self.imgsize[1]
                squadnum = 0
        #^ End subunit position list

    def changeposscale(self):
        """Change position variable to new camera scale"""
        self.truenumberpos = self.numberpos * (11 - self.zoom)

    def setuparmy(self, gamestart=True):
        """Grab stat from all subunit in the parentunit"""
        self.troopnumber = 0
        self.stamina = 0
        self.morale = 0
        allspeed = [] # list of subunit spped, use to get the slowest one
        self.ammo = 0
        howmany = 0
        allshootrange = [] # list of shoot range, use to get the shortest and longest one

        #v Grab subunit stat
        for subunit in self.subunitsprite:
            if subunit.state != 100: # only get stat from alive subunit
                self.troopnumber += subunit.troopnumber
                self.stamina += subunit.stamina
                self.morale += subunit.morale
                allspeed.append(subunit.speed)
                self.ammo += subunit.ammo
                if subunit.shootrange > 0:
                    allshootrange.append(subunit.shootrange)
                subunit.useskillcond = self.useskillcond
                howmany += 1
        self.troopnumber = int(self.troopnumber) # convert to int to prevent float decimal
        #^ End grab subunit stat

        #v calculate stat for parentunit related calculation
        if self.troopnumber > 0:
            self.stamina = int(self.stamina/howmany) # Average stamina of all subunit
            self.morale = int(self.morale/howmany) # Average moorale of all subunit
            self.speed = min(allspeed) # use slowest subunit
            self.walkspeed, self.runspeed = self.speed / 20, self.speed / 15
            if len(allshootrange) > 0:
                self.maxrange = max(allshootrange) # Max shoot range of all subunit
                self.minrange = min(allshootrange) # Min shoot range of all subunit
            if gamestart is False: # Only do once when game start
                self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.stamina, round(self.stamina * 0.75), round(
                    self.stamina * 0.50), round(self.stamina * 0.25)
                self.ammolist = (round(self.ammo * 0.75), round(self.ammo * 0.50), round(self.ammo * 0.25), 0, -1)
                self.lasthealthstate, self.laststaminastate, self.lastammostate = 4, 4, 0
                self.maxmorale = self.morale
                self.maxhealth, self.health75, self.health50, self.health25, = self.troopnumber, round(self.troopnumber * 0.75), round(
                    self.troopnumber * 0.50), round(self.troopnumber * 0.25)
            self.moralestate = round((self.morale * 100) / self.maxmorale)
            self.staminastate = round((self.stamina * 100) / self.maxstamina)
        #^ End cal stat

    def setupfrontline(self):
        """Setup frontline array"""

        #v check if complelely empty side row/col, then delete and re-adjust array
        stoploop = False
        while stoploop is False: # loop until no longer find completely empty row/col
            whoarray = self.armysubunit
            fullwhoarray = [whoarray, np.fliplr(whoarray.swapaxes(0, 1)), np.rot90(whoarray),
                            np.fliplr([whoarray])[0]]  # rotate the array based on the side
            whoarray = [whoarray[0], fullwhoarray[1][0], fullwhoarray[2][0], fullwhoarray[3][0]]
            for index, whofrontline in enumerate(whoarray):
                if any(subunit != 0 for subunit in whofrontline) is False:
                    if index == 0: # front side
                        self.armysubunit = np.delete(self.armysubunit, index, 0)
                        for subunit in self.subunitsprite:
                            subunit.armypos = (subunit.armypos[0], subunit.armypos[1] - (self.imgsize[1] / 8))
                    elif index == 1: # left side
                        self.armysubunit = np.delete(self.armysubunit, 0, 1)
                        for subunit in self.subunitsprite:
                            subunit.armypos = (subunit.armypos[0] - (self.imgsize[0] / 8), subunit.armypos[1])
                    elif index == 2: # right side
                        self.armysubunit = np.delete(self.armysubunit, -1, 1)
                    elif index == 3: # rear side
                        self.armysubunit = np.delete(self.armysubunit, -1, 0)

                    if len(self.armysubunit) > 0:
                        oldwidthbox, oldheightbox = self.basewidthbox, self.baseheightbox
                        self.basewidthbox, self.baseheightbox = len(self.armysubunit[0]) * (self.imgsize[0] + 10) / 20, \
                                                                len(self.armysubunit) * (self.imgsize[1] + 2) / 20

                        numberpos = (self.basepos[0] - self.basewidthbox,
                                     (self.basepos[1] + self.baseheightbox))  # find position for number text
                        self.numberpos = self.rotationxy(self.basepos, numberpos, self.radians_angle)
                        self.changeposscale()

                        oldwidthbox = oldwidthbox - self.basewidthbox
                        oldheightbox = oldheightbox - self.baseheightbox
                        if index == 0: # front
                            newpos = (self.basepos[0], self.basepos[1] + oldheightbox)
                        elif index == 1: # left
                            newpos = (self.basepos[0] + oldwidthbox, self.basepos[1])
                        elif index == 2: # right
                            newpos = (self.basepos[0] - oldwidthbox, self.basepos[1])
                        else: # rear
                            newpos = (self.basepos[0], self.basepos[1] - oldheightbox)
                        self.basepos = self.rotationxy(self.basepos, newpos, self.radians_angle)
                        self.lastbasepos = self.basepos

                        frontpos = (self.basepos[0], (self.basepos[1] - self.baseheightbox))  # find front position of unit
                        self.frontpos = self.rotationxy(self.basepos, frontpos, self.radians_angle)
                    else:
                        stoploop = True
                    break
            else:
                stoploop = True
        #^ End check completely empty row

        gotanother = True # keep finding another subunit while true

        for index, whofrontline in enumerate(whoarray):
            newwhofrontline = whofrontline.copy()
            dead = np.where((newwhofrontline == 0) | (newwhofrontline == 1)) # replace the dead in frontline with other subunit in the same column
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
                gotanother = True # reset for another loop
            emptyarray = newwhofrontline
            newwhofrontline = emptyarray.copy()

            self.frontline[index] = newwhofrontline

        self.frontlineobject = self.frontline.copy() # frontline array as object instead of index
        for arrayindex ,whofrontline in enumerate(list(self.frontline.values())):
            self.frontlineobject[arrayindex] = self.frontlineobject[arrayindex].tolist()
            for index, stuff in enumerate(whofrontline):
                for subunit in self.subunitsprite:
                    if subunit.gameid == stuff:
                        self.frontlineobject[arrayindex][index] = subunit
                        break

        for subunit in self.subunitsprite: # assign frontline variable to subunit for only front side
            subunit.frontline = False
            if subunit in self.frontlineobject[0]:
                subunit.frontline = True

        self.authpenalty = 0
        for subunit in self.subunitsprite:
            if subunit.state != 100:
                self.authpenalty += subunit.authpenalty # add authority penalty of all alive subunit

    # def useskill(self,whichskill):
    #     ##charge skill
    #     skillstat = self.skill[list(self.skill)[0]].copy()
    #     if whichskill == 0:
    #         self.skilleffect[self.chargeskill] = skillstat
    #         if skillstat[26] != 0:
    #             self.statuseffect[self.chargeskill] = skillstat[26]
    #         self.skillcooldown[self.chargeskill] = skillstat[4]
    #     ##other skill
    #     else:
    #         if skillstat[1] == 1:
    #             self.skill[whichskill]
    #         self.skillcooldown[whichskill] = skillstat[4]
    # self.skillcooldown[whichskill] =


    def setsubunittarget(self, target="rotate"):
        """generate all four side, hitbox and subunit positions"""
        if target == "rotate": # rotate unit before moving
            parentunittopleft = pygame.Vector2(self.basepos[0] - self.basewidthbox,  # get the top left corner of sprite to generate subunit position
                                               self.basepos[1] - self.baseheightbox)
            # parentunittopleft = self.rotationxy(self.basepos, parentunittopleft, self.radians_angle)
            # firstpos = pygame.Vector2(self.rotationxy(parentunittopleft, firstpos, self.radians_angle))


            for subunit in self.subunitsprite: # generate position of each subunit
                newtarget = parentunittopleft + subunit.armypos
                subunit.commandtarget = pygame.Vector2(self.rotationxy(self.basepos, newtarget, self.radians_angle)) # rotate according to sprite current rotation
                subunit.newangle = self.newangle

        elif target == "stop": # stop unit from moving
            pass

        else: # moving unit
            parentunittopleft = pygame.Vector2(target[0] - self.basewidthbox, # get the top left corner of sprite to generate subunit position
                                             target[1]) #- (self.baseheightbox/2)
            # parentunittopleft = self.rotationxy(basetarget, parentunittopleft, self.radians_angle)

            for subunit in self.subunitsprite: # generate position of each subunit
                subunit.newangle = self.newangle
                newtarget = parentunittopleft + subunit.armypos
                subunit.commandtarget = pygame.Vector2(self.rotationxy(target, newtarget, self.radians_angle)) # rotate according to sprite current rotation


    def authrecal(self):
        """recalculate authority from all alive leaders"""
        self.authority = int((self.leader[0].authority / 2) + (self.leader[1].authority / 4) + (self.leader[2].authority / 4) + (self.leader[3].authority / 10))
        self.leadersocial = self.leader[0].social
        if self.authority > 0:
            bigarmysize = self.armysubunit > 0
            bigarmysize = bigarmysize.sum()
            if bigarmysize > 20: # army size larger than 20 will reduce main leader authority
                self.authority = int((self.teamcommander.authority/2) +
                    (self.leader[0].authority / 2 * (100 - (bigarmysize)) / 100) + self.leader[1].authority / 2 + self.leader[2].authority / 2 +
                    self.leader[3].authority / 4)
            else:
                self.authority = int(self.authority + (self.teamcommander.authority/2))

    def startset(self, squadgroup):
        """Setup stuff at the start of game or when parentunit spawn"""
        self.setuparmy(False)
        self.setupfrontline()
        self.oldarmyhealth, self.oldarmystamina = self.troopnumber, self.stamina
        self.spritearray = self.armysubunit
        self.leadersocial = self.leader[0].social
        for leader in self.leader:
            if leader.gameid != 1:
                self.subunitsprite[leader.subunitpos].leader = leader  ## put in leader to subunit with the set pos

        # v assign team leader commander to every parentunit in team if this is commander parentunit
        if self.commander:
            whicharmy = self.maingame.team1army
            if self.team == 2:  # team2
                whicharmy = self.maingame.team2army
            for army in whicharmy:
                army.teamcommander = self.leader[0]
        # ^ End assign commander

        self.authrecal()
        self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                            (self.leader[0].cavcommand - 5) * 0.1] # parentunit leader command buff

        for subunit in squadgroup:
            self.spritearray = np.where(self.spritearray == subunit.gameid, subunit, self.spritearray)

        parentunittopleft = pygame.Vector2(self.basepos[0] - self.basewidthbox,
                                           # get the top left corner of sprite to generate subunit position
                                           self.basepos[1] - self.baseheightbox)
        for subunit in self.subunitsprite:  # generate start position of each subunit
            subunit.basepos = parentunittopleft + subunit.armypos
            subunit.basepos = pygame.Vector2(self.rotationxy(self.basepos, subunit.basepos, self.radians_angle))
            subunit.pos = subunit.basepos * subunit.zoom
            subunit.rect.center = subunit.pos
            subunit.commandtarget = subunit.basepos# rotate according to sprite current rotation
            subunit.makefrontsidepos()

        self.changeposscale()

    def update(self, weather, squadgroup, dt, zoom, mousepos, mouseup):
        #v redraw if troop num or stamina change
        if self.lastzoom != zoom:
            if self.lastzoom != zoom: # camera zoom is changed
                self.lastzoom = zoom
                self.zoomchange = True
                self.zoom = (11 - zoom) # save scale
                self.changeposscale() # update parentunit sprite according to new scale

        #v Setup frontline again when any subunit die
        if self.deadchange:
            self.setupfrontline()

            for subunit in self.subunitsprite:
                subunit.basemorale -= (30 * subunit.mental)
            self.deadchange = False
        #^ End setup frontline when subunit die

        #v remove when go pass the map border for any reason or when troop number reach 0
        if len(self.armysubunit) < 1 or self.basepos[0] < 0 or self.basepos[0] > 999 or self.basepos[1] < 0 or self.basepos[
            1] > 999:
            self.stamina, self.morale, self.speed = 0, 0, 0

            leaderlist = [leader for leader in self.leader]  # create temp list to remove leader
            for leader in leaderlist:  # leader retreat
                if leader.state < 90:  # Leaders may get flee/captured/die when parentunit destroyed
                    leader.state = 96
                    leader.gone()

            self.state = 100
        #^ End remove

        if self.state != 100:
            if self.team == 1:
                self.maingame.team1poslist[self.gameid] = self.basepos # update current position to team list
                thisposlist = self.maingame.team2poslist # update position list
            else:
                self.maingame.team2poslist[self.gameid] = self.basepos # update current position to team list
                thisposlist = self.maingame.team1poslist # update position list

            if dt > 0: # Set timer for complex calculation that cannot happen every loop as it drop too much fps
                self.timer += dt
                self.maingame.teamtroopnumber[self.team] += self.troopnumber
                if self.timer >= 1:
                    self.setuparmy()

                    #v Find near enemy basetarget
                    self.neartarget = {}  # Near basetarget is enemy that is nearest
                    for n, thisside in thisposlist.items():
                        self.neartarget[n] = pygame.Vector2(thisside).distance_to(self.basepos)
                    self.neartarget = {k: v for k, v in sorted(self.neartarget.items(), key=lambda item: item[1])} # sort to the closest one
                    for n in thisposlist:
                        self.neartarget[n] = thisposlist[n]  ## change back near basetarget list value to vector with sorted order
                    #^ End find near basetarget

                    #v Check if any subunit still fighting, if not change to idle state
                    if self.state == 10:
                        stopfight = True
                        for subunit in self.subunitsprite:
                            if subunit.state == 10:
                                stopfight = False
                                break
                        if stopfight:
                            self.state = 0
                    #^ End check fighting

                    self.timer -= 1 # reset timer, not reset to 0 because higher speed can cause inconsistency in update timing

            if self.justselected: # add highlight to subunit in selected unit
                for subunit in self.subunitsprite:
                    subunit.zoomscale()
                self.justselected = False

            elif self.selected and self.maingame.lastselected != self: # no longer selected
                self.selected = False
                for subunit in self.subunitsprite: # remove highlight
                    subunit.image_original = subunit.image_original2.copy()
                    subunit.rotate()
                    subunit.selected = False

            #v Recal stat involve leader if one die
            if self.leaderchange:
                self.authrecal()
                self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                                    (self.leader[0].cavcommand - 5) * 0.1]
                self.leaderchange = False
            #^ End recal stat when leader die

            if self.rangecombatcheck:
                self.state = 11 # can only shoot if rangecombatcheck is true


            #v skirmishing
            if self.hold == 1 and self.state not in (97,98,99):
                minrange = self.minrange # run away from enemy that reach minimum range
                if minrange < 50: minrange = 50 # for in case minrange is 0 (melee troop only)
                if list(self.neartarget.values())[0].distance_to(self.basepos) <= minrange: # if there is any enemy in minimum range
                    self.state = 96 # retreating
                    basetarget = self.basepos - ((list(self.neartarget.values())[0] - self.basepos)/5) # generate basetarget to run away, opposite direction at same distance

                    if basetarget[0] < 1: # can't run away when reach corner of map same for below if elif
                        basetarget[0] = 1
                    elif basetarget[0] > 998:
                        basetarget[0] = 998
                    if basetarget[1] < 1:
                        basetarget[1] = 1
                    elif basetarget[1] > 998:
                        basetarget[1] = 998

                    self.processcommand(basetarget, True, True) # set basetarget position to run away
            #^ End skirmishing

            # v Chase basetarget and rotate accordingly
            if self.state in (3, 4, 5, 6, 10) and self.commandstate in (3, 4, 5, 6) and self.attacktarget is not None and self.hold == 0:
                if self.attacktarget.state != 100:
                    if self.collide is False:
                        self.state = self.commandstate  # resume attack command
                        self.set_target(self.attacktarget.leadersubunit.basepos)  # set basetarget to cloest enemy's side
                        self.baseattackpos = self.basetarget
                        self.newangle = self.setrotate()  # keep rotating while chasing
                else: # enemy dead stop chasing
                    self.attacktarget = None
                    self.baseattackpos = 0
                    self.processcommand(self.frontpos, othercommand=1)
            # ^ End chase

            #v Morale/authority state function
            if self.authority <= 0: # disobey
                self.state = 95
                if random.randint(0,100) == 100 and self.leader[0].state < 90: # chance to recover
                    self.leader[0].authority += 20
                    self.authrecal()

            if round(self.morale) <= 10 and self.state != 97:  # Retreat state when morale lower than 20
                if self.state not in (98,99):
                    if self.brokenlimit > 50:  # begin checking broken state
                        if random.randint(self.brokenlimit, 100) > 80: # check whether unit enter broken state or not
                            self.morale, self.state = 0, 99 # Broken state
                    else:
                        self.state = 98
                if self.retreatstart is False:
                    self.retreatstart = True

            if self.state == 98 and self.morale >= self.brokenlimit/2:  # quit retreat when morale reach increasing limit
                self.state = 0 # become idle, not resume previous command
                self.retreatstart = False
                self.retreatway = None
                self.processcommand(self.basepos, False, False, othercommand=1)
                self.brokenlimit += random.randint(1,20)

            if self.retreatstart:
                retreatside = ([any(subunit.enemyfront != [] and subunit.enemyside != [] for subunit in self.frontlineobject[0] if subunit != 0)][0],
                               [any(subunit.enemyfront != [] and subunit.enemyside != [] for subunit in self.frontlineobject[1] if subunit != 0)][0],
                               [any(subunit.enemyfront != [] and subunit.enemyside != [] for subunit in self.frontlineobject[2] if subunit != 0)][0],
                               [any(subunit.enemyfront != [] and subunit.enemyside != [] for subunit in self.frontlineobject[3] if subunit != 0)][0])
                if any(side is False for side in retreatside): # has no collided side to flee
                    if self.state in (98, 99): # retreat/broken state
                        if self.retreatway is None or retreatside[self.retreatway[1]]: # not yet start retreat or previous retreat way got blocked
                            if retreatside[3] is False: # prioritise rear retreat
                                self.retreatway = (self.basepos[0], (self.basepos[1] + self.baseheightbox))  # find rear position to retreat
                                self.retreatway = [self.rotationxy(self.basepos, self.retreatway, self.radians_angle), 3]
                            else:
                                for index, side in enumerate(retreatside):
                                    if side is False:
                                        if index == 0: # front
                                            self.retreatway = (self.basepos[0], (self.basepos[1] - self.baseheightbox))  # find position to retreat
                                        elif index == 1: # left
                                            self.retreatway = (self.basepos[0] - self.basewidthbox, self.basepos[1])  # find position to retreat
                                        else: # right
                                            self.retreatway = (self.basepos[0] + self.basewidthbox, self.basepos[1])  # find position to retreat
                                        self.retreatway = [self.rotationxy(self.basepos, self.retreatway, self.radians_angle), index]
                            basetarget = self.basepos + ((self.retreatway[0] - self.basepos)*100)
                            self.processcommand(basetarget, True, True)
                else:  # no way to retreat, Fight to the death
                    self.state = 10
                    for subunit in self.subunitsprite:
                        if 9 not in subunit.statuseffect:
                            subunit.statuseffect[9] = self.statuslist[9].copy() # fight to the death status
                    # if random.randint(0, 100) > 99:  ## change side via surrender or betrayal
                    #     if self.team == 1:
                    #         self.maingame.allunitindex = self.switchfaction(self.maingame.team1army, self.maingame.team2army,
                    #                                                         self.maingame.team1poslist, self.maingame.allunitindex,
                    #                                                         self.maingame.enactment)
                    #     else:
                    #         self.maingame.allunitindex = self.switchfaction(self.maingame.team2army, self.maingame.team1army,
                    #                                                         self.maingame.team2poslist, self.maingame.allunitindex,
                    #                                                         self.maingame.enactment)
                    #     self.maingame.eventlog.addlog([0, str(self.leader[0].name) + "'s parentunit surrender"], [0, 1])
                    #     self.maingame.setuparmyicon()
            #^ End retreat function

            #v Rotate Function
            if self.angle != self.newangle and self.state != 10 and self.stamina > 0 and self.collide is False:
                self.rotatecal = abs(self.newangle - self.angle) # amount of angle left to rotate
                self.rotatecheck = 360 - self.rotatecal # rotate distance used for preventing angle calculation bug (pygame rotate related)
                self.moverotate = True
                self.radians_angle = math.radians(360 - self.angle) # for subunit rotate
                if self.angle < 0: # negative angle (rotate to left side)
                    self.radians_angle = math.radians(-self.angle)

                ## Rotate logic to continuously rotate based on angle and shortest length
                if self.state in (1, 3, 5):
                    self.rotatespeed = round(self.walkspeed * 50 / (len(self.armysubunit[0]) * len(self.armysubunit))) # rotate speed is based on move speed and parentunit block size (not subunit total number)
                else:
                    self.rotatespeed = round(self.runspeed * 50 / (len(self.armysubunit[0]) * len(self.armysubunit)))

                if self.rotatespeed > 20: self.rotatespeed = 20 # state 10 melee combat rotate is auto placement
                if self.rotatespeed < 1: # no less than speed 1, it will be too slow or can't rotate with speed 0
                    self.rotatespeed = 1

                rotatetiny = self.rotatespeed * dt # rotate little by little according to time
                if self.newangle > self.angle: # rotate to angle more than the current one
                    if self.rotatecal > 180: # rotate with the smallest angle direction
                        self.angle -= rotatetiny
                        self.rotatecheck -= rotatetiny
                        if self.rotatecheck <= 0: self.angle = self.newangle # if rotate pass basetarget angle, rotate to basetarget angle
                    else:
                        self.angle += rotatetiny
                        if self.angle > self.newangle: self.angle = self.newangle # if rotate pass basetarget angle, rotate to basetarget angle
                elif self.newangle < self.angle:  # rotate to angle less than the current one
                    if self.rotatecal > 180: # rotate with the smallest angle direction
                        self.angle += rotatetiny
                        self.rotatecheck -= rotatetiny
                        if self.rotatecheck <= 0: self.angle = self.newangle # if rotate pass basetarget angle, rotate to basetarget angle
                    else:
                        self.angle -= rotatetiny
                        if self.angle < self.newangle: self.angle = self.newangle # if rotate pass basetarget angle, rotate to basetarget angle
                self.setsubunittarget() # generate new pos related to side
            elif self.moverotate and self.angle == self.newangle:  # Finish
                self.moverotate = False
                if self.rotateonly is False: # continue moving to basetarget after finish rotate
                    self.setsubunittarget(self.basetarget)
                else:
                    self.state = 0  # idle state
                    self.commandstate = self.state
                    self.rotateonly = False  # reset rotate only condition
            #^ End rotate function

            if self.state not in (0, 95) and self.frontpos.distance_to(self.commandtarget) < 1: # reach destination and not in combat
                nothalt = False # check if any subunit in combat
                for subunit in self.subunitsprite:
                    if subunit.state == 10:
                        nothalt = True
                    if subunit.unitleader and subunit.state != 10:
                        nothalt = False
                        break
                if nothalt is False:
                    self.retreatstart = False # reset retreat
                    self.revert = False  # reset revert order
                    self.processcommand(self.basetarget, othercommand=1) # reset command basetarget state will become 0 idle

            #v Perform range attack, can only enter range attack state after finishing rotate
            shootrange = self.maxrange
            if self.useminrange == 0: # use minimum range to shoot
                shootrange = self.minrange

            if self.state in (5, 6) and self.moverotate is False and ((self.attacktarget is not None and self.basepos.distance_to(self.attacktarget.basepos) <= shootrange)
                                         or self.basepos.distance_to(self.baseattackpos) <= shootrange): # in shoot range
                self.set_target(self.frontpos)
                self.rangecombatcheck = True # set range combat check to start shooting
            elif self.state == 11 and self.attacktarget is not None and self.basepos.distance_to(self.attacktarget.basepos) > shootrange \
                    and self.hold == 0 and self.collide is False:  # chase basetarget if it go out of range and hold condition not hold
                self.state = self.commandstate # set state to attack command state
                self.rangecombatcheck = False # stop range combat check
                self.set_target(self.attacktarget.basepos) # move to new basetarget
                self.newangle = self.setrotate() # also keep rotate to basetarget
            #^ End range attack state

            self.collide = False # reset collide

        else: # dead parentunit
            #v parentunit just got killed
            if self.gotkilled is False:
                if self.team == 1:
                    self.die(self.maingame, self.maingame.team1army, self.maingame.team2army)
                else:
                    self.die(self.maingame, self.maingame.team2army, self.maingame.team1army)


                self.maingame.setuparmyicon() # reset army icon (remove dead one)
                self.maingame.eventlog.addlog([0, str(self.leader[0].name) + "'s parentunit is destroyed"], [0, 1]) # put destroyed event in war and army log

                self.kill()
                for subunit in self.subunitsprite:
                    subunit.kill()
            #^ End got killed

    def set_target(self, pos):
        """set new basetarget, scale basetarget from basetarget according to zoom scale"""
        self.basetarget = pygame.Vector2(pos) # Set new base basetarget
        self.setsubunittarget(self.basetarget)

    def revertmove(self):
        """Only subunit will rotate to move, not the entire unit"""
        self.newangle = self.angle
        self.moverotate = False # will not rotate to move
        self.revert = True
        newangle = self.setrotate()
        for subunit in self.subunitsprite:
            subunit.newangle = newangle

    def processcommand(self, targetpoint, runcommand=False, revertmove=False, enemy=None, othercommand=0):
        """Process input order into state and subunit basetarget action"""
        if othercommand == 0: # command command
            self.state = 1

            if self.attackplace or (enemy is not None and (self.team != enemy.team)): # attack
                if self.ammo <= 0 or self.forcedmelee: # no ammo to shoot or forced attack command
                    self.state = 3 # move to melee
                elif self.ammo > 0:  # have ammo to shoot
                    self.state = 5 # Move to range attack
                if self.attackplace: # attack specific location
                    self.set_target(targetpoint)
                    # if self.ammo > 0:
                    self.baseattackpos = targetpoint
                else:
                    self.attacktarget = enemy
                    self.baseattackpos = enemy.basepos
                    self.set_target(self.baseattackpos)

            else:
                self.set_target(targetpoint)

            if runcommand or self.runtoggle == 1:
                self.state += 1 # run state

            self.commandstate = self.state
            self.rangecombatcheck = False
            self.commandtarget = self.basetarget
            self.newangle = self.setrotate()

            if revertmove: ## Revert subunit without rotate, cannot run in this state
                self.revertmove()
                # if runcommand or self.runtoggle:
                #     self.state -= 1

            if self.charging: # change order when attacking will cause authority penalty
                self.leader[0].authority -= self.authpenalty
                self.authrecal()

        elif othercommand in (1, 2) and self.state != 10: # Pause all action command except combat or broken
            if self.charging and othercommand == 2: # halt order instead of auto halt
                self.leader[0].authority -= self.authpenalty  # decrease authority of the first leader for stop charge
                self.authrecal()  # recal authority

            self.state = 0  # go into idle state
            self.commandstate = self.state  # reset command state
            self.set_target(self.frontpos)  # set basetarget at self
            self.commandtarget = self.basetarget  # reset command basetarget
            self.rangecombatcheck = False  # reset range combat check
            self.newangle = self.setrotate()  # set rotation basetarget

    def processretreat(self, mouse_pos, whomouseover):
        if whomouseover is None: # click at empty map
            self.state = 96 # retreat state (not same as 98)
            self.commandstate = self.state # command retreat
            self.rotateonly = False
            self.forcedmelee = False
            self.attacktarget = None
            self.baseattackpos = 0
            self.leader[0].authority -= self.authpenalty # retreat reduce main leader authority
            if self.charging:  # change order when attacking will cause authority penalty
                self.leader[0].authority -= self.authpenalty
            self.authrecal()
            self.retreatstart = True # start retreat process
            self.set_target(mouse_pos)
            self.revertmove()
            self.commandtarget = self.basetarget

    def command(self, mouse_pos, mouse_right, double_mouse_right, whomouseover, keystate, othercommand=0):
        """othercommand is special type of command such as stop all action, raise flag, decimation, duel and so on"""
        if self.state not in (95, 97, 98, 99):
            self.revert = False
            self.retreatstart = False  # reset retreat
            self.rotateonly = False
            self.forcedmelee = False
            self.attacktarget = None
            self.baseattackpos = 0
            self.attackplace = False

            #register user keyboard
            if keystate[pygame.K_LCTRL]: self.forcedmelee = True
            if keystate[pygame.K_LALT]: self.attackplace = True

            if self.control and self.state != 100:
                if mouse_right and mouse_pos[0] >= 1 and mouse_pos[0] < 998 and mouse_pos[1] >= 1 and mouse_pos[1] < 998:
                    if self.state in (10,96) and whomouseover is None:
                        self.processretreat(mouse_pos, whomouseover)  # retreat
                    else:
                        for subunit in self.subunitsprite:
                            subunit.attacking = True
                        # if self.state == 10:
                        if keystate[pygame.K_LSHIFT]:
                            self.rotateonly = True
                        if keystate[pygame.K_z]:
                            self.revert = True
                        self.processcommand(mouse_pos, double_mouse_right, self.revert, whomouseover)
                elif othercommand != 0:
                    self.processcommand(mouse_pos, double_mouse_right, self.revert, whomouseover, othercommand)

    def switchfaction(self, oldgroup, newgroup, oldposlist, allunitindex, enactment):
        """Change army group and gameid when change side"""
        self.colour = (144, 167, 255) # team1 colour
        self.control = True #TODO need to change later when player can choose team

        if self.team == 2:
            self.team = 1 # change to team 1
        else: # originally team 1, new team would be 2
            self.team = 2 # change to team 2
            self.colour = (255, 114, 114) # team2 colour
            if enactment is False:
                self.control = False

        newgameid = newgroup[-1].gameid + 1
        oldgroup.remove(self) # remove from old team group
        newgroup.append(self) # add to new team group
        oldposlist.pop(self.gameid) # remove from old pos list
        allunitindex = [newgameid if index == self.gameid else index for index in allunitindex] # replace index in allunitindex
        self.gameid = newgameid # change game id
        # self.changescale() # reset scale to the current zoom
        self.icon.changeimage(changeside=True) # change army icon to new team
        return allunitindex

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.icon
            del self.teamcommander
            del self.startwhere
            del self.subunitsprite
            del self.neartarget
            del self.leader
            del self.frontlineobject
            del self.attacktarget
            del self.leadersubunit
