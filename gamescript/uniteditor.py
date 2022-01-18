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
        self.army_position = army_position  # position in the unit (e.g. general or sub-general)
        self.img_position = self.base_img_position[self.army_position]  # image position based on army_position

        self.change_preview_leader(leader_id, leader_stat)

    def change_preview_leader(self, leader_id, leader_stat):
        self.leader_id = leader_id  # leader_id is only used as reference to the leader data

        stat = leader_stat.leader_list[leader_id]

        self.name = stat["Name"]
        self.authority = stat["Authority"]
        self.social = leader_stat.leader_class[stat["Social Class"]]
        self.description = stat["Description"]

        try:  # Put leader image into leader slot
            image_name = str(leader_id) + ".png"
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
            self.subunit_pos = subunit.game_id


class SelectedPresetBorder(pygame.sprite.Sprite):
    def __init__(self, width, height):
        self._layer = 16
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width + 1, height + 1), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (203, 176, 99), (0, 0, self.image.get_width(), self.image.get_height()), 6)
        self.rect = self.image.get_rect(topleft=(0, 0))

    def change_pos(self, pos):
        self.rect = self.image.get_rect(topleft=pos)


class UnitBuildSlot(pygame.sprite.Sprite):

    def __init__(self, team, colour):
        """Dummy unit for editing"""
        self._layer = 2
        pygame.sprite.Sprite.__init__(self)
        self.selected = False
        self.team = team
        self.colour = colour
        self.leader = None
        self.authority = 100
        self.state = 0
        self.ammo_now = 0
        self.game_id = 0

        self.terrain = 0
        self.feature = 0
        self.weather = 0

        self.commander = True

        self.coa = pygame.Surface((0, 0))  # empty coa_list to prevent leader ui error


class WarningMsg(pygame.sprite.Sprite):
    eightsubunit_warn = "- Require at least 8 sub-units for both test and employment"
    mainleader_warn = "- Require a gamestart leader for both test and employment"
    emptyrowcol_warn = "- Empty row or column will be removed when employed"
    duplicateleader_warn = "- Duplicated leader will be removed with No Duplicated leader option enable"
    multifaction_warn = "- Leaders or subunits from multiple factions will not be usable with No Multiple Faction option enable"

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
        pygame.sprite.Sprite.__init__(self)
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
