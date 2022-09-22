import datetime

import pygame
import pygame.freetype
from gamescript.common import utility, animation

text_render = utility.text_render

class UIButton(pygame.sprite.Sprite):
    def __init__(self, image, event=None, layer=11):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self)
        self.pos = (0, 0)
        self.image = image
        self.event = event
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)


class SwitchButton(pygame.sprite.Sprite):
    def __init__(self, images):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (0, 0)
        self.images = images
        self.image = self.images[0]
        self.event = 0
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False
        self.last_event = 0

    def update(self):
        if self.event != self.last_event:
            self.image = self.images[self.event]
            self.rect = self.image.get_rect(center=self.pos)
            self.last_event = self.event

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def change_genre(self, images):
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)


class PopupIcon(pygame.sprite.Sprite):
    def __init__(self, image, pos, event, game_ui, item_id=""):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.image = image
        self.event = 0
        self.rect = self.image.get_rect(center=(self.pos))
        self.mouse_over = False
        self.item_id = item_id


class InspectUI(pygame.sprite.Sprite):
    def __init__(self, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image_original = self.image.copy()

    def change_pos(self, pos):
        """change position of ui to new one"""
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)


class TopBar(pygame.sprite.Sprite):
    def __init__(self, image, icon, text="", text_size=16):
        from gamescript import game
        self.unit_state_text = game.unit_state_text
        self.morale_state_text = game.morale_state_text
        self.stamina_state_text = game.stamina_state_text

        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", text_size)
        self.text = text
        self.image = image
        self.icon = icon
        self.value = [-1, -1]
        self.last_value = 0
        self.option = 0
        self.last_who = -1  # last showed parent unit, start with -1 which mean any new clicked will show up at start

        position = 10
        for ic in self.icon:  # Blit icon into topbar ui
            self.icon_rect = self.icon[ic].get_rect(
                topleft=(self.image.get_rect()[0] + position, self.image.get_rect()[1]))
            self.image.blit(self.icon[ic], self.icon_rect)
            position += 90

        self.image_original = self.image.copy()

    def change_pos(self, pos):
        """change position of ui to new one"""
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def value_input(self, who, weapon_list="", armour_list="", button="", change_option=0, split=False):
        position = 65
        self.value = ["{:,}".format(who.troop_number) + " (" + "{:,}".format(who.max_health) + ")", who.stamina_state,
                      who.morale_state, who.state]
        if self.value[3] in self.unit_state_text:  # Check subunit state and blit name
            self.value[3] = self.unit_state_text[self.value[3]]
        # if type(self.value[2]) != str:

        self.value[2] = round(self.value[2] / 10)  # morale state
        if self.value[2] in self.morale_state_text:  # Check if morale state in the list and blit the name
            self.value[2] = self.morale_state_text[self.value[2]]
        elif self.value[2] > 15:  # if morale somehow too high use the highest morale state one
            self.value[2] = self.morale_state_text[15]

        self.value[1] = round(self.value[1] / 10)  # stamina state
        if self.value[1] in self.stamina_state_text:  # Check if stamina state and blit the name
            self.value[1] = self.stamina_state_text[self.value[1]]

        if self.value != self.last_value or split:  # only blit new text when value change or subunit split
            self.image = self.image_original.copy()
            for value in self.value:  # blit value text
                text_surface = self.font.render(str(value), True, (0, 0, 0))
                text_rect = text_surface.get_rect(
                    center=(self.image.get_rect()[0] + position, self.image.get_rect()[1] + 25))
                self.image.blit(text_surface, text_rect)
                if position >= 200:
                    position += 50
                else:
                    position += 95
            self.last_value = self.value
    # for line in range(len(label)):
    #     surface.blit(label(line), (position[0], position[1] + (line * font_size) + (15 * line)))


class TroopCard(pygame.sprite.Sprite):
    weapon_list = None
    armour_list = None
    terrain_list = None
    feature_list = None

    def __init__(self, image, font_size=16):
        from gamescript import game

        self.subunit_state_text = game.subunit_state_text
        self.quality_text = game.quality_text
        self.leader_state_text = game.leader_state_text
        # self.terrain_list = terrain_list

        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", font_size)
        self.image = image
        self.value = [-1, -1]
        self.last_value = 0
        self.option = 0

        self.image_original = self.image.copy()

        self.font_head = pygame.font.SysFont("curlz", font_size + 4)
        self.font_head.set_italic(True)
        self.font_long = pygame.font.SysFont("helvetica", font_size - 2)
        self.value = {"": "", "Troop: ": 0, "Stamina: ": 0, "Morale: ": 0, "Discipline: ": 0, "Melee Attack: ": 0,
                      "Melee Defense: ": 0, "Range Defense: ": 0, "Speed: ": 0, "Accuracy: ": 0,
                      "Range: ": 0, "Reload: ": 0, "Ammunition: ": 0, "Weapon CD: ": 0, "Charge Power: ": 0,
                      "Charge Defense: ": 0, "Mental: ": 0}  # stat

    def change_pos(self, pos):
        """change position of ui to new one"""
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def value_input(self, who, button="", change_option=0, split=False):
        make_long_text = utility.make_long_text
        position = 15  # starting row
        position_x = 45  # starting point of text
        self.value[""] = who.name
        self.value["Troop: "] = str(who.troop_number) + " (" + str(int(who.max_troop)) + ")"
        self.value["Stamina: "] = str(int(who.stamina)) + ", " + str(self.subunit_state_text[who.state])
        self.value["Morale: "] = str(int(who.morale))
        self.value["Discipline: "] = str(int(who.discipline))
        self.value["Melee Attack: "] = str(int(who.melee_attack))
        self.value["Melee Defense: "] = str(int(who.melee_def))
        self.value["Range Defense: "] = str(int(who.range_def))
        self.value["Speed: "] = str(int(who.speed))
        self.value["Accuracy: "] = str(int(who.accuracy))
        self.value["Range: "] = str(who.shoot_range).replace("{", "").replace("}", "")
        self.value["Reload: "] = str(int(who.reload))
        self.value["Weapon CD: "] = str(int(who.weapon_cooldown[0])) + ", " + str(int(who.weapon_cooldown[1]))
        self.value["Ammunition: "] = str([str(key + key2) + " : " + str(int(value2)) + "/" +
                                          str(int(who.magazine_size[key][key2])) for key, value in
                                          who.magazine_count.items()
                                          for key2, value2 in value.items()]).replace("'", "").replace("[", "").replace(
            "]", "")
        self.value["Charge Power: "] = str(int(who.charge))
        self.value["Charge Defense: "] = str(int(who.charge_def))
        self.value["Mental: "] = str(int(who.mental_text))

        self.value2 = [who.trait["Original"] | who.trait["Weapon"], who.skill, who.skill_cooldown, who.skill_effect, who.status_effect]
        self.description = who.description
        if type(self.description) == list:
            self.description = self.description[0]
        if self.value.values() != self.last_value or change_option == 1 or who.game_id != self.last_who:
            self.image = self.image_original.copy()
            row = 0
            leader_text = ""
            if who.leader is not None and who.leader.name != "None":
                leader_text = "/" + str(who.leader.name)
                if who.leader.state in self.leader_state_text:
                    leader_text += " " + "(" + self.leader_state_text[who.leader.state] + ")"
            text_surface = self.font_head.render(self.value[""] + leader_text, True,
                                                 (0, 0, 0))  # subunit and leader name at the top
            text_rect = text_surface.get_rect(
                midleft=(self.image.get_rect()[0] + position_x, self.image.get_rect()[1] + position))
            self.image.blit(text_surface, text_rect)
            row += 1
            position += 20
            if self.option == 1:  # stat card
                for key, value in self.value.items():
                    if key != "" and value != "":
                        value = value.replace("inf", "\u221e")  # use infinity sign
                        text_surface = self.font.render(key + value, True, (0, 0, 0))
                        text_rect = text_surface.get_rect(
                            midleft=(self.image.get_rect()[0] + position_x, self.image.get_rect()[1] + position))
                        self.image.blit(text_surface, text_rect)
                        position += 20
                        row += 1
                        if row == 9:
                            position_x, position = 200, 35
            elif self.option == 0:  # description card
                make_long_text(self.image, self.description, (42, 25), self.font_long)  # blit long description
            elif self.option == 3:  # equipment and terrain
                # Terrain text
                terrain = self.terrain_list[who.terrain]
                if who.feature is not None:
                    terrain += "/" + self.feature_list[who.feature]

                # Equipment text
                text_value = ["Weapon 1: " +
                              self.quality_text[who.primary_main_weapon[1]] + " " + str(
                    self.weapon_list[who.primary_main_weapon[0]]["Name"]) + " / " +
                              self.quality_text[who.primary_sub_weapon[1]] + " " + str(
                    self.weapon_list[who.primary_sub_weapon[0]]["Name"]),
                              "Weapon 2: " + self.quality_text[who.secondary_main_weapon[1]] + " " + str(
                                  self.weapon_list[who.secondary_main_weapon[0]]["Name"]) + " / " +
                              self.quality_text[who.secondary_sub_weapon[1]] + " " + str(
                                  self.weapon_list[who.secondary_sub_weapon[0]]["Name"])]

                text_value += ["Armour : " + str(self.armour_list[who.armour_gear[0]]["Name"]) + ", W: " +
                               str(self.armour_list[who.armour_gear[0]]["Weight"]),
                               "Total Weight:" + str(who.weight), "Terrain:" + terrain,
                               "Height:" + str(who.height), "Temperature:" + str(who.temperature_count).split(".")[0]]

                if who.mount["Name"] != "None":  # if mount is not the None mount id 1
                    armour_text = "//" + who.mount_armour["Name"]
                    if who.mount_armour["Name"] != "None":
                        armour_text = ""
                    text_value.insert(3, "Mount:" + who.mount_grade["Name"] + " " + who.mount["Name"] + armour_text)

                # Add text
                for text in text_value:
                    text_surface = self.font.render(str(text), 1, (0, 0, 0))
                    text_rect = text_surface.get_rect(
                        midleft=(self.image.get_rect()[0] + position_x, self.image.get_rect()[1] + position))
                    self.image.blit(text_surface, text_rect)
                    position += 20

        self.last_value = self.value.values()
        self.last_who = who.game_id


class CommandBar(pygame.sprite.Sprite):
    def __init__(self, text_size=16):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", text_size)
        self.value = [-1, -1]
        self.last_value = 0
        self.option = 0
        self.last_who = -1  # last showed parent unit, start with -1 which mean any new clicked will show up at start
        self.last_auth = 0

    def load_sprite(self, image, icon):
        self.image = image
        self.icon = icon
        self.inspect_pos = ((self.image.get_width() / 2.1, self.image.get_height() / 2.5),  # general
                            (self.image.get_width() / 3.5, self.image.get_height() / 1.6),  # left sub general
                            (self.image.get_width() / 1.5, self.image.get_height() / 1.6),  # right sub general
                            (self.image.get_width() / 2.1, self.image.get_height() / 1.2))  # advisor

        icon_rect = self.icon["authority"].get_rect(
            center=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.1, self.image.get_rect()[1] + 40))
        self.image.blit(self.icon["authority"], icon_rect)
        try:
            self.white = [self.icon["white_king"], self.icon["white_queen"], self.icon["white_rook"],
                          self.icon["white_knight_left"],
                          self.icon["white_knight_right"], self.icon["white_bishop"]]  # team 1 white chess head
            self.black = [self.icon["red_king"], self.icon["red_queen"], self.icon["red_rook"],
                          self.icon["red_knight_left"],
                          self.icon["red_knight_right"], self.icon["red_bishop"]]  # team 2 black chess head
        except KeyError:
            self.white = [self.icon["king"], self.icon["queen"], self.icon["rook"],
                          self.icon["knight"], self.icon["knight"], self.icon["bishop"]]  # team 1 white chess head
            self.black = self.white  # no colour change

        self.leader_pos = ((self.inspect_pos[0][0], self.inspect_pos[0][1]),
                           (self.inspect_pos[1][0], self.inspect_pos[1][1]),
                           (self.inspect_pos[2][0], self.inspect_pos[2][1]),
                           (self.inspect_pos[3][0], self.inspect_pos[3][1]))

        self.image_original = self.image.copy()

    def change_pos(self, pos):
        """change position of ui to new one"""
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

        self.leader_pos = (
        (self.inspect_pos[0][0] + self.rect.topleft[0], self.inspect_pos[0][1] + self.rect.topleft[1]),
        (self.inspect_pos[1][0] + self.rect.topleft[0], self.inspect_pos[1][1] + self.rect.topleft[1]),
        (self.inspect_pos[2][0] + self.rect.topleft[0], self.inspect_pos[2][1] + self.rect.topleft[1]),
        (self.inspect_pos[3][0] + self.rect.topleft[0], self.inspect_pos[3][1] + self.rect.topleft[1]))

    def value_input(self, who, weapon_list="", armour_list="", button="", change_option=0, split=False):
        for this_button in button:
            this_button.draw(self.image)

        if who.game_id != self.last_who or split:  # only redraw leader circle when change subunit
            use_colour = self.white  # colour of the chess icon for leader, white for team 1
            if who.team == 2:  # black for team 2
                use_colour = self.black
            self.image = self.image_original.copy()
            self.image.blit(who.coa, who.coa.get_rect(topleft=self.image.get_rect().topleft))  # blit coa

            pic_list = (0, 3, 4, 5)  # rook, bishop, left knight, right knight
            if who.commander:
                pic_list = (2, 3, 4, 5)  # king, queen, left knight, right knight
            for index, _ in enumerate(who.leader):
                icon_rect = use_colour[pic_list[index]].get_rect(midbottom=self.inspect_pos[index])
                self.image.blit(use_colour[pic_list[index]], icon_rect)

            self.image_original2 = self.image.copy()

        authority = str(who.authority).split(".")[0]
        if self.last_auth != authority or who.game_id != self.last_who or split:  # authority number change only when not same as last
            self.image = self.image_original2.copy()
            text_surface = self.font.render(authority, True, (0, 0, 0))
            text_rect = text_surface.get_rect(
                center=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.12, self.image.get_rect()[1] + 83))
            self.image.blit(text_surface, text_rect)
            self.last_auth = authority

        self.last_value = self.value
        self.last_who = who.game_id


class SkillCardIcon(pygame.sprite.Sprite):
    cooldown = None
    active_skill = None

    def __init__(self, image, pos, icon_type, game_id=None):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icon_type = icon_type  # type 0 is trait 1 is skill
        self.game_id = game_id  # ID of the skill
        self.pos = pos  # pos of the skill on ui
        self.font = pygame.font.SysFont("helvetica", 18)
        self.cooldown_check = 0  # cooldown number
        self.active_check = 0  # active timer number
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.image_original = self.image.copy()  # keep original image without number
        self.cooldown_rect = self.image.get_rect(topleft=(0, 0))

    def change_number(self, number):
        """Change number more than a thousand to K digit e.g. 1k = 1000"""
        return str(round(number / 1000, 1)) + "K"

    def icon_change(self, cooldown, active_timer):
        """Show active effect timer first if none show cooldown"""
        if active_timer != self.active_check:
            self.active_check = active_timer  # renew number
            self.image = self.image_original.copy()
            if self.active_check > 0:
                rect = self.image.get_rect(topleft=(0, 0))
                self.image.blit(self.active_skill, rect)
                output_number = str(self.active_check)
                if self.active_check >= 1000:
                    output_number = self.change_number(output_number)
                text_surface = self.font.render(output_number, 1, (0, 0, 0))  # timer number
                text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(text_surface, text_rect)

        elif cooldown != self.cooldown_check and self.active_check == 0:  # Cooldown only get blit when skill is not active
            self.cooldown_check = cooldown
            self.image = self.image_original.copy()
            if self.cooldown_check > 0:
                self.image.blit(self.cooldown, self.cooldown_rect)
                output_number = str(self.cooldown_check)
                if self.cooldown_check >= 1000:  # change a thousand number into k (1k,2k)
                    output_number = self.change_number(output_number)
                text_surface = self.font.render(output_number, 1, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(text_surface, text_rect)


class EffectCardIcon(pygame.sprite.Sprite):

    def __init__(self, image, pos, icon_type, game_id=None):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icon_type = icon_type
        self.game_id = game_id
        self.pos = pos
        self.cooldown_check = 0
        self.active_check = 0
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.image_original = self.image.copy()


class FPScount(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.font = pygame.font.SysFont("Arial", 18)
        self.rect = self.image.get_rect(center=(30, 110))
        fps_text = self.font.render("60", True, pygame.Color("blue"))
        self.text_rect = fps_text.get_rect(center=(25, 25))

    def fps_show(self, clock):
        """Update current fps"""
        self.image = self.image_original.copy()
        fps = str(int(clock.get_fps()))
        fps_text = self.font.render(fps, True, pygame.Color("blue"))
        text_rect = fps_text.get_rect(center=(25, 25))
        self.image.blit(fps_text, text_rect)


class SelectedSquad(pygame.sprite.Sprite):
    image = None

    def __init__(self, pos, layer=17):
        """Used for showing selected subunit in inpeact ui and unit editor"""
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

    def pop(self, pos):
        """pop out at the selected subunit in inspect uo"""
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


class MiniMap(pygame.sprite.Sprite):
    def __init__(self, pos, screen_scale):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.screen_scale = screen_scale

        team2_dot = pygame.Surface((10 * self.screen_scale[0], 10 * self.screen_scale[1]))  # dot for team2 subunit
        team2_dot.fill((0, 0, 0))  # black corner
        team1_dot = pygame.Surface((10 * self.screen_scale[0], 10 * self.screen_scale[1]))  # dot for team1 subunit
        team1_dot.fill((0, 0, 0))  # black corner
        team2 = pygame.Surface((8 * self.screen_scale[0], 8 * self.screen_scale[1]))  # size 6x6
        team2.fill((255, 0, 0))  # red rect
        team1 = pygame.Surface((8 * self.screen_scale[0], 8 * self.screen_scale[1]))
        team1.fill((0, 0, 255))  # blue rect
        rect = team2_dot.get_rect(center=(team2_dot.get_width() / 2, team2_dot.get_height() / 2))
        team2_dot.blit(team2, rect)
        team1_dot.blit(team1, rect)
        self.dot_images = {1: team1_dot, 2: team2_dot}

        self.last_scale = 10

    def draw_image(self, image, camera):
        self.image = image
        size = (200 * self.screen_scale[0], 200 * self.screen_scale[1])  # default minimap size is 200 x 200
        self.map_scale_width = 1000 / size[0]
        self.map_scale_height = 1000 / size[1]
        self.dim = pygame.Vector2(size[0], size[1])
        self.image = pygame.transform.scale(self.image, (int(self.dim[0]), int(self.dim[1])))
        self.image_original = self.image.copy()
        self.camera_border = [camera.image.get_width(), camera.image.get_height()]
        self.camera_pos = camera.pos
        self.rect = self.image.get_rect(bottomright=self.pos)

    def update(self, view_mode, camera_pos, team_pos_list):
        """update unit dot on map"""
        self.camera_pos = camera_pos
        self.image = self.image_original.copy()
        for unit, pos in team_pos_list["alive"].items():
            scaled_pos = (pos[0] / self.map_scale_width, pos[1] / self.map_scale_height)
            rect = self.dot_images[unit.team].get_rect(center=scaled_pos)
            self.image.blit(self.dot_images[unit.team], rect)
        pygame.draw.rect(self.image, (0, 0, 0),
                         ((camera_pos[1][0] / self.screen_scale[0] / (self.map_scale_width)) / view_mode,
                          (camera_pos[1][1] / self.screen_scale[1] / (self.map_scale_height)) / view_mode,
                          (self.camera_border[0] / self.screen_scale[0] / view_mode) / self.map_scale_width,
                          (self.camera_border[1] / self.screen_scale[1] / view_mode) / self.map_scale_height), 2)


class EventLog(pygame.sprite.Sprite):
    max_row_show = 9  # maximum 9 text rows can appear at once

    def __init__(self, image, pos):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", 16)
        self.pos = pos
        self.image = image
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(bottomleft=self.pos)
        self.len_check = 0
        self.current_start_row = 0
        self.mode = 0
        self.battle_log = []  # 0 troop
        self.unit_log = []  # 1 army
        self.leader_log = []  # 2 leader
        self.subunit_log = []  # 3 subunit
        self.current_start_row = 0
        self.scroll = None  # Link from battle after creation of the object

    def make_new_log(self):
        self.mode = 0  # 0=troop,1=army(subunit),2=leader,3=subunit(sub-subunit)
        self.battle_log = []  # 0 troop
        self.unit_log = []  # 1 army
        self.leader_log = []  # 2 leader
        self.subunit_log = []  # 3 subunit
        self.current_start_row = 0
        self.len_check = 0  # total number of row in the current mode

    def add_event_log(self, map_event):
        self.map_event = map_event
        if self.map_event != {}:  # Edit map based event
            self.map_event.pop("id")
            for event in self.map_event:
                if type(self.map_event[event][2]) == int:
                    self.map_event[event][2] = [self.map_event[event][2]]
                elif "," in self.map_event[event][
                    2]:  # Change mode list to list here since csvread don't have that function
                    self.map_event[event][2] = [int(item) if item.isdigit() else item for item in
                                                self.map_event[event][2].split(",")]
                if self.map_event[event][3] != "":  # change time string to time delta same reason as above
                    new_time = datetime.datetime.strptime(self.map_event[event][3], "%H:%M:%S").time()
                    new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
                    self.map_event[event][3] = new_time
                else:
                    self.map_event[event][3] = None

    def change_mode(self, mode):
        """Change tab"""
        self.mode = mode
        self.len_check = len((self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode])
        self.current_start_row = 0
        if self.len_check > self.max_row_show:  # go to last row if there are more log than limit
            self.current_start_row = self.len_check - self.max_row_show
        self.scroll.current_row = self.current_start_row
        self.scroll.change_image(row_size=self.len_check)
        self.recreate_image()

    def clear_tab(self, all_tab=False):
        """Clear event from log for that mode"""
        self.len_check = 0
        self.current_start_row = 0
        log = (self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode]  # log to edit
        log.clear()
        if all_tab:  # Clear event from every mode
            for log in (self.battle_log, self.unit_log, self.leader_log, self.subunit_log):
                log.clear()
        self.scroll.current_row = self.current_start_row
        self.scroll.change_image(row_size=self.len_check)
        self.recreate_image()

    def recreate_image(self):
        log = (self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode]  # log to edit
        self.image = self.image_original.copy()
        row = 10
        for index, text in enumerate(log[self.current_start_row:]):
            if index == self.max_row_show:
                break
            text_surface = self.font.render(text[1], True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(40, row))
            self.image.blit(text_surface, text_rect)
            row += 20  # Whitespace between text row

    def log_text_process(self, who, mode_list, text_output):
        """Cut up whole log into separate sentence based on space"""
        image_change = False
        for mode in mode_list:
            log = (self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[mode]  # log to edit
            if len(text_output) <= 45:  # EventLog each row cannot have more than 45 characters including space
                log.append([who, text_output])
            else:  # Cut the text log into multiple row if more than 45 char
                cut_space = [index for index, letter in enumerate(text_output) if letter == " "]
                loop_number = len(text_output) / 45  # number of row
                if loop_number.is_integer() is False:  # always round up if there is decimal number
                    loop_number = int(loop_number) + 1
                starting_index = 0

                for run in range(1, int(loop_number) + 1):
                    text_cut_number = [number for number in cut_space if number <= run * 45]
                    cut_number = text_cut_number[-1]
                    final_text_output = text_output[starting_index:cut_number]
                    if run == loop_number:
                        final_text_output = text_output[starting_index:]
                    if run == 1:
                        log.append([who, final_text_output])
                    else:
                        log.append([-1, final_text_output])
                    starting_index = cut_number + 1

            if len(log) > 1000:  # log cannot be more than 1000 length
                log_delete = len(log) - 1000
                del log[0:log_delete]  # remove the first few so only 1000 left
            if mode == self.mode:
                image_change = True
        return image_change

    def add_log(self, log, mode_list, event_id=None):
        """Add log to appropriate event log, the log must be in list format following this rule [attacker (game_id), logtext]"""
        at_last_row = False
        image_change = False
        image_change2 = False
        if self.current_start_row + self.max_row_show >= self.len_check:
            at_last_row = True
        if log is not None:  # when event map log commentary come in, log will be none
            text_output = ": " + log[1]
            image_change = self.log_text_process(log[0], mode_list, text_output)
        if event_id is not None and event_id in self.map_event:  # Process whether there is historical commentary to add to event log
            text_output = self.map_event[event_id]
            image_change2 = self.log_text_process(text_output[0], text_output[2],
                                                  str(text_output[3]) + ": " + text_output[1])
        if image_change or image_change2:
            self.len_check = len((self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode])
            if at_last_row and self.len_check > 9:
                self.current_start_row = self.len_check - self.max_row_show
                self.scroll.current_row = self.current_start_row
            self.scroll.change_image(row_size=self.len_check)
            self.recreate_image()


class UIScroll(pygame.sprite.Sprite):
    def __init__(self, ui, pos):
        """
        Scroll for any applicable ui
        :param ui: Any ui object, the ui must has max_row_show attribute, layer, and image surface
        :param pos: Starting pos
        :param layer: Surface layer value
        """
        self.ui = ui
        self._layer = self.ui.layer + 2  # always 2 layer higher than the ui and its item
        pygame.sprite.Sprite.__init__(self)

        self.ui.scroll = self
        self.height_ui = self.ui.image.get_height()
        self.max_row_show = self.ui.max_row_show
        self.pos = pos
        self.image = pygame.Surface((10, self.height_ui))
        self.image.fill((255, 255, 255))
        self.image_original = self.image.copy()
        self.button_colour = (100, 100, 100)
        pygame.draw.rect(self.image, self.button_colour, (0, 0, self.image.get_width(), self.height_ui))
        self.rect = self.image.get_rect(topright=self.pos)
        self.current_row = 0
        self.row_size = 0

    def create_new_image(self):
        percent_row = 0
        max_row = 100
        self.image = self.image_original.copy()
        if self.row_size > 0:
            percent_row = self.current_row * 100 / self.row_size
        if self.row_size > 0:
            max_row = (self.current_row + self.max_row_show) * 100 / self.row_size
        max_row = max_row - percent_row
        pygame.draw.rect(self.image, self.button_colour,
                         (0, int(self.height_ui * percent_row / 100), self.image.get_width(),
                          int(self.height_ui * max_row / 100)))

    def change_image(self, new_row=None, row_size=None):
        """New row is input of scrolling by user to new row, row_size is changing based on adding more log or clear"""
        if row_size is not None and self.row_size != row_size:
            self.row_size = row_size
            self.create_new_image()
        if new_row is not None and self.current_row != new_row:  # accept from both wheeling scroll and drag scroll bar
            self.current_row = new_row
            self.create_new_image()

    def player_input(self, mouse_pos, mouse_scroll_up=False, mouse_scroll_down=False):
        """Player input update via click or scrolling"""
        if mouse_pos is not None and self.rect.collidepoint(mouse_pos):
            mouse_value = (mouse_pos[1] - self.pos[
                1]) * 100 / self.height_ui  # find what percentage of mouse_pos at the scroll bar (0 = top, 100 = bottom)
            if mouse_value > 100:
                mouse_value = 100
            if mouse_value < 0:
                mouse_value = 0
            new_row = int(self.row_size * mouse_value / 100)
            if self.row_size > self.max_row_show and new_row > self.row_size - self.max_row_show:
                new_row = self.row_size - self.max_row_show
            if self.row_size > self.max_row_show:  # only change scroll position in list longer than max length
                self.change_image(new_row)
            return self.current_row


class UnitSelector(pygame.sprite.Sprite):
    def __init__(self, pos, image, icon_scale=1):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)
        self.icon_scale = icon_scale
        self.current_row = 0
        self.max_row_show = 2
        self.row_size = 0
        self.scroll = None  # got add after create scroll object

    def setup_unit_icon(self, unit_icon_group, unit_list):
        """Setup unit selection list in unit selector ui top left of screen"""
        for this_unit in unit_list:
            max_column_show = int(
                self.image.get_width() / ((this_unit.leader[0].full_image.get_width() * self.icon_scale * 1.5)))
            break
        current_index = int(self.current_row * max_column_show)  # the first index of current row
        self.row_size = len(unit_list) / max_column_show

        if self.row_size.is_integer() is False:
            self.row_size = int(self.row_size) + 1

        if self.current_row > self.row_size - 1:
            self.current_row = self.row_size - 1
            current_index = int(self.current_row * max_column_show)
            self.scroll.change_image(new_row=self.current_row)

        if len(unit_icon_group) > 0:  # remove all old icon first before making new list
            for icon in unit_icon_group:
                icon.kill()
                del icon

        if len(unit_list) > 0:
            for index, this_unit in enumerate(
                    unit_list):  # add unit icon for drawing according to appropriated current row
                if index == 0:
                    start_column = self.rect.topleft[0] + (this_unit.leader[0].image.get_width() / 1.5)
                    column = start_column
                    row = self.rect.topleft[1] + (this_unit.leader[0].image.get_height() / 1.5)
                if index >= current_index:
                    new_icon = UnitIcon((column, row), this_unit,
                                        (int(this_unit.leader[0].full_image.get_width() * self.icon_scale),
                                         int(this_unit.leader[0].full_image.get_height() * self.icon_scale)))
                    unit_icon_group.add(new_icon)
                    column += new_icon.image.get_width() * 1.2
                    if column > self.rect.topright[0] - ((new_icon.image.get_width() * self.icon_scale) * 3):
                        row += new_icon.image.get_height() * 1.5
                        column = start_column
                    if row > self.rect.bottomright[1] - ((new_icon.image.get_height() / 2) * self.icon_scale):
                        break  # do not draw for row that exceed the box
        self.scroll.change_image(row_size=self.row_size)


class UnitIcon(pygame.sprite.Sprite):
    def __init__(self, pos, unit, size):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.unit = unit  # link unit object so when click can correctly select or go to position
        unit.icon = self  # link this icon to unit object, mostly for when it gets killed so can easily remove from list
        self.pos = pos  # position on unit selector ui
        self.selected = False

        self.leader_image = self.unit.leader[0].image.copy()  # get leader image
        self.leader_image = pygame.transform.scale(self.leader_image, size)  # scale leader image to fit the icon
        self.not_selected_image = pygame.Surface((self.leader_image.get_width() + (self.leader_image.get_width() / 7),
                                                  self.leader_image.get_height() + (
                                                              self.leader_image.get_height() / 7)))  # create image black corner block
        self.selected_image = self.not_selected_image.copy()
        self.selected_image.fill((200, 200, 0))  # fill gold corner
        self.not_selected_image.fill((0, 0, 0))  # fill black corner

        for image in (self.not_selected_image, self.selected_image):  # add team colour and leader image
            center_image = pygame.Surface((self.leader_image.get_width() + (self.leader_image.get_width() / 14),
                                           self.leader_image.get_height() + (
                                                       self.leader_image.get_height() / 14)))  # create image block
            center_image.fill((144, 167, 255))  # fill colour according to team, blue for team 1
            if self.unit.team == 2:
                center_image.fill((255, 114, 114))  # red colour for team 2
            image_rect = center_image.get_rect(center=((image.get_width() / 2),
                                                       (image.get_height() / 2)))
            image.blit(center_image, image_rect)  # blit colour block into border image
            self.leader_image_rect = self.leader_image.get_rect(center=(image.get_width() / 2,
                                                                        image.get_height() / 2))
            image.blit(self.leader_image, self.leader_image_rect)  # blit leader image

        self.image = self.not_selected_image
        self.rect = self.image.get_rect(center=self.pos)

    def change_pos(self, pos):
        """change position of icon to new one"""
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def change_image(self, new_image=None, change_side=False):
        """For changing side"""
        if change_side:
            self.image.fill((144, 167, 255))
            if self.unit.team == 2:
                self.image.fill((255, 114, 114))
            self.image.blit(self.leader_image, self.leader_image_rect)
        if new_image is not None:
            self.leader_image = new_image
            self.image.blit(self.leader_image, self.leader_image_rect)

    def selection(self):
        if self.selected:
            self.selected = False
            self.image = self.not_selected_image
        else:
            self.selected = True
            self.image = self.selected_image


class Timer(pygame.sprite.Sprite):
    def __init__(self, pos, text_size=20):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", text_size)
        self.pos = pos
        self.image = pygame.Surface((100, 30), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.timer = 0

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)

    def start_setup(self, time_start):
        self.timer = time_start.total_seconds()
        self.old_timer = self.timer
        self.image = self.image_original.copy()
        self.time_number = time_start  # datetime.timedelta(seconds=self.timer)
        self.timer_surface = self.font.render(str(self.timer), True, (0, 0, 0))
        self.timer_rect = self.timer_surface.get_rect(topleft=(5, 5))
        self.image.blit(self.timer_surface, self.timer_rect)

    def timer_update(self, dt):
        """Update in-self timer number"""
        if dt > 0:
            self.timer += dt
            if self.timer - self.old_timer > 1:
                self.old_timer = self.timer
                if self.timer >= 86400:  # Time pass midnight
                    self.timer -= 86400  # Restart clock to 0
                    self.old_timer = self.timer
                self.image = self.image_original.copy()
                self.time_number = datetime.timedelta(seconds=self.timer)
                time_num = str(self.time_number).split(".")[0]
                self.timer_surface = self.font.render(time_num, True, (0, 0, 0))
                self.image.blit(self.timer_surface, self.timer_rect)


class TimeUI(pygame.sprite.Sprite):
    def __init__(self, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.pos = (0, 0)
        self.image = image.copy()
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

    def change_pos(self, pos, time_number, speed_number=None, time_button=None):
        """change position of the ui and related buttons"""
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)
        time_number.change_pos(self.rect.topleft)
        if speed_number is not None:
            speed_number.change_pos((self.rect.center[0] + int(self.rect.center[0] / 10), self.rect.center[1]))


class BattleScaleUI(pygame.sprite.Sprite):
    def __init__(self, image, team_colour):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.team_colour = team_colour
        self.font = pygame.font.SysFont("helvetica", 12)
        self.pos = (0, 0)
        self.image = image
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.rect = self.image.get_rect(topleft=self.pos)
        self.troop_number_list = []

    def change_fight_scale(self, troop_number_list):
        if self.troop_number_list != troop_number_list:
            self.troop_number_list = troop_number_list.copy()
            total = sum(self.troop_number_list)
            percent_scale = 0  # start point fo fill colour of team scale
            for team, value in enumerate(self.troop_number_list):
                if value > 1:
                    self.image.fill(self.team_colour[team], (percent_scale, 0, self.image_width, self.image_height))

                    # team_text = self.font.render("{:,}".format(int(value - 1)), True, (0, 0, 0))  # add troop number text
                    # team_text_rect = team_text.get_rect(topleft=(percent_scale, 0))
                    # self.image.blit(team_text, team_text_rect)
                    percent_scale = (value / total * 100) + percent_scale

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


class WheelUI(pygame.sprite.Sprite):
    sprite_fading = animation.sprite_fading

    def __init__(self, images, selected_images, pos, screen_size, text_size=20):
        """Wheel choice ui with text or image inside the choice.
        Works similar to Fallout companion wheel and similar system"""
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", text_size)
        self.pos = pos
        self.screen_size = screen_size
        self.choice_list = ()

        self.image_original2 = pygame.Surface((images[0].get_width() * 3.5,
                                               images[0].get_height() * 3.5), pygame.SRCALPHA)  # empty image
        self.rect = self.image_original2.get_rect(center=self.pos)
        image_center = (self.image_original2.get_width() / 2, self.image_original2.get_height() / 2)
        if len(images) == 2:  # create 8 direction wheel ui
            self.wheel_image_list = (images[0].copy(),  # top up left
                                     images[1].copy(),  # top left
                                     pygame.transform.flip(images[0], False, True),  # bottom down left
                                     pygame.transform.flip(images[1], False, True),  # bottom left
                                     pygame.transform.flip(images[0], True, False),  # top up right
                                     pygame.transform.flip(images[1], True, False),  # top right
                                     pygame.transform.flip(images[0], True, True),  # bottom down right
                                     pygame.transform.flip(images[1], True, True)  # bottom right
                                     )

            self.wheel_selected_image_list = (selected_images[0].copy(),  # top up left
                                              selected_images[1].copy(),  # top left
                                              pygame.transform.flip(selected_images[0], False, True),
                                              # bottom lower left
                                              pygame.transform.flip(selected_images[1], False, True),  # bottom left
                                              pygame.transform.flip(selected_images[0], True, False),  # top upper right
                                              pygame.transform.flip(selected_images[1], True, False),  # top right
                                              pygame.transform.flip(selected_images[0], True, True),
                                              # bottom lower right
                                              pygame.transform.flip(selected_images[1], True, True)  # bottom right
                                              )

            self.wheel_inactive_image_list = [image.copy() for image in
                                              self.wheel_image_list]  # wheel choice that not active
            for image in self.wheel_inactive_image_list:
                image.fill((50, 50, 50, 150))
            self.wheel_rect = (
            images[0].get_rect(center=(image_center[0] * 0.7, image_center[1] * 0.36)),  # top upper left
            images[0].get_rect(center=(image_center[0] * 0.45, image_center[1] * 0.65)),  # top left
            images[0].get_rect(center=(image_center[0] * 0.7, image_center[1] * 1.64)),  # bottom lower left
            images[0].get_rect(center=(image_center[0] * 0.45, image_center[1] * 1.3)),  # bottom left
            images[0].get_rect(center=(image_center[0] * 1.3, image_center[1] * 0.36)),  # top upper right
            images[0].get_rect(center=(image_center[0] * 1.6, image_center[1] * 0.65)),  # top right
            images[0].get_rect(center=(image_center[0] * 1.3, image_center[1] * 1.64)),  # bottom lower right
            images[0].get_rect(center=(image_center[0] * 1.6, image_center[1] * 1.3))  # bottom right
            )

        elif len(images) == 1:  # create 4 direction wheel ui
            self.wheel_image_list = (images[0].copy(),  # top left
                                     pygame.transform.flip(images[0], False, True),  # bottom left
                                     pygame.transform.flip(images[0], True, False),  # top right
                                     pygame.transform.flip(images[0], True, True),  # bottom right
                                     )

            self.wheel_selected_image_list = (selected_images[0].copy(),  # top left
                                              pygame.transform.flip(selected_images[0], False, True),  # bottom left
                                              pygame.transform.flip(selected_images[0], True, False),  # top upper right
                                              pygame.transform.flip(selected_images[0], True, True),  # bottom right
                                              )
            self.wheel_rect = (images[0].get_rect(center=(image_center[0] * 0.6, image_center[1] * 0.6)),  # top left
                               images[0].get_rect(center=(image_center[0] * 0.6, image_center[1] * 1.4)),  # bottom left
                               images[0].get_rect(center=(image_center[0] * 1.4, image_center[1] * 0.6)),  # top right
                               images[0].get_rect(center=(image_center[0] * 1.4, image_center[1] * 1.4))  # bottom right
                               )
        self.wheel_image_with_stuff = [image.copy() for image in self.wheel_image_list]
        self.wheel_selected_image_with_stuff = [image.copy() for image in self.wheel_selected_image_list]

        self.image = self.image_original2.copy()
        for index, rect in enumerate(self.wheel_rect):
            self.image.blit(self.wheel_image_with_stuff[index], rect)

    def selection(self, mouse_pos):
        closest_rect_distance = None
        closest_rect_index = None
        new_mouse_pos = pygame.Vector2(mouse_pos[0] / self.screen_size[0] * self.image.get_width(),
                                       mouse_pos[1] / self.screen_size[1] * self.image.get_height())
        for index, rect in enumerate(self.wheel_rect):
            distance = pygame.Vector2(rect.center).distance_to(new_mouse_pos)
            if closest_rect_distance is None or distance < closest_rect_distance:
                closest_rect_index = index
                closest_rect_distance = distance
        self.image = self.image_original2.copy()

        for index, rect in enumerate(self.wheel_rect):
            if index == closest_rect_index:
                self.image.blit(self.wheel_selected_image_with_stuff[index], rect)
            else:
                self.image.blit(self.wheel_image_with_stuff[index], rect)
        if self.choice_list and closest_rect_index <= len(self.choice_list) - 1:
            text_surface = self.font.render(self.choice_list[closest_rect_index], True, (0, 0, 0))
            text_box = pygame.Surface((text_surface.get_width() * 1.2,
                                       text_surface.get_height() * 1.2))  # empty image
            text_box.fill((255, 255, 255))
            text_rect = text_surface.get_rect(center=(text_box.get_width() / 2,
                                                      text_box.get_height() / 2))
            text_box.blit(text_surface, text_rect)
            box_rect = text_surface.get_rect(center=(self.image.get_width() / 2,
                                                     self.image.get_height() / 2.5))
            self.image.blit(text_box, box_rect)  # blit text description at the center of wheel
            return self.choice_list[closest_rect_index]

    def change_text_icon(self, blit_list):
        """Add icon or text to the wheel choice"""
        self.image = self.image_original2.copy()
        self.wheel_image_with_stuff = [image.copy() for image in self.wheel_image_list]
        self.wheel_selected_image_with_stuff = [image.copy() for image in self.wheel_selected_image_list]
        self.choice_list = tuple(blit_list.keys())
        for index, item in enumerate(blit_list):
            if item is not None:  # Wheel choice with icon or text inside
                if type(item) == str:  # text
                    surface = self.font.render(item, True, (0, 0, 0))

                else:
                    surface = item
                rect = surface.get_rect(center=(self.wheel_image_with_stuff[index].get_width() / 2,
                                                self.wheel_image_with_stuff[index].get_height() / 2))
                self.wheel_image_with_stuff[index].blit(surface, rect)
                self.wheel_selected_image_with_stuff[index].blit(surface, rect)
                self.image.blit(self.wheel_image_with_stuff[index], self.wheel_rect[index])
            else:  # inactive wheel choice
                self.image.blit(self.wheel_inactive_image_list[index], self.wheel_rect[index])


class TextSprite(pygame.sprite.Sprite):
    def __init__(self, value, text_size=20):
        """Sprite of text with transparent background.
        The size of text should be static or as close as the original text as possible"""
        self._layer = 11
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", text_size)
        self.pos = (0, 0)
        self.value = str(value)
        self.image = pygame.Surface((len(self.value) * (text_size + 4), text_size * 1.5), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        text_surface = self.font.render(self.value, True, (0, 0, 0))
        self.text_rect = text_surface.get_rect(topleft=(self.image.get_width() / 10, self.image.get_height() / 10))
        self.image.blit(text_surface, self.text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def speed_update(self, new_value):
        """change speed number text"""
        self.image = self.image_original.copy()
        self.value = new_value
        text_surface = self.font.render(str(self.value), True, (0, 0, 0))
        self.image.blit(text_surface, self.text_rect)

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)


class InspectSubunit(pygame.sprite.Sprite):
    def __init__(self, pos):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.who = None
        self.image = pygame.Surface((0, 0))
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

    def add_subunit(self, who):
        if who is not None:
            self.who = who
            self.image = self.who.block
        else:
            self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=self.pos)


class BattleDone(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, box_image, result_image):
        self._layer = 18
        pygame.sprite.Sprite.__init__(self)
        self.screen_scale = screen_scale
        self.box_image = box_image
        self.result_image = result_image
        self.font = pygame.font.SysFont("oldenglishtext", int(self.screen_scale[1] * 36))
        self.text_font = pygame.font.SysFont("timesnewroman", int(self.screen_scale[1] * 24))
        self.pos = pos
        self.image = self.box_image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.winner = None

    def pop(self, winner):
        self.winner = winner
        self.image = self.box_image.copy()
        text_surface = self.font.render(self.winner, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.screen_scale[1] * 36) + 3))
        self.image.blit(text_surface, text_rect)
        if self.winner != "Draw":
            text_surface = self.font.render("Victory", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.screen_scale[1] * 36) * 2))
            self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def show_result(self, team1_coa, team2_coa, stat):
        self.image = self.result_image.copy()
        text_surface = self.font.render(self.winner, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.height_adjust * 36) + 3))
        self.image.blit(text_surface, text_rect)
        if self.winner != "Draw":
            text_surface = self.font.render("Victory", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.height_adjust * 36) * 2))
            self.image.blit(text_surface, text_rect)
        coa1_rect = team1_coa.get_rect(center=(self.image.get_width() / 3, int(self.height_adjust * 36) * 5))
        coa2_rect = team2_coa.get_rect(center=(self.image.get_width() / 1.5, int(self.height_adjust * 36) * 5))
        self.image.blit(team1_coa, coa1_rect)
        self.image.blit(team2_coa, coa2_rect)
        self.rect = self.image.get_rect(center=self.pos)
        team_coa_rect = (coa1_rect, coa2_rect)
        text_header = ("Total Troop: ", "Remaining: ", "Injured: ", "Death: ", "Flee: ", "Captured: ")
        for index, team in enumerate([1, 2]):
            row_number = 1
            for stat_index, this_stat in enumerate(stat):
                if stat_index == 1:
                    text_surface = self.font.render(text_header[stat_index] + str(this_stat[team] - 1), True, (0, 0, 0))
                else:
                    text_surface = self.font.render(text_header[stat_index] + str(this_stat[team]), True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(team_coa_rect[index].midbottom[0],
                                                          team_coa_rect[index].midbottom[1] + (
                                                                      int(self.height_adjust * 25) * row_number)))
                self.image.blit(text_surface, text_rect)
                row_number += 1


class DirectionArrow(pygame.sprite.Sprite):  # TODO make it work so it can be implemented again
    def __init__(self, who):
        """Layer must be called before sprite_init"""
        self._layer = 40
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.who = who
        self.pos = self.who.pos
        self.who.direction_arrow = self
        self.length_gap = self.who.image.get_height() / 2
        self.length = self.who.pos.distance_to(self.who.base_target) + self.length_gap
        self.previous_length = self.length
        self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        # self.image_original = self.image.copy()
        # pygame.draw.line(self.image, (0, 0, 0), (self.image.get_width()/2, 0),(self.image.get_width()/2,self.image.get_height()), 5)
        self.image = pygame.transform.rotate(self.image, self.who.angle)
        self.rect = self.image.get_rect(midbottom=self.who.front_pos)

    def update(self, zoom):
        self.length = self.who.pos.distance_to(self.who.base_target) + self.length_gap
        distance = self.who.front_pos.distance_to(self.who.base_target) + self.length_gap
        if self.length != self.previous_length and distance > 2 and self.who.state != 0:
            self.pos = self.who.pos
            self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
            self.image.fill((0, 0, 0))
            self.image = pygame.transform.rotate(self.image, self.who.angle)
            self.rect = self.image.get_rect(midbottom=self.who.front_pos)
            self.previous_length = self.length
        elif distance < 2 or self.who.state in (0, 10, 11, 100):
            self.who.direction_arrow = False
            self.kill()


class TroopNumber(pygame.sprite.Sprite):
    def __init__(self, screen_scale, who):
        self._layer = 35
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.screen_scale = screen_scale
        self.who = who
        self.text_colour = pygame.Color("blue")
        if self.who.team == 2:
            self.text_colour = pygame.Color("red")
        self.last_number_pos = self.who.number_pos
        self.pos = (self.who.number_pos[0], self.who.number_pos[1])
        self.number = self.who.troop_number
        self.zoom = 0

        self.font = pygame.font.SysFont("timesnewroman", int(22 * self.screen_scale[1]))

        self.image = self.render(str(self.number), self.font, self.text_colour)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, *args, **kwargs) -> None:
        if self.last_number_pos != self.who.number_pos:  # new position
            self.pos = (self.who.number_pos[0], self.who.number_pos[1])
            self.rect = self.image.get_rect(topleft=self.pos)
            self.last_number_pos = self.who.number_pos

        if self.zoom != args[2]:  # zoom argument
            self.zoom = int(args[2])
            zoom = (11 - self.zoom) / 2
            if zoom < 1:
                zoom = 1
            new_font_size = int(60 / zoom * self.screen_scale[1])
            self.font = pygame.font.SysFont("timesnewroman", new_font_size)
            self.image = text_render(str(self.number), self.font, self.text_colour)
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.number != self.who.troop_number:  # new troop number
            self.number = self.who.troop_number
            self.image = text_render(str(self.number), self.font, self.text_colour)
            self.rect = self.image.get_rect(topleft=self.pos)

        if self.who.state == 100:
            self.who = None
            self.kill()

