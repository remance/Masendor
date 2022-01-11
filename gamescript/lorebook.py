import pygame
import pygame.freetype

from gamescript import commonscript


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

    def __init__(self, main_dir, screen_scale, screenrect, image, textsize=17):
        """ Lorebook section: 0 = welcome/concept, 1 world history, 2 = faction, 3 = subunit, 4 = equipment, 5 = subunit status, 6 = subunit skill,
        7 = subunit trait, 8 = leader, 9 terrain, 10 = landmark"""
        self.main_dir = main_dir
        self.SCREENRECT = screenrect
        self.screen_scale = screen_scale

        self._layer = 23
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", int(textsize * self.screen_scale[1]))
        self.fontheader = pygame.font.SysFont("oldenglishtext", int(40 * self.screen_scale[1]))
        self.image = pygame.transform.scale(image, (int(image.get_width() * self.screen_scale[0]),
                                                    int(image.get_height() * self.screen_scale[1])))
        self.image_original = self.image.copy()
        self.leader_stat = self.leader.leader_list
        self.section = 0
        self.subsection = 1  # subsection of that section e.g. swordmen subunit in subunit section Start with 1 instead of 0
        self.stat_data = None  # for getting the section stat data
        self.lore_data = None  # for getting the section lore data
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
        if self.lore_data is None or self.page == self.maxpage or \
                self.lore_data[self.subsection][self.page * 4] == "":  # remove next page button when reach last page
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
        self.stat_data = self.section_list[self.section][0]  # get new stat data of the new section
        self.lore_data = self.section_list[self.section][1]  # get new lore data of the new section
        self.maxpage = 0  # reset max page
        self.current_subsection_row = 0  # reset subsection scroll to the top one
        thislist = self.stat_data.values()  # get list of subsection
        self.subsection_list = [name[0] for name in thislist if "Name" != name[0]]  # remove the header from subsection list
        self.logsize = len(self.subsection_list)  # get size of subsection list

        self.change_subsection(self.subsection, pagebutton, allui)
        self.setup_subsection_list(listsurface, listgroup)

        lorescroll.change_image(log_size=self.logsize)
        lorescroll.change_image(new_row=self.current_subsection_row)

    def change_subsection(self, subsection, pagebutton, allui):
        self.subsection = subsection
        self.page = 0  # reset page to the first one
        self.image = self.image_original.copy()
        self.portrait = None  # reset portrait, possible for subsection to not have portrait
        allui.remove(pagebutton[0])
        allui.remove(pagebutton[1])
        self.maxpage = 0  # some subsection may not have lore data in file (maxpage would be just 0)
        if self.lore_data is not None:  # some subsection may not have lore data
            try:
                if self.lore_data[self.subsection][0] != "":
                    self.maxpage = 0 + int(len(self.lore_data[subsection]) / 4)  # Number of maximum page of lore for that subsection (4 para per page)
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
                text_image = font.render(str(self.subsection), True, pygame.Color("white"))
                text_rect = text_image.get_rect(center=(self.portrait.get_width() / 2, self.portrait.get_height() / 1.3))
                self.portrait.blit(text_image, text_rect)

            self.portrait = pygame.transform.scale(self.portrait,
                                                   (int(150 * self.screen_scale[0]), int(150 * self.screen_scale[1])))  # scale leader image to 150x150
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
        row = 15 * self.screen_scale[1]
        column = 15 * self.screen_scale[0]
        pos = listsurface.rect.topleft
        if self.current_subsection_row > self.logsize - self.max_subsection_show:
            self.current_subsection_row = self.logsize - self.max_subsection_show

        if len(listgroup) > 0:  # remove previous subsection in the group before generate new one
            for stuff in listgroup:
                stuff.kill()
                del stuff

        listloop = [item for item in list(self.stat_data.keys()) if type(item) != str]
        for index, item in enumerate(self.subsection_list):
            if index >= self.current_subsection_row:
                listgroup.add(SubsectionName([self.screen_scale[0], self.screen_scale[1]], (pos[0] + column, pos[1] + row), item,
                                             listloop[index]))  # add new subsection sprite to group
                row += (30 * self.screen_scale[1])  # next row
                if len(listgroup) > self.max_subsection_show:
                    break  # will not generate more than space allowed

    def pagedesign(self):
        """Lore book format position of the text"""
        stat = self.stat_data[self.subsection]
        if self.section != 4:
            statheader = self.section_list[self.section][0]["ID"][1:-2]
        else:  # equipment section use slightly different stat header
            statheader = []
            for index in self.equipmentstat:
                if type(index) != int and "ID" in index:
                    statheader.append(self.equipmentstat[index][1:-2])

        name = stat[0]
        text_surface = self.fontheader.render(str(name), True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(int(28 * self.screen_scale[0]), int(10 * self.screen_scale[1])))
        self.image.blit(text_surface, text_rect)  # add name of item to the top of page

        if self.portrait is not None:
            portraitrect = self.portrait.get_rect(topleft=(int(20 * self.screen_scale[0]), int(60 * self.screen_scale[1])))
            self.image.blit(self.portrait, portraitrect)

        description = stat[-1]
        description_surface = pygame.Surface((int(300 * self.screen_scale[0]), int(350 * self.screen_scale[1])), pygame.SRCALPHA)
        description_rect = description_surface.get_rect(topleft=(int(180 * self.screen_scale[1]), int(60 * self.screen_scale[0])))
        self.blit_text(description_surface, description, (int(5 * self.screen_scale[1]), int(5 * self.screen_scale[0])), self.font)
        self.image.blit(description_surface, description_rect)

        if self.page == 0:
            row = 350 * self.screen_scale[1]
            col = 60 * self.screen_scale[0]

            # self concept, history, faction sectionis is simply to processed and does not need specific column read
            if self.section in (0, 1, 2):
                frontstat_text = stat[1:-1]
                for index, text in enumerate(frontstat_text):

                    # blit text
                    if "IMAGE:" not in text:
                        text_surface = pygame.Surface((int(400 * self.screen_scale[1]), int(300 * self.screen_scale[0])), pygame.SRCALPHA)
                        text_rect = description_surface.get_rect(topleft=(col, row))
                        self.blit_text(text_surface, str(text), (int(5 * self.screen_scale[1]), int(5 * self.screen_scale[0])), self.font)

                    # blit image instead of text
                    else:
                        if "FULLIMAGE:" in text:  # full image to whole two pages
                            filename = text[10:].split("\\")[-1]
                            text_surface = commonscript.load_image(self.main_dir, filename, text[10:].replace(filename, ""))
                            text_surface = pygame.transform.scale(text_surface, (self.image.get_width(), self.image.get_height()))
                            text_rect = description_surface.get_rect(topleft=(0, 0))
                        else:
                            filename = text[6:].split("\\")[-1]
                            text_surface = commonscript.load_image(self.main_dir, filename, text[6:].replace(filename, ""))
                            text_rect = description_surface.get_rect(topleft=(col, row))
                    self.image.blit(text_surface, text_rect)

                    row += (200 * self.screen_scale[1])
                    if row >= 600 * self.screen_scale[1]:  # continue drawing on the right page after reaching the end of left page
                        if col == 520 * self.screen_scale[0]:  # already on the right page
                            break
                        else:
                            col = 520 * self.screen_scale[0]
                            row = 50 * self.screen_scale[1]

            # more complex section
            elif self.section in (3, 4, 5, 6, 7, 8, 9, 10):
                frontstat_text = stat[1:-2]
                # newtext = []
                for index, text in enumerate(frontstat_text):
                    if text != "":
                        if self.section != 4:  # equipment section need to be processed differently
                            createtext = statheader[index] + ": " + str(text)
                            if statheader[index] == "ImageID":
                                # IMAGEID column in other section does not provide information, skip
                                createtext = ""
                                pass

                            elif self.section == 3:
                                if statheader[index] == "Role":  # Replace imageid to subunit role in troop section
                                    rolelist = {0: "None", 1: "Offensive", 2: "Defensive", 3: "Skirmisher", 4: "Shock", 5: "Support", 6: "Magic",
                                                7: "Ambusher",
                                                8: "Sniper", 9: "Recon"}
                                    role = [rolelist[item] for item in
                                            text]  # role is not type, it represent subunit classification from base stat to tell what it excel
                                    createtext = "Specilaised Role: "
                                    if len(role) == 0:
                                        createtext += "None, "
                                    for thisrole in role:
                                        createtext += thisrole + ", "
                                    createtext = createtext[0:-2]
                                elif statheader[index] == "Type":
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

                                elif statheader[index] == "Armour":  # armour text with quality
                                    qualitytext = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")
                                    createtext = statheader[index] + ": " + qualitytext[text[1]] + " " + self.armour_stat[text[0]][0] \
                                        # + ", Base Armour: " + str( self.armour_stat[text[0]][1])

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
                                        createtext = statheader[index] + ": " + abilitylist
                                        # + ", Base Speed: " + str(speed)  # add subunit speed after
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
                            text_surface = self.font.render(createtext, True, (0, 0, 0))
                            text_rect = text_surface.get_rect(topleft=(col, row))
                            self.image.blit(text_surface, text_rect)
                            row += (25 * self.screen_scale[1])
                            if row >= 600 * self.screen_scale[1]:
                                col = 520 * self.screen_scale[0]
                                row = 50 * self.screen_scale[1]

        else:  # lore page, the paragraph can be in text or image (IMAGE:)
            if self.lore_data is not None and self.maxpage != 0:
                lore = self.lore_data[self.subsection][(self.page - 1) * 4:]
                row = 400 * self.screen_scale[1]
                col = 60 * self.screen_scale[0]
                for index, text in enumerate(lore):
                    if text != "":

                        # blit paragraph of text
                        if "IMAGE:" not in text:
                            text_surface = pygame.Surface((400 * self.screen_scale[0], 300 * self.screen_scale[1]), pygame.SRCALPHA)
                            self.blit_text(text_surface, text, (5 * self.screen_scale[0], 5 * self.screen_scale[1]), self.font)
                            text_rect = description_surface.get_rect(topleft=(col, row))

                        # blit image
                        else:
                            if "FULLIMAGE:" in text:
                                filename = text[10:].split("\\")[-1]
                                text_surface = commonscript.load_image(self.main_dir, filename, text[10:].replace(filename, ""))
                                text_surface = pygame.transform.scale(text_surface, (self.image.get_width(), self.image.get_height()))
                                text_rect = description_surface.get_rect(topleft=(0, 0))
                            else:
                                filename = text[6:].split("\\")[-1]
                                text_surface = commonscript.load_image(self.main_dir, filename, text[6:].replace(filename, ""))
                                text_rect = description_surface.get_rect(topleft=(col, row))
                        self.image.blit(text_surface, text_rect)

                        row += (200 * self.screen_scale[1])
                        if row >= 600 * self.screen_scale[1]:
                            if col == 550 * self.screen_scale[0]:
                                break
                            else:
                                col = 550 * self.screen_scale[0]
                                row = 50 * self.screen_scale[1]


class SubsectionList(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, image):
        self._layer = 23
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[0]),
                                                    int(image.get_height() * screen_scale[1])))
        self.rect = self.image.get_rect(topright=pos)


class SubsectionName(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, name, subsection, textsize=16):
        self._layer = 24
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(textsize * screen_scale[1]))
        self.image = pygame.Surface((int(180 * screen_scale[0]), int(25 * screen_scale[1])))  # black corner
        self.image.fill((0, 0, 0))

        # v White body square
        small_image = pygame.Surface((int(178 * screen_scale[0]), int(23 * screen_scale[1])))
        small_image.fill((255, 255, 255))
        small_rect = small_image.get_rect(topleft=(int(1 * screen_scale[0]), int(1 * screen_scale[1])))
        self.image.blit(small_image, small_rect)
        # ^ End white body

        # v Subsection name text
        text_surface = self.font.render(str(name), 1, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(int(3 * screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
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
#     def __init__(self, text_size=16):
#         self._layer = 14
#         pygame.sprite.Sprite.__init__(self, self.containers)
#         self.font = pygame.font.SysFont("helvetica", text_size)
#         self.image = pygame.Surface(100, 50)
#         self.text = ""
#         self.text_surface = self.font.render(str(self.text), 1, (0, 0, 0))
#         self.text_rect = self.text_surface.get_rect(centerleft=(3, self.image.get_height() / 2))
#
#     def textchange(self, input):
#         newcharacter = pygame.key.name(input)
#         self.text += newcharacter

def lorebook_process(self, uidraw, mouse_up, mouse_down, mouse_scrollup, mouse_scrolldown):
    """Lorebook user interaction"""
    command = None
    if mouse_up or mouse_down:  # mouse down (hold click) only for subsection listscroller
        if mouse_up:
            for button in self.lore_button_ui:
                if button in uidraw and button.rect.collidepoint(self.mouse_pos):  # click button
                    if button.event in range(0, 11):  # section button
                        self.lorebook.change_section(button.event, self.lore_name_list, self.subsection_name, self.lore_scroll,
                                                     self.page_button, uidraw)  # change to section of that button

                    elif button.event == 19:  # Close button
                        uidraw.remove(self.lorebook, *self.lore_button_ui, self.lore_scroll,
                                      self.lore_name_list)  # remove enclycopedia related sprites
                        for name in self.subsection_name:  # remove subsection name
                            name.kill()
                            del name
                        command = "exit"

                    elif button.event == 20:  # Previous page button
                        self.lorebook.change_page(self.lorebook.page - 1, self.page_button, uidraw)  # go back 1 page

                    elif button.event == 21:  # Next page button
                        self.lorebook.change_page(self.lorebook.page + 1, self.page_button, uidraw)  # go forward 1 page

                    break  # found clicked button, break loop

            for name in self.subsection_name:
                if name.rect.collidepoint(self.mouse_pos):  # click on subsection name
                    self.lorebook.change_subsection(name.subsection, self.page_button, uidraw)  # change subsection
                    break  # found clicked subsection, break loop

        if self.lore_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroller
            self.lorebook.current_subsection_row = self.lore_scroll.update(
                self.mouse_pos)  # update the scroller and get new current subsection
            self.lorebook.setup_subsection_list(self.lore_name_list, self.subsection_name)  # update subsection name list

    elif mouse_scrollup:
        if self.lore_name_list.rect.collidepoint(self.mouse_pos):  # Scrolling at lore book subsection list
            self.lorebook.current_subsection_row -= 1
            if self.lorebook.current_subsection_row < 0:
                self.lorebook.current_subsection_row = 0
            else:
                self.lorebook.setup_subsection_list(self.lore_name_list, self.subsection_name)
                self.lore_scroll.change_image(new_row=self.lorebook.current_subsection_row)

    elif mouse_scrolldown:
        if self.lore_name_list.rect.collidepoint(self.mouse_pos):  # Scrolling at lore book subsection list
            self.lorebook.current_subsection_row += 1
            if self.lorebook.current_subsection_row + self.lorebook.max_subsection_show - 1 < self.lorebook.log_size:
                self.lorebook.setup_subsection_list(self.lore_name_list, self.subsection_name)
                self.lore_scroll.change_image(new_row=self.lorebook.current_subsection_row)
            else:
                self.lorebook.current_subsection_row -= 1

    return command