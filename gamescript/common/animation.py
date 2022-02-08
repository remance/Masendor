import time
import pygame

from PIL import Image, ImageOps, ImageFilter, ImageEnhance

from gamescript import readstat

stat_convert = readstat.stat_convert

default_sprite_size = (200, 200)


def play_animation(self, surface, position, speed, play_list):
    if time.time() - self.first_time >= speed:
        if self.show_frame < len(play_list):
            self.show_frame += 1
        self.first_time = time.time()
    # if self.show_frame > self.end_frame:  # TODO add property
    #     self.show_frame = self.start_frame
    #     while self.show_frame < 10 and play_list[self.show_frame] is False:
    #         self.show_frame += 1

    surface.blit(self.frames[int(self.show_frame)], position)


def apply_colour(surface, colour=None):
    """Colorise body part sprite"""
    size = (surface.get_width(), surface.get_height())
    data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
    surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
    alpha = surface.split()[-1]  # save alpha
    surface = surface.convert("L")  # convert to grey scale for colourise
    if colour is not None:
        max_colour = 255  # - (colour[0] + colour[1] + colour[2])
        mid_colour = [int(c - ((max_colour - c) / 2)) for c in colour]
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


def generate_head(p, body_part_list, pool, troop_part_list):
    head_sprite_surface = None
    # try:
    print(body_part_list)
    head_race = body_part_list[0]
    head_side = body_part_list[1]
    head = pool[head_race][head_side]["head"][body_part_list[2]].copy()
    head_sprite_surface = pygame.Surface((head.get_width(), head.get_height()), pygame.SRCALPHA)
    head_rect = head.get_rect(midtop=(head_sprite_surface.get_width() / 2, 0))
    head_sprite_surface.blit(head, head_rect)
    face = [pool[head_race][head_side]["eyebrow"][troop_part_list[p + "_eyebrow"]].copy(),
               grab_face_part(head_race, head_side, "eye", body_part_list[p + "_eye"], troop_part_list[p + "_eye"]),
               pool[head_race][head_side]["beard"][troop_part_list[p + "_beard"]].copy(),
               grab_face_part(head_race, head_side, "mouth", body_part_list[p + "_mouth"], troop_part_list[p + "_mouth"])]
    # if skin != "white":
    #     face[0] = self.apply_colour(face[0], skin_colour)
    face[0] = apply_colour(face[0], troop_part_list[p + "_hair"][1])
    face[2] = apply_colour(face[2], troop_part_list[p + "_hair"][1])
    face[1] = apply_colour(face[1], troop_part_list[p + "_eye"][1])

    head_sprite_surface = pygame.Surface((face[2].get_width(), face[2].get_height()), pygame.SRCALPHA)
    head_rect = head.get_rect(midtop=(head_sprite_surface.get_width() / 2, 0))
    head_sprite_surface.blit(head, head_rect)

    for index, item in enumerate(face):
        rect = item.get_rect(topleft=(0, 0))
        head_sprite_surface.blit(item, rect)
    # except KeyError:  # some head direction show no face
    #     pass
    # except TypeError:  # empty
    #     pass

    # if self.armour["p1_armour"] != "None":
    #     armour = self.armour["p1_armour"].split("/")
    #     gear_image = gen_armour_sprite_pool[p1_head_race][armour[0]][armour[1]][p1_head_side]["helmet"][bodypart_list["p1_head"][2]].copy()
    #     temp_p1_head_sprite_surface = p1_head_sprite_surface.copy()
    #     size = [gear_image.get_width(), gear_image.get_height()]
    #     if size[0] < temp_p1_head_sprite_surface.get_width():
    #         size[0] = temp_p1_head_sprite_surface.get_width()
    #     if size[1] < temp_p1_head_sprite_surface.get_height():
    #         size[1] = temp_p1_head_sprite_surface.get_height()
    #     p1_head_sprite_surface = pygame.Surface(size, pygame.SRCALPHA)
    #     rect = temp_p1_head_sprite_surface.get_rect(center=(p1_head_sprite_surface.get_width() / 2, p1_head_sprite_surface.get_height() / 2))
    #     p1_head_sprite_surface.blit(temp_p1_head_sprite_surface, rect)
    #     rect = gear_image.get_rect(center=(p1_head_sprite_surface.get_width() / 2, p1_head_sprite_surface.get_height() / 2))
    #     p1_head_sprite_surface.blit(gear_image, rect)

    return head_sprite_surface

def generate_body(part, colour, body_part_list, troop_part_list, pool):

    # main/body first
    sprite_image = pool[body_part_list[part][0]][body_part_list[part][1]][part][
        body_part_list[part][2]].copy()

    if colour != "None":
        sprite_image = apply_colour(sprite_image, colour)

    # add armour if there is one
    if part in troop_part_list and troop_part_list[part] != "None":
        gear_image = pool[body_part_list[part][0]][body_part_list[part][1]][part][body_part_list[part][2]].copy()
        rect = gear_image.get_rect(center=(sprite_image.get_width / 2, sprite_image.get_height / 2))
        sprite_image.blit(gear_image, rect)

    # weapon_joint_pos_list = {}
    # for part_index, part in enumerate(part_name_header):
    #     if part in self.weapon and self.weapon[part] in weapon_joint_list[self.side]:  # weapon joint
    #             weapon_joint_pos_list[part] = list(weapon_joint_pos_list[self.side][self.weapon[part]][0].values())[0]

    return sprite_image


def make_sprite(size, animation_part_list, troop_part_list, body_sprite_pool, weapon_sprite_pool, effect_sprite_pool, animation_property):
    surface = pygame.Surface((default_sprite_size[0] * size, default_sprite_size[1] * size),
                           pygame.SRCALPHA)  # default size will scale down later

    except_list = ["eye", "mouth", "size", "property"]

    pose_layer_list = {k: v[7] for k, v in animation_part_list.items() if v != [0] and any(ext in k for ext in except_list) is False}  # layer list
    pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
    for index, layer in enumerate(pose_layer_list):
        part = animation_part_list[layer]
        print(part)
        if "head" in layer:
            image_part = generate_head(layer[:2], part[0:3], body_sprite_pool, troop_part_list)
        elif "weapon" in layer:
            image_part = generate_body(layer, part[0:2], weapon_sprite_pool, troop_part_list)
        elif "effect" in layer:
            image_part = generate_body(layer, part[0:3], effect_sprite_pool, troop_part_list)
        else:  # other body part
            image_part = generate_head(layer, part[0:3], body_sprite_pool, troop_part_list)
        main_joint_pos = part[1]
        target = part[3]
        angle = part[4]
        flip = part[5]
        scale = part[8]

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

        center = pygame.Vector2(part.get_width() / 2, part.get_height() / 2)
        new_target = target  # - pos_different  # find new center point
        # if "weapon" in list(self.rect_part_list.keys())[part_index] and main_joint_pos != "center":  # only weapon use joint to calculate position
        #     print(main_joint_pos)
        #     pos_different = main_joint_pos - center  # find distance between image center and connect point main_joint_pos
        #     new_target = main_joint_pos + pos_different
        # if angle != 0:
        #     radians_angle = math.radians(360 - angle)
        #     new_target = rotation_xy(target, new_target, radians_angle)  # find new center point with rotation

        rect = part_rotated.get_rect(center=new_target)
        surface.blit(part_rotated, rect)

    frame_property = animation_part_list["frame_property"]
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

    return surface, frame_property
