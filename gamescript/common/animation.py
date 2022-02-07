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


def generate_body(body_part_list, troop_part_list, pool, effect_sprite_pool):
    p1_head_sprite_surface = None
    try:
        p1_head_race = body_part_list["p1_head"][0]
        p1_head_side = body_part_list["p1_head"][1]
        p1_head = pool[p1_head_race][p1_head_side]["head"][body_part_list["p1_head"][2]].copy()
        p1_head_sprite_surface = pygame.Surface((p1_head.get_width(), p1_head.get_height()), pygame.SRCALPHA)
        head_rect = p1_head.get_rect(midtop=(p1_head_sprite_surface.get_width() / 2, 0))
        p1_head_sprite_surface.blit(p1_head, head_rect)
        p1_face = [pool[p1_head_race][p1_head_side]["eyebrow"][troop_part_list["p1_eyebrow"]].copy(),
                   grab_face_part(p1_head_race, p1_head_side, "eye", body_part_list["p1_eye"], troop_part_list["p1_eye"]),
                   pool[p1_head_race][p1_head_side]["beard"][troop_part_list["p1_beard"]].copy(),
                   grab_face_part(p1_head_race, p1_head_side, "mouth", body_part_list["p1_mouth"], troop_part_list["p1_mouth"])]
        # if skin != "white":
        #     face[0] = self.apply_colour(face[0], skin_colour)
        p1_face[0] = apply_colour(p1_face[0], troop_part_list["p1_hair"][1])
        p1_face[2] = apply_colour(p1_face[2], troop_part_list["p1_hair"][1])
        p1_face[1] = apply_colour(p1_face[1], troop_part_list["p1_eye"][1])

        p1_head_sprite_surface = pygame.Surface((p1_face[2].get_width(), p1_face[2].get_height()), pygame.SRCALPHA)
        head_rect = p1_head.get_rect(midtop=(p1_head_sprite_surface.get_width() / 2, 0))
        p1_head_sprite_surface.blit(p1_head, head_rect)

        for index, item in enumerate(p1_face):
            rect = item.get_rect(topleft=(0, 0))
            p1_head_sprite_surface.blit(item, rect)
    except KeyError:  # some head direction show no face
        pass
    except TypeError:  # empty
        pass

    p2_head_sprite_surface = None
    try:
        p2_head_race = body_part_list["p2_head"][0]
        p2_head_side = body_part_list["p2_head"][1]
        p2_head = pool[p2_head_race][p2_head_side]["head"][body_part_list["p2_head"][2]].copy()
        p2_head_sprite_surface = pygame.Surface((p2_head.get_width(), p2_head.get_height()), pygame.SRCALPHA)
        head_rect = p2_head.get_rect(midtop=(p2_head_sprite_surface.get_width() / 2, 0))
        p2_head_sprite_surface.blit(p2_head, head_rect)
        p2_face = [pool[p2_head_race][p2_head_side]["eyebrow"][self.p2_eyebrow].copy(),
                   grab_face_part(p2_head_race, p2_head_side, "eye", body_part_list["p2_eye"], self.p2_any_eye),
                   pool[p2_head_race][p2_head_side]["beard"][self.p2_beard].copy(),
                   grab_face_part(p2_head_race, p2_head_side, "mouth", body_part_list["p2_mouth"], self.p2_any_mouth)]
        # if skin != "white":
        #     face[0] = self.apply_colour(face[0], skin_colour)
        p2_face[0] = apply_colour(p2_face[0], troop_part_list["p2_hair"][1])
        p2_face[2] = apply_colour(p2_face[2], self.p2_hair_colour)
        p2_face[1] = apply_colour(p2_face[1], self.p2_eye_colour)
        p2_head_sprite_surface = pygame.Surface((p2_face[2].get_width(), p2_face[2].get_height()), pygame.SRCALPHA)
        head_rect = p2_head.get_rect(midtop=(p2_head_sprite_surface.get_width() / 2, 0))
        p2_head_sprite_surface.blit(p2_head, head_rect)

        for index, item in enumerate(p2_face):
            rect = item.get_rect(topleft=(0, 0))
            p2_head_sprite_surface.blit(item, rect)
    except KeyError:  # some head direction show no face
        pass
    except TypeError:  # empty
        pass

    sprite_image = {key: None for key in self.rect_part_list.keys()}
    except_list = ["eye", "mouth", "head"]  # skip doing these
    for stuff in body_part_list:  # create stat and image
        if body_part_list[stuff] is not None:
            if any(ext in stuff for ext in except_list) is False:
                if "weapon" in stuff:
                    part_name = self.weapon[stuff]
                    if part_name is not None and body_part_list[stuff][2]:
                        sprite_image[stuff] = pool[part_name][body_part_list[stuff][1]][body_part_list[stuff][2]].copy()
                elif "effect_" in stuff:
                    sprite_image[stuff] = effect_sprite_pool[body_part_list[stuff][0]][body_part_list[stuff][1]][
                        body_part_list[stuff][2]].copy()
                else:
                    if "p1_" in stuff or "p2_" in stuff:
                        part_name = stuff[3:]  # remove p1_ or p2_ to get part name
                    if "special" in stuff:
                        part_name = "special"
                    if "r_" in part_name[0:2] or "l_" in part_name[0:2]:
                        part_name = part_name[2:]  # remove side
                    sprite_image[stuff] = pool[body_part_list[stuff][0]][body_part_list[stuff][1]][part_name][
                        body_part_list[stuff][2]].copy()
            elif "head" in stuff:
                if "p1" in stuff:
                    sprite_image[stuff] = p1_head_sprite_surface
                else:
                    sprite_image[stuff] = p2_head_sprite_surface

    # if skin != "white":
    #     for part in list(self.sprite_image.keys())[1:]:
    #         self.sprite_image[part] = self.apply_colour(self.sprite_image[part], skin_colour)

    weapon_joint_pos_list = {}
    for part_index, part in enumerate(part_name_header):
        if part in self.weapon and self.weapon[part] in weapon_joint_list[self.side]:  # weapon joint
                weapon_joint_pos_list[part] = list(weapon_joint_pos_list[self.side][self.weapon[part]][0].values())[0]

    return weapon_joint_pos_list


def make_sprite(size, animation_part_list, troop_part_list):
    surface = pygame.Surface((default_sprite_size[0] * size, default_sprite_size[1] * size),
                           pygame.SRCALPHA)  # default size will scale down later

    except_list = ["eye", "mouth", "size", "property"]

    pose_layer_list = {k: v[7] for k, v in animation_part_list.items() if v != [0] and any(ext in k for ext in except_list) is False}  # layer list
    pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))

    for index, layer in enumerate(pose_layer_list):
        part = animation_part_list[layer]
        image_part = part[0]
        main_joint_pos = part[1]
        target = part[2]
        angle = part[3]
        flip = part[4]
        scale = part[6]

        part_rotated = part.copy()
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

    for prop in frame_property:
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

    return surface
