import math
import numpy as np

import pygame

def add_weapon_stat(self):
    """Combine weapon stat"""
    weapon_reload = 0
    base_range = []
    arrow_speed = []

    for index, weapon in enumerate([self.primary_main_weapon, self.primary_sub_weapon, self.secondary_main_weapon, self.secondary_sub_weapon]):
        if self.weapon_list.weapon_list[weapon[0]]["Range"] == 0:  # melee weapon if range 0
            self.melee_dmg[0] += self.weapon_list.weapon_list[weapon[0]]["Minimum Damage"] * \
                                 self.weapon_list.quality[weapon[1]] / (index + 1)
            self.melee_dmg[1] += self.weapon_list.weapon_list[weapon[0]]["Maximum Damage"] * \
                                 self.weapon_list.quality[weapon[1]] / (index + 1)

            self.melee_penetrate += self.weapon_list.weapon_list[weapon[0]]["Armour Penetration"] * \
                                    self.weapon_list.quality[weapon[1]] / (index + 1)
            self.melee_speed += self.weapon_list.weapon_list[weapon[0]]["Speed"] / (index + 1)
        else:
            self.range_dmg[0] += self.weapon_list.weapon_list[weapon[0]]["Minimum Damage"] * \
                                 self.weapon_list.quality[weapon[1]]
            self.range_dmg[1] += self.weapon_list.weapon_list[weapon[0]]["Maximum Damage"] * \
                                 self.weapon_list.quality[weapon[1]]

            self.range_penetrate += self.weapon_list.weapon_list[weapon[0]]["Armour Penetration"] * \
                                    self.weapon_list.quality[weapon[1]] / (index + 1)
            self.magazine_size += self.weapon_list.weapon_list[weapon[0]][
                "Magazine"]  # can shoot how many times before have to reload
            weapon_reload += self.weapon_list.weapon_list[weapon[0]]["Speed"] * (index + 1)
            base_range.append(self.weapon_list.weapon_list[weapon[0]]["Range"] * self.weapon_list.quality[weapon[1]])
            arrow_speed.append(self.weapon_list.weapon_list[weapon[0]]["Travel Speed"])  # travel speed of range attack
        self.base_melee_def += self.weapon_list.weapon_list[weapon[0]]["Defense"] / (index + 1)
        self.base_range_def += self.weapon_list.weapon_list[weapon[0]]["Defense"] / (index + 1)
        self.skill += self.weapon_list.weapon_list[weapon[0]]["Skill"]
        self.trait += self.weapon_list.weapon_list[weapon[0]]["Trait"]
        self.weight += self.weapon_list.weapon_list[weapon[0]]["Weight"]

        if base_range != []:
            self.base_range = np.mean(base_range)  # use average range
        if arrow_speed != []:
            self.arrow_speed = np.mean(arrow_speed)  # use average speed
        else:
            self.arrow_speed = 0
        self.base_reload = weapon_reload + ((50 - self.base_reload) * weapon_reload / 100)  # final reload speed from weapon and skill


def add_mount_stat(self):
    """Combine mount stat"""
    self.base_charge_def = 25  # charge defence only 25 for cav
    self.base_speed = (
            self.mount["Speed"] + self.mount_grade["Speed Bonus"])  # use mount base speed instead
    self.troop_health += (self.mount["Health Bonus"] * self.mount_grade["Health Effect"]) + \
                         self.mount_armour["Health"]  # Add mount health to the troop health
    self.base_charge += (self.mount["Charge Bonus"] +
                         self.mount_grade["Charge Bonus"])  # Add charge power of mount to troop
    self.base_morale += self.mount_grade["Morale Bonus"]
    self.base_discipline += self.mount_grade["Discipline Bonus"]
    self.stamina += self.mount["Stamina Bonus"]
    self.trait += self.mount["Trait"]  # Apply mount trait to subunit
    self.subunit_type = 2  # If subunit has a mount, count as cav for command buff
    self.feature_mod = 4  # the starting column in unit_terrainbonus of cavalry


def create_sprite(self):
    # v Subunit image sprite
    image = self.images["ui_squad_player.png"].copy()  # Subunit block blue colour for team1 for shown in inspect ui
    if self.team == 2:
        image = self.images["ui_squad_enemy.png"].copy()  # red colour

    sprite_image = pygame.Surface((image.get_width() + 10, image.get_height() + 10), pygame.SRCALPHA)  # subunit sprite image
    pygame.draw.circle(sprite_image, self.unit.colour, (sprite_image.get_width() / 2, sprite_image.get_height() / 2), image.get_width() / 2)

    if self.subunit_type == 2:  # cavalry draw line on block
        pygame.draw.line(image, (0, 0, 0), (0, 0), (image.get_width(), image.get_height()), 2)
        radian = 45 * 0.0174532925  # top left
        start = (
            sprite_image.get_width() / 3 * math.cos(radian), sprite_image.get_width() / 3 * math.sin(radian))  # draw line from 45 degree in circle
        radian = 225 * 0.0174532925  # bottom right
        end = (sprite_image.get_width() * -math.cos(radian), sprite_image.get_width() * -math.sin(radian))  # draw line to 225 degree in circle
        pygame.draw.line(sprite_image, (0, 0, 0), start, end, 2)

    selected_image = pygame.Surface((image.get_width(), image.get_height()), pygame.SRCALPHA)
    pygame.draw.circle(selected_image, (255, 255, 255, 150), (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2)
    pygame.draw.circle(selected_image, (0, 0, 0, 255), (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2, 1)
    selected_image_original = selected_image.copy()
    selected_image_original2 = selected_image.copy()
    selected_image_rect = selected_image.get_rect(topleft=(0, 0))

    far_image = sprite_image.copy()
    pygame.draw.circle(far_image, (0, 0, 0), (far_image.get_width() / 2, far_image.get_height() / 2),
                       far_image.get_width() / 2, 4)
    far_selected_image = selected_image.copy()
    pygame.draw.circle(far_selected_image, (0, 0, 0), (far_selected_image.get_width() / 2, far_selected_image.get_height() / 2),
                       far_selected_image.get_width() / 2, 4)

    scale_width = sprite_image.get_width() * 1 / self.max_zoom
    scale_height = sprite_image.get_height() * 1 / self.max_zoom
    dim = pygame.Vector2(scale_width, scale_height)
    far_image = pygame.transform.scale(far_image, (int(dim[0]), int(dim[1])))
    far_selected_image = pygame.transform.scale(far_selected_image, (int(dim[0]), int(dim[1])))

    block = image.copy()  # image shown in inspect ui as square instead of circle
    # ^ End subunit base sprite

    # v health and stamina related
    health_image_list = [self.images["ui_health_circle_100.png"], self.images["ui_health_circle_75.png"],
                              self.images["ui_health_circle_50.png"], self.images["ui_health_circle_25.png"],
                              self.images["ui_health_circle_0.png"]]
    stamina_image_list = [self.images["ui_stamina_circle_100.png"], self.images["ui_stamina_circle_75.png"],
                               self.images["ui_stamina_circle_50.png"], self.images["ui_stamina_circle_25.png"],
                               self.images["ui_stamina_circle_0.png"]]

    health_image = self.images["ui_health_circle_100.png"]
    health_image_rect = health_image.get_rect(center=sprite_image.get_rect().center)  # for battle sprite
    health_block_rect = health_image.get_rect(center=block.get_rect().center)  # for ui sprite
    sprite_image.blit(health_image, health_image_rect)
    block.blit(health_image, health_block_rect)

    stamina_image = self.images["ui_stamina_circle_100.png"]
    stamina_image_rect = stamina_image.get_rect(center=sprite_image.get_rect().center)  # for battle sprite
    stamina_block_rect = stamina_image.get_rect(center=block.get_rect().center)  # for ui sprite
    sprite_image.blit(stamina_image, stamina_image_rect)
    block.blit(stamina_image, stamina_block_rect)
    # ^ End health and stamina

    # v weapon class icon in middle circle
    image1 = self.weapon_list.images[self.weapon_list.weapon_list[self.primary_main_weapon[0]]["ImageID"]]  # image on subunit sprite
    image1_rect = image1.get_rect(center=sprite_image.get_rect().center)
    sprite_image.blit(image1, image1_rect)

    image1_rect = image1.get_rect(center=block.get_rect().center)
    block.blit(image1, image1_rect)
    block_original = block.copy()

    corner_image_rect = self.images["ui_squad_combat.png"].get_rect(center=block.get_rect().center)  # red corner when take melee_dmg shown in image block
    # ^ End weapon icon

    image_original = sprite_image.copy()  # original for rotate
    image_original2 = sprite_image.copy()  # original2 for saving original not clicked
    image_original3 = sprite_image.copy()  # original3 for saving original zoom level

    return {"sprite": sprite_image, "original": image_original, "original2": image_original2, "original3": image_original3,
            "block": block, "block_original": block_original, "selected": selected_image, "selected_rect": selected_image_rect,
            "selected_original": selected_image_original, "selected_original2": selected_image_original2,
            "far": far_image, "far_selected": far_selected_image, "health_rect": health_image_rect, "health_block_rect": health_block_rect,
            "stamina_rect": stamina_image_rect, "stamina_block_rect": stamina_block_rect,
            "corner_rect": corner_image_rect, "health_list": health_image_list, "stamina_list": stamina_image_list}
