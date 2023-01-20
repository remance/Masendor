import math

import pygame
from gamescript import unit

team_colour = unit.team_colour


def create_subunit_sprite(self, inspect_subunit_size, sprite_troop_size):
    """
    Create subunit sprite for furthest zoom and inspect ui
    :param self: Subunit object
    :param inspect_subunit_size: Size of subunit inspect sprite used to created sprite
    :param sprite_troop_size: Size of troop sprite based on troop size
    :return: Dict with sprites
    """
    # Subunit image sprite in inspect ui and far zoom
    colour = team_colour[self.team]
    ui_image = pygame.Surface(inspect_subunit_size, pygame.SRCALPHA)
    ui_image.fill((0, 0, 0))
    pygame.draw.rect(ui_image, (255, 255, 255), (ui_image.get_width() / 20, ui_image.get_height() / 20,
                                                 ui_image.get_width() - (ui_image.get_width() / 10),
                                                 ui_image.get_height() - (ui_image.get_height() / 10)),
                     width=int(ui_image.get_width() / 20))
    pygame.draw.rect(ui_image, colour, (ui_image.get_width() / 8, ui_image.get_height() / 8,
                                        ui_image.get_width() - (ui_image.get_width() / 4),
                                        ui_image.get_height() - (ui_image.get_height() / 4)))

    if sprite_troop_size > 1:
        ui_image = pygame.transform.smoothscale(ui_image, (ui_image.get_width() * sprite_troop_size,
                                                           ui_image.get_height() * sprite_troop_size))

    image = pygame.Surface((ui_image.get_width(), ui_image.get_height()),
                           pygame.SRCALPHA)  # subunit sprite image
    pygame.draw.circle(image, self.unit.colour, (image.get_width() / 2, image.get_height() / 2),
                       ui_image.get_width() / 2)

    if self.subunit_type == 2:  # cavalry draw line on block
        radian = 45 * 0.0174532925  # top left
        start = (
            image.get_width() / 3 * math.cos(radian),
            image.get_width() / 3 * math.sin(radian))  # draw line from 45 degree in circle
        radian = 225 * 0.0174532925  # bottom right
        end = (image.get_width() * -math.cos(radian),
               image.get_width() * -math.sin(radian))  # draw line to 225 degree in circle
        pygame.draw.line(image, (0, 0, 0), start, end, int(ui_image.get_width() / 20))

    selected_image = pygame.Surface((ui_image.get_width(), ui_image.get_height()), pygame.SRCALPHA)
    pygame.draw.circle(selected_image, (255, 255, 255, 150), (ui_image.get_width() / 2, ui_image.get_height() / 2),
                       ui_image.get_width() / 2)
    pygame.draw.circle(selected_image, (0, 0, 0, 255), (ui_image.get_width() / 2, ui_image.get_height() / 2),
                       ui_image.get_width() / 2, 1)
    selected_image_original = selected_image.copy()
    selected_image_original2 = selected_image.copy()
    selected_image_rect = selected_image.get_rect(topleft=(0, 0))

    far_image = image.copy()
    pygame.draw.circle(far_image, (0, 0, 0), (far_image.get_width() / 2, far_image.get_height() / 2),
                       far_image.get_width() / 2, 4)
    far_selected_image = selected_image.copy()
    pygame.draw.circle(far_selected_image, (0, 0, 0),
                       (far_selected_image.get_width() / 2, far_selected_image.get_height() / 2),
                       far_selected_image.get_width() / 2, 4)

    dim = pygame.Vector2(image.get_width() / self.max_camera_zoom, image.get_height() / self.max_camera_zoom)
    far_image = pygame.transform.smoothscale(far_image, (int(dim[0]), int(dim[1])))
    far_selected_image = pygame.transform.smoothscale(far_selected_image, (int(dim[0]), int(dim[1])))

    block = ui_image.copy()  # image shown in inspect ui as square instead of circle

    # Health and stamina related
    if sprite_troop_size == 1:
        health_image_list = (self.subunit_ui_images["health_circle_100"], self.subunit_ui_images["health_circle_75"],
                             self.subunit_ui_images["health_circle_50"], self.subunit_ui_images["health_circle_25"],
                             self.subunit_ui_images["health_circle_0"])
        stamina_image_list = (self.subunit_ui_images["stamina_circle_100"], self.subunit_ui_images["stamina_circle_75"],
                              self.subunit_ui_images["stamina_circle_50"], self.subunit_ui_images["stamina_circle_25"],
                              self.subunit_ui_images["stamina_circle_0"])
    elif sprite_troop_size != 1:  # use scaled bar image to subunit sprite size
        health_image_list = (self.subunit_ui_images["health" + str(sprite_troop_size)]["health_circle_100"],
                             self.subunit_ui_images["health" + str(sprite_troop_size)]["health_circle_75"],
                             self.subunit_ui_images["health" + str(sprite_troop_size)]["health_circle_50"],
                             self.subunit_ui_images["health" + str(sprite_troop_size)]["health_circle_25"],
                             self.subunit_ui_images["health" + str(sprite_troop_size)]["health_circle_0"])
        stamina_image_list = (self.subunit_ui_images["stamina" + str(sprite_troop_size)]["stamina_circle_100"],
                              self.subunit_ui_images["stamina" + str(sprite_troop_size)]["stamina_circle_75"],
                              self.subunit_ui_images["stamina" + str(sprite_troop_size)]["stamina_circle_50"],
                              self.subunit_ui_images["stamina" + str(sprite_troop_size)]["stamina_circle_25"],
                              self.subunit_ui_images["stamina" + str(sprite_troop_size)]["stamina_circle_0"])

    health_image = health_image_list[0]
    health_image_rect = health_image.get_rect(center=image.get_rect().center)  # for battle sprite
    health_block_rect = health_image.get_rect(center=block.get_rect().center)  # for ui sprite

    stamina_image = stamina_image_list[0]
    stamina_image_rect = stamina_image.get_rect(center=image.get_rect().center)  # for battle sprite
    stamina_block_rect = stamina_image.get_rect(center=block.get_rect().center)  # for ui sprite

    # Weapon class icon in middle circle or leader (hero) portrait

    if type(self.troop_id) != int and "h" in self.troop_id:
        try:
            image1 = self.leader_data.images[self.troop_id.replace("h", "") + ""].copy()
        except KeyError:
            image1 = self.leader_data.images["9999999"].copy()
        image1 = pygame.transform.smoothscale(image1,
                                              (stamina_image.get_width() * 0.65, stamina_image.get_height() * 0.65))
    else:
        image1 = self.troop_data.weapon_icon[
            self.troop_data.weapon_list[self.primary_main_weapon[0]]["ImageID"]]  # image on subunit sprite
        if sprite_troop_size > 1:
            new_size = self.subunit_ui_images["stamina" + str(sprite_troop_size)]["stamina_circle_100"].get_width() / \
                       self.subunit_ui_images["stamina_circle_100"].get_width()
            image1 = pygame.transform.smoothscale(image1,
                                                  (image1.get_width() * new_size, image1.get_height() * new_size))

    image_rect = image1.get_rect(center=image.get_rect().center)
    image.blit(image1, image_rect)
    image_rect = image1.get_rect(center=block.get_rect().center)
    block.blit(image1, image_rect)

    image.blit(health_image, health_image_rect)  # blit hp and stamina bar after weapon/portrait
    block.blit(health_image, health_block_rect)
    image.blit(stamina_image, stamina_image_rect)
    block.blit(stamina_image, stamina_block_rect)

    block_original = block.copy()

    corner_image_rect = block.get_rect(center=block.get_rect().center)

    inspect_image_original = image.copy()  # original for rotate
    inspect_image_original2 = image.copy()  # original2 for saving original not clicked
    inspect_image_original3 = image.copy()  # original3 for saving original zoom level

    return {"image": image, "original": inspect_image_original, "original2": inspect_image_original2,
            "original3": inspect_image_original3,
            "block": block, "block_original": block_original, "selected": selected_image,
            "selected_rect": selected_image_rect,
            "selected_original": selected_image_original, "selected_original2": selected_image_original2,
            "far": far_image, "far_selected": far_selected_image, "health_rect": health_image_rect,
            "health_block_rect": health_block_rect,
            "stamina_rect": stamina_image_rect, "stamina_block_rect": stamina_block_rect,
            "corner_rect": corner_image_rect, "health_list": health_image_list, "stamina_list": stamina_image_list}
