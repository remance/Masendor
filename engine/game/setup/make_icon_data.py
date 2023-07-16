import pygame

from engine.uibattle.uibattle import SkillIcon
from engine.utility import load_images


def make_icon_data(main_dir, screen_scale):
    skill_images = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "skill_icon"))
    cooldown = pygame.Surface((skill_images["0"].get_width(), skill_images["0"].get_height()), pygame.SRCALPHA)
    cooldown.fill((230, 70, 80, 200))  # red colour filter for skill cooldown timer
    SkillIcon.cooldown = cooldown

    active_skill = pygame.Surface((skill_images["0"].get_width(), skill_images["0"].get_height()), pygame.SRCALPHA)
    active_skill.fill((170, 220, 77, 200))  # green colour filter for skill active timer
    SkillIcon.active_skill = active_skill

    return skill_images
