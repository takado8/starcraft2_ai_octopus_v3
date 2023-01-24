from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2 import Race
from .microABS import MicroABS


class StalkerMicro(MicroABS):
    def __init__(self, ai):
        self.name = 'StalkerMicro'
        super().__init__(self.name, ai)

    def select_target(self, targets, stalker):
        if self.ai.enemy_race == Race.Protoss:
            a = targets[0].shield_percentage
        else:
            a = 1
        if targets[0].health_percentage * a == 1:
            target = targets.closest_to(stalker)
        else:
            target = targets[0]
        return target

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        stalkers = division.get_units(self.ai.iteration, unit.STALKER)
        priority_ids = {unit.COLOSSUS, unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE, unit.GHOST, unit.VIPER,
                    unit.MEDIVAC, unit.SIEGETANKSIEGED, unit.SIEGETANK, unit.LIBERATOR, unit.INFESTOR, unit.CORRUPTOR,
                        unit.MUTALISK, unit.VIKING, unit.THOR, unit.BUNKER, unit.QUEEN}

        attacking_friends = None
        division_position = None
        dist = 10
        units_in_position = 0
        for stalker in stalkers:
            if enemy.exists:
                threats = enemy.filter(
                    lambda unit_: ((unit_.can_attack_ground and unit_.distance_to(stalker.position) <= dist and
                                  unit_.type_id not in self.ai.units_to_ignore) or unit_.type_id in priority_ids)
                                  and not unit_.is_hallucination)
                if self.ai.attack:
                    threats.extend(self.ai.enemy_structures().filter(lambda _x: (_x.can_attack_ground or _x.type_id == unit.BUNKER)
                                   and _x.distance_to(stalker) <= dist))
            else:
                threats = None
            if threats:
                close_threats = threats.closer_than(4, stalker)
                if close_threats.amount > 0:
                    threats = close_threats
                closest_enemy = threats.closest_to(stalker)
                priority = threats.filter(lambda x1: x1.type_id in priority_ids)
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, stalker)
                else:
                    targets = threats.filter(lambda x: x.is_armored)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, stalker)

                if stalker.shield_percentage < 0.4:
                    if stalker.health_percentage < 0.35:
                        stalker.move(self.find_back_out_position(stalker, closest_enemy.position))
                        continue
                    d = 4
                else:
                    d = 2

                if stalker.shield_percentage < 0.4 and upgrade.BLINKTECH in self.ai.state.upgrades and \
                        await self.is_blink_available(stalker):
                    back_out_position = self.find_blink_out_position(stalker, closest_enemy.position)
                    if back_out_position is not None and stalker.weapon_cooldown > 0:
                        await self.blink(stalker, back_out_position)
                    else:
                        stalker.attack(target)
                else:
                    back_out_position = self.find_back_out_position(stalker, closest_enemy.position)
                    if back_out_position is not None and stalker.weapon_cooldown > 0:
                        stalker.move(stalker.position.towards(back_out_position, d))
                    else:
                        stalker.attack(target)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(iteration=self.ai.iteration)
                    division_position = division.get_position(iteration=self.ai.iteration)
                if division_position and stalker.distance_to(division_position) > division.max_units_distance:
                    stalker.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    stalker.attack(enemy.closest_to(attacking_friends.closest_to(stalker)))
                else:
                    units_in_position += 1
        return units_in_position

    async def is_blink_available(self, stalker):
        abilities = await self.ai.get_available_abilities(stalker)
        return ability.EFFECT_BLINK_STALKER in abilities

    async def blink(self, stalker, target):
        stalker(ability.EFFECT_BLINK_STALKER, target)

    def find_blink_out_position(self, stalker, closest_enemy_position):
        i = 8
        position = stalker.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 14:
            position = stalker.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not self.in_grid(position) and j < 5:
                k = 0
                while not self.in_grid(position) and k < 7:
                    k += 1
                    position = position.random_on_distance(j * 2)
                j += 1
        return position

    def find_back_out_position(self, stalker, closest_enemy_position):
        i = 6
        position = stalker.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = stalker.position.towards(closest_enemy_position, -i)
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
