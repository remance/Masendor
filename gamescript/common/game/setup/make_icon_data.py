import pygame
from gamescript import battleui
from gamescript.common import utility

load_images = utility.load_images


def make_icon_data(main_dir, screen_scale):
    status_images = load_images(main_dir, screen_scale, ("ui", "status_icon"), load_order=False)
    role_images = load_images(main_dir, screen_scale, ("ui", "role_icon"), load_order=False)
    trait_images = load_images(main_dir, screen_scale, ("ui", "trait_icon"), load_order=False)
    skill_images = load_images(main_dir, screen_scale, ("ui", "skill_icon"), load_order=False)

    cooldown = pygame.Surface((skill_images["0"].get_width(), skill_images["0"].get_height()), pygame.SRCALPHA)
    cooldown.fill((230, 70, 80, 200))  # red colour filter for skill cooldown timer
    battleui.SkillCardIcon.cooldown = cooldown

    active_skill = pygame.Surface((skill_images["0"].get_width(), skill_images["0"].get_height()), pygame.SRCALPHA)
    active_skill.fill((170, 220, 77, 200))  # green colour filter for skill active timer
    battleui.SkillCardIcon.active_skill = active_skill

    return status_images, role_images, trait_images, skill_images
