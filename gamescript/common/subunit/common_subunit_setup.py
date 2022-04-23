import math
import pygame


def skill_convert(self, skill_list, add_charge_skill=False):
    """
    Convert skill id list to dict with its stat
    :param self: Subunit object
    :param skill_list: List of skill id
    :param add_charge_skill: Add charge skill to dict or not
    :return: Dict of skill with id as key and stat as value
    """
    skill_dict = list(set(skill_list))
    skill_dict = {x: self.troop_data.skill_list[x].copy() for x in skill_dict if
                  x != 0 and x in self.troop_data.skill_list}  # grab skill stat into dict
    if add_charge_skill:
        skill_dict[0] = self.troop_data.skill_list[self.charge_skill].copy()  # add charge skill with key 0
    skill_dict = {skill: skill_dict[skill] for skill in skill_dict if skill == 0 or   # keep skill if class match
                  (skill != 0 and (self.troop_data.skill_list[skill]["Troop Type"] == 0 or
                                   self.troop_data.skill_list[skill]["Troop Type"] == self.subunit_type + 1))}
    return skill_dict


def process_trait_skill(self):
    """
    Process subunit traits and skills into dict with their stat
    :param self: Subunit object
    """
    self.trait += self.armour_data.armour_list[self.armour_gear[0]]["Trait"]  # Apply armour trait to subunit
    self.trait = list(set([trait for trait in self.trait if trait != 0]))  # remove empty and duplicate traits
    if len(self.trait) > 0:
        self.trait = {x: self.troop_data.trait_list[x] for x in self.trait if
                      x in self.troop_data.trait_list}  # Any trait not available in ruleset will be ignored
        self.add_trait()

    self.troop_skill = [skill for skill in self.troop_skill if skill != 0 and
                        (self.troop_data.skill_list[skill]["Troop Type"] == 0 or
                         self.troop_data.skill_list[skill]["Troop Type"] == self.subunit_type + 1)]  # keep matched

    for weapon_set in self.weapon_skill:
        for weapon in self.weapon_skill[weapon_set]:
            skill = self.weapon_skill[weapon_set][weapon]
            if skill != 0 and (self.troop_data.skill_list[skill]["Troop Type"] != 0 and
                               self.troop_data.skill_list[skill]["Troop Type"] != self.subunit_type + 1):
                self.weapon_skill[weapon_set][weapon] = 0  # remove unmatch class skill
            else:
                self.skill.append(skill)
    self.skill = skill_convert(self, self.skill, add_charge_skill=True)


def create_inspect_sprite(self):
    """
    Create subunit sprite for furthest zoom and inspect ui
    :param self: Subunit object
    :return: Dict with sprites
    """
    # v Subunit image sprite in inspect ui and far zoom
    ui_image = self.unit_ui_images["ui_squad_player.png"].copy()  # Subunit block blue colour for team1 for shown in inspect ui
    if self.team == 2:
        ui_image = self.unit_ui_images["ui_squad_enemy.png"].copy()  # red colour

    image = pygame.Surface((ui_image.get_width() + 10, ui_image.get_height() + 10), pygame.SRCALPHA)  # subunit sprite image
    pygame.draw.circle(image, self.unit.colour, (image.get_width() / 2, image.get_height() / 2), ui_image.get_width() / 2)

    if self.subunit_type == 2:  # cavalry draw line on block
        pygame.draw.line(ui_image, (0, 0, 0), (0, 0), (ui_image.get_width(), ui_image.get_height()), 2)
        radian = 45 * 0.0174532925  # top left
        start = (
            image.get_width() / 3 * math.cos(radian),
            image.get_width() / 3 * math.sin(radian))  # draw line from 45 degree in circle
        radian = 225 * 0.0174532925  # bottom right
        end = (image.get_width() * -math.cos(radian), image.get_width() * -math.sin(radian))  # draw line to 225 degree in circle
        pygame.draw.line(image, (0, 0, 0), start, end, 2)

    selected_image = pygame.Surface((ui_image.get_width(), ui_image.get_height()), pygame.SRCALPHA)
    pygame.draw.circle(selected_image, (255, 255, 255, 150), (ui_image.get_width() / 2, ui_image.get_height() / 2), ui_image.get_width() / 2)
    pygame.draw.circle(selected_image, (0, 0, 0, 255), (ui_image.get_width() / 2, ui_image.get_height() / 2), ui_image.get_width() / 2, 1)
    selected_image_original = selected_image.copy()
    selected_image_original2 = selected_image.copy()
    selected_image_rect = selected_image.get_rect(topleft=(0, 0))

    far_image = image.copy()
    pygame.draw.circle(far_image, (0, 0, 0), (far_image.get_width() / 2, far_image.get_height() / 2),
                       far_image.get_width() / 2, 4)
    far_selected_image = selected_image.copy()
    pygame.draw.circle(far_selected_image, (0, 0, 0), (far_selected_image.get_width() / 2, far_selected_image.get_height() / 2),
                       far_selected_image.get_width() / 2, 4)

    dim = pygame.Vector2(image.get_width() * 1 / self.max_zoom, image.get_height() * 1 / self.max_zoom)
    far_image = pygame.transform.scale(far_image, (int(dim[0]), int(dim[1])))
    far_selected_image = pygame.transform.scale(far_selected_image, (int(dim[0]), int(dim[1])))

    block = ui_image.copy()  # image shown in inspect ui as square instead of circle
    # ^ End subunit base sprite

    # v health and stamina related
    health_image_list = [self.unit_ui_images["ui_health_circle_100.png"], self.unit_ui_images["ui_health_circle_75.png"],
                         self.unit_ui_images["ui_health_circle_50.png"], self.unit_ui_images["ui_health_circle_25.png"],
                         self.unit_ui_images["ui_health_circle_0.png"]]
    stamina_image_list = [self.unit_ui_images["ui_stamina_circle_100.png"], self.unit_ui_images["ui_stamina_circle_75.png"],
                          self.unit_ui_images["ui_stamina_circle_50.png"], self.unit_ui_images["ui_stamina_circle_25.png"],
                          self.unit_ui_images["ui_stamina_circle_0.png"]]

    health_image = self.unit_ui_images["ui_health_circle_100.png"]
    health_image_rect = health_image.get_rect(center=image.get_rect().center)  # for battle sprite
    health_block_rect = health_image.get_rect(center=block.get_rect().center)  # for ui sprite
    image.blit(health_image, health_image_rect)
    block.blit(health_image, health_block_rect)

    stamina_image = self.unit_ui_images["ui_stamina_circle_100.png"]
    stamina_image_rect = stamina_image.get_rect(center=image.get_rect().center)  # for battle sprite
    stamina_block_rect = stamina_image.get_rect(center=block.get_rect().center)  # for ui sprite
    image.blit(stamina_image, stamina_image_rect)
    block.blit(stamina_image, stamina_block_rect)
    # ^ End health and stamina

    # v weapon class icon in middle circle or leader
    image1 = self.weapon_data.images[self.weapon_data.weapon_list[self.primary_main_weapon[0]]["ImageID"]]  # image on subunit sprite
    if type(self.troop_id) != int and "h" in self.troop_id:
        try:
            image1 = self.leader_data.images[self.troop_id.replace("h", "") + ".png"].copy()
        except KeyError:
            image1 = self.leader_data.images["9999999.png"].copy()
        image1 = pygame.transform.scale(image1.copy(), stamina_image.get_size())
    image_rect = image1.get_rect(center=image.get_rect().center)
    image.blit(image1, image_rect)

    image_rect = image1.get_rect(center=block.get_rect().center)
    block.blit(image1, image_rect)
    block_original = block.copy()

    corner_image_rect = self.unit_ui_images["ui_squad_combat.png"].get_rect(
        center=block.get_rect().center)  # red corner when take melee_dmg shown in image block
    # ^ End weapon icon

    inspect_image_original = image.copy()  # original for rotate
    inspect_image_original2 = image.copy()  # original2 for saving original not clicked
    inspect_image_original3 = image.copy()  # original3 for saving original zoom level

    return {"image": image, "original": inspect_image_original, "original2": inspect_image_original2, "original3": inspect_image_original3,
            "block": block, "block_original": block_original, "selected": selected_image, "selected_rect": selected_image_rect,
            "selected_original": selected_image_original, "selected_original2": selected_image_original2,
            "far": far_image, "far_selected": far_selected_image, "health_rect": health_image_rect, "health_block_rect": health_block_rect,
            "stamina_rect": stamina_image_rect, "stamina_block_rect": stamina_block_rect,
            "corner_rect": corner_image_rect, "health_list": health_image_list, "stamina_list": stamina_image_list}
