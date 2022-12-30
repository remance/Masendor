import math
import random

import pygame

from gamescript import weather


def weather_matter_spawn(self):
    travel_angle = random.randint(self.current_weather.travel_angle[0], self.current_weather.travel_angle[1])

    screen_rect_width = self.screen_rect.width
    screen_rect_height = self.screen_rect.height

    if travel_angle >= 180:
        spawn_angle = travel_angle - 180
        height_cal = spawn_angle / 180
    else:
        spawn_angle = 360 - travel_angle
        height_cal = spawn_angle / 360

    if height_cal != 1:  # matter travel not from direct straight top to bottom angle
        start_width = random.randint(0, int(screen_rect_width * (2 / (screen_rect_width / screen_rect_height))))
        if start_width > screen_rect_width:  # matter must reach width screen border but not height
            if spawn_angle < 180:  # spawn from right screen, target must reach left border of screen
                target = (0, random.randint(int(screen_rect_height * height_cal), screen_rect_height))
            else:  # spawn from left screen, target must reach right border of screen
                target = (self.screen_rect.width, random.randint(int(screen_rect_height * height_cal), screen_rect_height))
        else:
            target = (start_width, screen_rect_height)
    else:
        target = (random.randint(0, screen_rect_width), screen_rect_height)

    start_pos = pygame.Vector2(target[0] + (screen_rect_width * 1.2 * math.sin(math.radians(spawn_angle))),
                               target[1] - (screen_rect_height * 1.2 * math.cos(math.radians(spawn_angle))))

    random_pic = random.randint(0, len(
        self.weather_matter_images[self.current_weather.name]) - 1)
    self.weather_matter.add(weather.MatterSprite(start_pos, target, self.current_weather.speed, travel_angle,
                                                 self.weather_matter_images[self.current_weather.name][random_pic],
                                                 self.screen_rect.size))
