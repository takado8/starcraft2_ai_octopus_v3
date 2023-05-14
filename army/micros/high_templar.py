from army.micros.microABS import MicroABS
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability
import time


class HighTemplarMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('HighTemplarMicro', ai)
        self.last_storm_time = time.time()
        self.storm_cooldown_time = 2


    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        high_templars = division.get_units(self.ai.iteration, unit.HIGHTEMPLAR)
        reserved_targets_tags = set()
        units_in_position = 0
        for high_templar in high_templars:
            threats = enemy.closer_than(20, high_templar)
            close_threats = threats.closer_than(5, high_templar)
            if high_templar.energy < 50 or high_templar.is_idle or close_threats.amount > 2:
                army_nearby = self.ai.army.closer_than(30, high_templar.position)
                if close_threats:
                    high_templar.move(high_templar.position.towards(close_threats.closest_to(high_templar), -5))

                elif army_nearby.exists and threats.exists:
                    units_in_position += 1
                    if threats.exists:
                        high_templar.move(army_nearby.center.towards(threats.closest_to(high_templar), -3))
                elif army_nearby.exists:
                    high_templar.move(army_nearby.center)
                else:
                    high_templar.move(self.ai.army().exclude_type({unit.SENTRY, unit.HIGHTEMPLAR,
                                                                   unit.WARPPRISM, unit.WARPPRISMPHASING})
                                                                                    .closest_to(high_templar))
                continue
            elif threats:
                # Cast spells   ---> look for group of enemy
                spell_target = threats.filter(lambda x: x.type_id != unit.BROODLING)
                target = None
                abilities = await self.ai.get_available_abilities(high_templar)
                if time.time() - self.last_storm_time > self.storm_cooldown_time and\
                        spell_target.amount > 5 and ability.PSISTORM_PSISTORM in abilities:
                    maxNeighbours = 0
                    for en in spell_target:
                        neighbours = threats.filter(lambda u: u.distance_to(en) <= 1.5)
                        if neighbours.amount > maxNeighbours:
                            maxNeighbours = neighbours.amount
                            target = en
                    if target is not None and maxNeighbours + 1 > 5 and self.ai.army.closer_than(1.7, target).amount < 3:
                        print("Casting Psi Storm on " + str(maxNeighbours + 1) + " units.")
                        high_templar(ability.PSISTORM_PSISTORM, target.position)
                        self.last_storm_time = time.time()

                elif ability.FEEDBACK_FEEDBACK in abilities:
                    spell_target = spell_target.filter(lambda z: z.energy > 100 and z.type_id != unit.OVERSEER
                                            and z.tag not in reserved_targets_tags)
                    if spell_target.exists:
                        spell_target = spell_target.sorted(lambda z: z.energy, reverse=True)
                        target = spell_target[0]
                        print("Casting Feedback on " + target.name + " with " + str(target.energy) + " energy.")
                        high_templar(ability.FEEDBACK_FEEDBACK, target)
                        reserved_targets_tags.add(target.tag)

        return units_in_position

    def select_target(self, targets):
        total_hp_in_range_of_fire = {}
        _range = 1
        for target in targets:
            enemy_in_range = self.ai.enemy_units.filter(lambda x: x.distance_to(target) <= _range and\
                                                        x.type_id not in self.ai.units_to_ignore)
            total_hp_in_range_of_fire[target] = \
                (enemy_in_range.amount, sum([enemy.health + enemy.shield for enemy in enemy_in_range]))
        max_targets = max(total_hp_in_range_of_fire, key=lambda x: total_hp_in_range_of_fire[x][0])

        targets_with_max_count = {}
        for target in total_hp_in_range_of_fire:
            if total_hp_in_range_of_fire[target][0] == max_targets:
                targets_with_max_count[target] = total_hp_in_range_of_fire[target]

        min_hp = 99999999
        final_target = None
        for target in targets_with_max_count:
            if targets_with_max_count[target][1] < min_hp:
                min_hp = targets_with_max_count[target][1]
                final_target = target

        return final_target

    def find_back_out_position(self, archon, closest_enemy_position):
        i = 6
        position = archon.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = archon.position.towards(closest_enemy_position, -i)
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




