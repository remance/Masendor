from pygame import Surface

from engine.effect.effect import ChargeDamageEffect
from engine.uibattle.uibattle import SpriteIndicator


def spawn_troop(self):
    from engine.unit.unit import Troop

    for troop_id, number in self.troop_dead_list.items():
        if troop_id in self.troop_reserve_list and self.troop_reserve_list[troop_id]:
            spawn_pos = self.current_camp_pos
            if not spawn_pos:  # not at camp, spawn at the main camp
                spawn_pos = self.camp_pos[0]
            add_unit = Troop(troop_id, self.battle.last_troop_game_id, None, self.team,
                             spawn_pos, self.angle, self.start_hp,
                             self.start_stamina, self, self.coa)
            add_unit.hitbox = ChargeDamageEffect(add_unit, add_unit.hitbox_image)
            add_unit.effectbox = SpriteIndicator(Surface((0, 0)), add_unit, layer=10000001)
            add_unit.enter_battle(self.battle.unit_animation_pool,
                                  self.battle.status_animation_pool)
            self.troop_dead_list[troop_id] -= 1
            self.battle.last_troop_game_id += 1
            self.troop_reserve_list[troop_id] -= 1

        if not self.troop_reserve_list[troop_id]:  # troop reserve run out, remove from dict
            self.troop_reserve_list.pop(troop_id)

    self.find_formation_size(troop=True)
    self.change_formation("troop")
    self.reserve_ready_timer = 0
