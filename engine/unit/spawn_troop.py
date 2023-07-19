from pygame import Surface

from engine.effect.effect import ChargeDamageEffect
from engine.uibattle.uibattle import SpriteIndicator


def spawn_troop(self):
    """
    Spawn new troops from camp
    :param self: Unit object
    """
    from engine.unit.unit import Troop

    spawn_pos = None

    if self.current_camp and not self.camp_enemy_check[self.current_camp]:
        spawn_pos = self.current_camp_pos
    elif not self.camp_enemy_check[0]:  # not at camp, spawn at the main camp
        spawn_pos = self.camp_pos[0]
    if spawn_pos:  # has camp to spawn
        for troop_id, number in self.troop_dead_list.items():
            if number and troop_id in self.troop_reserve_list and self.troop_reserve_list[troop_id]:
                add_unit = Troop(troop_id, self.battle.last_troop_game_id, None, self.team,
                                 spawn_pos, self.angle, self.start_hp,
                                 self.start_stamina, self, self.coa)
                add_unit.hitbox = ChargeDamageEffect(add_unit)
                add_unit.effectbox = SpriteIndicator(Surface((0, 0)), add_unit, layer=10000001)
                add_unit.enter_battle(self.battle.unit_animation_pool,
                                      self.battle.status_animation_pool)
                self.troop_dead_list[troop_id] -= 1
                self.battle.last_troop_game_id += 1
                self.troop_reserve_list[troop_id] -= 1

                if not self.troop_reserve_list[troop_id]:  # troop reserve run out, remove from dict
                    self.troop_reserve_list.pop(troop_id)
                break

        self.find_formation_size(troop=True)
        self.change_formation("group")
        self.reserve_ready_timer = 0
