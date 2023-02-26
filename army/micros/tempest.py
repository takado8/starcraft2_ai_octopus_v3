from army.micros.microABS import MicroABS
from bot.constants import AIR_PRIORITY_UNITS
from sc2.unit import UnitTypeId as unit


class TempestMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('TempestMicro', ai)
        self.targets_dict = {}

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        tempests = division.get_units(self.ai.iteration, unit.TEMPEST)
        units_in_position = 0
        attacking_friends = None
        division_position = None
        dist = 20
        enemy_tag_unit_dict = {}
        for en in enemy:
            enemy_tag_unit_dict[en.tag] = en

        targets_to_remove = []
        for target in self.targets_dict:
            if target.tag in enemy_tag_unit_dict:
                self.targets_dict[enemy_tag_unit_dict[target.tag]] = [x for x in self.targets_dict[target]]
            targets_to_remove.append(target)
        for target in targets_to_remove:
            self.targets_dict.pop(target)

        for target in self.targets_dict:
            if target.health + target.shield - sum(self.targets_dict[target]) <= 0:
                try:
                    enemy.remove(target)
                except:
                    pass
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
                    target_selected = False
                    for target_ in self.targets_dict:
                        if tempest.target_in_range(target_):
                            total_dmg = sum(self.targets_dict[target_])
                            target_hp = target_.health + target_.shield
                            if target_hp - total_dmg > 0:
                                dmg = self.targets_dict[target_][0]
                                self.targets_dict[target_].append(dmg)
                                tempest.attack(target_)
                                if target_hp - total_dmg - dmg <= 0:
                                    try:
                                        enemy.remove(target_)
                                    except:
                                        pass
                                target_selected = True
                                break
                    if target_selected:
                        continue
                closest = threats.closest_to(tempest.position)
                in_range_of = threats.filter(lambda x: x.can_attack_air and
                                                       x.distance_to(tempest.position) <= x.air_range + x.radius + 4)
                if in_range_of.exists:
                    total_dps = sum([x.air_dps for x in in_range_of])
                    if total_dps > 50 and tempest.shield_percentage < 0.85 or \
                            tempest.shield_percentage < 0.85 and tempest.health_percentage < 0.85:
                        tempest.move(tempest.position.towards(closest.position, -4))
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
                    if target not in self.targets_dict:
                        self.targets_dict[target] = [tempest.calculate_damage_vs_target(target)[0]]
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