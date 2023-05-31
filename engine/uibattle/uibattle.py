import cProfile
import datetime
from math import cos, sin, radians

from pygame import Vector2, Surface, SRCALPHA, Color, Rect, mouse, draw
from pygame.font import Font
from pygame.sprite import Sprite
from pygame.transform import flip, smoothscale, scale

from engine.uimenu.uimenu import UIMenu
from engine.utility import text_render, minimise_number_text, number_to_minus_or_plus


def change_number(number):
    """Change number more than a thousand to K digit e.g. 1k = 1000"""
    if number >= 1000000:
        return str(round(number / 1000000, 1)) + "m"
    elif number >= 1000:
        return str(round(number / 1000, 1)) + "k"


class UIBattle(UIMenu):
    def __init__(self, player_interact=True, has_containers=False):
        """
        Parent class for all battle menu user interface
        """
        from engine.battle.battle import Battle
        UIMenu.__init__(self, player_interact=player_interact, has_containers=has_containers)
        self.updater = Battle.battle_ui_updater  # change updater to use battle ui updater instead of main menu one
        self.battle = Battle.battle


class BattleCursor(UIBattle):
    def __init__(self, images, player_input):
        """Game battle cursor"""
        self._layer = 9999999999999  # as high as possible, always blit last
        UIBattle.__init__(self, has_containers=True)
        self.images = images
        self.image = images["normal"]
        self.pos = Vector2((self.screen_size[0] / 2, self.screen_size[1] / 2))
        self.rect = self.image.get_rect(topleft=self.pos)
        self.player_input = player_input

    def change_input(self, player_input):
        self.player_input = player_input

    def update(self):
        """Update cursor position based on joystick or mouse input"""
        if self.player_input == "keyboard":  # keyboard and mouse control
            self.pos = mouse.get_pos()
        else:  # joystick control
            for joystick in self.battle.joysticks.values():
                for i in range(joystick.get_numaxes()):
                    if joystick.get_axis(i) > 0.1 or joystick.get_axis(i) < -0.1:
                        axis_name = number_to_minus_or_plus(joystick.get_axis(i))
                        if i == 2:
                            if axis_name == "+":
                                self.pos[0] += 5
                                if self.pos[0] > self.screen_size[0]:
                                    self.pos[0] = self.screen_size[0]
                            else:
                                self.pos[0] -= 5
                                if self.pos[0] < 0:
                                    self.pos[0] = 0
                        if i == 3:
                            if axis_name == "+":
                                self.pos[1] += 5
                                if self.pos[1] > self.screen_size[1]:
                                    self.pos[1] = self.screen_size[1]
                            else:
                                self.pos[1] -= 5
                                if self.pos[1] < 0:
                                    self.pos[1] = 0

        self.rect.topleft = self.pos


class ButtonUI(UIBattle):
    def __init__(self, image, layer=11):
        self._layer = layer
        UIBattle.__init__(self)
        self.pos = (0, 0)
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)


class HeroUI(UIBattle):
    weapon_sprite_pool = None

    def __init__(self, weapon_box_images, status_box_image, text_size=24):
        self._layer = 10
        UIBattle.__init__(self)
        self.font = Font(self.ui_font["text_paragraph"], int(text_size * self.screen_scale[1]))

        self.image = Surface((400 * self.screen_scale[0], 200 * self.screen_scale[1]))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()

        self.health_bar_size = (10 * self.screen_scale[0], self.image.get_height())
        self.health_bar = Surface(self.health_bar_size, SRCALPHA)
        self.health_bar.fill((0, 0, 0))
        self.health_bar_original = self.health_bar.copy()
        self.health_bar_rect = self.health_bar.get_rect(topright=(self.image.get_width() - self.health_bar_size[0], 0))
        self.health_bar.fill((200, 0, 0))

        self.health_bar_height = self.health_bar.get_height()

        self.stamina_bar = Surface(self.health_bar_size, SRCALPHA)
        self.stamina_bar.fill((0, 0, 0))
        self.stamina_bar_original = self.stamina_bar.copy()
        self.stamina_bar_rect = self.stamina_bar.get_rect(topright=(self.image.get_width(), 0))
        self.stamina_bar.fill((0, 200, 0))

        self.weapon_box_images = weapon_box_images
        self.weapon_image = Surface((200 * self.screen_scale[0], 200 * self.screen_scale[1]),
                                    SRCALPHA)

        self.prim_main_weapon_box_rect = self.weapon_box_images[0].get_rect(topleft=(0, 0))
        self.weapon_image.blit(self.weapon_box_images[0], self.prim_main_weapon_box_rect)
        self.prim_sub_weapon_box_rect = self.weapon_box_images[0].get_rect(
            topleft=(self.weapon_box_images[0].get_width(), 0))
        self.weapon_image.blit(flip(self.weapon_box_images[0], True, False),
                               self.prim_sub_weapon_box_rect)

        self.sec_main_weapon_box_rect = self.weapon_box_images[1].get_rect(
            topleft=(self.weapon_box_images[0].get_width() * 2, 0))
        self.weapon_image.blit(self.weapon_box_images[1], self.sec_main_weapon_box_rect)
        self.sec_sub_weapon_box_rect = self.weapon_box_images[1].get_rect(
            topleft=(self.weapon_box_images[0].get_width() * 2,
                     self.weapon_box_images[1].get_height()))

        self.weapon_cooldown_rect = (
            self.weapon_box_images[0].get_rect(midbottom=self.prim_main_weapon_box_rect.midbottom),
            self.weapon_box_images[0].get_rect(midbottom=self.prim_sub_weapon_box_rect.midbottom))

        self.ammo_count_rect = ((self.prim_main_weapon_box_rect.midbottom, self.prim_sub_weapon_box_rect.midbottom),
                                (self.sec_main_weapon_box_rect.midbottom, self.sec_sub_weapon_box_rect.midbottom))

        self.weapon_image.blit(flip(self.weapon_box_images[1], True, False),
                               self.sec_sub_weapon_box_rect)

        self.weapon_image_set_pos = ((self.prim_main_weapon_box_rect.center, self.prim_sub_weapon_box_rect.center),
                                     (self.sec_main_weapon_box_rect.center, self.sec_sub_weapon_box_rect.center))

        self.weapon_base_image = self.weapon_image.copy()  # after adding weapon image
        self.weapon_base_image2 = self.weapon_image.copy()  # after other effect like ammo count, cooldown, holding
        self.weapon_image_rect = self.weapon_image.get_rect(
            topright=(self.image.get_width() - (self.health_bar_size[0] * 2), 0))

        self.leader_image_rect = self.weapon_image.get_rect(topleft=(0, 0))

        self.ammo_text_box = self.font.render("999", True, (0, 0, 0))  # make text box for ammo
        self.ammo_text_box.fill((255, 255, 255))
        self.ammo_text_box_base = self.ammo_text_box.copy()

        self.leader_count_text_box_base = self.font.render("L:999", True, (0, 0, 0))
        self.leader_count_text_box_base.fill((255, 255, 255))
        self.leader_count_text_rect = self.leader_count_text_box_base.get_rect(
            midleft=(0, self.image.get_height() - (self.leader_count_text_box_base.get_height() * 1.5)))

        self.troop_count_text_box_base = self.font.render("T:999/999 + 999", True, (0, 0, 0))
        self.troop_count_text_box_base.fill((255, 255, 255))
        self.troop_count_text_rect = self.leader_count_text_box_base.get_rect(
            midleft=(0, self.image.get_height() - (self.troop_count_text_box_base.get_height() / 2)))

        self.status_effect_image = status_box_image
        self.status_effect_image_rect = self.status_effect_image.get_rect(
            bottomright=(self.health_bar_rect.bottomleft[0],
                         self.health_bar_rect.bottomleft[1]))

        bar_bad = Surface((18 * self.screen_scale[0], 13 * self.screen_scale[1]))
        bar_bad.fill((100, 0, 0))
        bar_worst = Surface((18 * self.screen_scale[0], 13 * self.screen_scale[1]))
        bar_worst.fill((200, 0, 0))

        bar_good = Surface((18 * self.screen_scale[0], 13 * self.screen_scale[1]))
        bar_good.fill((0, 100, 0))
        bar_best = Surface((18 * self.screen_scale[0], 13 * self.screen_scale[1]))
        bar_best.fill((0, 200, 0))

        bar_normal = Surface((18 * self.screen_scale[0], 13 * self.screen_scale[1]))
        bar_normal.fill((100, 100, 100))

        self.status_bar_image = {-1: bar_worst, 0: bar_bad, 1: bar_normal, 2: bar_good, 3: bar_best}
        self.status_bar_rect = (
            self.status_bar_image[0].get_rect(midbottom=(13 * self.screen_scale[0], 16 * self.screen_scale[1])),
            self.status_bar_image[0].get_rect(midbottom=(37 * self.screen_scale[0], 16 * self.screen_scale[1])),
            self.status_bar_image[0].get_rect(midbottom=(61 * self.screen_scale[0], 16 * self.screen_scale[1])),
            self.status_bar_image[0].get_rect(midbottom=(85 * self.screen_scale[0], 16 * self.screen_scale[1])),
            self.status_bar_image[0].get_rect(midbottom=(109 * self.screen_scale[0], 16 * self.screen_scale[1])),
            self.status_bar_image[0].get_rect(midbottom=(132 * self.screen_scale[0], 16 * self.screen_scale[1])),
            self.status_bar_image[0].get_rect(midbottom=(155 * self.screen_scale[0], 16 * self.screen_scale[1])),
            self.status_bar_image[0].get_rect(midbottom=(179 * self.screen_scale[0], 16 * self.screen_scale[1])),
            self.status_bar_image[0].get_rect(midbottom=(203 * self.screen_scale[0], 16 * self.screen_scale[1])))

        self.base_image.blit(self.status_effect_image, self.status_effect_image_rect)

        self.equipped_weapon = None
        self.status = None
        self.magazine_count = None
        self.weapon_cooldown = None
        self.weapon_holding = [False, False]
        self.troop_follower_size = None
        self.leader_follower_size = None

        self.base_image.blit(self.health_bar, self.health_bar_rect)
        self.base_image.blit(self.stamina_bar, self.stamina_bar_rect)

        self.last_health = 0
        self.last_stamina = 0

        self.melee_attack_mod = 3
        self.melee_def_mod = 3
        self.range_attack_mod = 3
        self.range_def_mod = 3
        self.speed_mod = 3
        self.morale_mod = 3
        self.discipline_mod = 3
        self.hidden_mod = 3
        self.temperature_mod = 3

        self.pos = (0, 0)
        self.rect = self.image.get_rect(topleft=self.pos)

    def add_leader_image(self, leader_image):
        self.base_image.blit(smoothscale(leader_image,
                                         (150 * self.screen_scale[0], 150 * self.screen_scale[1])),
                             self.leader_image_rect)
        self.image = self.base_image.copy()

    def value_input(self, who):
        if self.last_health != who.health:
            self.last_health = who.health
            self.health_bar = self.health_bar_original.copy()
            health_percent = who.health / who.max_health
            health_bar = Surface((self.health_bar_size[0], self.health_bar_size[1] * health_percent))
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
            stamina_bar = Surface((self.health_bar_size[0], self.health_bar_size[1] * stamina_percent))
            stamina_bar.fill((0, 200, 0))
            stamina_bar_rect = stamina_bar.get_rect(bottomleft=(0, self.health_bar_height))
            self.stamina_bar.blit(stamina_bar, stamina_bar_rect)

            self.base_image.blit(self.stamina_bar, self.stamina_bar_rect)
            self.image.blit(self.stamina_bar, self.stamina_bar_rect)

        if self.leader_follower_size != len(who.alive_leader_follower):
            self.leader_follower_size = len(who.alive_leader_follower)
            leader_count_text_box = self.leader_count_text_box_base.copy()
            leader_count_text = self.font.render("L:" + str(len(who.alive_leader_follower)), True, (0, 0, 0))
            leader_count_text_box.blit(leader_count_text,
                                       leader_count_text.get_rect(midleft=(0,
                                                                           leader_count_text_box.get_height() / 2)))
            self.image.blit(leader_count_text_box, self.leader_count_text_rect)

        if self.troop_follower_size != len(who.alive_troop_follower):
            self.troop_follower_size = len(who.alive_troop_follower)
            troop_count_text_box = self.troop_count_text_box_base.copy()
            troop_count_text = self.font.render("T:" + minimise_number_text(self.troop_follower_size) + "/" +
                                                minimise_number_text(sum(who.troop_dead_list.values()) +
                                                                     self.troop_follower_size) + " + " +
                                                minimise_number_text(sum(who.troop_reserve_list.values())), True,
                                                (0, 0, 0))
            troop_count_text_box.blit(troop_count_text,
                                      troop_count_text.get_rect(midleft=(0,
                                                                         troop_count_text_box.get_height() / 2)))
            self.image.blit(troop_count_text_box, self.troop_count_text_rect)

        weapon_filter_change = False
        if (who.hold_timer > 1 or who.momentum) and "weapon" in who.current_action and True not in self.weapon_holding:
            self.weapon_holding[who.current_action["weapon"]] = True
            weapon_filter_change = True
        elif (who.hold_timer == 0 and not who.momentum) and True in self.weapon_holding:
            self.weapon_holding = [False, False]
            weapon_filter_change = True
        elif self.weapon_cooldown != who.weapon_cooldown:
            weapon_filter_change = True
            self.weapon_cooldown = who.weapon_cooldown.copy()

        if self.equipped_weapon != who.equipped_weapon:
            self.equipped_weapon = who.equipped_weapon
            self.weapon_image = self.weapon_base_image.copy()
            self.weapon_name_set = list(who.weapon_name)
            self.weapon_name_set.insert(0, self.weapon_name_set.pop(
                self.weapon_name_set.index(self.weapon_name_set[self.equipped_weapon])))
            self.weapon_set_index = list(range(0, len(who.weapon_name)))
            self.weapon_set_index.insert(0,
                                         self.weapon_set_index.pop(self.weapon_set_index.index(self.equipped_weapon)))
            for index, this_weapon_set in enumerate(self.weapon_name_set):
                if index > len(self.weapon_name_set) - 1:
                    index = len(self.weapon_name_set) - 1
                true_weapon_set_index = self.weapon_set_index[index]
                for index2, this_weapon in enumerate(this_weapon_set):
                    if who.weapon_version[true_weapon_set_index][index2] in self.weapon_sprite_pool[this_weapon]:
                        weapon_image = self.weapon_sprite_pool[this_weapon][who.weapon_version[
                            true_weapon_set_index][index2]]["Icon"].copy()
                    else:
                        weapon_image = self.weapon_sprite_pool[this_weapon]["Common"]["Icon"].copy()

                    if index > 0:  # unequipped weapon
                        weapon_image = scale(weapon_image,
                                             (self.weapon_image.get_width() / 5,
                                              self.weapon_image.get_height() / 5))
                    self.weapon_image.blit(weapon_image,
                                           weapon_image.get_rect(center=self.weapon_image_set_pos[index][index2]))
            self.weapon_base_image2 = self.weapon_image.copy()

        if self.equipped_weapon != who.equipped_weapon or weapon_filter_change:  # add weapon filter and ammo
            if weapon_filter_change:
                self.weapon_image = self.weapon_base_image2.copy()
            for index, this_weapon_set in enumerate(self.weapon_name_set):
                if index == 0:  # add cooldown in any
                    for index2, this_weapon in enumerate(this_weapon_set):
                        cooldown = who.weapon_cooldown[index2]
                        speed = who.weapon_speed[index2]
                        if 0 < cooldown < speed:
                            cooldown_image = Surface((self.weapon_box_images[0].get_width(),
                                                      self.weapon_box_images[0].get_height() *
                                                      (1 - (cooldown / speed))), SRCALPHA)
                            cooldown_image.fill((255, 50, 50, 200))
                            self.weapon_image.blit(cooldown_image, self.weapon_cooldown_rect[index2])
                        elif self.weapon_holding[index2]:  # holding weapon animation
                            hold_image = Surface((self.weapon_box_images[0].get_width(),
                                                  self.weapon_box_images[0].get_height()), SRCALPHA)
                            hold_image.fill((100, 200, 100, 200))
                            self.weapon_image.blit(hold_image, self.weapon_cooldown_rect[index2])

        if who.magazine_count != self.magazine_count:
            for index, this_weapon_set in enumerate(self.weapon_name_set):
                if index > len(self.weapon_name_set) - 1:
                    index = len(self.weapon_name_set) - 1
                true_weapon_set_index = self.weapon_set_index[index]
                for index2, this_weapon in enumerate(this_weapon_set):
                    if who.magazine_size[true_weapon_set_index][index2]:  # range weapon
                        if true_weapon_set_index not in who.magazine_count or \
                                (true_weapon_set_index in who.magazine_count and
                                 index2 not in who.magazine_count[true_weapon_set_index]):  # no ammo
                            ammo_count = 0
                            text_colour = (200, 100, 100)
                        else:
                            ammo_count = who.magazine_count[true_weapon_set_index][index2]
                            text_colour = (0, 0, 0)
                        ammo_text_surface = self.font.render(str(ammo_count), True, text_colour)  # ammo number
                        self.ammo_text_box = self.ammo_text_box_base.copy()
                        self.ammo_text_box.blit(ammo_text_surface,
                                                ammo_text_surface.get_rect(center=(self.ammo_text_box.get_width() / 2,
                                                                                   self.ammo_text_box.get_height() / 2)))
                        self.weapon_image.blit(self.ammo_text_box,
                                               self.ammo_text_box.get_rect(midtop=self.ammo_count_rect[index][index2]))

            self.magazine_count = {key: value.copy() for key, value in who.magazine_count.items()}

        if self.equipped_weapon != who.equipped_weapon or who.magazine_count != self.magazine_count or weapon_filter_change:
            self.image.blit(self.weapon_image, self.weapon_image_rect)

        status_change = False
        if who.melee_attack_mod != self.melee_attack_mod:
            self.melee_attack_mod = who.melee_attack_mod
            self.status_effect_image.blit(self.status_bar_image[self.melee_attack_mod], self.status_bar_rect[0])
            status_change = True

        if who.melee_def_mod != self.melee_def_mod:
            self.melee_def_mod = who.melee_def_mod
            self.status_effect_image.blit(self.status_bar_image[self.melee_def_mod], self.status_bar_rect[1])
            status_change = True

        if who.range_attack_mod != self.range_attack_mod:
            self.range_attack_mod = who.range_attack_mod
            self.status_effect_image.blit(self.status_bar_image[self.range_attack_mod], self.status_bar_rect[2])
            status_change = True

        if who.range_def_mod != self.range_def_mod:
            self.range_def_mod = who.range_def_mod
            self.status_effect_image.blit(self.status_bar_image[self.range_def_mod], self.status_bar_rect[3])
            status_change = True

        if who.speed_mod != self.speed_mod:
            self.speed_mod = who.speed_mod
            self.status_effect_image.blit(self.status_bar_image[self.speed_mod], self.status_bar_rect[4])
            status_change = True

        if who.morale_mod != self.morale_mod:
            self.morale_mod = who.morale_mod
            self.status_effect_image.blit(self.status_bar_image[self.morale_mod], self.status_bar_rect[5])
            status_change = True

        if who.discipline_mod != self.discipline_mod:
            self.discipline_mod = who.discipline_mod
            self.status_effect_image.blit(self.status_bar_image[self.discipline_mod], self.status_bar_rect[6])
            status_change = True

        if who.hidden_mod != self.hidden_mod:
            self.hidden_mod = who.hidden_mod
            self.status_effect_image.blit(self.status_bar_image[self.hidden_mod], self.status_bar_rect[7])
            status_change = True

        if who.temperature_mod != self.temperature_mod:
            self.temperature_mod = who.temperature_mod
            self.status_effect_image.blit(self.status_bar_image[self.temperature_mod], self.status_bar_rect[8])
            status_change = True

        if status_change:
            self.base_image.blit(self.status_effect_image, self.status_effect_image_rect)
            self.image.blit(self.status_effect_image, self.status_effect_image_rect)


class SkillCardIcon(UIBattle, Sprite):
    cooldown = None
    active_skill = None

    def __init__(self, image, pos, key):
        self._layer = 11
        UIBattle.__init__(self)
        Sprite.__init__(self, self.containers)
        self.pos = pos  # pos of the skill on ui
        self.font = Font(self.ui_font["main_button"], int(24 * self.screen_scale[1]))

        self.cooldown_check = 0  # cooldown number
        self.active_check = 0  # active timer number
        self.game_id = None

        self.key_font_size = int(24 * self.screen_scale[1])

        self.image = Surface((image.get_width(), image.get_height() + (self.key_font_size * 1.5)),
                             SRCALPHA)
        image_rect = image.get_rect(midtop=(self.image.get_width() / 2, 0))
        self.image.blit(image, image_rect)
        self.base_image = self.image.copy()  # original image before adding key name

        key_font = Font(self.ui_font["main_button"], self.key_font_size)
        text_surface = text_render(key, key_font)
        text_rect = text_surface.get_rect(midbottom=(self.image.get_width() / 2, self.image.get_height()))
        self.image.blit(text_surface, text_rect)
        self.base_image2 = self.image.copy()  # keep original image without timer

        self.rect = self.image.get_rect(topleft=pos)
        self.cooldown_rect = self.image.get_rect(topleft=(0, 0))

    def change_key(self, key):
        self.image = self.base_image.copy()
        key_font = Font(self.ui_font["main_button"], self.key_font_size)
        text_surface = text_render(key, key_font)
        text_rect = text_surface.get_rect(midbottom=(self.image.get_width() / 2, self.image.get_height()))
        self.image.blit(text_surface, text_rect)
        self.base_image2 = self.image.copy()  # keep original image without timer

    def icon_change(self, cooldown, active_timer):
        """Show active effect timer first if none show cooldown"""
        if active_timer != self.active_check:
            self.active_check = active_timer  # renew number
            self.image = self.base_image2.copy()
            if self.active_check:
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
            self.image = self.base_image2.copy()
            if self.cooldown_check:
                self.image.blit(self.cooldown, self.cooldown_rect)
                output_number = str(self.cooldown_check)
                if self.cooldown_check >= 1000:  # change a thousand number into k (1k,2k)
                    output_number = change_number(output_number)
                text_surface = self.font.render(output_number, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(text_surface, text_rect)


class FPScount(UIBattle):
    def __init__(self):
        self._layer = 12
        UIBattle.__init__(self, player_interact=False)
        self.image = Surface((50, 50), SRCALPHA)
        self.base_image = self.image.copy()
        self.font = Font(self.ui_font["main_button"], 18)
        fps_text = self.font.render("60", True, Color("red"))
        self.text_rect = fps_text.get_rect(center=(10, 10))
        self.rect = self.image.get_rect(topleft=(0, 0))

    def fps_show(self, clock):
        """Update current fps"""
        self.image = self.base_image.copy()
        fps = str(int(clock.get_fps()))
        fps_text = self.font.render(fps, True, Color("red"))
        text_rect = fps_text.get_rect(center=(10, 10))
        self.image.blit(fps_text, text_rect)


class MiniMap(UIBattle):
    colour = None
    selected_colour = None

    def __init__(self, pos):
        self._layer = 10
        UIBattle.__init__(self, player_interact=False)
        self.pos = pos
        self.leader_dot_images = {}
        self.player_dot_images = {}
        self.troop_dot_images = {}

        self.update_count = 0

        for team in self.colour:
            leader_dot = Surface(
                (10 * self.screen_scale[0], 10 * self.screen_scale[1]))  # dot for team2 leader
            leader_dot.fill((0, 0, 0))  # black corner
            team_part = Surface((8 * self.screen_scale[0], 8 * self.screen_scale[1]))  # size 6x6
            team_part.fill(self.colour[team])  # colour rect
            rect = leader_dot.get_rect(
                center=(leader_dot.get_width() / 2, leader_dot.get_height() / 2))
            leader_dot.blit(team_part, rect)
            self.leader_dot_images[team] = leader_dot.copy()
            team_part.fill(self.selected_colour[team])
            leader_dot.blit(team_part, rect)
            self.player_dot_images[team] = leader_dot.copy()
            troop_dot = Surface((4 * self.screen_scale[0], 4 * self.screen_scale[1]))  # dot for team2 leader
            troop_dot.fill(self.colour[team])
            self.troop_dot_images[team] = troop_dot

    def draw_image(self, base_map, image, camera):
        self.image = image
        size = self.image.get_size()
        self.map_scale_width = len(base_map.map_array[0]) / size[0]
        self.map_scale_height = len(base_map.map_array) / size[1]
        self.base_image = self.image.copy()
        self.camera_border = [camera.image.get_width(), camera.image.get_height()]
        self.rect = self.image.get_rect(bottomright=self.pos)

    def update(self):
        """update troop and leader dot on map"""
        self.update_count += 1
        if self.update_count > 5:
            self.update_count = 0
            self.image = self.base_image.copy()
            for subunit in self.battle.active_unit_list:
                scaled_pos = (subunit.base_pos[0] / self.map_scale_width, subunit.base_pos[1] / self.map_scale_height)
                if subunit.is_leader:
                    if subunit.player_control:
                        rect = self.player_dot_images[subunit.team].get_rect(center=scaled_pos)
                        self.image.blit(self.player_dot_images[subunit.team], rect)
                    else:
                        rect = self.leader_dot_images[subunit.team].get_rect(center=scaled_pos)
                        self.image.blit(self.leader_dot_images[subunit.team], rect)
                else:
                    rect = self.troop_dot_images[subunit.team].get_rect(center=scaled_pos)
                    self.image.blit(self.troop_dot_images[subunit.team], rect)

            draw.rect(self.image, (0, 0, 0),
                      ((self.battle.camera_topleft_corner[0] / self.screen_scale[0] / (self.map_scale_width)) / 5,
                       (self.battle.camera_topleft_corner[1] / self.screen_scale[1] / (self.map_scale_height)) / 5,
                       (self.camera_border[0] / self.screen_scale[0] / 5) / self.map_scale_width,
                       (self.camera_border[1] / self.screen_scale[1] / 5) / self.map_scale_height), 2)


class EventLog(UIBattle):

    def __init__(self, image, pos):
        self._layer = 10
        UIBattle.__init__(self)
        self.font = Font(self.ui_font["main_button"], int(image.get_height() / 15))
        self.pos = pos
        self.image = image
        self.max_row_show = int(image.get_height() / self.font.get_height())
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
        else:  # Cut the text log into multiple row if more than 45 unit
            cut_space = [index for index, letter in enumerate(text_output) if letter == " "]
            loop_number = len(text_output) / 45  # number of row
            if not loop_number.is_integer():  # always round up if there is decimal number
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
        following this rule [id, logtext]"""
        at_last_row = False
        image_change = False
        image_change2 = False
        if self.current_start_row + self.max_row_show >= self.len_check:
            at_last_row = True
        if log:  # when event map log commentary come in, log will be none
            text_output = ": " + log[1]
            image_change = self.log_text_process(log[0], text_output)
        if event_id and event_id in self.map_event:  # Process whether there is historical commentary to add to event log
            text_output = self.map_event[event_id]
            image_change2 = self.log_text_process(text_output["Who"],
                                                  str(text_output["Time"]) + ": " + str(text_output["Text"]))
        if image_change or image_change2:
            self.len_check = len(self.battle_log)
            if at_last_row and self.len_check > self.max_row_show:
                self.current_start_row = self.len_check - self.max_row_show
                self.scroll.current_row = self.current_start_row
            self.scroll.change_image(row_size=self.len_check)
            self.recreate_image()


class UIScroll(UIBattle):
    def __init__(self, ui, pos):
        """
        Scroll for any applicable ui
        :param ui: Any ui object, the ui must has max_row_show attribute, layer, and image surface
        :param pos: Starting pos
        :param layer: Surface layer value
        """
        self.ui = ui
        self._layer = self.ui.layer + 2  # always 2 layer higher than the ui and its item
        UIBattle.__init__(self)

        self.ui.scroll = self
        self.height_ui = self.ui.image.get_height()
        self.max_row_show = self.ui.max_row_show
        self.pos = pos
        self.image = Surface((10, self.height_ui))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.button_colour = (100, 100, 100)
        draw.rect(self.image, self.button_colour, (0, 0, self.image.get_width(), self.height_ui))
        self.rect = self.image.get_rect(topright=self.pos)
        self.current_row = 0
        self.row_size = 0

    def create_new_image(self):
        percent_row = 0
        max_row = 100
        self.image = self.base_image.copy()
        if self.row_size:
            percent_row = self.current_row * 100 / self.row_size
            max_row = (self.current_row + self.max_row_show) * 100 / self.row_size
        max_row = max_row - percent_row
        draw.rect(self.image, self.button_colour,
                  (0, int(self.height_ui * percent_row / 100), self.image.get_width(),
                   int(self.height_ui * max_row / 100)))

    def change_image(self, new_row=None, row_size=None):
        """New row is input of scrolling by user to new row, row_size is changing based on adding more log or clear"""
        if row_size is not None:
            self.row_size = row_size
        if new_row is not None:  # accept from both wheeling scroll and drag scroll bar
            self.current_row = new_row
        self.create_new_image()

    def player_input(self, mouse_pos, mouse_scroll_up=False, mouse_scroll_down=False):
        """Player input update via click or scrolling"""
        if mouse_pos and self.rect.collidepoint(mouse_pos):
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


class UnitSelector(UIBattle):
    def __init__(self, pos, image, icon_scale=1):
        self._layer = 10
        UIBattle.__init__(self, player_interact=False)
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)
        self.icon_scale = icon_scale
        self.current_row = 0
        self.max_row_show = 2
        self.row_size = 0
        self.scroll = None  # got add after create scroll object

    def setup_unit_icon(self, troop_icon_group, subunit_list):
        """Setup unit selection list in selector ui"""
        if troop_icon_group:  # remove all old icon first before making new list
            for icon in troop_icon_group:
                icon.kill()
                del icon

        if subunit_list:
            for this_subunit in subunit_list:
                max_column_show = int(
                    self.image.get_width() / ((this_subunit.portrait.get_width() * self.icon_scale * 1.5)))
                break
            current_index = int(self.current_row * max_column_show)  # the first index of current row
            self.row_size = len(subunit_list) / max_column_show

            if not self.row_size.is_integer():
                self.row_size = int(self.row_size) + 1

            if self.current_row > self.row_size - 1:
                self.current_row = self.row_size - 1
                current_index = int(self.current_row * max_column_show)

            for index, this_subunit in enumerate(
                    subunit_list):  # add unit icon for drawing according to appropriated current row
                if this_subunit.is_leader:
                    if index == 0:
                        start_column = self.rect.topleft[0] + (this_subunit.portrait.get_width() / 1.5)
                        column = start_column
                        row = self.rect.topleft[1] + (this_subunit.portrait.get_height() / 1.5)
                    if index >= current_index:
                        new_icon = UnitIcon((column, row), this_subunit,
                                            (int(this_subunit.portrait.get_width() * self.icon_scale),
                                             int(this_subunit.portrait.get_height() * self.icon_scale)))
                        troop_icon_group.add(new_icon)
                        column += new_icon.image.get_width() * 1.2
                        if column > self.rect.topright[0] - ((new_icon.image.get_width() * self.icon_scale) * 3):
                            row += new_icon.image.get_height() * 1.5
                            column = start_column
                        if row > self.rect.bottomright[1] - ((new_icon.image.get_height() / 2) * self.icon_scale):
                            break  # do not draw for row that exceed the box
        self.scroll.change_image(new_row=self.current_row, row_size=self.row_size)


class UnitIcon(UIBattle, Sprite):
    colour = None

    def __init__(self, pos, unit, size):
        self._layer = 11
        UIBattle.__init__(self)
        Sprite.__init__(self, self.containers)
        self.who = unit  # link unit object so when click can correctly select or go to position
        self.pos = pos  # pos on unit selector ui
        self.place_pos = pos  # pos when drag by mouse
        self.name = ""  # not used for unit icon, for checking with CampIcon
        self.selected = False
        self.right_selected = False

        self.leader_image = scale(unit.portrait,
                                  size)  # scale leader image to fit the icon
        self.not_selected_image = Surface((self.leader_image.get_width() + (self.leader_image.get_width() / 7),
                                           self.leader_image.get_height() + (
                                                   self.leader_image.get_height() / 7)))  # create image black corner block
        self.selected_image = self.not_selected_image.copy()
        self.selected_image.fill((0, 0, 0))  # fill black corner
        self.right_selected_image = self.not_selected_image.copy()
        self.right_selected_image.fill((150, 150, 150))  # fill grey corner
        self.not_selected_image.fill((255, 255, 255))  # fill white corner

        for image in (
                self.not_selected_image, self.selected_image,
                self.right_selected_image):  # add team colour and leader image
            center_image = Surface((self.leader_image.get_width() + (self.leader_image.get_width() / 14),
                                    self.leader_image.get_height() + (
                                            self.leader_image.get_height() / 14)))  # create image block
            center_image.fill(self.colour[self.who.team])  # fill colour according to team
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
        self.rect = self.image.get_rect(center=pos)

    def change_image(self, new_image=None, change_side=False):
        """For changing side"""
        if change_side:
            self.image.fill((144, 167, 255))
            if self.who.team == 2:
                self.image.fill((255, 114, 114))
            self.image.blit(self.leader_image, self.leader_image_rect)
        if new_image:
            self.leader_image = new_image
            self.image.blit(self.leader_image, self.leader_image_rect)

    def selection(self, how="left"):
        if how == "left":
            if self.selected:
                self.selected = False
                self.image = self.not_selected_image
            else:
                self.selected = True
                self.right_selected = False
                self.image = self.selected_image
        else:
            if self.right_selected:
                self.right_selected = False
                self.image = self.not_selected_image
            else:
                self.right_selected = True
                self.selected = False
                self.image = self.right_selected_image


class TempUnitIcon(UIBattle):
    def __init__(self, team, image, index):
        UIBattle.__init__(self)
        self.team = team
        self.index = index
        self.map_id = None
        self.portrait = Surface((200 * self.screen_scale[0], 200 * self.screen_scale[1]), SRCALPHA)
        if type(image) in (int, float, str):
            self.name = str(image)
            font = Font(self.ui_font["main_button"],
                        int(120 / (len(self.name) / 3) * self.screen_scale[1]))
            image_surface = font.render(self.name, True, (0, 0, 0))
            image_rect = image_surface.get_rect(center=(self.portrait.get_width() / 2, self.portrait.get_height() / 2))
            self.portrait.blit(image_surface, image_rect)
        else:
            self.name = image
            image_rect = image.get_rect(center=(self.portrait.get_width() / 2, self.portrait.get_height() / 2))
            self.portrait.blit(image, image_rect)
        self.is_leader = True


class Timer(UIBattle):
    def __init__(self, pos, text_size=20):
        self._layer = 11
        UIBattle.__init__(self, player_interact=False)
        self.font = Font(self.ui_font["main_button"], text_size)
        self.pos = pos
        self.image = Surface((100, 30), SRCALPHA)
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
        if dt:
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


class TimeUI(UIBattle):
    def __init__(self, image):
        self._layer = 10
        UIBattle.__init__(self, player_interact=False)
        self.pos = (0, 0)
        self.image = image.copy()
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

    def change_pos(self, pos, time_number, speed_number=None, time_button=None):
        """change position of the ui and related buttons"""
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)
        time_number.change_pos(self.rect.topleft)
        if speed_number:
            speed_number.change_pos((self.rect.center[0] + int(self.rect.center[0] / 10), self.rect.center[1]))

        if time_button:
            time_button[0].change_pos((self.rect.center[0] * 0.885,
                                       self.rect.center[1]))  # time pause button
            time_button[1].change_pos((self.rect.center[0] * 0.95,
                                       self.rect.center[1]))  # time decrease button
            time_button[2].change_pos((self.rect.center[0] * 1.03,
                                       self.rect.center[1]))  # time increase button


class BattleScaleUI(UIBattle):
    def __init__(self, image, team_colour):
        self._layer = 10
        UIBattle.__init__(self, player_interact=False)
        self.team_colour = team_colour
        self.font = Font(self.ui_font["main_button"], 12)
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
                    self.image.fill(self.team_colour[team], (self.image_width * percent_scale, 0,
                                                             self.image_width, self.image_height))
                    # team_text = self.font.render("{:,}".format(int(value - 1)), True, (0, 0, 0))  # add troop number text
                    # team_text_rect = team_text.get_rect(topleft=(percent_scale, 0))
                    # self.image.blit(team_text, team_text_rect)
                    percent_scale += value

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


class WheelUI(UIBattle):
    def __init__(self, image, selected_image, pos, text_size=20):
        """Wheel choice ui with text or image inside the choice.
        Works similar to Fallout companion wheel and similar system"""
        self._layer = 11
        UIBattle.__init__(self)
        self.font = Font(self.ui_font["main_button"], text_size)
        self.pos = pos
        self.choice_list = ()

        self.wheel_button_image = image
        self.wheel_selected_button_image = selected_image

        self.base_image2 = Surface((image.get_width() * 6,
                                    image.get_height() * 6), SRCALPHA)  # empty image
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
            base_target = Vector2(image_center[0] - (image_center[0] / 2 *
                                                     sin(radians(angle))),
                                  image_center[1] + (image_center[1] / 2 *
                                                     cos(radians(angle))))
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
        new_mouse_pos = Vector2(mouse_pos[0] / self.screen_size[0] * self.image.get_width(),
                                mouse_pos[1] / self.screen_size[1] * self.image.get_height())
        for index, rect in enumerate(self.wheel_rect):
            distance = Vector2(rect.center).distance_to(new_mouse_pos)
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
            text_box = Surface((text_surface.get_width() * 1.2,
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
            if item:  # Wheel choice with icon or text inside
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


class EscBox(UIBattle):
    images = {}

    def __init__(self):
        self._layer = 24
        UIBattle.__init__(self, player_interact=False)
        self.pos = (self.screen_size[0] / 2, self.screen_size[1] / 2)
        self.mode = "menu"  # Current menu mode
        self.image = self.images[self.mode]
        self.rect = self.image.get_rect(center=self.pos)

    def change_mode(self, mode):
        """Change between 0 menu, 1 option, 2 encyclopedia mode"""
        self.mode = mode
        if self.mode != "encyclopedia":
            self.image = self.images[mode]
            self.rect = self.image.get_rect(center=self.pos)


class EscButton(UIBattle):
    def __init__(self, images, pos, text="", text_size=16):
        self._layer = 25
        UIBattle.__init__(self)
        self.pos = pos
        self.images = [image.copy() for image in list(images.values())]
        self.text = text
        self.font = Font(self.ui_font["main_button"], text_size)

        if text != "":  # blit menu text into button image
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(text_surface, text_rect)  # button idle image
            self.images[1].blit(text_surface, text_rect)  # button mouse over image
            self.images[2].blit(text_surface, text_rect)  # button click image

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)


class BattleDone(UIBattle):
    def __init__(self, pos, box_image, result_image):
        self._layer = 18
        UIBattle.__init__(self, player_interact=False)
        self.box_image = box_image
        self.result_image = result_image
        self.font = Font(self.ui_font["name_font"], int(self.screen_scale[1] * 60))
        self.header_font = Font(self.ui_font["text_paragraph_bold"], int(self.screen_scale[1] * 36))
        self.text_font = Font(self.ui_font["text_paragraph"], int(self.screen_scale[1] * 24))
        self.pos = pos
        self.image = self.box_image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.winner = None
        self.result_showing = False

        self.result_text_x = {"Faction": 10 * self.screen_scale[0], "Total": 500 * self.screen_scale[0],
                              "Alive": 650 * self.screen_scale[0],
                              "Flee": 800 * self.screen_scale[0],
                              "Death": 950 * self.screen_scale[0]}

    def pop(self, winner, coa=None):
        self.winner = str(winner)
        self.image = self.box_image.copy()
        text_surface = self.font.render(self.winner, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.screen_scale[1] * 36) + 3))
        self.image.blit(text_surface, text_rect)
        if self.winner != "Draw":
            text_surface = self.font.render("Victory", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.screen_scale[1] * 60) * 2))
            self.image.blit(text_surface, text_rect)
            new_coa = smoothscale(coa, (200 * self.screen_scale[0], 200 * self.screen_scale[1]))
            coa_rect = new_coa.get_rect(midtop=text_rect.midbottom)
            self.image.blit(new_coa, coa_rect)
        self.result_showing = False

    def show_result(self, team_coa, stat):
        self.result_showing = True
        self.image = self.result_image.copy()

        for key, value in self.result_text_x.items():
            text_surface = self.header_font.render(key, True, (0, 0, 0))
            if key == "Faction":
                text_rect = text_surface.get_rect(midleft=(value, 60 * self.screen_scale[1]))
            else:
                text_rect = text_surface.get_rect(midright=(value, 60 * self.screen_scale[1]))
            self.image.blit(text_surface, text_rect)

        # draw.line(self.image, "black", )
        y = 150 * self.screen_scale[1]
        for team, coa in enumerate(team_coa):
            new_coa = smoothscale(coa, (50 * self.screen_scale[0], 50 * self.screen_scale[1]))
            coa_rect = new_coa.get_rect(midleft=(10 * self.screen_scale[0], y))
            self.image.blit(new_coa, coa_rect)
            for key, value in self.result_text_x.items():
                try:
                    text_surface = self.header_font.render(str(stat[key][team + 1]), True, (0, 0, 0))
                except IndexError:  # no number in list, e.g., no wounded troops
                    text_surface = self.header_font.render(str(0), True, (0, 0, 0))
                if key == "Faction":
                    text_rect = text_surface.get_rect(midleft=(65 * self.screen_scale[0], y))
                else:
                    text_rect = text_surface.get_rect(midright=(value, y))
                self.image.blit(text_surface, text_rect)

            y += 150 * self.screen_scale[1]

        self.rect = self.image.get_rect(center=self.pos)


class AimTarget(Sprite):
    aim_images = None

    def __init__(self, who):
        self._layer = 2000000
        Sprite.__init__(self, self.containers)
        self.who = who
        self.who.shoot_line = self
        self.pos = Vector2(self.who.pos)
        self.base_target_pos = None
        self.can_shoot = [False, False]

        self.image = self.aim_images[0]
        self.rect = self.image.get_rect(center=(0, 0))

    def update(self, base_target_pos, target_pos, can_shoot):
        if not self.who.alive:
            self.who.shoot_line = None
            self.kill()
        else:
            if self.can_shoot != can_shoot:
                self.can_shoot = can_shoot
                if False not in self.can_shoot:  # both weapon can shoot
                    self.image = self.aim_images[0]
                elif True not in self.can_shoot:  # no weapon can shoot use empty image
                    self.image = self.aim_images[3]
                else:
                    if self.can_shoot[0]:  # only main weapon can shoot
                        self.image = self.aim_images[1]
                    else:  # only sub weapon can shoot
                        self.image = self.aim_images[2]
            if self.pos != target_pos:
                self.base_target_pos = base_target_pos
                self.pos = target_pos
                self.rect.center = self.pos

    def delete(self):
        self.who.shoot_line = None
        self.kill()


class SkillAimTarget(AimTarget):
    base_image = Surface((500, 500), SRCALPHA)
    draw.circle(base_image, (0, 0, 0, 200), (base_image.get_width() / 2, base_image.get_height() / 2),
                base_image.get_width() / 2, width=20)
    draw.circle(base_image, (125, 125, 125, 200), (base_image.get_width() / 2, base_image.get_height() / 2),
                base_image.get_width() / 4, width=20)

    def __init__(self, who, aoe_size):
        AimTarget.__init__(who)
        self.image = smoothscale(self.base_image,
                                 (aoe_size * 5 * self.screen_scale[0],
                                  aoe_size * 5 * self.screen_scale[1]))
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, base_target_pos, target_pos, can_shoot):
        if not self.who.alive:
            self.who.shoot_line = None
            self.kill()

        if self.pos != target_pos:
            self.base_target_pos = base_target_pos
            self.pos = target_pos
            self.rect.center = self.pos


class SpriteIndicator(Sprite):
    def __init__(self, image, who, layer=1):
        """Indicator for unit status effect sprite"""
        self.who = who
        self._layer = layer
        Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(center=self.who.pos)


class Profiler(cProfile.Profile, UIBattle):

    def __init__(self):
        UIBattle.__init__(self, player_interact=False)
        self.size = (900, 550)
        self.image = Surface(self.size)
        self.rect = Rect((0, 0, *self.size))
        self.font = Font(self.ui_font["main_button"], 16)
        self._layer = 12
        self.visible = False

    def refresh(self):
        import io
        from pstats import Stats

        # There should be a way to hide/show something using the sprite api but
        # I didn't get it to work so I did this solution instead

        if self.visible:
            self.image = Surface(self.size)
            s_io = io.StringIO()
            stats = Stats(self, stream=s_io)
            stats.sort_stats('tottime').print_stats(20)
            info_str = s_io.getvalue()
            self.enable()  # profiler must be re-enabled after get stats
            self.image.fill(0x112233)
            self.image.blit(self.font.render("press F7 to clear times", True, Color("white")), (0, 0))
            for e, line in enumerate(info_str.split("\n"), 1):
                self.image.blit(self.font.render(line, True, Color("white")), (0, e * 20))
        else:
            self.image = Surface((1, 1))

    def switch_show_hide(self):
        self.visible = not self.visible
        self.refresh()
