import ast
import csv
import os

import pygame
import pygame.freetype
from pygame.transform import scale


class PreviewBox(pygame.sprite.Sprite):
    main_dir = None
    effect_image = None

    def __init__(self, pos):
        import main
        screen_rect = main.screen_rect
        self.width_adjust = screen_rect.width / 1366
        self.height_adjust = screen_rect.height / 768

        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.max_width = int(500 * self.width_adjust)
        self.max_height = int(500 * self.height_adjust)
        self.image = pygame.Surface((self.max_width, self.max_height))

        self.font = pygame.font.SysFont("timesnewroman", int(24 * self.height_adjust))

        self.new_colour_list = {}
        with open(self.main_dir + os.path.join("data", "map", "colourchange.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    elif "," in i:
                        row[n] = ast.literal_eval(i)
                self.new_colour_list[row[0]] = row[1:]

        self.change_terrain(self.new_colour_list[0])

        self.rect = self.image.get_rect(center=pos)

    def change_terrain(self, new_terrain):
        self.image.fill(new_terrain[1])

        rect = self.image.get_rect(topleft=(0, 0))
        self.image.blit(self.effect_image, rect)  # add special filter effect that make it look like old map

        text_surface = self.font.render(new_terrain[0], True, (0, 0, 0))
        text_rect = text_surface.get_rect(
            center=(self.image.get_width() / 2, self.image.get_height() - (text_surface.get_height() / 2)))
        self.image.blit(text_surface, text_rect)


class PreviewLeader(pygame.sprite.Sprite):
    base_img_position = [(134, 185), (80, 235), (190, 235), (134, 283)]  # leader image position in command ui

    def __init__(self, leader_id, subunit_pos, army_position, leader_stat):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.state = 0
        self.subunit = None

        self.leader_id = leader_id

        self.subunit_pos = subunit_pos  # Squad position is the index of subunit in subunit sprite loop
        self.army_position = army_position  # position in the parentunit (e.g. general or sub-general)
        self.img_position = self.base_img_position[self.army_position]  # image position based on armyposition

        self.change_leader(leader_id, leader_stat)

    def change_leader(self, leader_id, leader_stat):
        self.leader_id = leader_id  # leaderid is only used as reference to the leader data

        stat = leader_stat.leader_list[leader_id]
        leader_header = leader_stat.leader_list_header

        self.name = stat[0]
        self.authority = stat[2]
        self.social = leader_stat.leader_class[stat[leader_header["Social Class"]]]
        self.description = stat[-1]

        try:  # Put leader image into leader slot
            image_name = str(leader_stat.image_order.index(leader_id)) + ".png"
            self.full_image = leader_stat.images[image_name].copy()
        except:  # Use Unknown leader image if there is none in list
            self.full_image = leader_stat.images["9999999.png"].copy()

        self.image = pygame.transform.scale(self.full_image, (50, 50))
        self.rect = self.image.get_rect(center=self.img_position)
        self.image_original = self.image.copy()

        self.commander = False  # army commander
        self.originalcommander = False  # the first army commander at the start of battle

    def change_subunit(self, subunit):
        self.subunit = subunit
        if subunit is None:
            self.subunit_pos = 0
        else:
            self.subunit_pos = subunit.slot_number


class SelectedPresetBorder(pygame.sprite.Sprite):
    def __init__(self, width, height):
        self._layer = 16
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width + 1, height + 1), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (203, 176, 99), (0, 0, self.image.get_width(), self.image.get_height()), 6)
        self.rect = self.image.get_rect(topleft=(0, 0))

    def change_pos(self, pos):
        self.rect = self.image.get_rect(topleft=pos)


class Unitbuildslot(pygame.sprite.Sprite):
    sprite_width = 0  # subunit sprite width size get add from gamestart
    sprite_height = 0  # subunit sprite height size get add from gamestart
    images = []  # image related to subunit sprite, get add from loadgamedata in gamelongscript
    weapon_list = None
    armour_list = None
    stat_list = None
    genre = None

    def __init__(self, game_id, team, army_id, position, start_pos, slot_number, team_colour):
        self.colour = team_colour
        self._layer = 2
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.selected = False
        self.game_id = game_id
        self.team = team
        self.army_id = army_id
        self.troop_id = 0  # index according to sub-unit file
        self.name = "None"
        self.leader = None
        self.height = 100
        self.commander = False
        if self.army_id == 0:
            self.commander = True
        self.authority = 100
        self.state = 0
        self.ammo_now = 0

        self.terrain = 0
        self.feature = 0
        self.weather = 0

        self.coa = pygame.Surface((0, 0))  # empty coa_list to prevent leader ui error

        self.change_team(False)

        self.slot_number = slot_number
        self.army_pos = position  # position in parentunit sprite
        self.inspect_pos = (self.army_pos[0] + start_pos[0], self.army_pos[1] + start_pos[1])  # position in inspect ui
        self.rect = self.image.get_rect(topleft=self.inspect_pos)

    def change_team(self, change_troop):
        self.image = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        white_image = pygame.Surface((self.sprite_width - 2, self.sprite_height - 2))
        white_image.fill(self.colour[self.team])
        white_rect = white_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(white_image, white_rect)
        self.image_original = self.image.copy()
        if change_troop:
            self.change_troop(self.troop_id, self.terrain, self.feature, self.weather)

    def change_troop(self, troop_index, terrain, feature, weather):
        self.image = self.image_original.copy()
        if self.troop_id != troop_index:
            self.troop_id = troop_index
            self.create_troop_stat(self.stat_list.troop_list[troop_index].copy(), 100, 100, [1, 1])

        self.terrain = terrain
        self.feature = feature
        self.weather = weather
        if self.name != "None":
            # v subunit block team colour
            if self.subunit_type == 2:  # cavalry draw line on block
                pygame.draw.line(self.image, (0, 0, 0), (0, 0), (self.image.get_width(), self.image.get_height()), 2)
            # ^ End subunit block team colour

            # v health circle image setup
            health_image = self.images["ui_health_circle_100.png"]
            health_image_rect = health_image.get_rect(center=self.image.get_rect().center)
            self.image.blit(health_image, health_image_rect)
            # ^ End health circle

            # v stamina circle image setup
            stamina_image = self.images["ui_stamina_circle_100.png"]
            stamina_image_rect = stamina_image.get_rect(center=self.image.get_rect().center)
            self.image.blit(stamina_image, stamina_image_rect)
            # ^ End stamina circle

            # v weapon class icon in middle circle
            image1 = self.weapon_list.images[
                self.weapon_list.weapon_list[self.primary_main_weapon[0]][-3]]  # image on subunit sprite
            image1rect = image1.get_rect(center=self.image.get_rect().center)
            self.image.blit(image1, image1rect)
            # ^ End weapon icon


class WarningMsg(pygame.sprite.Sprite):
    eightsubunit_warn = "- Require at least 8 sub-units for both test and employment"
    mainleader_warn = "- Require a gamestart leader for both test and employment"
    emptyrowcol_warn = "- Empty row or column will be removed when employed"
    duplicateleader_warn = "- Duplicated leader will be removed with No Duplicated leaer option enable"
    multifaction_warn = "- Leaders or subunits from multiple factions will not be usable with No Multiple Faction option enable"

    # outofmap_warn = "- There are sub-unit(s) outside of map border, they will retreat when test start"

    def __init__(self, screen_scale, pos):
        self._layer = 18
        pygame.sprite.Sprite.__init__(self)
        self.screen_scale = screen_scale
        self.font = pygame.font.SysFont("timesnewroman", int(20 * self.screen_scale[1]))
        self.rowcount = 0
        self.warning_log = []
        self.fix_width = int(230 * screen_scale[1])
        self.pos = pos

    def warning(self, warn_list):
        self.warning_log = []
        self.rowcount = len(warn_list)
        for warn_item in warn_list:
            if len(warn_item) > 25:
                new_row = len(warn_item) / 25
                if new_row.is_integer() is False:
                    new_row = int(new_row) + 1
                else:
                    new_row = int(new_row)
                self.rowcount += new_row

                cut_space = [index for index, letter in enumerate(warn_item) if letter == " "]
                start_index = 0
                for run in range(1, new_row + 1):
                    text_cut_number = [number for number in cut_space if number <= run * 25]
                    cut_number = text_cut_number[-1]
                    final_text_output = warn_item[start_index:cut_number]
                    if run == new_row:
                        final_text_output = warn_item[start_index:]
                    self.warning_log.append(final_text_output)
                    start_index = cut_number + 1
            else:
                self.warning_log.append(warn_item)

        self.image = pygame.Surface((self.fix_width, int(22 * self.screen_scale[1]) * self.rowcount))
        self.image.fill((0, 0, 0))
        white_image = pygame.Surface((self.fix_width - 2, (int(22 * self.screen_scale[1]) * self.rowcount) - 2))
        white_image.fill((255, 255, 255))
        white_image_rect = white_image.get_rect(topleft=(1, 1))
        self.image.blit(white_image, white_image_rect)
        row = 5
        for index, text in enumerate(self.warning_log):
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(5, row))
            self.image.blit(text_surface, text_rect)
            row += 20  # Whitespace between text row
        self.rect = self.image.get_rect(topleft=self.pos)


class PreviewChangeButton(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, image, text):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("timesnewroman", int(30 * screen_scale[1]))

        self.image = image.copy()
        self.image_original = self.image.copy()

        self.text = text
        self.textsurface = self.font.render(text, True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.textsurface, self.textrect)

        self.rect = self.image.get_rect(midbottom=pos)

    def changetext(self, text):
        self.image = self.image_original.copy()
        self.text = text
        self.textsurface = self.font.render(text, True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.textsurface, self.textrect)


class FilterBox(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[0]),
                                                    int(image.get_height() * screen_scale[1])))
        self.rect = self.image.get_rect(topleft=pos)
