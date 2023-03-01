from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability


class PhoenixMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('PhoenixMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        phoenixes = division.get_units(self.ai.iteration, unit.PHOENIX)
        units_in_position = 0
        attacking_friends = None
        division_position = None
        for phoenix in phoenixes:
            if enemy.exists:
                threats = self.ai.enemy_units().filter(
                    lambda z: z.is_flying and z.distance_to(phoenix.position) < 12 and z.type_id not in self.ai.units_to_ignore
                              and not z.is_hallucination)
                can_attack_air = threats.filter(lambda x: x.can_attack_air)
                if can_attack_air.exists:
                    threats = can_attack_air
                threats.extend(
                    self.ai.enemy_structures().filter(lambda z: z.distance_to(phoenix.position) < 12 and
                                                                (z.can_attack_air or z.type_id == unit.BUNKER)))
            else:
                threats = None
            if threats:
                close_threats = threats.closer_than(6, phoenix)
                if close_threats.exists:
                    threats = close_threats
                priority = threats.filter(lambda z: z.can_attack_air) \
                    .sorted(lambda z: z.health + z.shield)
                if priority.exists:
                    target2 = priority[0]
                else:
                    target2 = threats.sorted(lambda z: z.health + z.shield)[0]
                if target2 is not None:

                    # elif not phoenix.is_attacking:
                    phoenix.attack(target2)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(self.ai.iteration)
                    division_position = division.get_position(self.ai.iteration)
                if division_position and phoenix.distance_to(division_position) > division.max_units_distance:
                    phoenix.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    attacking_enemy = enemy.closest_to(attacking_friends.closest_to(phoenix))
                    if attacking_enemy.is_flying:
                        phoenix.attack(attacking_enemy)
                else:
                    units_in_position += 1
        return units_in_position