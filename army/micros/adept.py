from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2 import Race


class AdeptMicro(MicroABS):

    def __init__(self, ai):
        super().__init__('AdeptMicro', ai)
        self.enemy_base_idx = 0
        expansions = sorted(self.ai.expansion_locations,
                            key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        self.mineral_lines = [self.ai.mineral_field.closer_than(9, exp).center.towards(exp, -2)
                              for exp in expansions][:5]


    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        adepts = division.get_units(self.ai.iteration, unit.ADEPT)
        if self.ai.attack:
            for adept in adepts:
                workers = self.ai.enemy_units().filter(lambda x: x.distance_to(adept) < 17 and x.type_id in
                                                                 self.ai.workers_ids)
                threats = enemy.filter(
                    lambda unit_: unit_.can_attack_ground and unit_.distance_to(adept.position) <= 9 and
                                  unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination and
                                  not unit_.is_flying)
                if workers.amount < 3 or threats.amount > 2:
                    queue = False
                    if ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT in await self.ai.get_available_abilities(adept):
                        adept(ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT, adept.position)
                        queue = True
                    if threats.exists:
                        closer_enemy = threats.closer_than(3, adept)
                        if closer_enemy:
                            threats = closer_enemy
                        closest_enemy = threats.closest_to(adept)
                        priority = threats.filter(
                            lambda x1: x1.type_id in {unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                                                      unit.QUEEN})
                        if priority.exists:
                            targets = priority.sorted(lambda x1: x1.health + x1.shield)
                            target = self.select_target(targets, adept)
                        else:
                            targets = threats.filter(lambda x: x.is_light)
                            if not targets.exists:
                                targets = threats
                            targets = targets.sorted(lambda x1: x1.health + x1.shield)
                            target = self.select_target(targets, adept)

                        if adept.shield_percentage < 0.4:
                            if adept.health_percentage < 0.35:
                                adept.move(self.find_back_out_position(adept, closest_enemy.position), queue=queue)
                                continue
                            d = 4
                        else:
                            d = 2

                        back_out_position = self.find_back_out_position(adept, closest_enemy.position)
                        if back_out_position is not None and adept.weapon_cooldown > 0:
                            adept.move(adept.position.towards(back_out_position, d), queue=queue)
                        else:
                            adept.attack(target, queue=queue)
                elif workers.amount > 1:
                    workers_in_range = workers.closer_than(5, adept)
                    if workers_in_range.exists:
                        workers_in_range = sorted(workers_in_range, key=lambda x: x.health + x.shield)
                        target3 = workers_in_range[0]
                    else:
                        target3 = workers.closest_to(adept)
                    if adept.weapon_cooldown == 0:
                        adept.attack(target3)
            for shadow in self.ai.units(unit.ADEPTPHASESHIFT):
                workers = self.ai.enemy_units().filter(lambda x: x.distance_to(shadow) < 12 and x.type_id in
                                                                 self.ai.workers_ids)
                threats = self.ai.enemy_units().filter(lambda x: x.distance_to(shadow) < 9 and x.type_id not in
                                                                 self.ai.workers_ids)
                if workers.amount > 3 and threats.amount < 5:
                    workers = sorted(workers, key=lambda x: x.health + x.shield)
                    shadow.move(workers[0])
                else:
                    shadow.move(self.mineral_lines[self.enemy_base_idx])
                    if shadow.distance_to(self.mineral_lines[self.enemy_base_idx]) < 2:
                        self.enemy_base_idx += 1
                        if self.enemy_base_idx > 2:
                            self.enemy_base_idx = 0

        return adepts.amount

    def select_target(self, targets, adept):
        if self.ai.enemy_race == Race.Protoss:
            a = targets[0].shield_percentage
        else:
            a = 1
        if targets[0].health_percentage * a == 1:
            target = targets.closest_to(adept)
        else:
            target = targets[0]
        return target

    def find_back_out_position(self, adept, closest_enemy_position):
        i = 6
        position = adept.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = adept.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not self.in_grid(position) and j < 5:
                k = 0
                distance = j * 2
                while not self.in_grid(position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position

