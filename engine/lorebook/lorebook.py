import pygame

from engine.uimenu.uimenu import UIMenu
from engine import utility

# TODO paragraph syntax,

subsection_tag_colour = [(128, 255, 128), (237, 128, 128), (255, 255, 128), (128, 255, 255),
                         (128, 128, 255), (255, 128, 255), (220, 158, 233), (191, 191, 191), (255, 140, 85)]

subsection_tag_colour = ([(255, 255, 255)] + subsection_tag_colour +
                         [(item, item2) for item in subsection_tag_colour for item2 in subsection_tag_colour if
                          item != item2] +
                         [(item, item2, item3) for item in subsection_tag_colour for item2 in subsection_tag_colour for
                          item3 in subsection_tag_colour if len(set((item, item2, item3))) > 1])


class Lorebook(pygame.sprite.Sprite):
    concept_stat = None
    concept_lore = None
    history_stat = None
    history_lore = None

    faction_data = None
    troop_data = None
    leader_data = None
    battle_map_data = None
    preview_sprite_pool = None

    concept_section = 0
    history_section = 1
    faction_section = 2
    troop_section = 3
    equipment_section = 4
    status_section = 5
    skill_section = 6
    trait_section = 7
    leader_section = 8
    terrain_section = 9
    weather_section = 10
    leader_text = ("E", "E+", "D", "D+", "C", "C+", "B", "B+", "A", "A+", "S")

    def __init__(self, game, image, text_size=24):
        self.game = game
        self.main_dir = game.main_dir
        self.module_dir = game.module_dir
        self.screen_rect = game.screen_rect
        self.screen_scale = game.screen_scale
        self.localisation = game.localisation

        self._layer = 23
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(game.ui_font["main_button"], int(text_size * self.screen_scale[1]))
        self.font_header = pygame.font.Font(game.ui_font["name_font"], int(52 * self.screen_scale[1]))
        self.image = image
        self.base_image = self.image.copy()
        self.section = 0
        self.subsection = 1  # subsection of that section
        self.stat_data = None  # for getting the section stat data
        self.lore_data = None  # for getting the section lore data
        self.index_data = None  # for getting old and new subsection index reference
        self.current_subsection = None  # Subsection stat currently viewing
        self.current_subsection2 = None  # Subsection lore currently viewing
        self.subsection_list = None
        self.portrait = None
        self.preview_sprite = None

        # some sections get stat from multiple list, need to keep track of last item index
        self.equipment_stat = {}
        self.equipment_lore = {}
        self.skill_stat = {}
        self.skill_lore = {}
        self.skill_id_reindex = {}
        self.section_list = ()

        self.current_subsection_row = 0
        self.current_filter_row = 0
        self.max_row_show = 19
        self.row_size = 0
        self.filter_size = 0
        self.page = 0
        self.max_page = 0
        self.rect = self.image.get_rect(center=(self.screen_rect.width / 2, self.screen_rect.height / 2))

    def change_module(self):
        # Make new equipment list that contain all type weapon, armour, mount
        self.equipment_stat = {}
        run = 1
        for stat_list in (self.troop_data.weapon_list,
                          self.troop_data.armour_list, self.troop_data.mount_list, self.troop_data.mount_armour_list):
            for index in stat_list:
                self.equipment_stat[run] = stat_list[index]
                run += 1

        self.equipment_lore = {}
        run = 1
        for stat_list in (self.troop_data.weapon_lore,
                          self.troop_data.armour_lore, self.troop_data.mount_lore, self.troop_data.mount_armour_lore):
            for index in stat_list:
                self.equipment_lore[run] = stat_list[index]
                run += 1

        # reindex string id
        self.troop_id_reindex = {}
        run = 1
        for index in self.troop_data.troop_list:
            self.skill_stat[run] = self.troop_data.troop_list[index]
            self.troop_id_reindex[index] = run
            run += 1

        self.troop_stat = {}
        run = 1
        for key, value in self.troop_data.troop_list.items():
            self.troop_stat[run] = value | {"True ID": key}
            run += 1

        self.troop_lore = {}
        run = 1
        for value in self.troop_data.troop_lore.values():
            self.troop_lore[run] = value
            run += 1

        self.leader_id_reindex = {}
        run = 1
        for index in self.leader_data.leader_list:
            self.skill_stat[run] = self.leader_data.leader_list[index]
            self.leader_id_reindex[index] = run
            run += 1

        self.leader_stat = {}
        run = 1
        for key, value in self.leader_data.leader_list.items():
            self.leader_stat[run] = value | {"True ID": key}
            run += 1

        self.leader_lore = {}
        run = 1
        for value in self.leader_data.leader_lore.values():
            self.leader_lore[run] = value
            run += 1

        # Make new skill list that contain all troop and leader skills
        self.skill_stat = {}
        self.skill_id_reindex = {}
        run = 1
        for stat_list in (
                self.troop_data.skill_list, self.leader_data.skill_list):
            for index in stat_list:
                self.skill_stat[run] = stat_list[index]
                self.skill_id_reindex[index] = run
                run += 1

        self.skill_lore = {}
        run = 1
        for index in self.troop_data.skill_lore:  # get only from troop data
            self.skill_lore[run] = self.localisation.grab_text(key=("skill", index))
            run += 1

        self.section_tag_header = ("Tag", "Tag", "Type", "Troop Class", "Type", "Type", "Type", "Type", "Type",
                                   "Type", "Type",)

        self.tag_list = [{stuff["Tag"]: True for stuff in self.concept_stat.values() if stuff["Tag"] != ""},
                         {stuff["Tag"]: True for stuff in self.history_stat.values() if stuff["Tag"] != ""},
                         {stuff["Type"]: True for stuff in self.faction_data.faction_list.values() if
                          stuff["Type"] != ""},
                         {stuff["Troop Class"]: True for stuff in self.troop_data.troop_list.values() if
                          stuff["Troop Class"] != ""},
                         {stuff["Type"]: True for stuff in self.equipment_stat.values() if stuff["Type"] != ""},
                         {stuff["Type"]: True for stuff in self.troop_data.status_list.values() if type(stuff) != int
                          and stuff["Type"] != ""},
                         {stuff["Type"]: True for stuff in self.skill_stat.values() if stuff["Type"] != ""},
                         {stuff["Type"]: True for stuff in self.troop_data.trait_list.values() if stuff["Type"] != ""},
                         {stuff["Type"]: True for stuff in self.leader_data.leader_list.values() if
                          stuff["Type"] != ""},
                         {stuff["Type"]: True for stuff in self.battle_map_data.feature_mod.values() if
                          stuff["Type"] != ""},
                         {stuff["Type"]: True for stuff in self.battle_map_data.weather_data.values() if
                          stuff["Type"] != ""}]
        for index, tag_list in enumerate(self.tag_list):
            tag_list["No Tag"] = True
            self.tag_list[index] = {"No Tag": self.tag_list[index].pop("No Tag"), **self.tag_list[index]}

        self.section_list = ((self.concept_stat, self.concept_lore), (self.history_stat, self.history_lore),
                             (self.faction_data.faction_list, self.faction_data.faction_lore),
                             (self.troop_stat, self.troop_lore, self.troop_id_reindex),
                             (self.equipment_stat, self.equipment_lore),
                             (self.troop_data.status_list, self.troop_data.status_lore),
                             (self.skill_stat, self.skill_lore, self.skill_id_reindex),
                             (self.troop_data.trait_list, self.troop_data.trait_lore),
                             (self.leader_stat, self.leader_lore, self.leader_id_reindex),
                             (self.battle_map_data.feature_mod, self.battle_map_data.feature_mod_lore),
                             (self.battle_map_data.weather_data, self.battle_map_data.weather_lore))

    def change_page(self, page, page_button, main_ui, portrait=None):
        """Change page of the current subsection, either next or previous page"""
        self.page = page
        self.image = self.base_image.copy()  # reset encyclopedia image
        self.page_design()  # draw new pages

        # Add or remove next/previous page button
        if self.page >= self.max_page:  # remove next page button when reach last page
            main_ui.remove(page_button[1])
        else:
            main_ui.add(page_button[1])

        if self.page != 0:  # add previous page button when not at first page
            main_ui.add(page_button[0])
        else:
            main_ui.remove(page_button[0])
        # ^ End page button

    def change_section(self, section, subsection_list_box, subsection_name_group, tag_filter_group,
                       subsection_list_scroll, filter_list_box, filter_list_scroll, page_button, main_ui):
        """Change to new section either by open encyclopedia or click section button"""
        self.portrait = None
        self.section = section  # get new section
        self.subsection = 1  # reset subsection to the first one
        self.stat_data = self.section_list[self.section][0]  # get new stat data of the new section
        self.lore_data = self.section_list[self.section][1]  # get new lore data of the new section
        self.index_data = None
        if len(self.section_list[self.section]) > 2:  # section has new subsection index data
            self.index_data = self.section_list[self.section][2]
        self.max_page = 0  # reset max page
        self.current_subsection_row = 0  # reset subsection scroll to the top one
        self.current_filter_row = 0
        this_list = tuple(self.stat_data.values())  # get list of subsection
        self.subsection_list = []  # remove the header from subsection list
        # name[0] if
        # type(name) == list and "Name" != name[0] else name["Name"]
        # for name in
        #     this_list
        for index, name in enumerate(this_list):
            if type(name) is list and "Name" != name[0]:
                self.subsection_list.append(name[0])
            elif type(name) is dict:
                self.subsection_list.append(name["Name"])

        if "Name" in self.subsection_list:
            self.subsection_list.remove("Name")
        self.row_size = len(self.subsection_list)  # get size of subsection list
        self.filter_size = len(self.tag_list[self.section])

        self.change_subsection(self.subsection, page_button, main_ui)
        self.setup_subsection_list(subsection_list_box, subsection_name_group, "subsection")

        subsection_list_scroll.change_image(row_size=self.row_size)
        subsection_list_scroll.change_image(new_row=self.current_subsection_row)

        self.setup_subsection_list(filter_list_box, tag_filter_group, "tag")
        filter_list_scroll.change_image(row_size=self.filter_size)
        filter_list_scroll.change_image(new_row=self.current_filter_row)

    def change_subsection(self, subsection, page_button, main_ui):
        self.subsection = subsection
        if type(subsection) == str and self.subsection in self.index_data:  # use new subsection index instead of old one
            self.subsection = self.index_data[self.subsection]
        self.page = 0  # reset page to the first one
        self.image = self.base_image.copy()
        self.portrait = None  # reset portrait, possible for subsection to not have portrait
        main_ui.remove(page_button[0])
        main_ui.remove(page_button[1])
        self.max_page = 0  # some subsection may not have lore data in file (maxpage would be just 0)

        # Number of maximum page of lore for that subsection (4 para per page) and not count first one (name + description)
        # print(self.lore_data)
        # lore_data = self.localisation.grab_text(key=(self.subsection, ), alternative_text_data=self.lore_data)
        # print(lore_data)
        if len(self.lore_data[self.subsection]) > 2:
            self.max_page = int((len(self.lore_data[subsection]) - 2) / 4)
            main_ui.add(page_button[1])

        if self.section == self.leader_section:  # leader section exclusive for now (will merge with other section when add portrait for others)
            try:
                self.portrait = self.leader_data.images[
                    self.stat_data[self.subsection]["True ID"]]  # get leader portrait based on subsection number
            except KeyError:
                self.portrait = self.leader_data.images[
                    "other"].copy()  # Use Unknown leader image if there is none in list
                name = self.stat_data[self.subsection]["Name"].split(" ")[0]
                font = pygame.font.Font(self.game.ui_font["text_paragraph"],
                                        int(100 / (len(name) / 3) * self.screen_scale[1]))
                text_image = font.render(name, True, pygame.Color("white"))
                text_rect = text_image.get_rect(
                    center=(self.portrait.get_width() / 2, self.portrait.get_height() / 1.3))
                self.portrait.blit(text_image, text_rect)

            self.portrait = pygame.transform.scale(self.portrait, (int(200 * self.screen_scale[0]),
                                                                   int(200 * self.screen_scale[
                                                                       1])))

        elif self.section == self.troop_section:
            try:
                who_todo = {key: value for key, value in self.troop_data.troop_list.items() if key ==
                            self.stat_data[self.subsection]["True ID"]}
                preview_sprite_pool, _ = self.game.create_troop_sprite_pool(who_todo, preview=True)
                self.portrait = preview_sprite_pool[self.stat_data[self.subsection]["True ID"]]["sprite"]

            except KeyError:
                pass

        self.page_design()

    def setup_subsection_list(self, list_surface, list_group, list_type):
        """generate list of subsection of the left side of encyclopedia"""
        row = 0
        pos = list_surface.rect.topleft
        if self.current_subsection_row > self.row_size - self.max_row_show:
            self.current_subsection_row = self.row_size - self.max_row_show

        if len(list_group) > 0:  # remove previous subsection in the group before generate new one
            for stuff in list_group:
                stuff.kill()
                del stuff

        if list_type == "subsection":  # subsection list
            stat_key = tuple(self.stat_data.keys())
            loop_list = [item for item in stat_key if type(item) != str]
            for index, item in enumerate(self.subsection_list):
                if index >= self.current_subsection_row:
                    tag = "No Tag"  # white colour
                    tag_index = 0
                    if self.stat_data[stat_key[index]][self.section_tag_header[self.section]] != "":
                        tag = self.stat_data[stat_key[index]][self.section_tag_header[self.section]]
                        tag_index = tuple(self.tag_list[self.section].keys()).index(tag)
                    if self.tag_list[self.section][tag]:  # not creating subsection with disabled tag
                        list_group.add(SubsectionName(self.screen_scale, (pos[0], pos[1] + row), item,
                                                      loop_list[index],
                                                      tag_index))  # add new subsection sprite to group
                        row += (41 * self.screen_scale[1])  # next row
                        if len(list_group) > self.max_row_show:
                            break  # will not generate more than space allowed
        elif list_type == "tag":  # tag filter list
            loop_list = self.tag_list[self.section]
            for index, item in enumerate(loop_list):
                tag = tuple(self.tag_list[self.section].keys()).index(item)
                list_group.add(SubsectionName(self.screen_scale, (pos[0], pos[1] + row), item,
                                              item, tag, selected=True))  # add new subsection sprite to group
                row += (41 * self.screen_scale[1])  # next row
                if len(list_group) > self.max_row_show:
                    break  # will not generate more than space allowed

    def page_design(self):
        """Lore book format position of the text"""
        make_long_text = utility.make_long_text

        stat = self.stat_data[self.subsection]
        lore = self.lore_data[self.subsection]

        name = lore["Name"]
        text_surface = self.font_header.render(str(name), True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(int(28 * self.screen_scale[0]), int(20 * self.screen_scale[1])))
        self.image.blit(text_surface, text_rect)  # add name of item to the top of page

        if self.page == 0:
            description = lore["Description"]

            description_pos = (int(20 * self.screen_scale[1]), int(100 * self.screen_scale[0]))

            if self.portrait is not None:
                description_pos = (int(20 * self.screen_scale[1]), int(300 * self.screen_scale[0]))

                portrait_rect = self.portrait.get_rect(
                    center=(int(300 * self.screen_scale[0]), int(200 * self.screen_scale[1])))
                self.image.blit(self.portrait, portrait_rect)

            description_surface = pygame.Surface((int(550 * self.screen_scale[0]), int(400 * self.screen_scale[1])),
                                                 pygame.SRCALPHA)
            description_rect = description_surface.get_rect(topleft=description_pos)
            make_long_text(description_surface, description,
                           (int(5 * self.screen_scale[1]), int(5 * self.screen_scale[0])),
                           self.font)
            self.image.blit(description_surface, description_rect)

            row = 400 * self.screen_scale[1]
            col = 60 * self.screen_scale[0]
            if self.portrait is not None:
                row = 650 * self.screen_scale[1]
                col = 60 * self.screen_scale[0]

            # concept, history, faction section is simply for processed and does not need specific column read
            if self.section in (self.concept_section, self.history_section, self.faction_section):
                for key, value in stat.items():
                    # blit text
                    if "IMAGE:" not in value:
                        text_surface = pygame.Surface(
                            (int(480 * self.screen_scale[1]), int(300 * self.screen_scale[0])), pygame.SRCALPHA)
                        text_rect = description_surface.get_rect(topleft=(col, row))
                        make_long_text(text_surface, (key + ": " + str(value)),
                                       (int(8 * self.screen_scale[1]), int(8 * self.screen_scale[0])), self.font)

                    # blit image instead of text
                    else:
                        if "FULLIMAGE:" in value:  # full image to whole two pages
                            filename = value[10:].split("\\")[-1]
                            text_surface = utility.load_image(self.main_dir, self.screen_scale, filename,
                                                              value[10:].replace(filename, ""))
                            text_surface = pygame.transform.scale(text_surface,
                                                                  (self.image.get_width(), self.image.get_height()))
                            text_rect = description_surface.get_rect(topleft=(0, 0))
                        else:
                            filename = value[6:].split("\\")[-1]
                            text_surface = utility.load_image(self.main_dir, self.screen_scale, filename,
                                                              value[6:].replace(filename, ""))
                            text_rect = description_surface.get_rect(topleft=(col, row))
                    self.image.blit(text_surface, text_rect)

                    row += (200 * self.screen_scale[1])
                    if row >= 750 * self.screen_scale[
                        1]:  # continue drawing on the right page after reaching the end of left page
                        if col == 520 * self.screen_scale[0]:  # already on the right page
                            break
                        else:
                            col = 650 * self.screen_scale[0]
                            row = 50 * self.screen_scale[1]

            # more complex section
            elif self.section in (
                    self.troop_section, self.equipment_section, self.status_section, self.skill_section,
                    self.trait_section,
                    self.leader_section, self.terrain_section, self.weather_section):
                front_text = {key: value for key, value in stat.items() if key != "Name"}
                for key, value in front_text.items():
                    if value != "":
                        if self.section != self.equipment_section:  # equipment section need to be processed differently
                            create_text = key + ": " + str(value)
                            if key == "module":
                                create_text = ""
                            if self.section == self.troop_section or self.section == self.leader_section:  # troop section
                                if "Weapon" in key:  # weapon text with quality
                                    if value:
                                        create_text = key + ": " + self.troop_data.equipment_grade_list[value[1]][
                                            "Name"] \
                                                      + " " + self.troop_data.weapon_list[value[0]]["Name"]
                                    else:
                                        create_text = key + ": Standard Unarmed"

                                elif key == "Armour":  # armour text with quality
                                    if value:
                                        create_text = key + ": " + self.troop_data.equipment_grade_list[value[1]][
                                            "Name"] \
                                                      + " " + self.troop_data.armour_list[value[0]]["Name"]
                                    else:
                                        create_text = key + ": No Armour"

                                elif key == "Race":
                                    create_text = key + ": " + self.troop_data.race_list[value]["Name"]

                                elif key == "Mount":  # mount text with grade
                                    if value:
                                        create_text = key + ": " + self.troop_data.mount_grade_list[value[1]][
                                            "Name"] + " " + \
                                                      self.troop_data.mount_list[value[0]]["Name"] + "//" + \
                                                      self.troop_data.mount_armour_list[value[2]]["Name"]
                                    else:
                                        create_text = key + ": No Mount"

                                elif key == "Trait":  # troop properties list
                                    trait_list = ""
                                    if 0 not in value:
                                        for this_text in value:
                                            if this_text in self.troop_data.trait_list:  # in case user put in trait not existed in module
                                                trait_list += self.troop_data.trait_list[this_text]["Name"] + ", "
                                        trait_list = trait_list[0:-2]
                                        create_text = key + ": " + trait_list

                                    else:
                                        create_text = ""
                                        pass

                                if self.section == self.troop_section:  # troop section
                                    if key == "Grade":  # grade text instead of number
                                        create_text = key + ": " + self.troop_data.grade_list[value]["Name"]

                                    elif key == "Troop Type":
                                        create_text = key + ": " + self.troop_data.troop_class_list[value]["Name"]

                                    elif "Skill" in key:  # skill text instead of number
                                        skill_list = ""
                                        if key == "Charge Skill":
                                            if value in self.troop_data.skill_list:  # only include skill if exist in module
                                                skill_list += self.troop_data.skill_list[value]["Name"]
                                            create_text = key + ": " + skill_list
                                        elif 0 not in value:
                                            for this_text in value:
                                                if this_text in self.troop_data.skill_list:  # only include skill in module
                                                    skill_list += self.troop_data.skill_list[this_text]["Name"] + ", "
                                            skill_list = skill_list[0:-2]
                                            create_text = key + ": " + skill_list
                                        else:
                                            create_text = ""
                                            pass

                                    elif key == "Role":
                                        # role is not type, it represents troop classification to suggest what it excels
                                        role_list = {0: "None", 1: "Offensive", 2: "Defensive", 3: "Skirmisher",
                                                     4: "Shock", 5: "Support", 6: "Artillery",
                                                     7: "Ambusher", 8: "Sniper", 9: "Recon", "": ""}
                                        role = [role_list[item] for item in
                                                value]

                                        create_text = "Specilaised Role: "
                                        if len(role) == 0:
                                            create_text += "None, "
                                        for this_role in role:
                                            create_text += this_role + ", "
                                        create_text = create_text[0:-2]

                                    elif key == "Type":
                                        create_text = ""
                                        pass

                                else:  # leader section
                                    if key in ("Melee Command", "Range Command", "Cavalry Command", "Combat"):
                                        create_text = key + ": " + self.leader_text[value]

                                    elif key == "Social Class":
                                        create_text = key + ": " + self.leader_data.leader_class[value][
                                            "Leader Social Class"]

                                    elif key == "Skill":  # skill text instead of number
                                        skill_list = ""
                                        if 0 not in value:
                                            for this_text in value:
                                                if this_text in self.leader_data.skill_list:  # only include skill in module
                                                    skill_list += self.leader_data.skill_list[this_text]["Name"] + ", "
                                            skill_list = skill_list[0:-2]
                                            create_text = key + ": " + skill_list
                                        else:
                                            create_text = ""
                                            pass

                                    elif key == "Formation":
                                        create_text = key + ": " + str(value).replace("[", "").replace("]", ""). \
                                            replace("'", "")

                                    elif key in ("Size", "True ID", "Sprite ID"):
                                        create_text = ""

                            elif self.section in (self.skill_section, self.trait_section, self.status_section):
                                if key == "Status" or key == "Enemy Status":  # status list
                                    status_list = ""
                                    if 0 not in value:
                                        for this_text in value:
                                            if this_text in self.troop_data.status_list:  # in case user put in trait not existed in module
                                                status_list += self.troop_data.status_list[this_text]["Name"] + ", "
                                        status_list = status_list[0:-2]
                                        create_text = key + ": " + status_list
                                    else:
                                        create_text = ""
                                        pass
                                if self.section == self.skill_section:
                                    if key == "Troop Type":
                                        create_text = key + ": " + ("Any", "Infantry", "Cavalry")[value]

                                if value in (0, 1):
                                    create_text = ""

                        else:  # equipment section, header depends on equipment type
                            create_text = key + ": " + str(value)

                            if key == "ImageID":  # not used in encyclopedia
                                create_text = ""
                                pass

                            elif key == "Properties":
                                trait_list = ""
                                if 0 not in value:
                                    for this_text in value:
                                        if this_text in self.troop_data.trait_list:  # in case user put in trait not existed in module
                                            trait_list += self.troop_data.trait_list[this_text][0] + ", "
                                    trait_list = trait_list[0:-2]
                                    create_text = key + ": " + trait_list
                                else:
                                    create_text = ""
                                    pass

                        if create_text != "":  # text not empty, draw it. Else do nothing
                            text_surface = self.font.render(create_text, True, (0, 0, 0))
                            text_rect = text_surface.get_rect(topleft=(col, row))
                            self.image.blit(text_surface, text_rect)
                            row += (30 * self.screen_scale[1])
                            if row >= 750 * self.screen_scale[1]:
                                col = 650 * self.screen_scale[0]
                                row = 50 * self.screen_scale[1]

        else:  # lore page, the paragraph can be in text or image (IMAGE:)
            if self.max_page != 0:
                if self.page == 1:  # first page skip first two paragraph (name and description)
                    lore = self.lore_data[self.subsection][2:]
                else:
                    lore = self.lore_data[self.subsection][(self.page * 4) + 2:]

                row = int(80 * self.screen_scale[1])
                col = int(50 * self.screen_scale[0])
                for index, text in enumerate(lore):
                    if text != "":
                        # blit paragraph of text
                        text_surface = pygame.Surface((500 * self.screen_scale[0], 370 * self.screen_scale[1]),
                                                      pygame.SRCALPHA)
                        paragraph_font = self.font
                        if "{" in text and "}" in text:
                            syntax = text.split("}")[0][1:]
                            syntax = syntax.split(",")
                            text = text.split("}")[1]
                            for this_syntax in syntax:
                                if "FULLIMAGE:" in this_syntax:  # blit image to whole lore book image
                                    filename = this_syntax[10:].split("\\")[-1]
                                    image_surface = utility.load_image(self.module_dir, self.screen_scale, filename,
                                                                       this_syntax[10:].replace(filename, "").split("\\"))
                                    image_surface = pygame.transform.scale(image_surface, (self.image.get_width(),
                                                                                           self.image.get_height()))
                                    self.image.blit(image_surface, image_surface.get_rect(topleft=(0, 0)))
                                elif "IMAGE:" in this_syntax:  # blit image to paragraph
                                    filename = this_syntax[6:].split("\\")[-1]
                                    image_surface = utility.load_image(self.module_dir, self.screen_scale, filename,
                                                                       this_syntax[6:].replace(filename, "").split("\\"))
                                    self.image.blit(image_surface, image_surface.get_rect(topleft=(col, row)))
                                elif "FONT:" in this_syntax:
                                    new_font = this_syntax[4:].split("\\")[0]
                                    new_font_size = self.font.get_height()
                                    if "\\" in this_syntax:
                                        new_font_size = this_syntax[4:].split("\\")[1]
                                    paragraph_font = pygame.font.Font(self.game.ui_font[new_font],
                                                                      int(new_font_size * self.screen_scale[1]))

                        make_long_text(text_surface, text, (5 * self.screen_scale[0], 5 * self.screen_scale[1]),
                                       paragraph_font)
                        text_rect = text_surface.get_rect(topleft=(col, row))

                        self.image.blit(text_surface, text_rect)

                        row += (400 * self.screen_scale[1])
                        if row >= 600 * self.screen_scale[1]:
                            if col == 650 * self.screen_scale[0]:
                                break
                            else:
                                col = 650 * self.screen_scale[0]
                                row = 50 * self.screen_scale[1]


class SubsectionList(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 23
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(topright=pos)
        self.max_row_show = 19


class SubsectionName(UIMenu, pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, name, subsection, tag, selected=False, text_size=28):
        self._layer = 24
        UIMenu.__init__(self)
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(self.ui_font["main_button"], int(text_size * screen_scale[1]))
        self.selected = False
        self.name = str(name)

        # Border
        self.image = pygame.Surface((int(300 * screen_scale[0]), int(40 * screen_scale[1])))
        self.image.fill((0, 0, 0))  # black corner

        # Body square
        self.small_image = pygame.Surface((int(290 * screen_scale[0]), int(34 * screen_scale[1])))
        colour = subsection_tag_colour[tag]
        if type(colour[0]) == int:
            self.small_image.fill(colour)
        else:  # multiple colour
            starting_pos = 0
            colour_size = self.small_image.get_width() / len(colour)
            for this_colour in colour:
                colour_1_surface = pygame.Surface((colour_size, self.small_image.get_height()))
                rect = colour_1_surface.get_rect(topleft=(starting_pos, 0))
                colour_1_surface.fill(this_colour)
                self.small_image.blit(colour_1_surface, rect)
                starting_pos += colour_size
        self.small_rect = self.small_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.small_image, self.small_rect)

        # Subsection name text
        self.text_surface = self.font.render(self.name, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(midleft=(int(5 * screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(self.text_surface, self.text_rect)

        self.subsection = subsection
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

        if selected:
            self.selection()

    def selection(self):
        if self.selected:
            self.selected = False
        else:
            self.selected = True
        if self.selected:
            self.image.fill((233, 214, 82))
        else:
            self.image.fill((0, 0, 0))
        self.image.blit(self.small_image, self.small_rect)
        self.image.blit(self.text_surface, self.text_rect)


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

def lorebook_process(self, ui, mouse_up, mouse_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    """Lorebook user interaction"""
    command = None
    close = False
    if mouse_up or mouse_down:  # mouse down (hold click) only for subsection list scroll
        if mouse_up:
            for button in self.lore_button_ui:
                if button in ui and button.rect.collidepoint(self.mouse_pos):  # click button
                    if button.event in range(0, 11):  # section button
                        self.encyclopedia.change_section(button.event, self.lore_name_list, self.subsection_name,
                                                         self.tag_filter_name, self.lore_name_list.scroll,
                                                         self.filter_tag_list, self.filter_tag_list.scroll,
                                                         self.page_button, ui)  # change to section of that button

                    elif button.event == "close" or esc_press:  # Close button
                        close = True

                    elif button.event == "previous":  # Previous page button
                        self.encyclopedia.change_page(self.encyclopedia.page - 1, self.page_button,
                                                      ui)  # go back 1 page

                    elif button.event == "next":  # Next page button
                        self.encyclopedia.change_page(self.encyclopedia.page + 1, self.page_button,
                                                      ui)  # go forward 1 page

                    break  # found clicked button, break loop

        if self.lore_name_list.scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
            self.encyclopedia.current_subsection_row = self.lore_name_list.scroll.player_input(
                self.mouse_pos)  # update the scroll and get new current subsection
            self.encyclopedia.setup_subsection_list(self.lore_name_list,
                                                    self.subsection_name, "subsection")  # update subsection name list
        elif self.filter_tag_list.scroll.rect.collidepoint(self.mouse_pos):  # click on filter list scroll
            self.encyclopedia.current_filter_row = self.filter_tag_list.scroll.player_input(
                self.mouse_pos)  # update the scroll and get new current subsection
            self.encyclopedia.setup_subsection_list(self.filter_tag_list,
                                                    self.tag_filter_name, "tag")  # update subsection name list
        else:
            if mouse_up:
                for name in self.subsection_name:
                    if name.rect.collidepoint(self.mouse_pos):  # click on subsection name
                        self.encyclopedia.change_subsection(name.subsection, self.page_button, ui)  # change subsection
                        break  # found clicked subsection, break loop
                for name in self.tag_filter_name:
                    if name.rect.collidepoint(self.mouse_pos):  # click on subsection name
                        name.selection()
                        self.encyclopedia.tag_list[self.encyclopedia.section][name.name] = name.selected
                        self.encyclopedia.setup_subsection_list(self.lore_name_list, self.subsection_name,
                                                                "subsection")  # update subsection name list
                        break  # found clicked subsection, break loop

    elif mouse_scroll_up:
        if self.lore_name_list.rect.collidepoint(self.mouse_pos):  # Scrolling at lore book subsection list
            if self.encyclopedia.current_subsection_row > 0:
                self.encyclopedia.current_subsection_row -= 1
                self.encyclopedia.setup_subsection_list(self.lore_name_list, self.subsection_name, "subsection")
                self.lore_name_list.scroll.change_image(new_row=self.encyclopedia.current_subsection_row)
        elif self.filter_tag_list.rect.collidepoint(self.mouse_pos):  # Scrolling at lore book subsection list
            if self.encyclopedia.current_filter_row > 0:
                self.encyclopedia.current_filter_row -= 1
                self.encyclopedia.setup_subsection_list(self.filter_tag_list, self.tag_filter_name, "tag")
                self.filter_tag_list.scroll.change_image(new_row=self.encyclopedia.current_filter_row)

    elif mouse_scroll_down:
        if self.lore_name_list.rect.collidepoint(self.mouse_pos):  # Scrolling at lore book subsection list
            if self.encyclopedia.current_subsection_row + self.encyclopedia.max_row_show - 1 < self.encyclopedia.row_size:
                self.encyclopedia.current_subsection_row += 1
                self.encyclopedia.setup_subsection_list(self.lore_name_list, self.subsection_name, "subsection")
                self.lore_name_list.scroll.change_image(new_row=self.encyclopedia.current_subsection_row)

        elif self.filter_tag_list.rect.collidepoint(self.mouse_pos):  # Scrolling at lore book subsection list
            if self.encyclopedia.current_filter_row + self.encyclopedia.max_row_show - 1 < self.encyclopedia.row_size:
                self.encyclopedia.current_filter_row += 1
                self.encyclopedia.setup_subsection_list(self.filter_tag_list, self.tag_filter_name, "tag")
                self.filter_tag_list.scroll.change_image(new_row=self.encyclopedia.current_filter_row)

    if close or esc_press:
        self.portrait = None
        ui.remove(self.encyclopedia_stuff)  # remove encyclopedia related sprites
        for group in (self.subsection_name, self.tag_filter_name):
            for name in group:  # remove subsection name
                name.kill()
                del name
        command = "exit"

    return command
