from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.buff_id import BuffId as buff


class PhoenixMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('PhoenixMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        phoenixes = division.get_units(self.ai.iteration, unit.PHOENIX)
        units_in_position = 0
        attacking_friends = None
        division_position = None
        beaming_phoenixes_nb = 0
        beaming_phoenixes_max_nb = phoenixes.amount * 0.7
        for phoenix in phoenixes:
            if enemy.exists:
                flying_threats = self.ai.enemy_units().filter(
                    lambda z: z.is_flying and z.distance_to(phoenix.position) < 15 and z.type_id not in self.ai.units_to_ignore
                              and not z.is_hallucination and (z.can_attack_air or z.type_id in {unit.MEDIVAC,
                                                                                        unit.RAVEN, unit.VIPER}))
                # can_attack_air = threats.filter(lambda x: x.can_attack_air)
                # if can_attack_air.exists:
                #     threats = can_attack_air
                excluded_types = {unit.ZERGLING, unit.CHANGELING, unit.MARINE, unit.BROODLING}
                ground_threats = self.ai.enemy_units().filter(
                    lambda z: not z.is_flying and z.distance_to(phoenix.position) < 12 and z.type_id not in self.ai.units_to_ignore
                              and not z.is_hallucination and z.type_id not in excluded_types)
                # priority_ground_threats = ground_threats.filter(lambda x: x.type_id not in excluded_types)
                # if priority_ground_threats:
                #     ground_threats = priority_ground_threats
            else:
                ground_threats = None
                flying_threats = None

            abilities = await self.ai.get_available_abilities(phoenix)
            if ground_threats and beaming_phoenixes_nb < beaming_phoenixes_max_nb:

                if ability.GRAVITONBEAM_GRAVITONBEAM in abilities:
                    priority_ids = {unit.SIEGETANKSIEGED, unit.CYCLONE, unit.QUEEN, unit.WIDOWMINE, unit.GHOST,
                                    unit.INFESTOR, unit.WIDOWMINEBURROWED, unit.INFESTORBURROWED}
                    ground_priority = ground_threats.filter(lambda x: x.type_id in priority_ids)
                    if ground_priority:
                        targets = ground_priority
                    else:
                        can_attack_air = ground_threats.filter(lambda x: x.can_attack_air)
                        if can_attack_air.exists:
                            targets = can_attack_air
                        else:
                            targets = ground_threats
                    if targets:
                        target = targets.closest_to(phoenix)
                        close_own_units = self.ai.units.filter(lambda x: x.can_attack_air and
                                                x.distance_to(target) <= 6)
                        close_enemy = ground_threats.closer_than(7, target.position.towards(phoenix, 4))
                        if close_own_units.amount > close_enemy.amount / 1.5 and close_own_units.amount >= 3:
                            phoenix(ability.GRAVITONBEAM_GRAVITONBEAM, target)
                            beaming_phoenixes_nb += 1
            elif flying_threats:
                beamed_units = flying_threats.filter(lambda x: x.has_buff(buff.GRAVITONBEAM))
                if phoenix.shield_percentage < 0.80:
                    batteries = self.ai.structures().filter(lambda x: x.type_id == unit.SHIELDBATTERY and
                                                            x.energy > 10 and x.distance_to(phoenix)<=24)
                    if batteries:
                        phoenix.move(batteries.closest_to(phoenix))
                    else:
                        phoenix.move(phoenix.position.towards(flying_threats.closest_to(phoenix), -9))
                    continue
                if beamed_units:
                    flying_threats = beamed_units
                else:
                    close_threats = flying_threats.closer_than(6, phoenix)
                    if close_threats.exists:
                        flying_threats = close_threats

                priority = flying_threats.filter(lambda z: z.can_attack_air or z.type_id == unit.MEDIVAC) \
                    .sorted(lambda z: z.health + z.shield)
                if priority.exists:
                    target2 = priority[0]
                else:
                    target2 = flying_threats.sorted(lambda z: z.health + z.shield)[0]

                if target2 is not None:
                    attack_position = target2.position.towards(phoenix, 5)
                    if enemy.filter(lambda x: x.can_attack_air and x.distance_to(attack_position) <= 5).amount \
                        < self.ai.units.filter(lambda x: x.distance_to(attack_position) <= 6).amount/2:
                        phoenix.attack(target2)
            elif ability.GRAVITONBEAM_GRAVITONBEAM not in abilities and (ground_threats or flying_threats):
                if ground_threats:
                    closest_enemy = ground_threats.closest_to(phoenix)
                else:
                    closest_enemy = flying_threats.closest_to(phoenix)
                phoenix.move(phoenix.position.towards(closest_enemy, -7))
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