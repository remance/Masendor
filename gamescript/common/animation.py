import time
import math
import pygame

from PIL import Image, ImageOps, ImageFilter, ImageEnhance

from gamescript import readstat
from gamescript.common import utility

stat_convert = readstat.stat_convert
rotation_xy = utility.rotation_xy

default_sprite_size = (200, 200)


def play_animation(self, scale, speed):
    if time.time() - self.first_time >= speed:
        if self.show_frame < len(self.current_animation):
            self.show_frame += 1
        self.first_time = time.time()
        if self.show_frame >= len(self.current_animation):  # TODO add property
            self.show_frame = 0

    if scale == 1:
        self.image = self.current_animation[self.show_frame]["sprite"]
    else:
        self.image = self.current_animation[self.show_frame]["sprite"].copy()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * scale, self.image.get_height() * scale))

def apply_colour(surface, colour=None, colour_list=None):
    """Colorise body part sprite"""
    if colour is not None and colour != "none":
        max_colour = 255  # - (colour[0] + colour[1] + colour[2])
        if colour_list is not None:
            mid_colour = colour_list[colour]
        else:
            mid_colour = [int(c - ((max_colour - c) / 2)) for c in colour]

        size = (surface.get_width(), surface.get_height())
        data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
        surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
        alpha = surface.split()[-1]  # save alpha
        surface = surface.convert("L")  # convert to grey scale for colourise
        surface = ImageOps.colorize(surface, black="black", mid=mid_colour, white=colour).convert("RGB")
        surface.putalpha(alpha)  # put back alpha
        surface = surface.tobytes()
        surface = pygame.image.fromstring(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface


def grab_face_part(pool, race, side, part, part_check, part_default):
    """For creating body part like eye or mouth in animation that accept any part (1) so use default instead"""
    if part_check == 1:  # any part
        surface = pool[race][side][part][part_default].copy()
    else:
        surface = pool[race][side][part][part_check].copy()
    return surface


def generate_head(p, animation_part_list, body_part_list, troop_sprite_list, pool, armour_pool, armour, hair_colour_list, skin_colour_list):
    head_sprite_surface = None
    try:
        head_race = body_part_list[0]
        head_side = body_part_list[1]
        head = pool[head_race][head_side]["head"][body_part_list[2]].copy()
        head_sprite_surface = pygame.Surface((head.get_width(), head.get_height()), pygame.SRCALPHA)
        head_rect = head.get_rect(midtop=(head_sprite_surface.get_width() / 2, 0))
        head_sprite_surface.blit(head, head_rect)
        face = [pool[head_race][head_side]["eyebrow"][troop_sprite_list[p + "_eyebrow"][0]].copy(),
                   grab_face_part(pool, head_race, head_side, "eye", animation_part_list[p + "_eye"], troop_sprite_list[p + "_eye"][0]),
                   pool[head_race][head_side]["beard"][troop_sprite_list[p + "_beard"][0]].copy(),
                   grab_face_part(pool, head_race, head_side, "mouth", animation_part_list[p + "_mouth"], troop_sprite_list[p + "_mouth"])]

        # if skin != "white":
        #     face[0] = self.apply_colour(face[0], skin_colour)

        face[0] = apply_colour(face[0], troop_sprite_list[p + "_hair"][1], hair_colour_list)
        face[1] = apply_colour(face[1], troop_sprite_list[p + "_eye"][1], hair_colour_list)
        face[2] = apply_colour(face[2], troop_sprite_list[p + "_beard"][1], hair_colour_list)

        head_sprite_surface = pygame.Surface((face[0].get_width(), face[0].get_height()), pygame.SRCALPHA)
        head_rect = head.get_rect(midtop=(head_sprite_surface.get_width() / 2, 0))
        head_sprite_surface.blit(head, head_rect)

        for index, item in enumerate(face):
            rect = item.get_rect(topleft=(0, 0))
            head_sprite_surface.blit(item, rect)
    except KeyError:  # some head direction show no face
        pass
    except TypeError:  # empty
        pass

    if troop_sprite_list[p + "_head"] != "none":
        gear_image = armour_pool[head_race][armour][troop_sprite_list[p + "_head"]][head_side]["helmet"][body_part_list[2]]
        rect = gear_image.get_rect(center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
        head_sprite_surface.blit(gear_image, rect)

    return head_sprite_surface


def generate_body(part, body_part_list, troop_sprite_list, sprite_pool, armour_sprite_pool=None, colour=None,
                  weapon=None, armour=None, colour_list=None):
    # main/body first
    sprite_image = None
    try:
        if "weapon" in part:
            weapon_part = part[:3] + "primary_" + part[3:]  # primary set
            if weapon_part == 1:
                weapon_part = part[:3] + "secondary_" + part[3:]  # secondary set
            part_name = weapon[1][0]  # main weapon
            if "sub" in part:
                part_name = weapon[1][1]  # sub weapon
            if part_name is not None and part_name != "Unarmed":
                sprite_image = sprite_pool[part_name][troop_sprite_list[weapon_part]][body_part_list[0]][body_part_list[1]].copy()
        else:
            new_part_name = part
            if "p1_" in part or "p2_" in part:
                part_name = part[3:]  # remove p1_ or p2_ to get part name
                new_part_name = part_name
            if "special" in part:
                part_name = "special"
            if "r_" in part_name[0:2] or "l_" in part_name[0:2]:
                new_part_name = part_name[2:]  # remove side
            sprite_image = sprite_pool[body_part_list[0]][body_part_list[1]][new_part_name][body_part_list[2]].copy()

        if colour is not None:  # apply skin colour, maybe add for armour colour later
            sprite_image = apply_colour(sprite_image, colour, colour_list)

        # add armour if there is one
        if armour is not None and armour != "None":
            part_name = part
            if "p1_" in part or "p2_" in part:
                part_name = part[3:]  # remove p1_ or p2_ to get part name
            gear_image = armour_sprite_pool[body_part_list[0]][armour][troop_sprite_list[part]][body_part_list[1]][part_name][body_part_list[2]]
            new_sprite_image = pygame.Surface(gear_image.get_size(), pygame.SRCALPHA)  # create sprite based on armour size since it can be larger than body part
            rect = sprite_image.get_rect(center=(new_sprite_image.get_width() / 2, new_sprite_image.get_height() / 2))
            new_sprite_image.blit(sprite_image, rect)
            rect = gear_image.get_rect(center=(new_sprite_image.get_width() / 2, new_sprite_image.get_height() / 2))
            new_sprite_image.blit(gear_image, rect)
            sprite_image = new_sprite_image
    except KeyError:  # sprite simply not existed
        pass

    return sprite_image


def make_sprite(size, animation_part_list, troop_sprite_list, body_sprite_pool, weapon_sprite_pool, armour_sprite_pool, effect_sprite_pool, animation_property,
                weapon_joint_list, weapon, armour, hair_colour_list, skin_colour_list):
    frame_property = animation_part_list["frame_property"]

    surface = pygame.Surface(default_sprite_size, pygame.SRCALPHA)  # default size will scale down later

    except_list = ["eye", "mouth", "size", "property"]
    pose_layer_list = {k: v[7] for k, v in animation_part_list.items() if v != [0] and any(ext in k for ext in except_list) is False}  # layer list
    pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
    for index, layer in enumerate(pose_layer_list):
        part = animation_part_list[layer]
        new_part = part.copy()
        if "p1_" in layer:
            this_armour = armour[0]
        elif "p2_" in layer:
            this_armour = armour[1]
        if "head" in layer:
            image_part = generate_head(layer[:2], animation_part_list, part[0:3], troop_sprite_list, body_sprite_pool, armour_sprite_pool,
                                       this_armour, hair_colour_list, skin_colour_list)
        elif "weapon" in layer:
            new_part.insert(2, "Dummy")  # insert dummy value for weapon list so can use indexing similar as other part
            image_part = generate_body(layer, part[0:2], troop_sprite_list, weapon_sprite_pool, weapon=weapon)
        elif "effect" in layer:
            image_part = generate_body(layer, part[0:3], troop_sprite_list, effect_sprite_pool)
        else:  # other body part
            image_part = generate_body(layer, part[0:3], troop_sprite_list, body_sprite_pool, armour_sprite_pool=armour_sprite_pool,
                                       colour_list=skin_colour_list, armour=this_armour)
        if image_part is not None:  # skip for empty image
            target = (new_part[3], new_part[4])
            angle = new_part[5]
            flip = new_part[6]
            scale = new_part[8]

            part_rotated = image_part.copy()
            if scale != 1:
                part_rotated = pygame.transform.scale(part_rotated, (part_rotated.get_width() * scale,
                                                                     part_rotated.get_height() * scale))
            if flip != 0:
                if flip == 1:
                    part_rotated = pygame.transform.flip(part_rotated, True, False)
                elif flip == 2:
                    part_rotated = pygame.transform.flip(part_rotated, False, True)
                elif flip == 3:
                    part_rotated = pygame.transform.flip(part_rotated, True, True)
            if angle != 0:
                part_rotated = pygame.transform.rotate(part_rotated, angle)  # rotate part sprite

            center = pygame.Vector2(part_rotated.get_width() / 2, part_rotated.get_height() / 2)
            new_target = target  # - pos_different  # find new center point

            if "weapon" in layer:  # only weapon use joint to calculate position
                part_name = weapon[1][0]  # main weapon
                if "sub" in part:
                    part_name = weapon[1][1]  # sub weapon
                check_prop = frame_property + animation_property
                if ("p1_main" in layer and "p1_fix_main_weapon" not in check_prop) or \
                    ("p2_main" in layer and "p2_fix_main_weapon" not in check_prop) or \
                    ("p1_sub" in layer and "p1_fix_sub_weapon" not in check_prop) or \
                    ("p2_sub" in layer and "p2_fix_sub_weapon" not in check_prop):
                    main_joint_pos = weapon_joint_list[part_name]
                    if main_joint_pos != "center":
                        hand_pos = (animation_part_list["p1_r_hand"][3], animation_part_list["p1_r_hand"][4])
                        if "p2_main" in layer:
                            hand_pos = (animation_part_list["p2_r_hand"][3], animation_part_list["p2_r_hand"][4])
                        elif "p1_sub" in layer:
                            hand_pos = (animation_part_list["p1_l_hand"][3], animation_part_list["p1_l_hand"][4])
                        elif "p2_sub" in layer:
                            hand_pos = (animation_part_list["p2_l_hand"][3], animation_part_list["p2_l_hand"][4])
                        pos_different = main_joint_pos - center  # find distance between image center and connect point main_joint_pos
                        new_target = main_joint_pos + pos_different
                        if angle != 0:
                            radians_angle = math.radians(360 - angle)
                            target = hand_pos # use hand pos instead of file
                            new_target = rotation_xy(target, new_target, radians_angle)  # find new center point with rotation

            rect = part_rotated.get_rect(center=new_target)
            surface.blit(part_rotated, rect)

    surface = pygame.transform.scale(surface, (default_sprite_size[0] * size, default_sprite_size[1] * size))

    for prop in (frame_property + animation_property):
        if "effect" in prop:
            if "grey" in prop:  # not work with just convert L for some reason
                width, height = surface.get_size()
                for x in range(width):
                    for y in range(height):
                        red, green, blue, alpha = surface.get_at((x, y))
                        average = (red + green + blue) // 3
                        gs_color = (average, average, average, alpha)
                        surface.set_at((x, y), gs_color)
            data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
            surface = Image.frombytes("RGBA", surface.get_size(), data)  # use PIL to get image data
            alpha = surface.split()[-1]  # save alpha
            if "blur" in prop:
                surface = surface.filter(
                    ImageFilter.GaussianBlur(radius=float(prop[prop.rfind("_") + 1:])))  # blur Image (or apply other filter in future)
            if "contrast" in prop:
                enhancer = ImageEnhance.Contrast(surface)
                surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
            if "brightness" in prop:
                enhancer = ImageEnhance.Brightness(surface)
                surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
            if "fade" in prop:
                empty = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
                empty.fill((255, 255, 255, 255))
                empty = pygame.image.tostring(empty, "RGBA")  # convert image to string data for filtering effect
                empty = Image.frombytes("RGBA", surface.get_size(), empty)  # use PIL to get image data
                surface = Image.blend(surface, empty, alpha=float(prop[prop.rfind("_") + 1:]) / 10)
            surface.putalpha(alpha)  # put back alpha
            surface = surface.tobytes()
            surface = pygame.image.fromstring(surface, surface.get_size(),
                                              "RGBA")  # convert image back to a pygame surface
            if "colour" in prop:
                colour = prop[prop.rfind("_") + 1:]
                colour = [int(this_colour) for this_colour in colour.split(",")]
                surface = apply_colour(surface, colour)

            if prop in frame_property:
                frame_property.remove(prop)
            if prop in animation_property:
                animation_property.remove(prop)

    return {"sprite": surface, "animation_property": animation_property, "frame_property": frame_property}
