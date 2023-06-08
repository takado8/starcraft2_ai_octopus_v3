from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2 import Race

from bot.constants import WORKERS_IDS
from .microABS import MicroABS


class StalkerMicro(MicroABS):
    def __init__(self, ai, use_division_backout_position=None):
        super().__init__('StalkerMicro', ai, use_division_backout_position)

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
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore and not x.is_snapshot)
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
                    lambda unit_: (unit_.can_attack_ground or unit_.type_id in priority_ids) and
                                  unit_.distance_to(stalker.position) < dist and
                                  unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination
                                and not unit_.is_snapshot and unit_.is_visible and unit_.cloak != 1)
                if self.ai.attack:
                    threats.extend(self.ai.enemy_structures().filter(lambda x: x.can_attack_ground and not x.is_snapshot
                                                                               and x.distance_to(stalker) < dist))
                    if self.ai.enemy_race == Race.Terran:
                        # deal with terran bunkers
                        bunkers = self.ai.enemy_structures().filter(lambda x: x.type_id == unit.BUNKER and x.distance_to(stalker) < dist)
                        if bunkers:
                            closest_bunker = bunkers.closest_to(stalker)

                            # try to go pass over it
                            closest_minerals = self.ai.mineral_field.closest_to(closest_bunker)
                            # can_pass = await self.ai._client.query_pathing(stalker.position, closest_minerals.position)
                            # if can_pass:
                            # avoid bunker range
                            # if stalker.distance_to(closest_bunker) < 8:
                            #     stalker.move(stalker.position.towards(closest_bunker, -4))
                            #     continue
                            # go kill tanks
                            tanks = enemy.filter(lambda x: x.type_id in {unit.SIEGETANK, unit.SIEGETANKSIEGED}
                                                           and not x.is_snapshot)
                            if tanks:
                                threats = tanks
                            # or workers if no threats
                            elif not threats:
                                workers = enemy.filter(lambda x: x.type_id in {unit.SCV, unit.MULE} and
                                                       x.distance_to(closest_minerals) < 10)
                                threats = workers


                            elif not threats or not any([t.target_in_range(stalker) for t in threats]):
                                workers_near_bunkers = enemy.filter(lambda x: x.type_id == unit.SCV and
                                                                      any([x.distance_to(building) < 3 for building in
                                                                           bunkers]))
                                if workers_near_bunkers:
                                    threats = workers_near_bunkers
                                else:
                                    threats = bunkers
                        # # get on ramp and kill tanks
                        # enemy_main_ramp = self.ai.enemy_main_base_ramp
                        # if stalker.distance_to(enemy_main_ramp.bottom_center) < 14 and enemy.exists:
                        #     if stalker.distance_to(enemy_main_ramp.top_center) > 4 and threats.closer_than(
                        #         6, stalker).exists:
                        #         threats_in_range = threats.in_attack_range_of(stalker)
                        #         if stalker.weapon_ready and threats_in_range.exists:
                        #             stalker.attack(self.select_target(threats_in_range, stalker))
                        #         else:
                        #             stalker.move(enemy_main_ramp.top_center)
                        #         continue

                        # deal with terran wall
                        if not threats or threats.exists and not threats.in_attack_range_of(stalker):
                            enemy_main_ramp = self.ai.enemy_main_base_ramp.top_center

                            wall_buildings = self.ai.enemy_structures().filter(lambda x: x.type_id in {unit.SUPPLYDEPOT,
                                    unit.BARRACKS,unit.BARRACKSREACTOR} and x.distance_to(enemy_main_ramp) < 5 and
                                                                                         x.distance_to(stalker) < dist)
                            if wall_buildings.amount >= 3:
                                workers_near_wall = enemy.filter(lambda x: x.type_id == unit.SCV and
                                                                   any([x.distance_to(building) < 3 for building in
                                                                        wall_buildings]))
                                if workers_near_wall:
                                    threats = workers_near_wall
                                else:
                                    threats = wall_buildings
            else:
                threats = None
            if threats:
                closest_enemy = None
                target = None
                for i in range(2, dist + 4, 2):
                    close_threats = threats.closer_than(i, stalker)
                    if not close_threats:
                        continue
                    closest_enemy = close_threats.closest_to(stalker)
                    priority = close_threats.filter(lambda x1: x1.type_id in priority_ids)
                    if priority.exists:
                        targets = priority.sorted(lambda x1: x1.health + x1.shield)
                        target = self.select_target(targets, stalker)
                    else:
                        targets = close_threats.filter(lambda x: x.is_armored)
                        if not targets.exists:
                            targets = close_threats
                        targets = targets.sorted(lambda x1: x1.health + x1.shield)
                        target = self.select_target(targets, stalker)
                    if target:
                        break

                if stalker.shield_percentage < 0.4:
                    if stalker.health_percentage < 0.35:
                        if not closest_enemy and enemy:
                            closest_enemy = enemy.closest_to(stalker)
                        if closest_enemy:
                            stalker.move(self.find_back_out_position(stalker, closest_enemy.position, division))
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
                    back_out_position = self.find_back_out_position(stalker, closest_enemy.position, division)\
                                                if closest_enemy else None
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

    def find_back_out_position(self, stalker, closest_enemy_position, division):
        if self.use_division_backout_position:
            backout_position = division.get_safety_backout_position(self.ai.iteration)
            if backout_position is not None:
                return backout_position
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
