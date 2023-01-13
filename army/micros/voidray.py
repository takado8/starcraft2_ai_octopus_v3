from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability


class VoidrayMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('VoidrayMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        void_rays = division.get_units(unit.VOIDRAY)
        units_in_position = 0
        for voidray in void_rays:
            threats = self.ai.enemy_units().filter(
                lambda z: z.distance_to(voidray.position) < 12 and z.type_id not in self.ai.units_to_ignore
                          and not z.is_hallucination)
            can_attack_air = threats.filter(lambda x: x.can_attack_air)
            if can_attack_air.exists:
                threats = can_attack_air
            threats.extend(
                self.ai.enemy_structures().filter(lambda z: z.distance_to(voidray.position) < 15 and
                                                            (z.can_attack_air or z.type_id == unit.BUNKER)))
            if threats.exists:
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
                attacking_friends = division.get_attacking_units()
                division_position = division.get_position()
                if attacking_friends.exists and enemy.exists:
                    voidray.attack(enemy.closest_to(attacking_friends.closest_to(voidray)))
                elif division_position and voidray.distance_to(division_position) > division.max_units_distance:
                    voidray.attack(division_position)
                else:
                    units_in_position += 1
        return units_in_position