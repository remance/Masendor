import pygame
import pygame.freetype

from gamescript import gamelongscript


class Lorebook(pygame.sprite.Sprite):
    concept_stat = None
    concept_lore = None
    history_stat = None
    history_lore = None
    faction_lore = None
    unit_stat = None
    unit_lore = None
    armour_stat = None
    weapon_stat = None
    mount_stat = None
    mount_armour_stat = None
    status_stat = None
    skillstat = None
    trait_stat = None
    leader_stat = None
    leader_lore = None
    terrain_stat = None
    landmark_stat = None
    weather_stat = None
    unit_grade_stat = None
    unit_class_list = None
    leader_class_list = None
    mount_grade_stat = None
    race_list = None
    statetext = None

    def __init__(self, main, image, textsize=18):
        """ Lorebook section: 0 = welcome/concept, 1 world history, 2 = faction, 3 = subunit, 4 = equipment, 5 = subunit status, 6 = subunit skill,
        7 = subunit trait, 8 = leader, 9 terrain, 10 = landmark"""
        self.main_dir = main.main_dir
        self.SCREENRECT = main.SCREENRECT
        self.width_adjust = main.width_adjust
        self.height_adjust = main.height_adjust

        self._layer = 23
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("timesnewroman", int(textsize * self.height_adjust))
        self.fontheader = pygame.font.SysFont("oldenglishtext", int(40 * self.height_adjust))
        self.image = pygame.transform.scale(image, (int(image.get_width() * self.width_adjust),
                                                    int(image.get_height() * self.height_adjust)))
        self.image_original = self.image.copy()
        self.leader_stat = self.leader.leader_list
        self.section = 0
        self.subsection = 1  # subsection of that section e.g. swordmen subunit in subunit section Start with 1 instead of 0
        self.statdata = None  # for getting the section stat data
        self.loredata = None  # for getting the section lore data
        self.showsubsection = None  # Subsection stat currently viewing
        self.showsubsection2 = None  # Subsection lore currently viewing
        self.subsection_list = None
        self.portrait = None

        # v Make new equipment list that contain all type weapon, armour, mount
        self.equipmentstat = {}
        run = 1
        self.equipment_last_index = []
        for statlist in (self.weapon_stat, self.armour_stat, self.mount_stat, self.mount_armour_stat):
            for index in statlist:
                if index != "ID":
                    self.equipmentstat[run] = statlist[index]
                    run += 1
                else:
                    self.equipmentstat[index + str(run)] = statlist[index]
            self.equipment_last_index.append(run)
        # ^ End new equipment list

        self.section_list = (
            (self.concept_stat, self.concept_lore), (self.history_stat, self.history_lore), (self.faction_lore, None),
            (self.unit_stat, self.unit_lore),
            (self.equipmentstat, None), (self.status_stat, None), (self.skillstat, None),
            (self.trait_stat, None), (self.leader_stat, self.leader_lore), (self.terrain_stat, None), (self.weather_stat, None))
        self.current_subsection_row = 0
        self.max_subsection_show = 21
        self.logsize = 0
        self.page = 0
        self.maxpage = 0
        self.rect = self.image.get_rect(center=(self.SCREENRECT.width / 1.9, self.SCREENRECT.height / 1.9))
        self.quality_text = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")  # text for item quality
        self.leader_text = (
            "Detrimental", "Incompetent", "Inferior", "Unskilled", "Dull", "Average", "Decent", "Skilled", "Master", "Genius", "Unmatched")

    def change_page(self, page, pagebutton, allui, portrait=None):
        """Change page of the current subsection, either next or previous page"""
        self.page = page
        self.image = self.image_original.copy()  # reset encyclopedia image
        self.pagedesign()  # draw new pages

        # v Next/previous page button
        if self.loredata is None or self.page == self.maxpage or \
                self.loredata[self.subsection][self.page * 4] == "":  # remove next page button when reach last page
            allui.remove(pagebutton[1])
        else:
            allui.add(pagebutton[1])

        if self.page != 0:  # add previous page button when not at first page
            allui.add(pagebutton[0])
        else:
            allui.remove(pagebutton[0])
        # ^ End page button

    def change_section(self, section, listsurface, listgroup, lorescroll, pagebutton, allui):
        """Change to new section either by open encyclopedia or click section button"""
        self.portrait = None
        self.section = section  # get new section
        self.subsection = 1  # reset subsection to the first one
        self.statdata = self.section_list[self.section][0]  # get new stat data of the new section
        self.loredata = self.section_list[self.section][1]  # get new lore data of the new section
        self.maxpage = 0  # reset max page
        self.current_subsection_row = 0  # reset subsection scroll to the top one
        thislist = self.statdata.values()  # get list of subsection
        self.subsection_list = [name[0] for name in thislist if "Name" != name[0]]  # remove the header from subsection list
        self.logsize = len(self.subsection_list)  # get size of subsection list

        self.change_subsection(self.subsection, pagebutton, allui)
        self.setup_subsection_list(listsurface, listgroup)

        lorescroll.changeimage(logsize=self.logsize)
        lorescroll.changeimage(newrow=self.current_subsection_row)

    def change_subsection(self, subsection, pagebutton, allui):
        self.subsection = subsection
        self.page = 0  # reset page to the first one
        self.image = self.image_original.copy()
        self.portrait = None  # reset portrait, possible for subsection to not have portrait
        allui.remove(pagebutton[0])
        allui.remove(pagebutton[1])
        self.maxpage = 0  # some subsection may not have lore data in file (maxpage would be just 0)
        if self.loredata is not None:  # some subsection may not have lore data
            try:
                if self.loredata[self.subsection][0] != "":
                    self.maxpage = 0 + int(len(self.loredata[subsection]) / 4)  # Number of maximum page of lore for that subsection (4 para per page)
                    allui.add(pagebutton[1])
            except:
                pass

        if self.section != 8:  # TODO change this when other sections have portrait
            self.pagedesign()
        else:  # leader section exclusive for now (will merge wtih other section when add portrait for others)
            try:
                self.portrait = self.leader.imgs[self.leader.imgorder.index(self.subsection)].copy()  # get leader portrait based on subsection number
            except:
                self.portrait = self.leader.imgs[-1].copy()  # Use Unknown leader image if there is none in list
                font = pygame.font.SysFont("timesnewroman", 300)
                textimage = font.render(str(self.subsection), True, pygame.Color("white"))
                textrect = textimage.get_rect(center=(self.portrait.get_width() / 2, self.portrait.get_height() / 1.3))
                self.portrait.blit(textimage, textrect)

            self.portrait = pygame.transform.scale(self.portrait,
                                                   (int(150 * self.width_adjust), int(150 * self.height_adjust)))  # scale leader image to 150x150
            self.pagedesign()

    def blit_text(self, surface, text, pos, font, color=pygame.Color("black")):
        words = [word.split(" ") for word in text.splitlines()]  # 2D array where each row is a list of words
        space = font.size(" ")[0]  # the width of a space
        maxwidth, maxheight = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                wordsurface = font.render(word, 0, color)
                wordwidth, wordheight = wordsurface.get_size()
                if x + wordwidth >= maxwidth:
                    x = pos[0]  # reset x
                    y += wordheight  # start on new row.
                surface.blit(wordsurface, (x, y))
                x += wordwidth + space
            x = pos[0]  # reset x
            y += wordheight  # start on new row

    def setup_subsection_list(self, listsurface, listgroup):
        """generate list of subsection of the left side of encyclopedia"""
        row = 15 * self.height_adjust
        column = 15 * self.width_adjust
        pos = listsurface.rect.topleft
        if self.current_subsection_row > self.logsize - self.max_subsection_show:
            self.current_subsection_row = self.logsize - self.max_subsection_show

        if len(listgroup) > 0:  # remove previous subsection in the group before generate new one
            for stuff in listgroup:
                stuff.kill()
                del stuff

        listloop = [item for item in list(self.statdata.keys()) if type(item) != str]
        for index, item in enumerate(self.subsection_list):
            if index >= self.current_subsection_row:
                listgroup.add(SubsectionName([self.width_adjust, self.height_adjust], (pos[0] + column, pos[1] + row), item,
                                             listloop[index]))  # add new subsection sprite to group
                row += (30 * self.height_adjust)  # next row
                if len(listgroup) > self.max_subsection_show:
                    break  # will not generate more than space allowed

    def pagedesign(self):
        """Lore book format position of the text"""
        firstpagecol = 50
        secondpagecol = 650
        stat = self.statdata[self.subsection]
        if self.section != 4:
            statheader = self.section_list[self.section][0]["ID"][1:-2]
        else:  # equipment section use slightly different stat header
            statheader = []
            for index in self.equipmentstat:
                if type(index) != int and "ID" in index:
                    statheader.append(self.equipmentstat[index][1:-2])

        name = stat[0]
        textsurface = self.fontheader.render(str(name), True, (0, 0, 0))
        textrect = textsurface.get_rect(topleft=(int(28 * self.width_adjust), int(10 * self.height_adjust)))
        self.image.blit(textsurface, textrect)  # add name of item to the top of page

        if self.portrait is not None:
            portraitrect = self.portrait.get_rect(topleft=(int(20 * self.width_adjust), int(60 * self.height_adjust)))
            self.image.blit(self.portrait, portraitrect)

        description = stat[-1]
        descriptionsurface = pygame.Surface((int(300 * self.height_adjust), int(300 * self.width_adjust)), pygame.SRCALPHA)
        descriptionrect = descriptionsurface.get_rect(topleft=(int(180 * self.height_adjust), int(60 * self.width_adjust)))
        self.blit_text(descriptionsurface, description, (int(5 * self.height_adjust), int(5 * self.width_adjust)), self.font)
        self.image.blit(descriptionsurface, descriptionrect)

        if self.page == 0:
            row = 350 * self.height_adjust
            col = 60 * self.width_adjust

            # game concept, history, faction sectionis is simply to processed and does not need specific column read
            if self.section in (0, 1, 2):
                frontstattext = stat[1:-1]
                for index, text in enumerate(frontstattext):

                    # blit text
                    if "IMAGE:" not in text:
                        textsurface = pygame.Surface((int(400 * self.height_adjust), int(300 * self.width_adjust)), pygame.SRCALPHA)
                        textrect = descriptionsurface.get_rect(topleft=(col, row))
                        self.blit_text(textsurface, str(text), (int(5 * self.height_adjust), int(5 * self.width_adjust)), self.font)

                    # blit image instead of text
                    else:
                        if "FULLIMAGE:" in text:  # full image to whole two pages
                            textsurface = gamelongscript.load_image(self.main_dir + text[10:])
                            textsurface = pygame.transform.scale(textsurface, (self.image.get_width(), self.image.get_height()))
                            textrect = descriptionsurface.get_rect(topleft=(0, 0))
                        else:
                            textsurface = gamelongscript.load_image(self.main_dir + text[6:])
                            textrect = descriptionsurface.get_rect(topleft=(col, row))
                    self.image.blit(textsurface, textrect)

                    row += (200 * self.height_adjust)
                    if row >= 600 * self.height_adjust:  # continue drawing on the right page after reaching the end of left page
                        if col == 520 * self.width_adjust:  # already on the right page
                            break
                        else:
                            col = 520 * self.width_adjust
                            row = 50 * self.height_adjust

            # more complex section
            elif self.section in (3, 4, 5, 6, 7, 8, 9, 10):
                frontstattext = stat[1:-2]
                # newtext = []
                for index, text in enumerate(frontstattext):
                    if text != "":
                        if self.section != 4:  # equipment section need to be processed differently
                            createtext = statheader[index] + ": " + str(text)
                            if statheader[index] == "ImageID":
                                if self.section == 3:  # Replace imageid to subunit role in troop section
                                    rolelist = {1: "Offensive", 2: "Defensive", 3: "Skirmisher", 4: "Shock", 5: "Support", 6: "Magic", 7: "Ambusher",
                                                8: "Sniper", 9: "Recon"}
                                    role = []  # role is not type, it represent subunit classification from base stat to tell what it excel
                                    print(type(stat[11][0]))
                                    basearmour = stat[11][1] + self.armour_stat[stat[11][0]][1]
                                    if basearmour >= 50 and stat[9] >= 50:
                                        role.append(rolelist[2])  # armour and melee defense (stat[9]), defensive role
                                    if stat[8] >= 50:
                                        role.append(rolelist[1])  # melee attack, offensive role

                                    speed = 50  # Default speed not counting weight yet

                                    mountstat = self.mount_stat[stat[29][0]]  # get mount stat
                                    if stat[29][0] != 1:
                                        speed = mountstat[2]  # replace speed from mount
                                    weight = self.armour_stat[stat[11][0]][2] + self.weapon_stat[stat[21][0]][3] + \
                                             self.weapon_stat[stat[22][0]][3] + self.mount_armour_stat[stat[29][2]][2]

                                    speed = round((speed * ((100 - weight) / 100)))
                                    if speed > 50 and basearmour < 30:
                                        role.append(rolelist[3])  # skirmisher role
                                    if stat[16] + mountstat[3] >= 60:
                                        role.append(rolelist[4])  # charge (stat[16]) and mount charge bonus, shock role

                                    createtext = "Specilaised Role: "
                                    if len(role) == 0:
                                        createtext += "None, "
                                    for thisrole in role:
                                        createtext += thisrole + ", "
                                    createtext = createtext[0:-2]

                                else:  # IMAGEID column in other section does not provide information, skip
                                    createtext = ""
                                    pass

                            elif statheader[index] == "Properties":  # troop properties list
                                traitlist = ""
                                if text != [0]:
                                    for thistext in text:
                                        if thistext in self.trait_stat:  # in case user put in trait not existed in ruleset
                                            traitlist += self.trait_stat[thistext][0] + ", "
                                    traitlist = traitlist[0:-2]
                                    createtext = statheader[index] + ": " + traitlist
                                else:
                                    createtext = ""
                                    pass

                            elif statheader[index] == "Status" or statheader[index] == "Enemy Status":  # status list
                                statuslist = ""
                                if text != [0]:
                                    for thistext in text:
                                        if thistext in self.status_stat:  # in case user put in trait not existed in ruleset
                                            statuslist += self.status_stat[thistext][0] + ", "
                                    statuslist = statuslist[0:-2]
                                    createtext = statheader[index] + ": " + statuslist
                                else:
                                    createtext = ""
                                    pass

                            if self.section == 3:  # troop section
                                if statheader[index] == "Grade":  # grade text instead of number
                                    createtext = statheader[index] + ": " + self.unit_grade_stat[text][0]

                                elif "Weapon" in statheader[index]:  # weapon text with quality
                                    qualitytext = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")
                                    createtext = statheader[index] + ": " + qualitytext[text[1]] + " " + self.weapon_stat[text[0]][0]
                                    if statheader[index] == "Range Weapon" and text[0] == 1:  # no need to create range weapon text for None
                                        createtext = ""
                                        pass

                                elif statheader[index] == "Armour":  # armour text with quality
                                    qualitytext = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")
                                    createtext = statheader[index] + ": " + qualitytext[text[1]] + " " + self.armour_stat[text[0]][
                                        0] + ", Base Armour: " + str(basearmour)

                                elif statheader[index] == "Unit Type":
                                    createtext = statheader[index] + ": " + self.unit_class_list[text][0]

                                elif statheader[index] == "Race":
                                    createtext = statheader[index] + ": " + self.race_list[text][0]

                                elif statheader[index] == "Mount":  # mount text with grade
                                    createtext = statheader[index] + ": " + self.mount_grade_stat[text[1]][0] + " " + self.mount_stat[text[0]][
                                        0] + "//" + self.mount_armour_stat[text[2]][0]
                                    if self.mount_stat[text[0]][0] == "None":
                                        createtext = ""
                                        pass

                                elif statheader[index] == "Abilities" or statheader[index] == "Charge Skill":  # skill text instead of number
                                    abilitylist = ""
                                    if statheader[index] == "Charge Skill":
                                        if text in self.skillstat:  # only include skill if exist in ruleset
                                            abilitylist += self.skillstat[text][0]
                                        createtext = statheader[index] + ": " + abilitylist + ", Base Speed: " + str(speed)  # add subunit speed after
                                    elif text != [0]:
                                        for thistext in text:
                                            if thistext in self.skillstat:  # only include skill in ruleset
                                                abilitylist += self.skillstat[thistext][0] + ", "
                                        abilitylist = abilitylist[0:-2]
                                        createtext = statheader[index] + ": " + abilitylist
                                    else:
                                        createtext = ""
                                        pass

                            elif self.section == 6 and (statheader[index] == "Restriction"
                                                        or statheader[index] == "Condition"):  # skill restriction and condition in skill section
                                statelist = ""
                                if text != "":
                                    for thistext in text:
                                        statelist += self.statetext[thistext] + ", "
                                    statelist = statelist[0:-2]  # remove the last ", "
                                    createtext = statheader[index] + ": " + statelist
                                else:
                                    createtext = ""
                                    pass

                            elif self.section == 8:  # leader section
                                if statheader[index] in ("Melee Command", "Range Command", "Cavalry Command", "Combat"):
                                    createtext = statheader[index] + ": " + self.leader_text[text]

                                elif statheader[index] == "Social Class":
                                    createtext = statheader[index] + ": " + self.leader_class_list[text][0]

                        else:  # equipment section, header depends on equipment type
                            for thisindex, lastindex in enumerate(self.equipment_last_index):
                                if self.subsection < lastindex:  # check if this index pass the last index of each type
                                    newstatheader = statheader[thisindex]
                                    break
                            createtext = newstatheader[index] + ": " + str(text)

                            if newstatheader[index] == "ImageID":  # not used in enclycopedia
                                createtext = ""
                                pass

                            elif newstatheader[index] == "Properties":
                                traitlist = ""
                                if text != [0]:
                                    for thistext in text:
                                        if thistext in self.trait_stat:  # in case user put in trait not existed in ruleset
                                            traitlist += self.trait_stat[thistext][0] + ", "
                                    traitlist = traitlist[0:-2]
                                    createtext = newstatheader[index] + ": " + traitlist
                                else:
                                    createtext = ""
                                    pass

                        if createtext != "":  # text not empty, draw it. Else do nothing
                            textsurface = self.font.render(createtext, 1, (0, 0, 0))
                            textrect = textsurface.get_rect(topleft=(col, row))
                            self.image.blit(textsurface, textrect)
                            row += (25 * self.height_adjust)
                            if row >= 600 * self.height_adjust:
                                col = 520 * self.width_adjust
                                row = 50 * self.height_adjust

        else:  # lore page, the paragraph can be in text or image (IMAGE:)
            if self.loredata is not None and self.maxpage != 0:
                lore = self.loredata[self.subsection][(self.page - 1) * 4:]
                row = 400 * self.height_adjust
                col = 60 * self.width_adjust
                for index, text in enumerate(lore):
                    if text != "":

                        # blit paragraph of text
                        if "IMAGE:" not in text:
                            textsurface = pygame.Surface((400 * self.width_adjust, 300 * self.height_adjust), pygame.SRCALPHA)
                            self.blit_text(textsurface, text, (5 * self.width_adjust, 5 * self.height_adjust), self.font)
                            textrect = descriptionsurface.get_rect(topleft=(col, row))

                        # blit image
                        else:
                            if "FULLIMAGE:" in text:
                                textsurface = gamelongscript.load_image(self.main_dir + text[10:])
                                textsurface = pygame.transform.scale(textsurface, (self.image.get_width(), self.image.get_height()))
                                textrect = descriptionsurface.get_rect(topleft=(0, 0))
                            else:
                                textsurface = gamelongscript.load_image(self.main_dir + text[6:])
                                textrect = descriptionsurface.get_rect(topleft=(col, row))
                        self.image.blit(textsurface, textrect)

                        row += (200 * self.height_adjust)
                        if row >= 600 * self.height_adjust:
                            if col == 550 * self.width_adjust:
                                break
                            else:
                                col = 550 * self.width_adjust
                                row = 50 * self.height_adjust


class SubsectionList(pygame.sprite.Sprite):
    def __init__(self, main, pos, image):
        self.widthadjust = main.width_adjust
        self.heightadjust = main.height_adjust

        self._layer = 23
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.transform.scale(image, (int(image.get_width() * self.widthadjust),
                                                    int(image.get_height() * self.heightadjust)))
        self.rect = self.image.get_rect(topright=pos)


class SubsectionName(pygame.sprite.Sprite):
    def __init__(self, adjust, pos, name, subsection, textsize=16):
        self.widthadjust = adjust[0]
        self.heightadjust = adjust[1]

        self._layer = 24
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(textsize * self.heightadjust))
        self.image = pygame.Surface((int(180 * self.widthadjust), int(25 * self.heightadjust)))  # black corner
        self.image.fill((0, 0, 0))

        # v White body square
        smallimage = pygame.Surface((int(178 * self.widthadjust), int(23 * self.heightadjust)))
        smallimage.fill((255, 255, 255))
        smallrect = smallimage.get_rect(topleft=(int(1 * self.widthadjust), int(1 * self.heightadjust)))
        self.image.blit(smallimage, smallrect)
        # ^ End white body

        # v Subsection name text
        textsurface = self.font.render(str(name), 1, (0, 0, 0))
        textrect = textsurface.get_rect(midleft=(int(3 * self.widthadjust), self.image.get_height() / 2))
        self.image.blit(textsurface, textrect)
        # ^ End subsection name

        self.subsection = subsection
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

# class Selectionbox(pygame.sprite.Sprite):
#     def __init__(self, pos, lorebook):
#         self._layer = 13
#         pygame.sprite.Sprite.__init__(self, self.containers)
#         self.image = pygame.Surface(300, lorebook.image.get_height())


# class Searchbox(pygame.sprite.Sprite):
#     def __init__(self, textsize=16):
#         self._layer = 14
#         pygame.sprite.Sprite.__init__(self, self.containers)
#         self.font = pygame.font.SysFont("helvetica", textsize)
#         self.image = pygame.Surface(100, 50)
#         self.text = ""
#         self.textsurface = self.font.render(str(self.text), 1, (0, 0, 0))
#         self.textrect = self.textsurface.get_rect(centerleft=(3, self.image.get_height() / 2))
#
#     def textchange(self, input):
#         newcharacter = pygame.key.name(input)
#         self.text += newcharacter
