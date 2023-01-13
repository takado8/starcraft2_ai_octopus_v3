from army.micros.microABS import MicroABS
from bot.constants import AIR_PRIORITY_UNITS
from sc2.unit import UnitTypeId as unit


class TempestMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('TempestMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        tempests = division.get_units(unit.TEMPEST)
        units_in_position = 0
        for tempest in tempests:
            threats = self.ai.enemy_units().filter(
                lambda z: z.distance_to(tempest.position) < 16 and z.type_id not in self.ai.units_to_ignore
                          and not z.is_hallucination)
            can_attack_air = threats.filter(lambda x: x.can_attack_air)
            if can_attack_air.exists:
                threats = can_attack_air
            threats.extend(
                self.ai.enemy_structures().filter(lambda z: z.distance_to(tempest.position) < 11 and
                                                            (z.can_attack_air or z.type_id == unit.BUNKER)))
            if threats.exists:
                if threats.closer_than(9, tempest.position).exists:
                    tempest.move(tempest.position.towards(threats.closest_to(tempest.position).position, -5))
                    continue
                priority = threats.filter(lambda z: z.can_attack_air or z.type_id in AIR_PRIORITY_UNITS).sorted(
                    lambda z: z.health + z.shield, reverse=False)
                if priority.exists:
                    air_priority = priority.filter(lambda z: z.type_id in AIR_PRIORITY_UNITS)
                    if air_priority.exists:
                        target2 = air_priority[0]
                    else:
                        target2 = priority[0]
                else:
                    target2 = threats.sorted(lambda z: z.health + z.shield)[0]
                if target2 is not None:
                    tempest.attack(target2)
            else:
                attacking_friends = division.get_attacking_units()
                division_position = division.get_position()
                if attacking_friends.exists and enemy.exists:
                    tempest.attack(enemy.closest_to(attacking_friends.closest_to(tempest)))
                elif division_position and tempest.distance_to(division_position) > division.max_units_distance:
                    tempest.attack(division_position)
                else:
                    units_in_position += 1
        return units_in_position