import pygame
import pygame.freetype


class Weather:
    images = []

    def __init__(self, timeui, weather_type, level, weather_list):
        self.weather_type = weather_type
        stat = weather_list[weather_type]
        self.level = level  # weather level 0 = Light, 1 = Normal, 2 = Strong
        if self.level > 2:  # in case adding higher level number by mistake
            self.level = 2

        self.melee_atk_buff = stat[1] * (self.level + 1)
        self.melee_def_buff = stat[2] * (self.level + 1)
        self.range_def_buff = stat[3] * (self.level + 1)
        self.armour_buff = stat[4] * (self.level + 1)
        self.speed_buff = stat[5] * (self.level + 1)
        self.accuracy_buff = stat[6] * (self.level + 1)
        self.reload_buff = stat[7] * (self.level + 1)
        self.charge_buff = stat[8] * (self.level + 1)
        self.charge_def_buff = stat[9] * (self.level + 1)
        self.hp_regen_buff = stat[10] * (self.level + 1)
        self.stamina_regen_buff = stat[11] * (self.level + 1)
        self.morale_buff = stat[12] * (self.level + 1)
        self.discipline_buff = stat[13] * (self.level + 1)
        # self.sight_buff = stat[14] * (self.level+1)
        # self.hidden_buff = stat[15] * (self.level+1)
        self.temperature = stat[16] * (self.level + 1)
        self.elem = (stat[17], (self.level + 1))
        self.status_effect = stat[18]
        self.spawn_rate = stat[19] * (self.level + 1)
        self.spawn_angle = stat[20]
        self.speed = stat[21] * (self.level + 1)
        image = self.images[(self.weather_type * 3) + self.level]
        cropped = pygame.Surface((image.get_width(), image.get_height()))
        cropped.blit(timeui.image_original, (0, 0), (0, 0, 80, 80))
        crop_rect = cropped.get_rect(topleft=(0, 0))
        cropped.blit(image, crop_rect)
        image = cropped

        rect = image.get_rect(topright=(timeui.image.get_width() - 5, 0))
        timeui.image.blit(image, rect)

    # def weatherchange(self, level):
    #     self.level = level


class MatterSprite(pygame.sprite.Sprite):
    def __init__(self, pos, target, speed, image):
        self._layer = 9
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.speed = speed
        self.pos = pygame.Vector2(pos)  # should be at the end corner of screen
        self.target = pygame.Vector2(target)  # should be at another end corner of screen
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt, timer):
        """Update sprite position movement"""
        move = self.target - self.pos
        move_length = move.length()
        if move_length > 0.1:
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.pos += move
                self.rect.center = list(int(v) for v in self.pos)
            else:
                self.pos = self.target
                self.rect.center = self.target
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
        pygame.sprite.Sprite.__init__(self, self.containers)
