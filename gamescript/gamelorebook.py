import pygame
import pygame.freetype

from gamescript import gamelongscript

class Lorebook(pygame.sprite.Sprite):
    conceptstat = None
    conceptlore = None
    historystat = None
    historylore = None
    factionlore = None
    unitstat = None
    unitlore = None
    armourstat = None
    weaponstat = None
    mountstat = None
    statusstat = None
    skillstat = None
    traitstat = None
    leader = None
    leaderlore = None
    terrainstat = None
    landmarkstat = None
    weatherstat = None
    unitgradestat = None
    unitclasslist = None
    leaderclasslist = None
    racelist = None
    SCREENRECT = None
    main_dir = None

    def __init__(self, image, textsize=18):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.fontheader = pygame.font.SysFont("oldenglishtext", 40)
        self.image = image
        self.image_original = self.image.copy()
        self.leaderstat = self.leader.leaderlist
        self.section = 0  ## 0 = welcome/concept, 1 world history, 2 = faction, 3 = unit, 4 = equipment, 5 = unit status, 6 = unit skill, 7 = unit trait, 8 = leader, 9 terrain, 10 = landmark
        self.subsection = 1  ## subsection of that section e.g. swordmen unit in unit section Start with 1 instead of 0
        self.statdata = None  ## for getting the section stat data
        self.loredata = None  ## for getting the section lore data
        self.showsubsection = None  ## Subsection stat showing
        self.showsubsection2 = None  ## Subsection lore showing
        self.subsectionlist = None
        self.portrait = None

        #v Make new equipment list that contain all type weapon, armour, mount
        self.equipmentstat = {}
        run = 1
        self.equipmentlastindex = []
        for statlist in (self.weaponstat, self.armourstat, self.mountstat):
            for index in statlist:
                if index != "ID":
                    self.equipmentstat[run] = statlist[index]
                    run += 1
                else:
                    self.equipmentstat[index + str(run)] = statlist[index]
            self.equipmentlastindex.append(run)
        #^ End new equipment list

        self.sectionlist = ((self.conceptstat,self.conceptlore), (self.historystat, self.historylore), (self.factionlore, None), (self.unitstat, self.unitlore),
                            (self.equipmentstat, None), (self.statusstat, None), (self.skillstat, None),
                            (self.traitstat, None), (self.leaderstat, self.leaderlore), (self.terrainstat, None), (self.weatherstat, None))
        self.currentsubsectionrow = 0
        self.maxsubsectionshow = 20
        self.logsize = 0
        self.page = 0
        self.maxpage = 0
        self.rect = self.image.get_rect(center=(self.SCREENRECT.width / 1.9, self.SCREENRECT.height / 1.9))
        self.qualitytext = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect") # text for item quality
        self.statetext = {0: "Idle", 1: "Walking", 2: "Running", 3: "Walk(Melee)", 4: "Run(Melee)", 5: "Walk(Range)", 6: "Run(Range)",
                             7: "Forced Walk", 8: "Forced Run",
                             10: "Fighting", 11: "shooting", 65: "Sleeping", 66: "Camping", 67: "Resting", 68: "Dancing",
                             69: "Partying", 96: "Retreating", 97: "Collapse", 98: "Retreating", 99: "Broken", 100: "Destroyed"}
        self.leadertext = ("Detrimental", "Incompetent", "Inferior", "Unskilled", "Dull", "Average", "Decent", "Skilled", "Master", "Genius", "Unmatched")

    def changepage(self, page, portrait=None):
        """Change page of the current subsection, either next or previous page"""
        self.page = page
        self.image = self.image_original.copy() # reset encyclopedia image
        self.pagedesign() # draw new pages

    def changesection(self, section, listsurface, listgroup, lorescroll):
        """Change to new section either by open encyclopedia or click section button"""
        self.portrait = None
        self.section = section # get new section
        self.subsection = 1 # reset subsection to the first one
        self.statdata = self.sectionlist[self.section][0] # get new stat data of the new section
        self.loredata = self.sectionlist[self.section][1] # get new lore data of the new section
        self.maxpage = 0 # reset max page
        self.currentsubsectionrow = 0 # reset subsection scroll to the top one
        thislist = self.statdata.values() # list of subsection
        self.subsectionlist = [name[0] for name in thislist if "Name" != name[0]] # remove the header from subsection list
        self.logsize = len(self.subsectionlist) # get size of subsection list
        self.changesubsection(self.subsection)
        self.setupsubsectionlist(listsurface, listgroup)
        lorescroll.changeimage(logsize=self.logsize)
        lorescroll.changeimage(newrow=self.currentsubsectionrow)

    def changesubsection(self, subsection):
        self.subsection = subsection
        self.page = 0 # reset page to the first one
        self.image = self.image_original.copy() # reset encyclopedia image
        self.portrait = None # reset portrait
        if self.loredata is not None: # some subsection may not have lore data
            self.maxpage = 1 + int(len(self.loredata[subsection]) / 4) # Number of maximum page of lore for that subsection (4 para per page)
        if self.section != 8:
            self.pagedesign() # draw new pages
        else: ## leader section exclusive for now (will merge wtih other section when add portrait for others)
            try:
                self.portrait = self.leader.imgs[self.leader.imgorder.index(self.subsection)].copy() # get leader portrait based on subsection number as index
            except:
                self.portrait = self.leader.imgs[-1].copy() # Use Unknown leader image if there is none in list
            self.portrait = pygame.transform.scale(self.portrait, (150, 150)) # scale leader image to 150x150
            self.pagedesign()

    def blit_text(self, surface, text, pos, font, color=pygame.Color('black')):
        words = [word.split(' ') for word in text.splitlines()]  ## 2D array where each row is a list of words
        space = font.size(' ')[0]  ## the width of a space
        maxwidth, maxheight = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                wordsurface = font.render(word, 0, color)
                wordwidth, wordheight = wordsurface.get_size()
                if x + wordwidth >= maxwidth:
                    x = pos[0]  ## reset x
                    y += wordheight  ## start on new row.
                surface.blit(wordsurface, (x, y))
                x += wordwidth + space
            x = pos[0]  ## reset x
            y += wordheight  ## start on new row

    def setupsubsectionlist(self, listsurface, listgroup):
        """generate list of subsection of the left side of encyclopedia"""
        row = 15
        column = 15
        pos = listsurface.rect.topleft
        if self.currentsubsectionrow > self.logsize - self.maxsubsectionshow:
            self.currentsubsectionrow = self.logsize - self.maxsubsectionshow
        if len(listgroup) > 0: # remove previous subsection in the group before generate new one
            for stuff in listgroup:
                stuff.kill()
                del stuff
        listloop = [item for item in list(self.statdata.keys()) if type(item) != str]
        for index, item in enumerate(self.subsectionlist):
            if index >= self.currentsubsectionrow:
                listgroup.add(Subsectionname((pos[0] + column, pos[1] + row), item, listloop[index])) # add new subsection sprite to group
                row += 30 # next row
                if len(listgroup) > self.maxsubsectionshow: break # will not generate more than space allowed

    def pagedesign(self):
        """Lore book format position of the text"""
        firstpagecol = 50
        secondpagecol = 650
        stat = self.statdata[self.subsection]
        if self.section != 4:
            statheader = self.sectionlist[self.section][0]['ID'][1:-2]
        else:  ## Equipment section use slightly different stat header
            statheader = []
            for index in self.equipmentstat:
                if type(index) != int and "ID" in index:
                    statheader.append(self.equipmentstat[index][1:-2])
        name = stat[0]
        textsurface = self.fontheader.render(str(name), 1, (0, 0, 0))
        textrect = textsurface.get_rect(topleft=(28, 10))
        self.image.blit(textsurface, textrect)  ## Add name of item to the top of page
        if self.portrait != None:
            portraitrect = self.portrait.get_rect(topleft=(20, 60))
            self.image.blit(self.portrait, portraitrect)
        description = stat[-1]
        descriptionsurface = pygame.Surface((300, 300), pygame.SRCALPHA)
        descriptionrect = descriptionsurface.get_rect(topleft=(180, 60))
        self.blit_text(descriptionsurface, description, (5, 5), self.font)
        self.image.blit(descriptionsurface, descriptionrect)
        if self.page == 0:
            row = 350
            col = 60
            if self.section in (0, 1, 2):
                frontstattext = stat[1:-1]
                # newtext = []
                for index, text in enumerate(frontstattext):
                    # if text != "":
                    if "IMAGE:" not in text:
                        textsurface = pygame.Surface((400, 300), pygame.SRCALPHA)
                        textrect = descriptionsurface.get_rect(topleft=(col, row))
                        self.blit_text(textsurface, text, (5, 5), self.font)
                    else:
                        textsurface = gamelongscript.load_image(self.main_dir+text[6:])
                        textrect = descriptionsurface.get_rect(topleft=(col, row))
                    self.image.blit(textsurface, textrect)
                    row += 200
                    if row >= 600:
                        if col == 500:
                            break
                        else:
                            col = 520
                            row = 50
            elif self.section in (3, 4, 5, 6, 7, 8, 9, 10):
                frontstattext = stat[1:-2]
                # newtext = []
                for index, text in enumerate(frontstattext):
                    if text != "":
                        if self.section != 4:
                            createtext = statheader[index] + ": " + str(text)
                            if statheader[index] == "ImageID":
                                if self.section == 3: # Replace imageid to unit role in unti section
                                    """Role is not type, it represent unit classification from base stat to tell what it excel and has no influence on stat"""
                                    rolelist = {1: "Offensive", 2: "Defensive", 3: "Skirmisher", 4: "Shock", 5: "Support", 6: "Magic", 7: "Ambusher",
                                                8: "Sniper", 9: "Recon"}
                                    role = []
                                    basearmour = stat[11][1]+ self.armourstat[stat[11][0]][1]
                                    if basearmour >= 50 and stat[9] >= 50: role.append(rolelist[2]) # armour and melee defense
                                    if stat[8] >= 50: role.append(rolelist[1]) # melee attack
                                    speed = 50 ## Not counting weight yet
                                    if stat[29] != 1 : speed = self.mountstat[stat[29]][2] ## speed from mount
                                    weight = self.armourstat[stat[11][0]][2] + self.weaponstat[stat[21][0]][3] + self.weaponstat[stat[22][0]][3]
                                    speed = round((speed * ((100 - weight) / 100)))
                                    if speed > 50 and basearmour < 30: role.append(rolelist[3])
                                    if stat[16] + self.mountstat[stat[29]][3] >= 60: role.append(rolelist[4]) # charge
                                    createtext = "Specilaised Role: "
                                    if len(role) == 0: createtext += "None, "
                                    for thisrole in role:
                                        createtext += thisrole + ", "
                                    createtext = createtext[0:-2]
                                else:
                                    createtext = ""
                                    pass
                            elif statheader[index] == "Properties":
                                traitlist = ""
                                if text != [0]:
                                    for thistext in text:
                                        if thistext in self.traitstat:  ## In case user put in trait not existed in ruleset
                                            traitlist += self.traitstat[thistext][0] + ", "
                                    traitlist = traitlist[0:-2]
                                    createtext = statheader[index] + ": " + traitlist
                                else:
                                    createtext = ""
                                    pass
                            elif statheader[index] == "Status" or statheader[index] == "Enemy Status":
                                statuslist = ""
                                if text != [0]:
                                    for thistext in text:
                                        if thistext in self.statusstat:  ## In case user put in trait not existed in ruleset
                                            statuslist += self.statusstat[thistext][0] + ", "
                                    statuslist = statuslist[0:-2]
                                    createtext = statheader[index] + ": " + statuslist
                                else:
                                    createtext = ""
                                    pass
                            if self.section == 3:
                                if statheader[index] == "Grade":
                                    createtext = statheader[index] + ": " + self.unitgradestat[text][0]
                                elif "Weapon" in statheader[index]:
                                    qualitytext = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")
                                    createtext = statheader[index] + ": " + qualitytext[text[1]] + " " + self.weaponstat[text[0]][0]
                                    if statheader[index] == "Range Weapon" and text[0] == 1:
                                        createtext = ""
                                        pass
                                elif statheader[index] == "Armour":
                                    qualitytext = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")
                                    createtext = statheader[index] + ": " + qualitytext[text[1]] + " " + self.armourstat[text[0]][0] + ", Base Armour: " + str(basearmour)
                                elif statheader[index] == "Unit Type":
                                    createtext = statheader[index] + ": " + self.unitclasslist[text][0]
                                elif statheader[index] == "Race":
                                    createtext = statheader[index] + ": " + self.racelist[text][0]
                                elif statheader[index] == "Mount":
                                    createtext = statheader[index] + ": " + self.mountstat[text][0]
                                    if self.mountstat[text][0] == "None":
                                        createtext = ""
                                        pass
                                elif statheader[index] == "Abilities" or statheader[index] == "Charge Skill":
                                    abilitylist = ""
                                    if statheader[index] == "Charge Skill":
                                        if text in self.skillstat:  ## In case user put in trait not existed in ruleset
                                            abilitylist += self.skillstat[text][0]
                                        createtext = statheader[index] + ": " + abilitylist + ", Base Speed: " + str(speed)
                                    elif text != [0]:
                                        for thistext in text:
                                            if thistext in self.skillstat:  ## In case user put in trait not existed in ruleset
                                                abilitylist += self.skillstat[thistext][0] + ", "
                                        abilitylist = abilitylist[0:-2]
                                        createtext = statheader[index] + ": " + abilitylist
                                    else:
                                        createtext = ""
                                        pass
                            elif self.section == 6 and (statheader[index] == "Restriction" or statheader[index] == "Condition"):
                                statelist = ""
                                if text != "":
                                    for thistext in text:
                                        statelist += self.statetext[thistext] + ", "
                                    statelist = statelist[0:-2]
                                    createtext = statheader[index] + ": " + statelist
                                else:
                                    createtext = ""
                                    pass
                            elif self.section == 8:
                                if statheader[index] in ("Melee Command", "Range Command", "Cavalry Command", "Combat"):
                                    createtext = statheader[index] + ": " + self.leadertext[text]
                                elif statheader[index] == "Social Class":
                                    createtext = statheader[index] + ": " + self.leaderclasslist[text]
                        else:  ## Header depends on equipment type
                            for thisindex, lastindex in enumerate(self.equipmentlastindex):
                                if self.subsection < lastindex:  ## Check if this index pass the last index of each type
                                    newstatheader = statheader[thisindex]
                                    break
                            createtext = newstatheader[index] + ": " + str(text)
                            if newstatheader[index] == "ImageID":
                                createtext = ""
                                pass
                            elif newstatheader[index] == "Properties":
                                traitlist = ""
                                if text != [0]:
                                    for thistext in text:
                                        if thistext in self.traitstat:  ## In case user put in trait not existed in ruleset
                                            traitlist += self.traitstat[thistext][0] + ", "
                                    traitlist = traitlist[0:-2]
                                    createtext = newstatheader[index] + ": " + traitlist
                                else:
                                    createtext = ""
                                    pass
                        if createtext != "":
                            textsurface = self.font.render(createtext, 1, (0, 0, 0))
                            textrect = textsurface.get_rect(topleft=(col, row))
                            self.image.blit(textsurface, textrect)
                            row += 25
                            if row >= 600:
                                col = 520
                                row = 50
        else: # Lore page, the paragraph can be in text or image (IMAGE:)
            if self.loredata is not None:
                lore = self.loredata[self.subsection][(self.page - 1) * 4:]
                row = 400
                col = 60
                for index, text in enumerate(lore):
                    if text != "":
                        if "IMAGE:" not in text:
                            textsurface = pygame.Surface((400, 300), pygame.SRCALPHA)
                        else:
                            textsurface = gamelongscript.load_image(self.main_dir+text[6:])
                        textrect = descriptionsurface.get_rect(topleft=(col, row))
                        self.blit_text(textsurface, text, (5, 5), self.font)
                        self.image.blit(textsurface, textrect)
                        row += 200
                        if row >= 600:
                            if col == 550:
                                break
                            else:
                                col = 550
                                row = 50

class Subsectionlist(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(topright=pos)


class Subsectionname(pygame.sprite.Sprite):
    def __init__(self, pos, name, subsection, textsize=16):
        self._layer = 14
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.image = pygame.Surface((180, 25))
        self.image.fill((0, 0, 0))
        smallimage = pygame.Surface((178, 23))
        smallimage.fill((255, 255, 255))
        smallrect = smallimage.get_rect(topleft=(1, 1))
        self.image.blit(smallimage, smallrect)
        textsurface = self.font.render(str(name), 1, (0, 0, 0))
        textrect = textsurface.get_rect(midleft=(3, self.image.get_height() / 2))
        self.image.blit(textsurface, textrect)
        self.subsection = subsection
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


class Selectionbox(pygame.sprite.Sprite):
    def __init__(self, pos, lorebook):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface(300, lorebook.image.get_height())


class Searchbox(pygame.sprite.Sprite):
    def __init__(self, textsize=16):
        self._layer = 14
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.image = pygame.Surface(100, 50)
        self.text = ""
        self.textsurface = self.font.render(str(self.text), 1, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(centerleft=(3, self.image.get_height() / 2))

    def textchange(self, input):
        newcharacter = pygame.key.name(input)
        self.text += newcharacter
