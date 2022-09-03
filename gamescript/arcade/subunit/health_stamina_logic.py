import random

infinity = float("inf")


def health_stamina_logic(self, dt):
    """Health and stamina calculation"""
    if self.subunit_health != infinity:
        if self.hp_regen > 0 and self.subunit_health % self.troop_health != 0:  # hp regen cannot resurrect troop only heal to max hp
            alive_hp = self.troop_number * self.troop_health  # max hp possible for the number of alive subunit
            self.subunit_health += self.hp_regen * dt  # regen hp back based on time and regen stat
            if self.subunit_health > alive_hp:
                self.subunit_health = alive_hp  # Cannot exceed health of alive subunit (exceed mean resurrection)
        elif self.hp_regen < 0:  # negative regen can kill
            self.subunit_health += self.hp_regen * dt  # use the same as positive regen (negative regen number * dt will reduce hp)

        if self.subunit_health < 0:
            self.subunit_health = 0  # can't have negative hp
        elif self.subunit_health > self.max_health:
            self.subunit_health = self.max_health  # hp can't exceed max hp (would increase number of troop)

        if self.old_subunit_health != self.subunit_health:
            remain = self.subunit_health / self.troop_health
            if remain.is_integer() is False:  # always round up if there is decimal number
                remain = int(remain) + 1
            else:
                remain = int(remain)
            loss = self.troop_number - remain
            wound = random.randint(0, loss)  # chance to be wounded instead of dead
            self.battle.death_troop_number[self.team] += loss - wound
            if self.state in (98, 99) and len(self.enemy_front) + len(
                    self.enemy_side) > 0:  # fleeing or broken got captured instead of wound
                self.battle.capture_troop_number[self.team] += wound
            else:
                self.battle.wound_troop_number[self.team] += wound
            self.troop_loss(loss)  # Recal number of troop again in case some destroyed from negative regen

            # v Health bar
            for index, health in enumerate(self.health_list):
                if self.subunit_health > health:
                    if self.last_health_state != abs(4 - index):
                        self.inspect_image_original3.blit(self.health_image_list[index + 1], self.health_image_rect)
                        self.block_original.blit(self.health_image_list[index + 1], self.health_block_rect)
                        self.block.blit(self.block_original, self.corner_image_rect)
                        self.last_health_state = abs(4 - index)
                        self.zoom_scale()
                    break

            self.old_subunit_health = self.subunit_health

    if self.stamina != infinity:
        if self.stamina < self.max_stamina:
            self.stamina = self.stamina + (dt * self.stamina_regen)  # regen
        else:  # stamina cannot exceed the max stamina
            self.stamina = self.max_stamina

        if self.old_last_stamina != self.stamina:
            for index, stamina in enumerate((self.stamina75, self.stamina50, self.stamina25, self.stamina5, -1)):
                if self.stamina >= stamina:
                    if self.last_stamina_state != abs(4 - index):
                        # if index != 3:
                        self.inspect_image_original3.blit(self.stamina_image_list[index + 6], self.stamina_image_rect)
                        self.zoom_scale()
                        self.block_original.blit(self.stamina_image_list[index + 6], self.stamina_block_rect)
                        self.block.blit(self.block_original, self.corner_image_rect)
                        self.last_stamina_state = abs(4 - index)
                    break

            self.old_last_stamina = self.stamina
