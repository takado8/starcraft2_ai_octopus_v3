from sc2.unit import UnitTypeId as unit

from army.attack.target_selector import TargetSelector
from bot.constants import BASES_IDS, WORKERS_IDS


class TargetSelectorAttack(TargetSelector):
    def __init__(self, ai):
        super().__init__(ai)
        self.enemy_main_base_down = False
        self.previous_destination = None

    def select_target(self):
        if self.ai.attack:
            enemy_units = self.ai.enemy_units()
            enemy = enemy_units.filter(
                lambda x: x.type_id not in self.ai.units_to_ignore and not x.is_hallucination and x.cloak != 1
                          and not x.is_snapshot and x.is_visible and x.type_id not in WORKERS_IDS and x.type_id not in {
                          unit.OVERLORD, unit.OVERSEER, unit.OVERLORDTRANSPORT} and (
                                      x.can_attack_ground or x.can_attack_air))
            enemy.extend(self.ai.enemy_structures().filter(lambda b: b.type_id in BASES_IDS or
                                                                     b.can_attack_ground or b.can_attack_air or b.type_id == unit.BUNKER))
            if not enemy:
                enemy = self.ai.enemy_structures()
            if self.enemy_main_base_down or (
                    self.ai.army.closer_than(17, self.ai.enemy_start_locations[0]).amount > 7 and
                    (not self.ai.enemy_structures().exists or self.ai.enemy_structures().closer_than(20,
                                                                                                     self.ai.enemy_start_locations[
                                                                                                         0]).amount < 3)):
                if not self.enemy_main_base_down:
                    # await self.ai.chat_send('enemy main base down.')
                    print('enemy main base down.')
                    self.enemy_main_base_down = True
                enemy.extend(self.ai.enemy_structures())

            if enemy.exists:
                if any([enemy.closer_than(40, townhall).amount > 3 for townhall in self.ai.townhalls]):
                    destination = enemy.closest_to(self.ai.start_location).position
                else:
                    if self.enemy_main_base_down:
                        destination = enemy
                    else:
                        destination = enemy.further_than(self.ai.start_location.position.distance_to(
                            self.ai.game_info.map_center), self.ai.start_location)

                    if destination.amount > 2 or destination.filter(lambda x: x.is_structure).exists:
                        destination = destination.closest_to(self.previous_destination if
                                                             self.previous_destination else self.ai.start_location).position
                    else:
                        destination = self.ai.enemy_start_locations[0].position
            elif not self.enemy_main_base_down:
                structures = self.ai.enemy_structures()
                if structures.exists:
                    destination = structures.closest_to(self.previous_destination if
                                                        self.previous_destination else self.ai.start_location)
                else:
                    destination = self.ai.enemy_start_locations[0].position
            else:
                destination = None
            if destination:
                self.previous_destination = destination
        else:
            destination = None
        return destination
