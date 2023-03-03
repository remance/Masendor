from math import cos, sin, radians
from random import randint

from pygame import Vector2
from gamescript import weather


def spawn_weather_matter(self):
    travel_angle = randint(self.current_weather.travel_angle[0], self.current_weather.travel_angle[1])

    screen_rect_width = self.screen_rect.width
    screen_rect_height = self.screen_rect.height

    if travel_angle >= 180:
        spawn_angle = travel_angle - 180
        height_cal = spawn_angle / 180
    elif travel_angle >= 135:
        spawn_angle = travel_angle * 2
        height_cal = spawn_angle / 360
    else:
        spawn_angle = 450 - travel_angle
        height_cal = spawn_angle / 360

    if height_cal != 1:  # matter travel not from direct straight top to bottom angle
        start_width = randint(0, int(screen_rect_width * (2 / (screen_rect_width / screen_rect_height))))
        if start_width > screen_rect_width:  # matter must reach width screen border but not height
            if spawn_angle < 180:  # spawn from right screen, target must reach left border of screen
                target = (0, randint(int(screen_rect_height * height_cal), screen_rect_height))
            else:  # spawn from left screen, target must reach right border of screen
                target = (self.screen_rect.width, randint(int(screen_rect_height * height_cal), screen_rect_height))
        else:
            target = (start_width, screen_rect_height)
    else:
        target = (randint(0, screen_rect_width), screen_rect_height)

    start_pos = Vector2(target[0] + (screen_rect_width * sin(radians(spawn_angle))),
                        target[1] - (screen_rect_height * cos(radians(spawn_angle))))

    random_pic = randint(0, len(self.weather_matter_images[self.current_weather.name]) - 1)
    self.weather_matter.add(weather.MatterSprite(start_pos, target, self.current_weather.speed,
                                                 self.weather_matter_images[self.current_weather.name][random_pic],
                                                 self.screen_rect.size))
