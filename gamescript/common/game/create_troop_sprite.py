import math

import pygame
from PIL import Image, ImageFilter, ImageEnhance
from gamescript.common import utility

rotation_xy = utility.rotation_xy
apply_sprite_colour = utility.apply_sprite_colour

default_sprite_size = (200, 200)


def create_troop_sprite(self, animation_name, troop_size, animation_part_list, troop_sprite_list,
                        animation_property, weapon, armour, idle_animation):
    frame_property = animation_part_list["frame_property"].copy()
    animation_property = animation_property.copy()
    check_prop = frame_property + animation_property
    dmg_sprite = None
    troop_size = int(troop_size)

    surface = pygame.Surface((default_sprite_size[0] * troop_size, default_sprite_size[1] * troop_size),
                             pygame.SRCALPHA)  # default size will scale down later

    except_list = ("eye", "mouth", "size", "property")
    pose_layer_list = {k: v[-2] for k, v in animation_part_list.items() if v != [0] and v != "" and v != [""] and
                       any(ext in k for ext in except_list) is False}  # layer list

    if "_Skill_" in animation_name:  # change layer of weapon for skill animation to match whether it is behind hand or not
        for key, layer in pose_layer_list.items():
            if "weapon" in key:
                part = animation_part_list[key]
                if "sheath" not in part[0]:
                    if "main" in key:
                        hand_layer = pose_layer_list[key[:2] + "_r_hand"]
                        idle_hand_layer = idle_animation[key[:2] + "_r_hand"]
                        idle_weapon_layer = idle_animation[key]
                    else:
                        hand_layer = pose_layer_list[key[:2] + "_l_hand"]
                        idle_hand_layer = idle_animation[key[:2] + "_l_hand"]
                        idle_weapon_layer = idle_animation[key]
                    if layer != idle_weapon_layer:
                        if idle_weapon_layer >= idle_hand_layer:  # weapon behind hand
                            pose_layer_list[key] = hand_layer + 1
                        else:  # weapon in front of hand
                            pose_layer_list[key] = hand_layer - 1

    pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))

    for index, layer in enumerate(pose_layer_list):
        part = animation_part_list[layer]
        new_part = part.copy()
        this_armour = None
        image_part = None
        if any(ext in layer for ext in ("p1_", "p2_", "p3_", "p4_")) and "weapon" not in layer:
            part_race = [value["Name"] for value in self.troop_data.race_list.values()].index(new_part[0])
            part_race = tuple(self.troop_data.race_list.keys())[part_race]
            if self.troop_data.race_list[part_race]["Mount Armour"] is False:
                this_armour = armour[0]
            else:
                this_armour = armour[1]

        if "head" in layer:
            image_part = generate_head(layer[:2], animation_part_list, part[:2], troop_sprite_list,
                                       self.gen_body_sprite_pool, self.gen_armour_sprite_pool,
                                       this_armour, self.colour_list)
        elif "weapon" in layer:
            new_part.insert(1, "Dummy")  # insert dummy value for weapon list so can use indexing similar as other part
            image_part = generate_body(layer, part[:1], troop_sprite_list, self.gen_weapon_sprite_pool, weapon=weapon)
        elif "effect" in layer:
            if "dmg_" not in layer:
                image_part = generate_body(layer, part[:2], troop_sprite_list, self.effect_sprite_pool)
            else:
                dmg_sprite = tuple(part)

        else:  # other body part
            colour = troop_sprite_list[layer[:2] + "_skin"]
            if any(ext in part[1] for ext in self.troop_data.race_list[part_race]["Special Hair Part"]):
                colour = troop_sprite_list[layer[:2] + "_hair"]
                if colour != "":
                    if len(colour) == 2:
                        colour = colour[1]
                    else:
                        colour = colour[0]
            if colour == "":  # no custom colour, use None
                colour = None

            image_part = generate_body(layer, part[:2], troop_sprite_list, self.gen_body_sprite_pool,
                                       armour_sprite_pool=self.gen_armour_sprite_pool, colour=colour,
                                       colour_list=self.colour_list, armour=this_armour)

        if image_part is not None:  # skip for empty image
            target = (new_part[2], new_part[3])
            flip = new_part[5]
            scale = new_part[-1]

            new_target = target

            use_center = False

            p = layer[:3]

            if "weapon" in layer:  # only weapon use joint to calculate position
                part_name = weapon[1][0]  # main weapon
                if "sub" in layer:
                    part_name = weapon[1][1]  # sub weapon
                center = pygame.Vector2(image_part.get_width() / 2, image_part.get_height() / 2)
                use_center = True
                if (p + "main_" in layer and p + "fix_main_weapon" not in check_prop) or \
                        (p + "sub_" in layer and p + "fix_sub_weapon" not in check_prop):
                    use_center = False
                    if p + "main_weapon" in layer:  # main weapon
                        if "sheath" not in part[0]:  # change main weapon pos to right hand, if part is not sheath
                            target = (animation_part_list[p + "r_hand"][2], animation_part_list[p + "r_hand"][3])
                            use_center = False  # use weapon joint
                        else:
                            target = (animation_part_list[p + "body"][2],
                                      animation_part_list[p + "body"][3])  # put on back
                            use_center = True
                    elif p + "sub_weapon" in layer:  # sub weapon
                        if "sheath" not in part[0]:  # change weapon pos to hand, if part is not sheath
                            if "_Sub_" in animation_name and weapon[2][
                                1] == 2:  # two-handed sub weapon use same animation as main for attack so put sub weapon in man hand, remove code if different
                                target = (animation_part_list[p + "r_hand"][2], animation_part_list[p + "r_hand"][3])
                            else:
                                target = (animation_part_list[p + "l_hand"][2], animation_part_list[p + "l_hand"][3])
                        else:
                            target = (animation_part_list[p + "body"][2],
                                      animation_part_list[p + "body"][3])  # put on back
                            use_center = True
                    new_target = target

            part_rotated = image_part.copy()
            if scale != 1:
                part_rotated = pygame.transform.smoothscale(part_rotated, (part_rotated.get_width() * scale,
                                                                           part_rotated.get_height() * scale))
            if flip != 0:
                if flip == 1:
                    part_rotated = pygame.transform.flip(part_rotated, True, False)
                elif flip == 2:
                    part_rotated = pygame.transform.flip(part_rotated, False, True)
                elif flip == 3:
                    part_rotated = pygame.transform.flip(part_rotated, True, True)

            angle = new_part[4]

            if angle != 0:
                part_rotated = pygame.transform.rotate(part_rotated, angle)  # rotate part sprite
            if "weapon" in layer and self.weapon_joint_list[
                part_name] != "center" and use_center is False:  # use weapon joint pos and hand pos for weapon position blit
                main_joint_pos = [self.weapon_joint_list[part_name][0],
                                  self.weapon_joint_list[part_name][1]]

                # change pos from flip
                if flip in (1, 3):  # horizontal flip
                    hori_diff = image_part.get_width() - main_joint_pos[0]
                    main_joint_pos = (hori_diff, main_joint_pos[1])
                if flip >= 2:  # vertical flip
                    vert_diff = image_part.get_height() - main_joint_pos[1]
                    main_joint_pos = (main_joint_pos[0], vert_diff)
                pos_different = center - main_joint_pos  # find distance between image center and connect point main_joint_pos
                new_target = new_target + pos_different
                if angle != 0:
                    radians_angle = math.radians(360 - angle)
                    if angle < 0:
                        radians_angle = math.radians(-angle)
                    new_target = rotation_xy(target, new_target,
                                             radians_angle)  # find new center point with rotation
            rect = part_rotated.get_rect(center=new_target)
            surface.blit(part_rotated, rect)

    for prop in check_prop:
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
                    ImageFilter.GaussianBlur(
                        radius=float(prop[prop.rfind("_") + 1:])))  # blur Image (or apply other filter in future)
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
                colour = [int(this_colour) for this_colour in colour.split(".")]
                surface = apply_sprite_colour(surface, colour)

            if prop in frame_property:
                frame_property.remove(prop)
            if prop in animation_property:
                animation_property.remove(prop)

    # Add white border
    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(surface)
    mask_outline = mask.outline()
    n = 0
    for point in mask_outline:
        mask_outline[n] = (point[0], point[1])
        n += 1
    pygame.draw.polygon(new_surface, (240, 240, 240), mask_outline, 10)
    new_surface.blit(surface, (0, 0))

    return {"sprite": new_surface, "animation_property": tuple(animation_property), "frame_property": tuple(frame_property),
            "dmg_sprite": dmg_sprite}


def grab_face_part(pool, race, part, part_check, part_default=None):
    """For creating body part like eye or mouth in animation that accept any part (1) so use default instead"""
    surface = None
    try:
        if part_check != "":
            if part_check == 1:  # any part
                if part_default is not None:
                    default = part_default
                    if type(part_default) != str:
                        default = part_default[0]
                    surface = pool[race][part][default].copy()
            else:
                check = part_check
                if type(part_check) != str:
                    check = part_check[0]
                if check != "none":
                    surface = pool[race][part][check].copy()
    except KeyError:
        pass
    return surface


def generate_head(p, animation_part_list, body_part_list, sprite_list, body_pool, armour_pool, armour,
                  colour_list):
    head_sprite_surface = None
    head_race = body_part_list[0]
    head = body_pool[head_race]["head"][body_part_list[1]].copy()
    head_sprite_surface = pygame.Surface((head.get_width(), head.get_height()), pygame.SRCALPHA)
    head_rect = head.get_rect(topleft=(0, 0))
    head_sprite_surface.blit(head, head_rect)
    if sprite_list[p + "_skin"] not in ("", "none"):
        head_sprite_surface = apply_sprite_colour(head_sprite_surface, sprite_list[p + "_skin"], colour_list,
                                                  keep_white=False)
    face = [grab_face_part(body_pool, head_race, "eyebrow", sprite_list[p + "_eyebrow"]),
            grab_face_part(body_pool, head_race, "eye", animation_part_list[p + "_eye"],
                           part_default=sprite_list[p + "_eye"]),
            grab_face_part(body_pool, head_race, "beard", sprite_list[p + "_beard"]),
            grab_face_part(body_pool, head_race, "mouth", animation_part_list[p + "_mouth"],
                           part_default=sprite_list[p + "_mouth"])]

    for face_index, face_part in enumerate(("_eyebrow", "_eye", "_beard")):
        if face[face_index] is not None:
            face[face_index] = apply_sprite_colour(face[face_index], sprite_list[p + face_part][1], colour_list)

    for index, item in enumerate(face):
        if item is not None:
            rect = item.get_rect(center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
            head_sprite_surface.blit(item, rect)

    if sprite_list[p + "_hair"] not in ("", "none") and "hair" in body_pool[head_race]["head"]:
        hair_sprite = body_pool[head_race]["head"]["hair"][sprite_list[p + "_hair"][0]].copy()
        hair_sprite = apply_sprite_colour(hair_sprite, sprite_list[p + "_hair"][1], colour_list)
        head_sprite_surface.blit(hair_sprite, rect)

    if sprite_list[p + "_head"] != "none":
        try:
            gear_image = armour_pool[head_race][armour][sprite_list[p + "_head"]]["head"][
                body_part_list[1]]

            gear_image_sprite = pygame.Surface(gear_image.get_size(), pygame.SRCALPHA)
            rect = head_sprite_surface.get_rect(
                center=(gear_image_sprite.get_width() / 2, gear_image_sprite.get_height() / 2))
            gear_image_sprite.blit(head_sprite_surface, rect)

            rect = gear_image.get_rect(
                center=(gear_image_sprite.get_width() / 2, gear_image_sprite.get_height() / 2))
            gear_image_sprite.blit(gear_image, rect)
            head_sprite_surface = gear_image_sprite
        except KeyError:  # head armour not existed
            pass

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
                try:
                    sprite_image = sprite_pool[part_name][troop_sprite_list[weapon_part]][body_part_list[0]].copy()
                except KeyError:  # use common variant if specified not found
                    sprite_image = sprite_pool[part_name]["Common"][body_part_list[0]].copy()
        else:
            new_part_name = part
            part_name = part
            if any(ext in part for ext in ("p1_", "p2_", "p3_", "p4_")):
                part_name = part[3:]  # remove person header
                new_part_name = part_name
            if "special" in part:
                new_part_name = "special"
            if "r_" in part_name[:2] or "l_" in part_name[:2]:
                new_part_name = part_name[2:]  # remove side
            if "effect_" not in part:
                sprite_image = sprite_pool[body_part_list[0]][new_part_name][body_part_list[1]].copy()
            else:
                sprite_image = sprite_pool[body_part_list[0]][body_part_list[1]].copy()

        if colour is not None:  # apply skin colour, maybe add for armour colour later
            sprite_image = apply_sprite_colour(sprite_image, colour, colour_list, keep_white=False)

        # if sprite_list[p + "_hair"] not in ("", "none"):
        #     hair_sprite = body_pool[head_race]["head"]["hair"][sprite_list[p + "_hair"][0]].copy()
        #     hair_sprite = apply_sprite_colour(hair_sprite, sprite_list[p + "_hair"][1], colour_list)
        #     head_sprite_surface.blit(hair_sprite, rect)

        if armour is not None and armour != "None":  # add armour if there is one
            part_name = part
            if any(ext in part for ext in ("p1_", "p2_", "p3_", "p4_")):
                part_name = part[3:]  # remove person prefix to get part name
            gear_image = \
                armour_sprite_pool[body_part_list[0]][armour][troop_sprite_list[part]][part_name][body_part_list[1]]
            new_sprite_image = pygame.Surface(gear_image.get_size(),
                                              pygame.SRCALPHA)  # create sprite based on armour size since it can be larger than body part
            rect = sprite_image.get_rect(center=(new_sprite_image.get_width() / 2, new_sprite_image.get_height() / 2))
            new_sprite_image.blit(sprite_image, rect)
            rect = gear_image.get_rect(center=(new_sprite_image.get_width() / 2, new_sprite_image.get_height() / 2))
            new_sprite_image.blit(gear_image, rect)
            sprite_image = new_sprite_image
    except KeyError:  # sprite simply not existed
        pass

    return sprite_image
