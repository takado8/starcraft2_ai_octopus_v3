from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability

from bot.constants import BASES_IDS


class VoidrayCannonDefenseMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('VoidrayMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore and x.cloak != 1)
        void_rays = division.get_units(self.ai.iteration, unit.VOIDRAY)
        units_in_position = 0
        attacking_friends = None
        division_position = None
        for voidray in void_rays:
            if enemy.exists:

                threats = self.ai.enemy_units().filter(
                    lambda z: z.distance_to(voidray.position) < 12 and z.type_id not in self.ai.units_to_ignore
                              and not z.is_hallucination)
                can_attack_air = threats.filter(lambda x: x.can_attack_air)
                if can_attack_air.exists:
                    threats = can_attack_air
                threats.extend(
                    self.ai.enemy_structures().filter(lambda z: z.distance_to(voidray.position) < 12 and
                                        (z.can_attack_air or z.type_id == unit.BUNKER or z.type_id in BASES_IDS)))
            else:
                threats = None
            # if not self.ai.strategy.attack.enemy_main_base_down:
                # enemy_cannons = self.ai.enemy_structures().filter(lambda s:
                #                                                   s.type_id in {unit.PHOTONCANNON,
                #                                                                 unit.BUNKER} and s.distance_to(
                #                                                       voidray) < s.air_range + s.radius + 1)
                # if enemy_cannons:
                #     voidray.move(voidray.position.towards(enemy_cannons.closest_to(voidray), -3))
                #     continue
            if voidray.shield_percentage < 0.45:
                batteries = self.ai.structures().filter(lambda x: x.type_id == unit.SHIELDBATTERY and x.energy > 20 and
                                                        x.distance_to(voidray) < 25)
                if batteries:
                    voidray.move(batteries.closest_to(voidray).position)
                    continue
            if threats:
                motherships = self.ai.units(unit.MOTHERSHIP).ready
                if motherships.exists:
                    mothership = motherships.first
                    if voidray.distance_to(mothership) > 5:
                        voidray.move(mothership)
                        continue

                    detectors = enemy.filter(lambda x: x.is_detector and
                                                       x.distance_to(voidray) < 7)
                    detectors.extend(self.ai.enemy_structures().filter(lambda x: x.is_detector and
                                                                                 x.distance_to(voidray) < 7))
                    if detectors.exists:
                        threats = detectors
                        target = threats.sorted(lambda z: z.health + z.shield)[0]
                        if target.is_armored and target.distance_to(voidray.position) < 7:
                            queue = False
                            abilities = await self.ai.get_available_abilities(voidray)
                            if ability.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities:
                                voidray(ability.EFFECT_VOIDRAYPRISMATICALIGNMENT)
                                queue = True
                            voidray.attack(target, queue=queue)
                        elif not voidray.is_attacking:
                            voidray.attack(target)
                            continue

                close_threats = threats.closer_than(4, voidray)
                if close_threats.exists:
                    threats = close_threats
                priority = threats.filter(lambda z: z.can_attack_air and z.is_armored) \
                    .sorted(lambda z: z.health + z.shield)
                if priority.exists:
                    target = priority[0]
                else:
                    target = threats.sorted(lambda z: z.health + z.shield)[0]
                if target is not None:
                    if target.is_armored and target.distance_to(voidray.position) < 7:
                        queue = False
                        abilities = await self.ai.get_available_abilities(voidray)
                        if ability.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities:
                            voidray(ability.EFFECT_VOIDRAYPRISMATICALIGNMENT)
                            queue = True
                        voidray.attack(target, queue=queue)
                    elif not voidray.is_attacking:
                        voidray.attack(target)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(self.ai.iteration)
                    division_position = division.get_position(self.ai.iteration)
                if division_position and voidray.distance_to(division_position) > division.max_units_distance \
                        and not self.ai.strategy.attack.enemy_main_base_down:
                    voidray.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    voidray.attack(enemy.closest_to(attacking_friends.closest_to(voidray)))
                else:
                    units_in_position += 1
        return units_in_position