import time
import pygame

from PIL import Image, ImageOps, ImageFilter, ImageEnhance

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


def make_sprite(size, animation_part_list, frame):
    surface = pygame.Surface((default_sprite_size[0] * size, default_sprite_size[1] * size),
                           pygame.SRCALPHA)  # default size will scale down later
    for index, layer in enumerate(animation_part_list):
        part = animation_part_list[frame][layer]
        part_index = list(animation_part_list[frame].keys()).index(layer)
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
