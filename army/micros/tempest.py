from army.micros.microABS import MicroABS
from bot.constants import AIR_PRIORITY_UNITS
from sc2.unit import UnitTypeId as unit


class TempestMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('TempestMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        tempests = division.get_units(self.ai.iteration, unit.TEMPEST)
        units_in_position = 0
        attacking_friends = None
        division_position = None
        dist = 20
        targets_dict = {}
        for tempest in tempests:
            if enemy.exists:
                threats = self.ai.enemy_units().filter(
                    lambda z: z.distance_to(tempest.position) < dist and z.type_id not in self.ai.units_to_ignore
                              and not z.is_hallucination)
                can_attack_air = threats.filter(lambda x: x.can_attack_air or x.type_id in AIR_PRIORITY_UNITS)
                if can_attack_air.exists:
                    threats = can_attack_air
                threats.extend(
                    self.ai.enemy_structures().filter(lambda z: z.distance_to(tempest.position) < 14 and
                                                                (z.can_attack_air or z.type_id == unit.BUNKER)))
            else:
                threats = None
            if threats:

                if tempest.weapon_cooldown == 0:
                    for target_ in targets_dict:
                        if tempest.target_in_range(target_):
                            total_dmg = sum(targets_dict[target_])
                            if total_dmg < target_.health + target_.shield:
                                targets_dict[target_].append(targets_dict[target_][0])
                                tempest.attack(target_)
                                continue
                closest = threats.closest_to(tempest.position)
                if threats.closer_than(9, tempest.position).amount > 2:
                    tempest.move(tempest.position.towards(closest.position, -5))
                    continue
                if closest.distance_to(tempest) < 12 and tempest.is_moving:
                    continue


                close_threats = threats.closer_than(8, tempest)
                if close_threats.exists:
                    threats = close_threats
                priority = threats.filter(lambda z: z.can_attack_air or z.type_id in AIR_PRIORITY_UNITS).sorted(
                    lambda z: (z.shield_max + z.health_max,  1 - z.shield_health_percentage), reverse=True)
                if priority.exists:
                    air_priority = priority.filter(lambda z: z.type_id in AIR_PRIORITY_UNITS)
                    if air_priority.exists:
                        target = air_priority[0]
                    else:
                        target = priority[0]
                else:
                    target = threats.sorted(
                    lambda z: (z.shield_max + z.health_max,  1 - z.shield_health_percentage), reverse=True)[0]
                if target is not None and tempest.weapon_cooldown == 0:
                    if target not in targets_dict:
                        targets_dict[target] = [tempest.calculate_damage_vs_target(target)[0]]
                    tempest.attack(target)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(self.ai.iteration)
                    division_position = division.get_position(self.ai.iteration)
                if division_position and tempest.distance_to(division_position) > division.max_units_distance:
                    tempest.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    tempest.attack(enemy.closest_to(attacking_friends.closest_to(tempest)))
                else:
                    units_in_position += 1
        return units_in_position