import datetime
import math

import pygame
import pygame.freetype
from gamescript.common import utility

apply_sprite_colour = utility.apply_sprite_colour
text_render = utility.text_render


def change_number(number):
    """Change number more than a thousand to K digit e.g. 1k = 1000"""
    if number >= 1000000:
        return str(round(number / 1000000, 1)) + "m"
    elif number >= 1000:
        return str(round(number / 1000, 1)) + "k"


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


class HeroUI(pygame.sprite.Sprite):
    weapon_sprite_pool = None

    def __init__(self, screen_scale, weapon_box_images, text_size=24):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.screen_scale = screen_scale
        self.font = pygame.font.SysFont("helvetica", int(text_size * screen_scale[1]))

        self.image = pygame.Surface((420 * self.screen_scale[0], 200 * self.screen_scale[1]), pygame.SRCALPHA)
        self.base_image = self.image.copy()

        self.health_bar_size = (10 * self.screen_scale[0], self.image.get_height())
        self.health_bar = pygame.Surface(self.health_bar_size, pygame.SRCALPHA)
        self.health_bar.fill((0, 0, 0))
        self.health_bar_original = self.health_bar.copy()
        self.health_bar_rect = self.health_bar.get_rect(topright=(self.image.get_width() - self.health_bar_size[0], 0))
        self.health_bar.fill((200, 0, 0))

        self.health_bar_height = self.health_bar.get_height()

        self.stamina_bar = pygame.Surface(self.health_bar_size, pygame.SRCALPHA)
        self.stamina_bar.fill((0, 0, 0))
        self.stamina_bar_original = self.stamina_bar.copy()
        self.stamina_bar_rect = self.stamina_bar.get_rect(topright=(self.image.get_width(), 0))
        self.stamina_bar.fill((0, 200, 0))

        self.weapon_box_images = weapon_box_images
        self.weapon_image = pygame.Surface((200 * self.screen_scale[0], 200 * self.screen_scale[1]),
                                           pygame.SRCALPHA)

        self.prim_main_weapon_box_rect = self.weapon_box_images[0].get_rect(midleft=(0, self.image.get_height() / 2))
        self.weapon_image.blit(self.weapon_box_images[0], self.prim_main_weapon_box_rect)
        self.prim_sub_weapon_box_rect = self.weapon_box_images[0].get_rect(midleft=(self.weapon_box_images[0].get_width(), self.image.get_height() / 2))
        self.weapon_image.blit(pygame.transform.flip(self.weapon_box_images[0], True, False),
                               self.prim_sub_weapon_box_rect)

        self.sec_main_weapon_box_rect = self.weapon_box_images[1].get_rect(topleft=(self.weapon_box_images[0].get_width() * 2, 0))
        self.weapon_image.blit(self.weapon_box_images[1], self.sec_main_weapon_box_rect)
        self.sec_sub_weapon_box_rect = self.weapon_box_images[1].get_rect(topleft=(self.weapon_box_images[0].get_width() * 2,
                                                                                   self.weapon_box_images[1].get_height() * 1.5))

        self.weapon_cooldown_rect = (self.weapon_box_images[0].get_rect(midbottom=self.prim_main_weapon_box_rect.midbottom),
                                     self.weapon_box_images[0].get_rect(midbottom=self.prim_sub_weapon_box_rect.midbottom))

        self.ammo_count_rect = ((self.prim_main_weapon_box_rect.midbottom, self.prim_sub_weapon_box_rect.midbottom),
                                (self.sec_main_weapon_box_rect.midbottom, self.sec_sub_weapon_box_rect.midbottom))

        self.weapon_image.blit(pygame.transform.flip(self.weapon_box_images[1], True, False),
                               self.sec_sub_weapon_box_rect)

        self.weapon_image_set_pos = ((self.prim_main_weapon_box_rect.center, self.prim_sub_weapon_box_rect.center),
                                     (self.sec_main_weapon_box_rect.center, self.sec_sub_weapon_box_rect.center))

        self.weapon_base_image = self.weapon_image.copy()
        self.weapon_image_rect = self.weapon_image.get_rect(topright=(self.image.get_width() - (self.health_bar_size[0] * 2), 0))

        self.leader_image_rect = self.weapon_image.get_rect(topleft=(0, 0))

        self.ammo_text_box = self.font.render("999", True, (0, 0, 0))  # make text box for ammo
        self.ammo_text_box.fill((0, 0, 0))
        self.ammo_text_box_original = self.ammo_text_box.copy()

        self.equipped_weapon = None
        self.magazine_count = None
        self.weapon_cooldown = None

        self.base_image.blit(self.health_bar, self.health_bar_rect)
        self.base_image.blit(self.stamina_bar, self.stamina_bar_rect)

        self.last_health = 0
        self.last_stamina = 0

        self.pos = (0, 0)
        self.rect = self.image.get_rect(topleft=self.pos)

    def add_leader_image(self, leader_image):
        self.base_image.blit(pygame.transform.smoothscale(leader_image,
                                                          (200 * self.screen_scale[0], self.image.get_height())),
                             self.leader_image_rect)
        self.image = self.base_image.copy()

    def value_input(self, who, *args):

        if self.last_health != who.health:
            self.last_health = who.health
            self.health_bar = self.health_bar_original.copy()
            health_percent = who.health / who.max_health
            health_bar = pygame.Surface((self.health_bar_size[0], self.health_bar_size[1] * health_percent))
            health_bar.fill((200, 0, 0))
            health_bar_rect = health_bar.get_rect(bottomleft=(0, self.health_bar_height))
            self.health_bar.blit(health_bar, health_bar_rect)

            self.base_image.blit(self.health_bar, self.health_bar_rect)
            self.image.blit(self.health_bar, self.health_bar_rect)

        if self.last_stamina != who.stamina:
            self.last_stamina = who.stamina
            self.stamina_bar = self.stamina_bar_original.copy()
            stamina_percent = who.stamina / who.max_stamina
            if stamina_percent < 0:
                stamina_percent = 0
            print(stamina_percent, )
            stamina_bar = pygame.Surface((self.health_bar_size[0], self.health_bar_size[1] * stamina_percent))
            stamina_bar.fill((0, 200, 0))
            stamina_bar_rect = stamina_bar.get_rect(bottomleft=(0, self.health_bar_height))
            self.stamina_bar.blit(stamina_bar, stamina_bar_rect)

            self.base_image.blit(self.stamina_bar, self.stamina_bar_rect)
            self.image.blit(self.stamina_bar, self.stamina_bar_rect)

        if self.equipped_weapon != who.equipped_weapon or who.magazine_count != self.magazine_count or \
                self.weapon_cooldown != who.weapon_cooldown:
            if self.equipped_weapon != who.equipped_weapon or self.weapon_cooldown != who.weapon_cooldown:
                self.equipped_weapon = who.equipped_weapon
                self.weapon_image = self.weapon_base_image.copy()
                self.image = self.base_image.copy()
            weapon_name_set = list(who.weapon_name)
            weapon_name_set.insert(0, weapon_name_set.pop(
                weapon_name_set.index(weapon_name_set[self.equipped_weapon])))
            weapon_set_index = list(range(0, len(who.weapon_name)))
            weapon_set_index.insert(0, weapon_set_index.pop(weapon_set_index.index(self.equipped_weapon)))
            for index, this_weapon_set in enumerate(weapon_name_set):
                if index > len(weapon_name_set) - 1:
                    index = len(weapon_name_set) - 1
                true_weapon_set_index = weapon_set_index[index]
                for index2, this_weapon in enumerate(this_weapon_set):
                    weapon_image = self.weapon_sprite_pool[this_weapon][who.weapon_version[
                        true_weapon_set_index][index2]]["icon"].copy()

                    if index > 0:  # unequipped weapon
                        weapon_image = pygame.transform.scale(weapon_image,
                                                              (self.weapon_image.get_width() / 4,
                                                               self.weapon_image.get_height() / 4))
                    weapon_image_rect = weapon_image.get_rect(center=self.weapon_image_set_pos[index][index2])
                    self.weapon_image.blit(weapon_image, weapon_image_rect)
                    if index == 0:  # add cooldown in any
                        cooldown = who.weapon_cooldown[index2]
                        speed = who.weapon_speed[index2]
                        if 0 < cooldown < speed:
                            cooldown_image = pygame.Surface((self.weapon_box_images[0].get_width(),
                                                             self.weapon_box_images[0].get_height() *
                                                             (1 - (cooldown / speed))), pygame.SRCALPHA)
                            cooldown_image.fill((255, 50, 50, 200))
                            self.weapon_image.blit(cooldown_image, self.weapon_cooldown_rect[index2])
                    if who.magazine_size[true_weapon_set_index][index2] > 0:  # range weapon
                        if true_weapon_set_index not in who.magazine_count or \
                                (true_weapon_set_index in who.magazine_count and
                                 index2 not in who.magazine_count[true_weapon_set_index]):  # no ammo
                            ammo_count = 0
                            text_colour = (200, 100, 100)
                            weapon_image = apply_sprite_colour(weapon_image, (200, 50, 50), None,
                                                               keep_white=False)
                        else:
                            ammo_count = who.magazine_count[true_weapon_set_index][index2]
                            text_colour = (255, 255, 255)
                        ammo_text_surface = self.font.render(str(ammo_count), 1, text_colour)  # ammo number
                        ammo_text_rect = ammo_text_surface.get_rect(center=(self.ammo_text_box.get_width() / 2,
                                                                            self.ammo_text_box.get_height() / 2))
                        self.ammo_text_box = self.ammo_text_box_original.copy()
                        self.ammo_text_box.blit(ammo_text_surface, ammo_text_rect)
                        ammo_text_rect = self.ammo_text_box.get_rect(midtop=self.ammo_count_rect[index][index2])
                        self.weapon_image.blit(self.ammo_text_box, ammo_text_rect)

            self.image.blit(self.weapon_image, self.weapon_image_rect)

            self.magazine_count = {key: value.copy() for key, value in who.magazine_count.items()}
            self.weapon_cooldown = who.weapon_cooldown.copy()


class SkillCardIcon(pygame.sprite.Sprite):
    cooldown = None
    active_skill = None

    def __init__(self, screen_scale, image, pos, key):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos  # pos of the skill on ui
        self.font = pygame.font.SysFont("helvetica", int(24 * screen_scale[1]))

        self.cooldown_check = 0  # cooldown number
        self.active_check = 0  # active timer number
        self.game_id = None

        key_font_size = int(24 * screen_scale[1])
        key_font = pygame.font.SysFont("helvetica", key_font_size)
        self.image = pygame.Surface((image.get_width(), image.get_height() + (key_font_size * 1.5)), pygame.SRCALPHA)
        text_surface = text_render(key, key_font)
        text_rect = text_surface.get_rect(midbottom=(self.image.get_width() / 2, self.image.get_height()))
        self.image.blit(text_surface, text_rect)

        image_rect = image.get_rect(midtop=(self.image.get_width() / 2, 0))
        self.image.blit(image, image_rect)
        self.base_image = self.image.copy()  # keep original image without number

        self.rect = self.image.get_rect(topleft=pos)
        self.cooldown_rect = self.image.get_rect(topleft=(0, 0))

    def icon_change(self, cooldown, active_timer):
        """Show active effect timer first if none show cooldown"""
        if active_timer != self.active_check:
            self.active_check = active_timer  # renew number
            self.image = self.base_image.copy()
            if self.active_check > 0:
                rect = self.image.get_rect(topleft=(0, 0))
                self.image.blit(self.active_skill, rect)
                output_number = str(self.active_check)
                if self.active_check >= 1000:
                    output_number = change_number(output_number)
                text_surface = self.font.render(output_number, True, (0, 0, 0))  # timer number
                text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(text_surface, text_rect)

        elif cooldown != self.cooldown_check and self.active_check == 0:  # Cooldown only get blit when skill is not active
            self.cooldown_check = cooldown
            self.image = self.base_image.copy()
            if self.cooldown_check > 0:
                self.image.blit(self.cooldown, self.cooldown_rect)
                output_number = str(self.cooldown_check)
                if self.cooldown_check >= 1000:  # change a thousand number into k (1k,2k)
                    output_number = change_number(output_number)
                text_surface = self.font.render(output_number, True, (0, 0, 0))
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
        self.base_image = self.image.copy()


class FPScount(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.base_image = self.image.copy()
        self.font = pygame.font.SysFont("Arial", 18)
        fps_text = self.font.render("60", True, pygame.Color("blue"))
        self.text_rect = fps_text.get_rect(center=(25, 25))
        self.rect = self.image.get_rect(topleft=(0, 0))

    def fps_show(self, clock):
        """Update current fps"""
        self.image = self.base_image.copy()
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
    colour = {0: (50, 50, 50), 1: (0, 0, 200), 2: (200, 0, 0)}
    selected_colour = {0: (200, 200, 200), 1: (150, 150, 255), 2: (255, 150, 150)}

    def __init__(self, pos, screen_scale):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.screen_scale = screen_scale
        self.leader_dot_images = {}
        self.player_dot_images = {}
        self.troop_dot_images = {}

        for team in self.colour:
            leader_dot = pygame.Surface(
                (10 * self.screen_scale[0], 10 * self.screen_scale[1]))  # dot for team2 leader
            leader_dot.fill((0, 0, 0))  # black corner
            team_part = pygame.Surface((8 * self.screen_scale[0], 8 * self.screen_scale[1]))  # size 6x6
            team_part.fill(self.colour[team])  # colour rect
            rect = leader_dot.get_rect(
                center=(leader_dot.get_width() / 2, leader_dot.get_height() / 2))
            leader_dot.blit(team_part, rect)
            self.leader_dot_images[team] = leader_dot.copy()
            team_part.fill(self.selected_colour[team])
            leader_dot.blit(team_part, rect)
            self.player_dot_images[team] = leader_dot.copy()
            troop_dot = pygame.Surface((4 * self.screen_scale[0], 4 * self.screen_scale[1]))  # dot for team2 leader
            troop_dot.fill(self.colour[team])
            self.troop_dot_images[team] = troop_dot

    def draw_image(self, base_map, image, camera):
        self.image = image
        size = self.image.get_size()
        self.map_scale_width = len(base_map.map_array[0]) / size[0]
        self.map_scale_height = len(base_map.map_array) / size[1]
        self.base_image = self.image.copy()
        self.camera_border = [camera.image.get_width(), camera.image.get_height()]
        self.camera_pos = camera.pos
        self.rect = self.image.get_rect(bottomright=self.pos)

    def update(self, camera_pos, subunit_list):
        """update troop and leader dot on map"""
        self.camera_pos = camera_pos
        self.image = self.base_image.copy()
        for subunit in subunit_list:
            scaled_pos = (subunit.base_pos[0] / self.map_scale_width, subunit.base_pos[1] / self.map_scale_height)
            if subunit.is_leader:
                if subunit.player_manual_control:
                    rect = self.player_dot_images[subunit.team].get_rect(center=scaled_pos)
                    self.image.blit(self.player_dot_images[subunit.team], rect)
                else:
                    rect = self.leader_dot_images[subunit.team].get_rect(center=scaled_pos)
                    self.image.blit(self.leader_dot_images[subunit.team], rect)
            else:
                rect = self.troop_dot_images[subunit.team].get_rect(center=scaled_pos)
                self.image.blit(self.troop_dot_images[subunit.team], rect)

        pygame.draw.rect(self.image, (0, 0, 0),
                         ((camera_pos[1][0] / self.screen_scale[0] / (self.map_scale_width)) / 5,
                          (camera_pos[1][1] / self.screen_scale[1] / (self.map_scale_height)) / 5,
                          (self.camera_border[0] / self.screen_scale[0] / 5) / self.map_scale_width,
                          (self.camera_border[1] / self.screen_scale[1] / 5) / self.map_scale_height), 2)


class EventLog(pygame.sprite.Sprite):
    max_row_show = 9  # maximum 9 text rows can appear at once

    def __init__(self, image, pos):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", 16)
        self.pos = pos
        self.image = image
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(bottomleft=self.pos)
        self.len_check = 0
        self.current_start_row = 0
        self.battle_log = []  # 0 troop
        self.current_start_row = 0
        self.scroll = None  # Link from battle after creation of the object

    def make_new_log(self):
        self.battle_log = []  # 0 troop
        self.current_start_row = 0
        self.len_check = 0  # total number of row in the current mode

    def add_event_log(self, map_event):
        self.map_event = map_event
        if self.map_event != {}:  # Edit map based event
            for event in self.map_event:
                if self.map_event[event]["Time"] != "":  # change time string to time delta same reason as above
                    new_time = datetime.datetime.strptime(self.map_event[event]["Time"], "%H:%M:%S").time()
                    new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
                    self.map_event[event]["Time"] = new_time
                else:
                    self.map_event[event]["Time"] = None

    def change_mode(self, mode):
        """Change tab"""
        self.mode = mode
        self.len_check = len(self.battle_log)
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
        self.battle_log.clear()
        self.scroll.current_row = self.current_start_row
        self.scroll.change_image(row_size=self.len_check)
        self.recreate_image()

    def recreate_image(self):
        self.image = self.base_image.copy()
        row = 10
        for index, text in enumerate(self.battle_log[self.current_start_row:]):
            if index == self.max_row_show:
                break
            text_surface = self.font.render(text[1], True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(40, row))
            self.image.blit(text_surface, text_rect)
            row += 20  # Whitespace between text row

    def log_text_process(self, who, text_output):
        """Cut up whole log into separate sentence based on space"""
        if len(text_output) <= 45:  # EventLog each row cannot have more than 45 characters including space
            self.battle_log.append([who, text_output])
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
                    self.battle_log.append([who, final_text_output])
                else:
                    self.battle_log.append([-1, final_text_output])
                starting_index = cut_number + 1

        if len(self.battle_log) > 1000:  # log cannot be more than 1000 length
            log_delete = len(self.battle_log) - 1000
            del self.battle_log[0:log_delete]  # remove the first few so only 1000 left
        return True

    def add_log(self, log, event_id=None):
        """Add log to appropriate event log, the log must be in list format
        following this rule [attacker (game_id), logtext]"""
        at_last_row = False
        image_change = False
        image_change2 = False
        if self.current_start_row + self.max_row_show >= self.len_check:
            at_last_row = True
        if log is not None:  # when event map log commentary come in, log will be none
            text_output = ": " + log[1]
            image_change = self.log_text_process(log[0], text_output)
        if event_id is not None and event_id in self.map_event:  # Process whether there is historical commentary to add to event log
            text_output = self.map_event[event_id]
            image_change2 = self.log_text_process(text_output["Who"], str(text_output["Time"]) + ": " + text_output["Text"])
        if image_change or image_change2:
            self.len_check = len(self.battle_log)
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
        self.base_image = self.image.copy()
        self.button_colour = (100, 100, 100)
        pygame.draw.rect(self.image, self.button_colour, (0, 0, self.image.get_width(), self.height_ui))
        self.rect = self.image.get_rect(topright=self.pos)
        self.current_row = 0
        self.row_size = 0

    def create_new_image(self):
        percent_row = 0
        max_row = 100
        self.image = self.base_image.copy()
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

    def setup_char_icon(self, troop_icon_group, subunit_list):
        """Setup character selection list in selector ui"""
        if troop_icon_group:  # remove all old icon first before making new list
            for icon in troop_icon_group:
                icon.kill()
                del icon

        if subunit_list:
            for this_subunit in subunit_list:
                if this_subunit.is_leader:
                    max_column_show = int(
                        self.image.get_width() / ((this_subunit.portrait.get_width() * self.icon_scale * 1.5)))
                    break
            current_index = int(self.current_row * max_column_show)  # the first index of current row
            self.row_size = len(subunit_list) / max_column_show

            if self.row_size.is_integer() is False:
                self.row_size = int(self.row_size) + 1

            if self.current_row > self.row_size - 1:
                self.current_row = self.row_size - 1
                current_index = int(self.current_row * max_column_show)
                self.scroll.change_image(new_row=self.current_row)

            for index, this_subunit in enumerate(
                    subunit_list):  # add unit icon for drawing according to appropriated current row
                if this_subunit.is_leader:
                    if index == 0:
                        start_column = self.rect.topleft[0] + (this_subunit.portrait.get_width() / 1.5)
                        column = start_column
                        row = self.rect.topleft[1] + (this_subunit.portrait.get_height() / 1.5)
                    if index >= current_index:
                        new_icon = CharIcon((column, row), this_subunit,
                                            (int(this_subunit.portrait.get_width() * self.icon_scale),
                                             int(this_subunit.portrait.get_height() * self.icon_scale)))
                        troop_icon_group.add(new_icon)
                        column += new_icon.image.get_width() * 1.2
                        if column > self.rect.topright[0] - ((new_icon.image.get_width() * self.icon_scale) * 3):
                            row += new_icon.image.get_height() * 1.5
                            column = start_column
                        if row > self.rect.bottomright[1] - ((new_icon.image.get_height() / 2) * self.icon_scale):
                            break  # do not draw for row that exceed the box
        self.scroll.change_image(row_size=self.row_size)


class CharIcon(pygame.sprite.Sprite):
    def __init__(self, pos, char, size):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.who = char  # link subunit object so when click can correctly select or go to position
        self.pos = pos  # position on unit selector ui
        self.selected = False

        self.leader_image = pygame.transform.scale(char.portrait,
                                                   size)  # scale leader image to fit the icon
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
            if self.who.team == 2:
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
            if self.who.team == 2:
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
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.timer = 0

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)

    def start_setup(self, time_start):
        self.timer = time_start.total_seconds()
        self.old_timer = self.timer
        self.image = self.base_image.copy()
        self.time_number = time_start  # datetime.timedelta(seconds=self.timer)
        self.timer_surface = self.font.render(str(self.timer), True, (0, 0, 0))
        self.timer_rect = self.timer_surface.get_rect(topleft=(5, 10))
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
                self.image = self.base_image.copy()
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
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

    def change_pos(self, pos, time_number, speed_number=None, time_button=None):
        """change position of the ui and related buttons"""
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)
        time_number.change_pos(self.rect.topleft)
        if speed_number is not None:
            speed_number.change_pos((self.rect.center[0] + int(self.rect.center[0] / 10), self.rect.center[1]))

        if time_button is not None:
            time_button[0].change_pos((self.rect.center[0] * 0.885,
                                       self.rect.center[1]))  # time pause button
            time_button[1].change_pos((self.rect.center[0] * 0.95,
                                       self.rect.center[1]))  # time decrease button
            time_button[2].change_pos((self.rect.center[0] * 1.03,
                                       self.rect.center[1]))  # time increase button


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
        self.battle_scale_list = []
        self.battle_scale = []

    def change_fight_scale(self, battle_scale_list):
        if self.battle_scale_list != battle_scale_list:
            self.battle_scale_list = battle_scale_list.copy()
            percent_scale = 0  # start point fo fill colour of team scale
            for team, value in enumerate(self.battle_scale_list):
                if value > 0:
                    self.image.fill(self.team_colour[team], (percent_scale, 0, self.image_width, self.image_height))
                    # team_text = self.font.render("{:,}".format(int(value - 1)), True, (0, 0, 0))  # add troop number text
                    # team_text_rect = team_text.get_rect(topleft=(percent_scale, 0))
                    # self.image.blit(team_text, team_text_rect)
                    percent_scale += value

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


class WheelUI(pygame.sprite.Sprite):
    def __init__(self, image, selected_image, pos, screen_size, text_size=20):
        """Wheel choice ui with text or image inside the choice.
        Works similar to Fallout companion wheel and similar system"""
        self._layer = 11
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", text_size)
        self.pos = pos
        self.screen_size = screen_size
        self.choice_list = ()

        self.wheel_button_image = image
        self.wheel_selected_button_image = selected_image

        self.base_image2 = pygame.Surface((image.get_width() * 6,
                                           image.get_height() * 6), pygame.SRCALPHA)  # empty image
        self.rect = self.base_image2.get_rect(center=self.pos)

        self.wheel_image_with_stuff = []
        self.wheel_selected_image_with_stuff = []
        self.wheel_rect = []

    def generate(self, blit_list):
        image_center = (self.base_image2.get_width() / 2, self.base_image2.get_height() / 2)
        self.wheel_image_with_stuff = []
        self.wheel_selected_image_with_stuff = []
        self.wheel_rect = []
        angle_space = 360 / len(blit_list)
        angle = 0
        for wheel_button in range(len(blit_list)):
            base_target = pygame.Vector2(image_center[0] - (image_center[0] / 2 *
                                                            math.sin(math.radians(angle))),
                                         image_center[1] + (image_center[1] / 2 *
                                                            math.cos(math.radians(angle))))
            angle += angle_space

            self.wheel_image_with_stuff.append(self.wheel_button_image.copy())
            self.wheel_selected_image_with_stuff.append(self.wheel_selected_button_image.copy())
            self.wheel_rect.append(self.wheel_button_image.get_rect(center=base_target))

        self.image = self.base_image2.copy()
        for index, rect in enumerate(self.wheel_rect):
            self.image.blit(self.wheel_image_with_stuff[index], rect)

        self.change_text_icon(blit_list)

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
        self.image = self.base_image2.copy()

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
        self.image = self.base_image2.copy()
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
        self.base_image = self.image.copy()
        text_surface = self.font.render(self.value, True, (0, 0, 0))
        self.text_rect = text_surface.get_rect(topleft=(self.image.get_width() / 10, self.image.get_height() / 10))
        self.image.blit(text_surface, self.text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def speed_update(self, new_value):
        """change speed number text"""
        self.image = self.base_image.copy()
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
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

    def add_subunit(self, who):
        if who is not None:
            self.who = who
            self.image = self.who.block_image
            self.rect = self.image.get_rect(topleft=self.pos)
        else:
            self.image = self.base_image.copy()


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


class ShootLine(pygame.sprite.Sprite):
    set_rotate = utility.set_rotate

    def __init__(self, screen_scale, who):
        self._layer = 40
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.screen_scale = screen_scale
        self.who = who
        self.who.shoot_line = self
        self.clip = (False, False)  # clip for weapon 1 and 2
        self.base_pos = pygame.Vector2(self.who.pos)
        self.base_target_pos = None
        self.target_pos = None
        self.camera_zoom_scale = 0
        self.line_size = 100 * self.screen_scale[0]
        self.can_shoot = [False, False]
        self.arc_shot = [False, False]

        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect(center=(0, 0))

    def update(self, base_target_pos, target_pos, clip, can_shoot, camera_zoom_scale, arc_shot):
        redo = False
        self.arc_shot = arc_shot
        if self.target_pos != target_pos:
            self.base_target_pos = base_target_pos
            self.target_pos = target_pos
            redo = True
        if self.clip != clip:
            self.clip = clip
            redo = True
        if self.can_shoot != can_shoot:
            self.can_shoot = can_shoot
            redo = True
        if self.base_pos != self.who.pos:
            self.base_pos = pygame.Vector2(self.who.pos)
            redo = True
        if self.camera_zoom_scale != camera_zoom_scale:
            self.camera_zoom_scale = camera_zoom_scale
            redo = True

        if self.who.alive is False:
            self.who.shoot_line = None
            self.kill()

        if redo:
            angle = self.set_rotate(self.target_pos)
            length = self.base_pos.distance_to(target_pos)
            half_length = length / 2
            self.image = pygame.Surface((self.line_size * self.camera_zoom_scale, length), pygame.SRCALPHA)
            check_image = pygame.Surface((self.line_size * self.camera_zoom_scale, length / 2))
            if self.who.state == 10:  # troop busy in melee
                self.image.fill((255, 127, 39, 50))
            else:
                self.image.fill((0, 0, 0, 50))
                rect_choice = ((0, 0), (check_image.get_width() / 2, 0))
                for index, this_clip in enumerate(self.clip):
                    if index == 0:
                        check_image2 = pygame.Surface((self.image.get_width() / 2, length / 2))
                    else:  # to make it so the bar fill entire line width
                        check_image2 = pygame.Surface((self.image.get_width(), length / 2))
                    if this_clip:  # shoot line block by friend
                        check_image2.fill((255, 0, 0, 50))
                    elif self.can_shoot[index]:  # can shoot
                        check_image2.fill(((100, 100, 255, 50), (100, 255, 100, 50))[index])
                    else:
                        check_image2.fill((100, 100, 100, 50))
                    rect = check_image2.get_rect(topleft=(rect_choice[index]))
                    check_image.blit(check_image2, rect)

            rect = check_image.get_rect(topleft=(0, 0))
            self.image.blit(check_image, rect)
            self.image = pygame.transform.rotate(self.image, angle)

            pos = pygame.Vector2(self.base_pos[0] - (half_length * math.sin(math.radians(angle))),
                                 self.base_pos[1] - (half_length * math.cos(math.radians(angle))))

            self.rect = self.image.get_rect(center=pos)

    def delete(self):
        self.who.shoot_line = None
        self.kill()


class SpriteIndicator(pygame.sprite.Sprite):
    def __init__(self, image, who, battle):
        """Indicator for subunit (coa) and effect sprite (shadow), also serve as hitbox"""
        self.who = who
        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.battle = battle
        self.image = image
        self.who.hitbox = self
        self.rect = self.image.get_rect(midtop=self.who.pos)

    def update(self, *args):
        self.rect = self.image.get_rect(midtop=self.who.pos)

