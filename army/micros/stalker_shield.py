from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.buff_id import BuffId as buff
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2 import Race

from bot.constants import WORKERS_IDS, BASES_IDS
from .microABS import MicroABS


class StalkerShieldMicro(MicroABS):
    def __init__(self, ai, use_division_backout_position=None, blink_locations=None):
        super().__init__('StalkerShieldMicro', ai, use_division_backout_position)
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
                        unit.MEDIVAC, unit.SIEGETANKSIEGED, unit.SIEGETANK, unit.LIBERATOR, unit.INFESTOR,
                        unit.CORRUPTOR,
                        unit.MUTALISK, unit.VIKING, unit.VIKINGFIGHTER, unit.VIKINGASSAULT, unit.THOR, unit.BUNKER,
                        unit.QUEEN, unit.IMMORTAL, unit.VOIDRAY,
                        unit.RAVEN}

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

        if self.blink_locations and self.ai.attack and self.ai.time < 900 and upgrade.BLINKTECH in self.ai.state.upgrades:
            blink_to_location = self.blink_locations[0].towards(enemy_main_base, 12)
            blink_location_height = self.ai.mineral_field.closest_to(self.blink_locations[0]).position3d.z
            enemy_main_base_height = self.ai.mineral_field.closest_to(enemy_main_base).position3d.z
            sentries = division.get_units(self.ai.iteration, unit.SENTRY)
            hallucinated_warp_prisms = self.ai.units().filter(lambda x: x.type_id == unit.WARPPRISM and
                                                                        x.is_hallucination)
            if sentries:
                division_position = division.get_position(iteration=self.ai.iteration)
                for sentry in sentries:
                    if not hallucinated_warp_prisms.exists and sentry.energy >= 75 and stalkers and \
                            (stalkers.closer_than(30, self.blink_locations[0]).amount >= 3 or
                             stalkers.closer_than(30, self.blink_locations[1]).amount >= 3):
                        sentry(ability.HALLUCINATION_WARPPRISM)
                    elif enemy and (enemy.closer_than(8, sentry).amount > 1 or
                            enemy.filter(lambda x: x.type_id == unit.SIEGETANKSIEGED and x.distance_to(sentry) <= 17)):
                        self.find_back_out_position(sentry, enemy.closest_to(sentry).position, division)
                    elif division_position and sentry.distance_to(division_position) > 12:
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
            if flying_units and not any(
                    [f.distance_to(self.blink_locations[0]) < 4 for f in flying_units]) and stalkers:
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
        division_units = division.get_units(self.ai.iteration)
        division_low_shield = division_units.filter(lambda x: x.shield_percentage < 0.5)
        stalkers_low_shield = stalkers.filter(lambda x: x.shield_percentage < 0.5)
        if stalkers_low_shield.amount > stalkers.amount * 0.65 or division_low_shield.amount > division_units.amount * 0.65:
            shield_regen_pause = True
        else:
            shield_regen_pause = False
        for stalker in stalkers:
            if stalker.shield_percentage < 0.45 or shield_regen_pause:
                batteries = self.ai.structures.filter(lambda x: x.type_id == unit.SHIELDBATTERY and
                                                      x.is_ready and x.energy_percentage >= 0.1)
                if batteries.exists:
                    stalker.move(batteries.closest_to(stalker))
                    continue
                elif stalker.distance_to(self.ai.defend_position) > 20:
                    stalker.move(self.ai.defend_position)
                    continue
            if blink_to_location:
                stalker_on_main_base_lvl = abs(enemy_main_base_height - stalker.position3d.z) < \
                                           abs(blink_location_height - stalker.position3d.z)
                if self.ai.attack and upgrade.BLINKTECH in self.ai.state.upgrades and \
                    stalker.distance_to(enemy_main_base) < stalker.distance_to(self.ai.defend_position):
                    if self.blink_locations and not stalker_on_main_base_lvl:
                        stalker_dist_to_blink = stalker.distance_to(self.blink_locations[0])
                        stalker_dist_to_wait_spot = stalker.distance_to(self.blink_locations[1])
                        if stalker_dist_to_wait_spot < 3 and stalkers.closer_than(6, self.blink_locations[1]).amount >= 5 \
                                and await self.is_blink_available(stalker) and flying_units and \
                                flying_units.closer_than(5, self.blink_locations[0]):
                            threats = []
                            if stalker.weapon_ready and enemy.exists:
                                threats = enemy.filter(
                                    lambda unit_: not unit_.has_buff(buff.IMMORTALOVERLOAD) and (unit_.can_attack_ground or
                                        unit_.type_id in priority_ids) and stalker.target_in_range(unit_)
                                        and not unit_.is_hallucination and unit_.is_visible and unit_.cloak != 1)
                            if threats:
                                stalker.attack(self.blink_locations[0])
                            else:
                                stalker.move(self.blink_locations[0])
                        elif stalker_dist_to_blink < 5 and await self.is_blink_available(stalker):
                            await self.blink(stalker, blink_to_location)
                            continue
                        elif stalker_dist_to_blink > 3 and stalker_dist_to_wait_spot > 45:
                            stalker.attack(self.blink_locations[1])
                            units_in_position -= 1
                elif not self.ai.attack and stalker_on_main_base_lvl and stalker.distance_to(blink_to_location) < 30:
                    if stalker.weapon_ready and enemy.exists:
                        threats = enemy.filter(
                            lambda unit_: not unit_.has_buff(buff.IMMORTALOVERLOAD) and (unit_.can_attack_ground or
                                        unit_.type_id in priority_ids) and stalker.target_in_range(unit_)
                                          and not unit_.is_hallucination and unit_.is_visible and unit_.cloak != 1)
                        if threats:
                            stalker.attack(threats.closest_to(stalker))
                            continue
                    if stalker.distance_to(blink_to_location) < 5 and self.is_blink_available(stalker):
                        await self.blink(stalker, self.blink_locations[0])
                    else:
                        stalker.move(blink_to_location)
            else:
                stalker_on_main_base_lvl = False
            if enemy.exists:
                threats = enemy.filter(
                    lambda unit_: not unit_.has_buff(buff.IMMORTALOVERLOAD) and (unit_.can_attack_ground or
                                                                                 unit_.type_id in priority_ids) and unit_.distance_to(
                        stalker.position) < dist and
                                  unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination
                                  and not unit_.is_snapshot and unit_.is_visible and unit_.cloak != 1)
                if self.ai.attack:
                    threats.extend(self.ai.enemy_structures().filter(lambda x: x.can_attack_ground and not x.is_snapshot
                                                                               and x.distance_to(stalker) < dist))
                    if blink_to_location and self.ai.time < 900 and stalker.distance_to(
                            enemy_main_base) < stalker.distance_to(
                            self.ai.defend_position):
                        # blink to main base
                        if self.blink_locations and not stalker_on_main_base_lvl:
                            if upgrade.BLINKTECH in self.ai.state.upgrades:
                                if not stalker.weapon_ready or not threats or threats and not threats.in_attack_range_of(
                                        stalker):
                                    stalker.move(self.blink_locations[0])
                            # elif not stalker.weapon_ready:
                            #     stalker.move(self.blink_locations[0])
                            #     continue

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
                        if stalker_on_main_base_lvl and upgrade.BLINKTECH in self.ai.state.upgrades:
                            main_base_minerals = self.ai.mineral_field.closest_to(enemy_main_base)
                            if (not threats or not threats.in_attack_range_of(
                                    stalker) or 1 > stalker.weapon_cooldown > 0) and \
                                    stalker.distance_to(enemy_main_base) > 12:
                                stalker.move(main_base_minerals)
                                continue
                    tanks = False
                    if self.ai.enemy_race == Race.Terran:
                        # stay away from tanks
                        tanks = self.ai.enemy_units().filter(lambda x: x.type_id in {unit.SIEGETANKSIEGED})
                        if tanks:
                            closest_tank = tanks.closest_to(stalker)
                            if stalker.distance_to(closest_tank) <= 17:
                                nearby_stalkers = stalkers.closer_than(9, stalker)
                                if tanks.amount >= 2 and nearby_stalkers.amount < 12 or \
                                        tanks.amount == 1 and nearby_stalkers.amount < 9:
                                    stalker.move(stalker.position.towards(closest_tank, -6))
                                    tanks = True
                                    continue
                        # else:
                        bunkers = self.ai.enemy_structures().filter(
                            lambda x: x.type_id == unit.BUNKER and x.distance_to(stalker) < dist)
                        if bunkers:
                            closest_bunker = bunkers.closest_to(stalker)
                            closest_minerals = self.ai.mineral_field.closest_to(closest_bunker)

                            if not threats:
                                workers = enemy.filter(lambda x: x.type_id in {unit.SCV, unit.MULE} and
                                                                 x.distance_to(closest_minerals) < 10)
                                threats = workers


                            elif not threats or not any([t.target_in_range(stalker) for t in threats]):
                                workers_near_bunkers = enemy.filter(lambda x: x.type_id == unit.SCV and
                                                                              any([x.distance_to(building) < 3 for
                                                                                   building in
                                                                                   bunkers]))
                                if workers_near_bunkers:
                                    threats = workers_near_bunkers
                                else:
                                    threats = bunkers
                    if (not enemy.exists or tanks) and stalker.distance_to(enemy_main_base) < 14:
                        workers = enemy.filter(lambda x: x.type_id in {unit.SCV, unit.MULE} and
                                                         x.distance_to(stalker) < 12)
                        if workers:
                            threats = workers
                        else:
                            threats = self.ai.enemy_structures().filter(lambda x: x.type_id in BASES_IDS)
                        if not threats:
                            threats = self.ai.enemy_structures()
                            if threats:

                                threats = self.ai.enemy_structures().closer_than(20, stalker)
                                if threats:
                                    priority_buildings_ids = {unit.FUSIONCORE, unit.STARPORT, unit.STARPORTFLYING,
                                                              unit.ENGINEERINGBAY, unit.GHOSTACADEMY, unit.FACTORY,
                                                              unit.FACTORYFLYING, unit.BARRACKS, unit.BARRACKSFLYING}
                                    for priority_id in priority_buildings_ids:
                                        targets = threats(priority_id)
                                        if targets:
                                            threats = targets
                                            break
                                else:
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
                        # elif not enemy.in_attack_range_of(stalker).exists and threats.exists:
                        #     stalker.move(stalker.position.towards(threats.closest_to(stalker.position)))
                    elif target:
                        queue = False
                        if upgrade.BLINKTECH in self.ai.state.upgrades and not stalker.target_in_range(target) and \
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
