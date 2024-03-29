from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability


class VoidrayMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('VoidrayMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        void_rays = division.get_units(self.ai.iteration, unit.VOIDRAY)
        units_in_position = 0
        attacking_friends = None
        division_position = None
        for voidray in void_rays:
            if voidray.shield_percentage < 0.25:
                batteries = self.ai.structures().filter(lambda x: x.type_id == unit.SHIELDBATTERY and x.energy > 20 and
                                                        x.distance_to(voidray) < 14)
                if batteries:
                    voidray.move(batteries.closest_to(voidray).position)
                    continue
            if enemy.exists:
                threats = self.ai.enemy_units().filter(
                    lambda z: z.distance_to(voidray.position) < 12 and z.type_id not in self.ai.units_to_ignore
                              and not z.is_hallucination and z.cloak != 1)
                can_attack_air = threats.filter(lambda x: x.can_attack_air)
                if can_attack_air.exists:
                    threats = can_attack_air
                threats.extend(
                    self.ai.enemy_structures().filter(lambda z: z.distance_to(voidray.position) < 12 and
                                                                (z.can_attack_air or z.type_id == unit.BUNKER)))
            else:
                threats = None
            if threats:
                close_threats = threats.closer_than(4, voidray)
                if close_threats.exists:
                    threats = close_threats
                priority = threats.filter(lambda z: z.can_attack_air and z.is_armored) \
                    .sorted(lambda z: z.health + z.shield)
                if priority.exists:
                    target2 = priority[0]
                else:
                    target2 = threats.sorted(lambda z: z.health + z.shield)[0]
                if target2 is not None:
                    if target2.is_armored and target2.distance_to(voidray.position) < 7:
                        queue = False
                        abilities = await self.ai.get_available_abilities(voidray)
                        if ability.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities:
                            voidray(ability.EFFECT_VOIDRAYPRISMATICALIGNMENT)
                            queue = True
                        voidray.attack(target2, queue=queue)
                    elif not voidray.is_attacking:
                        voidray.attack(target2)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(self.ai.iteration)
                    division_position = division.get_position(self.ai.iteration)
                if division_position and voidray.distance_to(division_position) > division.max_units_distance:
                    voidray.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    voidray.attack(enemy.closest_to(attacking_friends.closest_to(voidray)))
                else:
                    units_in_position += 1
        return units_in_position