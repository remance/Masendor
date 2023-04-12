from random import randint

import pygame
import pygame.freetype

from gamescript.common import utility


class Weather:
    weather_icons = {}
    wind_compass_images = {}

    def __init__(self, time_ui, weather_type, wind_direction, level, weather_data):
        self.weather_type = weather_type
        if self.weather_type == 0:
            self.weather_type = randint(1, len(weather_data) - 1)
        self.has_stat_effect = False
        if weather_data:
            self.has_stat_effect = True
            stat = weather_data[self.weather_type]
            self.name = stat["Name"]
            self.level = level  # weather level 0 = Light, 1 = Normal, 2 = Strong
            if self.level > 2:  # in case adding higher level number by mistake
                self.level = 2
            elif self.level < 0:  # can not be negative level
                self.level = 0
            cal_level = self.level + 1

            self.melee_atk_buff = stat["Melee Attack Bonus"] * cal_level
            self.melee_def_buff = stat["Melee Defense Bonus"] * cal_level
            self.range_def_buff = stat["Range Defense Bonus"] * cal_level
            self.speed_buff = stat["Speed Bonus"] * cal_level
            self.accuracy_buff = stat["Accuracy Bonus"] * cal_level
            self.range_buff = stat["Range Bonus"] * cal_level
            self.reload_buff = stat["Reload Bonus"] * cal_level
            self.charge_buff = stat["Charge Bonus"] * cal_level
            self.charge_def_buff = stat["Charge Defense Bonus"] * cal_level
            self.hp_regen_buff = stat["HP Regeneration Bonus"] * cal_level
            self.stamina_regen_buff = stat["Stamina Regeneration Bonus"] * cal_level
            self.morale_buff = stat["Morale Bonus"] * cal_level
            self.discipline_buff = stat["Discipline Bonus"] * cal_level
            self.sight_buff = stat["Sight Bonus"] * cal_level
            self.hidden_buff = stat["Hide Bonus"] * cal_level
            self.temperature = stat["Temperature"] * cal_level
            self.element = tuple([(element, cal_level) for element in stat["Element"] if element != ""])
            self.status_effect = stat["Status"]
            self.spawn_rate = stat["Spawn Rate"] / cal_level  # divide to make spawn increase with strength
            self.wind_strength = int(stat["Wind Strength"] * cal_level)
            self.speed = stat["Travel Speed"] * self.wind_strength

            self.wind_direction = wind_direction
            self.travel_angle = wind_direction
            if self.travel_angle > 255:
                self.travel_angle = 510 - self.travel_angle
            elif 0 <= self.travel_angle < 90:
                self.travel_angle = 180 - self.travel_angle
            elif 90 <= self.travel_angle < 105:
                self.travel_angle = 210 - self.travel_angle

            self.travel_angle = (int(self.travel_angle - (abs(180 - self.travel_angle) / 3)),
                                 int(self.travel_angle + (abs(180 - self.travel_angle) / 3)))

            image = pygame.Surface((self.wind_compass_images["wind_compass"].get_width() * 2,
                                    self.wind_compass_images["wind_compass"].get_height()), pygame.SRCALPHA)

            wind_compass_image = self.wind_compass_images["wind_compass"].copy()
            wind_compass_rect = wind_compass_image.get_rect(topleft=(0, 0))
            wind_arrow = self.wind_compass_images["wind_arrow"]
            angle = abs(360 - wind_direction)  # angle for arrow rotation
            wind_arrow = pygame.transform.rotate(wind_arrow, angle)
            wind_arrow_rect = wind_arrow.get_rect(center=(wind_compass_image.get_width() / 2,
                                                          wind_compass_image.get_height() / 2))
            wind_compass_image.blit(wind_arrow, wind_arrow_rect)
            font = pygame.font.SysFont("helvetica", int(wind_compass_image.get_height() / 2))
            text_surface = font.render(str(self.wind_strength), True, (0, 0, 0))
            text_rect = text_surface.get_rect(
                center=(wind_compass_image.get_width() / 2, wind_compass_image.get_height() / 2))
            wind_compass_image.blit(text_surface, text_rect)

            image.blit(wind_compass_image, wind_compass_rect)

            weather_image = self.weather_icons[self.name + "_" + str(self.level)]
            weather_image_rect = weather_image.get_rect(topright=(image.get_width(), 0))
            image.blit(weather_image, weather_image_rect)

            time_ui.image = time_ui.base_image.copy()  # reset time ui image
            rect = image.get_rect(topright=(time_ui.image.get_width(), 0))
            time_ui.image.blit(image, rect)


class MatterSprite(pygame.sprite.Sprite):
    set_rotate = utility.set_rotate

    def __init__(self, start_pos, target, speed, image, screen_rect_size):
        self._layer = 9
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.speed = speed
        self.base_pos = pygame.Vector2(start_pos)  # should be at the end corner of screen
        self.target = pygame.Vector2(target)  # should be at another end corner of screen
        travel_angle = self.set_rotate(self.target)  # calculate sprite angle
        self.image = pygame.transform.rotate(image, travel_angle)  # no need to copy since rotate only once
        self.screen_start = (-self.image.get_width(), -self.image.get_height())
        self.screen_end = (self.image.get_width() + screen_rect_size[0],
                           self.image.get_height() + screen_rect_size[1])
        self.rect = self.image.get_rect(center=self.base_pos)

    def update(self, dt, timer):
        """Update sprite position movement"""
        move = self.target - self.base_pos
        move_length = move.length()
        if move_length > 0.1:
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.base_pos += move
                self.rect.center = list(int(v) for v in self.base_pos)
            else:
                self.base_pos = self.target
                self.rect.center = self.target

            if self.screen_end[0] <= self.base_pos[0] <= self.screen_start[0] or \
                    self.screen_end[1] <= self.base_pos[1] <= self.screen_start[0]:  # pass through screen border
                self.kill()

        else:  # kill when it reach the end of screen
            self.kill()


class SpecialEffect(pygame.sprite.Sprite):
    """Special effect from weather beyond sprite such as thunder, fog etc."""

    def __init__(self, pos, target, speed, image, end_time):
        self._layer = 8
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pygame.Vector2(pos)
        self.target = pygame.Vector2(target)
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)
        self.end_time = end_time

    def update(self, dt, timer):
        """Update sprite movement and removal"""
        move = self.target - self.pos
        move_length = move.length()
        if (self.rect.midleft[0] > 0 and timer < self.end_time) or (
                self.end_time is not None and timer >= self.end_time and self.rect.midright[0] > 0):
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.pos += move
                if timer < self.end_time and self.pos[0] > 0:  # do not go beyond 0 if weather event not end yet
                    self.rect.midleft = list(int(v) for v in self.pos)
                else:
                    self.rect.midleft = pygame.Vector2(0, self.pos[1])
            else:
                self.rect.midleft = self.target
        elif timer >= self.end_time and self.rect.midright[0] < 0:
            self.kill()


class SuperEffect(pygame.sprite.Sprite):
    """Super effect that affect whole screen"""

    def __init__(self, pos, image):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self)
