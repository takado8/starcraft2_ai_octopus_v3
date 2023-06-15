from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2 import Race

from bot.constants import WORKERS_IDS
from .microABS import MicroABS


class StalkerBlinkMicro(MicroABS):
    def __init__(self, ai, use_division_backout_position=None, blink_locations=None):
        super().__init__('StalkerBlinkMicro', ai, use_division_backout_position)
        self.targets_dict = {}
        self.blink_locations = blink_locations

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
        dist = 14
        units_in_position = 0
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
        enemy_main_base = self.ai.enemy_start_locations[0]

        if self.blink_locations and self.ai.attack and self.ai.time < 900:
            blink_to_location = self.blink_locations[0].towards(enemy_main_base, 12)
            blink_location_height = self.ai.mineral_field.closest_to(self.blink_locations[0]).position3d.z
            enemy_main_base_height = self.ai.mineral_field.closest_to(enemy_main_base).position3d.z
            sentries = division.get_units(self.ai.iteration, unit.SENTRY)
            hallucinated_warp_prisms = self.ai.units().filter(lambda x: x.type_id == unit.WARPPRISM and
                                                                    x.is_hallucination)
            if sentries:
                division_position = division.get_position(iteration=self.ai.iteration)
                for sentry in sentries:
                    if not hallucinated_warp_prisms.exists and sentry.energy >= 75 and stalkers and\
                            (stalkers.closer_than(30, self.blink_locations[0]).amount >= 3 or
                             stalkers.closer_than(30, self.blink_locations[1]).amount >= 3):
                        sentry(ability.HALLUCINATION_WARPPRISM)
                    elif division_position and sentry.distance_to(division_position) > 7:
                        sentry.move(division_position)
                    elif not division_position:
                        if stalkers:
                            sentry.move(stalkers.closest_to(sentry))
                        else:
                            sentry.move(self.ai.defend_position)
            if hallucinated_warp_prisms.exists:
                flying_units = hallucinated_warp_prisms
            else:
                flying_units = self.ai.units().filter(lambda x: x.is_flying and x.type_id != unit.PHOENIX)
            if flying_units and not any([f.distance_to(self.blink_locations[0]) < 4 for f in flying_units]) and stalkers:
                flying_units.closest_to(self.blink_locations[0]).move(self.blink_locations[0])
            # else:
            #     for f in flying_units:
            #         if f.distance_to(self.blink_locations[0]) > 8 and f.distance_to(self.blink_locations[1]) > 5:
            #             f.move(self.blink_locations[1])
        else:
            enemy_main_base_height = 0
            blink_location_height = 0
            flying_units = []
            blink_to_location = None

        for stalker in stalkers:
            if self.ai.attack:
                stalker_on_main_base_lvl = abs(enemy_main_base_height - stalker.position3d.z) < \
                        abs(blink_location_height - stalker.position3d.z)
                if self.blink_locations and not stalker_on_main_base_lvl:
                    stalker_dist_to_blink = stalker.distance_to(self.blink_locations[0])
                    stalker_dist_to_wait_spot = stalker.distance_to(self.blink_locations[1])
                    if stalker_dist_to_wait_spot < 3 and stalkers.closer_than(6, self.blink_locations[1]).amount >= 3 \
                            and await self.is_blink_available(stalker) and flying_units and \
                             flying_units.closer_than(5,self.blink_locations[0]):
                        stalker.attack(self.blink_locations[0])
                    elif stalker_dist_to_blink < 5 and await self.is_blink_available(stalker):
                        await self.blink(stalker, blink_to_location)
                        continue
                    elif stalker_dist_to_blink > 3 and stalker_dist_to_wait_spot > 45:
                        stalker.attack(self.blink_locations[1])
                        continue
            else:
                stalker_on_main_base_lvl = False
            if enemy.exists:
                threats = enemy.filter(
                    lambda unit_: (unit_.can_attack_ground or unit_.type_id in priority_ids) and
                                  unit_.distance_to(stalker.position) < dist and
                                  unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination
                                and not unit_.is_snapshot and unit_.is_visible and unit_.cloak != 1)
                if self.ai.attack:
                    threats.extend(self.ai.enemy_structures().filter(lambda x: x.can_attack_ground and not x.is_snapshot
                                                                               and x.distance_to(stalker) < dist))
                    if self.ai.time < 900:
                        # blink to main base
                        if self.blink_locations and not stalker_on_main_base_lvl:
                            if not threats or not threats.in_attack_range_of(stalker):
                                stalker.attack(self.blink_locations[0])
                            elif not stalker.weapon_ready and sum([t.ground_dps for t in threats]) < 20:
                                stalker.move(self.blink_locations[0])
                                continue

                            # deal with terran wall
                            if not threats or threats.exists and not threats.in_attack_range_of(stalker):
                                enemy_main_ramp = self.ai.enemy_main_base_ramp.top_center

                                wall_buildings = self.ai.enemy_structures().filter(
                                    lambda x: x.type_id in {unit.SUPPLYDEPOT,
                                                            unit.BARRACKS, unit.BARRACKSREACTOR} and x.distance_to(
                                        enemy_main_ramp) < 5 and
                                              x.distance_to(stalker) < dist)
                                if wall_buildings.amount >= 3:
                                    if await self.is_blink_available(stalker):
                                        blink_spot = self.ai.enemy_main_base_ramp.top_center.towards(
                                            self.ai.enemy_main_base_ramp.bottom_center, -8)
                                        await self.blink(stalker, blink_spot)
                                        continue
                                    workers_near_wall = enemy.filter(lambda x: x.type_id == unit.SCV and
                                                                               any([x.distance_to(building) < 3 for
                                                                                    building in
                                                                                    wall_buildings]))
                                    if workers_near_wall:
                                        threats = workers_near_wall
                                    else:
                                        threats = wall_buildings
                        if stalker_on_main_base_lvl:
                            main_base_minerals = self.ai.mineral_field.closest_to(enemy_main_base)
                            if (not threats or not threats.in_attack_range_of(stalker) or 1 > stalker.weapon_cooldown > 0) and\
                                    stalker.distance_to(enemy_main_base) > 14:
                                stalker.move(main_base_minerals)
                                continue

                    if self.ai.enemy_race == Race.Terran:
                        # deal with tanks
                        tanks = enemy.filter(lambda x: x.type_id in {unit.SIEGETANK, unit.SIEGETANKSIEGED}
                                                       and not x.is_snapshot)
                        if tanks:
                            threats = tanks
                        else:
                            bunkers = self.ai.enemy_structures().filter(lambda x: x.type_id == unit.BUNKER and x.distance_to(stalker) < dist)
                            if bunkers:
                                closest_bunker = bunkers.closest_to(stalker)
                                closest_minerals = self.ai.mineral_field.closest_to(closest_bunker)

                                if not threats:
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
                    if not enemy.exists and stalker.distance_to(enemy_main_base) < 15:
                        threats = self.ai.enemy_structures()
            else:
                threats = None
            if threats:
                if stalker.weapon_cooldown == 0:
                    target_selected = False
                    for target_ in self.targets_dict:
                        if stalker.target_in_range(target_):
                            total_dmg = sum(self.targets_dict[target_])
                            target_hp = target_.health + target_.shield
                            if target_hp - total_dmg > 0:
                                dmg = self.targets_dict[target_][0]
                                self.targets_dict[target_].append(dmg)
                                stalker.attack(target_)
                                if target_hp - total_dmg - dmg <= 0:
                                    try:
                                        enemy.remove(target_)
                                    except:
                                        pass
                                target_selected = True
                                break
                    if target_selected:
                        continue
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
                            if upgrade.BLINKTECH in self.ai.state.upgrades and await self.is_blink_available(stalker):
                                back_out_position = self.find_blink_out_position(stalker, closest_enemy.position)
                                if back_out_position is not None and stalker.weapon_cooldown > 0:
                                    await self.blink(stalker, back_out_position)
                            else:
                                stalker.move(self.find_back_out_position(stalker, closest_enemy.position, division))
                        continue
                    d = 4
                else:
                    d = 2
                if not closest_enemy and enemy:
                    closest_enemy = enemy.closest_to(stalker)
                if stalker.shield_percentage < 0.4 and upgrade.BLINKTECH in self.ai.state.upgrades and \
                        await self.is_blink_available(stalker):

                    if stalker.weapon_cooldown > 0:
                        back_out_position = self.find_blink_out_position(stalker, closest_enemy.position)
                        if back_out_position is not None:
                            await self.blink(stalker, back_out_position)
                    elif target:
                        if target not in self.targets_dict:
                            self.targets_dict[target] = [stalker.calculate_damage_vs_target(target)[0]]
                        stalker.attack(target)
                else:
                    if stalker.weapon_cooldown > 0:
                        if stalker.shield_percentage < 1:
                            back_out_position = self.find_back_out_position(stalker, closest_enemy.position, division) \
                                if closest_enemy else None
                            if back_out_position is not None:
                                stalker.move(stalker.position.towards(back_out_position, d))
                        elif not enemy.in_attack_range_of(stalker).exists and threats.exists:
                            stalker.move(stalker.position.towards(threats.closest_to(stalker.position)))
                    elif target:
                        queue = False
                        if upgrade.BLINKTECH in self.ai.state.upgrades and not stalker.target_in_range(target) and\
                                await self.is_blink_available(stalker):
                            if enemy.closer_than(6, target.position).amount < 8 \
                                and stalker.distance_to(target) > 8:
                                await self.blink(stalker, target.position.towards(stalker.position, 5))
                                queue = True

                        if target not in self.targets_dict:
                            self.targets_dict[target] = [stalker.calculate_damage_vs_target(target)[0]]
                        stalker.attack(target, queue=queue)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(iteration=self.ai.iteration)
                    division_position = division.get_position(iteration=self.ai.iteration)
                if division_position and stalker.distance_to(division_position) > division.max_units_distance:
                    stalker.move(division_position)
                elif attacking_friends.exists and enemy.exists:
                    stalker.move(attacking_friends.closest_to(stalker))
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
