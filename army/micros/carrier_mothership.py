from army.micros.microABS import MicroABS
from bot.constants import AIR_PRIORITY_UNITS, UNITS_TO_IGNORE
from sc2.unit import UnitTypeId as unit
from sc2.ids.buff_id import BuffId as buff


class CarrierMothershipMicro(MicroABS):
    def __init__(self, ai, use_division_backout_position=None):
        super().__init__('CarrierMothershipMicro', ai, use_division_backout_position)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in UNITS_TO_IGNORE and
                                     not x.is_hallucination and not x.has_buff(buff.NEURALPARASITE))
        carriers = division.get_units(self.ai.iteration, unit.CARRIER)
        units_in_position = 0
        attacking_friends = None
        division_position = None
        dist = 12

        for carrier in carriers:
            if enemy.exists:
                threats = enemy.filter(
                    lambda z: z.distance_to(carrier.position) < dist)

                can_attack_air = threats.filter(lambda x: x.can_attack_air or x.is_detector)
                if can_attack_air.exists:
                    threats = can_attack_air
                threats.extend(
                    self.ai.enemy_structures().filter(lambda z: z.distance_to(carrier.position) < dist and
                                                                (z.can_attack_air or z.type_id == unit.BUNKER)))
            else:
                threats = None
            if carrier.shield_percentage <= 0.75:
                batteries = self.ai.structures().filter(lambda x: x.type_id == unit.SHIELDBATTERY and x.is_ready
                                                                  and x.energy > 20 and x.distance_to(
                    carrier) < 24)
                if batteries:
                    carrier.move(batteries.closest_to(carrier))
                    continue
            if threats:
                motherships = self.ai.units(unit.MOTHERSHIP).ready
                if motherships.exists:
                    mothership = motherships.first
                    if carrier.distance_to(mothership) > 5:
                        carrier.move(mothership)
                        continue
                closest = threats.closest_to(carrier)
                in_range_of = threats.filter(lambda x: x.can_attack_air and
                                                       x.distance_to(carrier.position) <= x.air_range + x.radius + 4)
                if in_range_of.exists:
                    total_dps = sum([x.air_dps for x in in_range_of])
                    if total_dps > 50 and carrier.shield_percentage < 0.85 or\
                            carrier.shield_percentage < 0.75:
                        batteries = self.ai.structures().filter(lambda x: x.type_id == unit.SHIELDBATTERY and x.is_ready
                                                                and x.energy > 20 and x.distance_to(carrier) < 24)
                        if batteries:
                            carrier.move(batteries.closest_to(carrier))
                            continue
                        if self.use_division_backout_position:
                            position = self.find_backout_position(division)
                        else:
                            position = carrier.position.towards(closest.position, -4)
                        carrier.move(carrier.position.towards(position, 4))
                        continue
                if (in_range_of and in_range_of.closest_to(carrier).distance_to(carrier) < 12 or not in_range_of and
                        closest.distance_to(carrier) < 12) and carrier.is_moving:
                    continue
                close_threats = threats.closer_than(7.5, carrier)
                if close_threats.exists:
                    threats = close_threats
                priority = threats.filter(lambda z: z.can_attack_air or z.type_id in AIR_PRIORITY_UNITS or z.is_detector).sorted(
                    lambda z: (z.shield_max + z.health_max,  1 - z.shield_health_percentage), reverse=True)
                if priority.exists:
                    air_priority = priority.filter(lambda z: z.type_id in AIR_PRIORITY_UNITS or z.is_detector)
                    if air_priority.exists:
                        target2 = air_priority[0]
                    else:
                        target2 = priority[0]
                else:
                    target2 = threats.sorted(
                    lambda z: (z.shield_max + z.health_max,  1 - z.shield_health_percentage), reverse=True)[0]
                if target2 is not None:
                    # queue = False
                    # if threats.closer_than(8, carrier).exists:
                    #     carrier.move(carrier.position.towards(threats.closest_to(carrier), -3))
                    carrier.attack(target2)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(self.ai.iteration)
                    division_position = division.get_position(self.ai.iteration)
                if division_position and carrier.distance_to(division_position) > division.max_units_distance:
                    carrier.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    carrier.attack(enemy.closest_to(attacking_friends.closest_to(carrier)))
                else:
                    units_in_position += 1
        interceptors = self.ai.units(unit.INTERCEPTOR)

        for interceptor in interceptors:

            enemies = self.ai.enemy_units().filter(lambda x: x.type_id not in UNITS_TO_IGNORE and not x.is_hallucination
                                                and x.distance_to(interceptor) < interceptor.ground_range + 1)
            if enemies:
                enemies = sorted(enemies, key=lambda x: (x.health, x.distance_to(interceptor)))
                interceptor.attack(enemies[0])
        return units_in_position

    def find_backout_position(self, division):
        if self.use_division_backout_position:
            backout_position = division.get_safety_backout_position(self.ai.iteration)
            if backout_position is not None:
                return backout_position