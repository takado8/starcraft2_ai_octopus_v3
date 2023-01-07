from sc2.constants import FakeEffectID
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.position import Point2
from sc2.ids.effect_id import EffectId as effect
from sc2.units import Units
from sc2 import Race
from .microABS import MicroABS
from bot.constants import ANTI_AIR_IDS, AIR_PRIORITY_UNITS
from sc2.ids.buff_id import BuffId as buff


def in_grid(ai, pos):
    try:
        return ai.in_pathing_grid(pos)
    except:
        return False




class AirMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('air', ai)
        self.enemy_base_idx = 0
        expansions = sorted(self.ai.expansion_locations,
                                 key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        self.mineral_lines = [self.ai.mineral_field.closer_than(9, exp).center.towards(exp, -3) for exp in expansions][:5]

        enemy_position = self.ai.enemy_start_locations[0]
        self.max_dist = min(self.ai.game_info.map_size) - 5
        short_dist = self.max_dist
        min_dist = 999999
        corners = [Point2((5,5)), Point2((5,self.max_dist)), Point2((self.max_dist, 5)),
                   Point2((self.max_dist,self.max_dist))]
        for position in corners:
            dist = enemy_position.distance_to(position)
            if dist < min_dist:
                self.oracle_safe_position = position
                min_dist = dist
        if self.ai.start_location.y < enemy_position.y:
            if self.ai.start_location.x < enemy_position.x:
                self.oracle_first_position = Point2((5, short_dist))
            else:
                self.oracle_first_position = Point2((short_dist, short_dist))
        else:
            if self.ai.start_location.x < enemy_position.x:
                self.oracle_first_position = Point2((5, 5))
            else:
                self.oracle_first_position = Point2((short_dist, 5))
        self.oracle_safe_position = Point2(self.oracle_safe_position.towards(self.oracle_first_position,self.max_dist/2))
        self.oracle_first_position = self.oracle_safe_position
        self.oracle_first_position_visited = False
        self.oracle_safe_position_visited = False
        self.oracle_last_dist = None
        self.oracle_on_harassment = True
        self.set_new_first_pos = False

    async def do_micro(self, soldiers):
        # Oracle
        all_units = Units([soldiers[soldier_tag].unit for soldier_tag in soldiers], self.ai)
        oracles = all_units(unit.ORACLE)
        for oracle in oracles:
            if self.oracle_on_harassment:
                abilities = await self.ai.get_available_abilities(oracle)
                workers = self.ai.enemy_units().filter(lambda x: x.distance_to(oracle.position) < 15 and x.type_id in
                                                                 self.ai.workers_ids)
                threats = self.ai.enemy_units().filter(lambda x: x.distance_to(oracle.position) < 10 and (x.can_attack_air or
                                                 x.type_id in [unit.SENTRY,unit.WIDOWMINE,unit.VOIDRAY]))
                threats.extend(self.ai.enemy_structures().filter(
                    lambda x: x.distance_to(oracle.position) < 11 and x.can_attack_air and x.is_ready))
                if threats.amount > 0 and threats.filter(lambda x: x.type_id in ANTI_AIR_IDS).amount > 0 and \
                        oracle.distance_to(self.mineral_lines[self.enemy_base_idx].position) < 19:
                    print('anti-air detected')
                    if len(self.mineral_lines) > 1:
                        print('removing mineral line: ' + str(self.mineral_lines[self.enemy_base_idx]))
                        self.mineral_lines.remove(self.mineral_lines[self.enemy_base_idx])
                    self.enemy_base_idx += 1
                    if self.enemy_base_idx >= len(self.mineral_lines):
                        self.enemy_base_idx = 0
                    self.set_new_first_pos = True
                    # x2 = self.oracle_first_position.x
                    # y2 = self.oracle_first_position.y
                    # if y2 == 5:
                    #     y2 = self.max_dist
                    # else:
                    #     y2 = 5
                    # self.oracle_first_position = Point2((y2,x2))
                    self.oracle_first_position_visited = False
                if (oracle.energy > 45 or ability.BEHAVIOR_PULSARBEAMOFF in abilities) and oracle.shield_percentage > 0.75:
                    if workers.amount < 1:
                        if self.enemy_base_idx >= len(self.mineral_lines):
                            self.enemy_base_idx = 0
                        if oracle.distance_to(self.mineral_lines[self.enemy_base_idx].position) < 7:
                            # print('close!')
                            if self.ai.enemy_structures().filter(lambda x1: x1.type_id in self.ai.bases_ids and
                                                                 x1.distance_to(oracle) < 10).amount < 1:
                                # print('no base here')
                                if len(self.mineral_lines) > 1:
                                    self.mineral_lines.remove(self.mineral_lines[self.enemy_base_idx])
                                self.enemy_base_idx += 1
                                if self.enemy_base_idx == len(self.mineral_lines):
                                    self.enemy_base_idx = 0
                        if not self.oracle_first_position_visited:
                            dist = oracle.distance_to(self.oracle_first_position)
                            if dist > 60 or (self.oracle_last_dist and dist < self.oracle_last_dist):
                                # print('going first pos dist: ' + str(dist) + '  pos: ' + str(self.oracle_first_position))
                                oracle.move(self.oracle_first_position)
                                self.oracle_last_dist = dist
                            else:
                                self.oracle_first_position_visited = True
                        else:
                            # print('attack lines')
                            if len(self.mineral_lines) <= self.enemy_base_idx:
                                self.enemy_base_idx = 0
                            attack_position = self.mineral_lines[self.enemy_base_idx].towards(self.oracle_first_position, 3)
                            if oracle.distance_to(attack_position) > 17 and\
                                    self.mineral_lines[self.enemy_base_idx].distance_to(self.ai.enemy_start_locations[0]) < 7:
                                oracle.move(self.mineral_lines[self.enemy_base_idx].towards(self.ai.enemy_start_locations[0], -22))
                            else:
                                oracle.move(attack_position)
                    elif workers.amount > 1 and oracle.is_idle:
                        self.oracle_first_position_visited = False
                        target = None
                        if self.ai.enemy_race == Race.Terran:
                            anti_air_in_build = self.ai.enemy_structures().filter(
                            lambda x: x.distance_to(oracle) < 15 and x.type_id in ANTI_AIR_IDS and not x.is_ready)
                            if anti_air_in_build.exists:
                                print('anti_air_in_build.exists!')
                                min_dist = 999
                                for anti_air in anti_air_in_build:
                                    closest_worker = workers.closest_to(anti_air)
                                    dist = closest_worker.distance_to(anti_air)
                                    if dist < min_dist:
                                        min_dist = dist
                                        target = closest_worker
                                print('target {}'.format(target))
                        if target is None:
                            workers_in_range = workers.closer_than(5,oracle.position)
                            if workers_in_range.exists:
                                workers_in_range = sorted(workers_in_range,key=lambda x1: x1.health + x1.shield)
                                target = workers_in_range[0]
                            else:
                                target = workers.closest_to(oracle)
                        # if target.distance_to(oracle) <= 5:
                        if ability.BEHAVIOR_PULSARBEAMON in abilities:
                            oracle(ability.BEHAVIOR_PULSARBEAMON)
                            oracle.attack(target, queue=True)
                        else:
                            oracle.attack(target)
                        # else:
                        #     oracle.move(oracle.position.towards(target, 3))
                        #     oracle.attack(target, queue=True)
                else:  # go safe
                    dist = oracle.distance_to(self.oracle_first_position)
                    # print('want go safe')
                    if dist > 30 or dist < self.oracle_last_dist:
                        # print('go safe')
                        if ability.BEHAVIOR_PULSARBEAMOFF in abilities:
                            oracle(ability.BEHAVIOR_PULSARBEAMOFF)
                            oracle.move(self.oracle_first_position, queue=True)
                        else:
                            oracle.move(self.oracle_first_position)
                        self.oracle_last_dist = dist
                    else:     # is in safe
                        if self.set_new_first_pos:
                            self.set_new_first_pos = False
                            x2 = self.oracle_first_position.x
                            y2 = self.oracle_first_position.y
                            if y2 == 5:
                                y2 = self.max_dist
                            else:
                                y2 = 5
                            self.oracle_first_position = Point2((y2,x2))
                        if oracle.health_percentage < 0.25:
                            self.oracle_on_harassment = False
                        self.oracle_first_position_visited = False
            else:       # end of harassment
                oracle.move(self.ai.defend_position)

        # Carrier
        carriers = all_units(unit.CARRIER)#and not x.is_attacking)
        for carrier in carriers:

            threats = self.ai.enemy_units().filter(
                lambda z: z.distance_to(carrier.position) < 10 and z.type_id not in self.ai.units_to_ignore
                          and not z.is_hallucination)
            can_attack_air = threats.filter(lambda x: x.can_attack_air)
            if can_attack_air.exists:
                threats = can_attack_air
            threats.extend(
                self.ai.enemy_structures().filter(lambda z: z.distance_to(carrier.position) < 10 and
                                                            (z.can_attack_air or z.type_id == unit.BUNKER)))

            if threats.exists:
                if threats.closer_than(8, carrier.position).exists:
                    carrier.move(carrier.position.towards(threats.closest_to(carrier), -3))
                    continue
                priority = threats.filter(lambda z: z.can_attack_air or z.type_id in AIR_PRIORITY_UNITS).sorted(
                    lambda z: z.health + z.shield,reverse=False)
                if priority.exists:
                    air_priority = priority.filter(lambda z: z.type_id in AIR_PRIORITY_UNITS)
                    if air_priority.exists:
                        target2 = air_priority[0]
                    else:
                        target2 = priority[0]
                else:
                    target2 = threats.sorted(lambda z: z.health + z.shield)[0]
                if target2 is not None:
                    # queue = False
                    # if threats.closer_than(8, carrier).exists:
                    #     carrier.move(carrier.position.towards(threats.closest_to(carrier), -3))
                    carrier.attack(target2)
        # Tempest
        tempests = all_units(unit.TEMPEST)  # and not x.is_attacking)
        for tempest in tempests:
            threats = self.ai.enemy_units().filter(
                lambda z: z.distance_to(tempest.position) < 16 and z.type_id not in self.ai.units_to_ignore
                          and not z.is_hallucination)
            can_attack_air = threats.filter(lambda x: x.can_attack_air)
            if can_attack_air.exists:
                threats = can_attack_air
            threats.extend(
                self.ai.enemy_structures().filter(lambda z: z.distance_to(tempest.position) < 11 and
                                                            (z.can_attack_air or z.type_id == unit.BUNKER)))
            if threats.exists:
                if threats.closer_than(9, tempest.position).exists:
                    tempest.move(tempest.position.towards(threats.closest_to(tempest.position).position, -5))
                    continue
                priority = threats.filter(lambda z: z.can_attack_air or z.type_id in AIR_PRIORITY_UNITS).sorted(
                    lambda z: z.health + z.shield, reverse=False)
                if priority.exists:
                    air_priority = priority.filter(lambda z: z.type_id in AIR_PRIORITY_UNITS)
                    if air_priority.exists:
                        target2 = air_priority[0]
                    else:
                        target2 = priority[0]
                else:
                    target2 = threats.sorted(lambda z: z.health + z.shield)[0]
                if target2 is not None:
                    tempest.attack(target2)


        void_rays = all_units.filter(lambda x: x.type_id == unit.VOIDRAY)
        for vr in void_rays:
            threats = self.ai.enemy_units().filter(
                lambda z: z.distance_to(vr.position) < 12 and z.type_id not in self.ai.units_to_ignore
            and not z.is_hallucination)
            can_attack_air = threats.filter(lambda x: x.can_attack_air)
            if can_attack_air.exists:
                threats = can_attack_air
            threats.extend(
                self.ai.enemy_structures().filter(lambda z: z.distance_to(vr.position) < 15 and
                                                            (z.can_attack_air or z.type_id == unit.BUNKER)))
            if threats.exists:
                # target2 = None
                priority = threats.filter(lambda z: z.can_attack_air and z.is_armored)\
                    .sorted(lambda z: z.health + z.shield)
                if priority.exists:
                    # closest = priority.closest_to(carrier)
                    # if carrier.distance_to(closest) < 7:
                    #     self.ai.do(carrier.move(carrier.position.towards(closest,-3)))
                    # else:
                    # if priority.amount > 2:
                    #     priority = sorted(priority[:int(len(priority) / 2)],key=lambda z: z.health + z.shield)
                    target2 = priority[0]
                else:
                    target2 = threats.sorted(lambda z: z.health + z.shield)[0]
                if target2 is not None:
                    if target2.is_armored and target2.distance_to(vr.position) < 7:
                        queue = False
                        abilities = await self.ai.get_available_abilities(vr)
                        if ability.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities:
                            vr(ability.EFFECT_VOIDRAYPRISMATICALIGNMENT)
                            queue = True
                        vr.attack(target2, queue=queue)
                    elif not vr.is_attacking:
                        vr.attack(target2)


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

    async def do_micro(self, soldiers):

        enemy = self.ai.enemy_units()
        if not enemy.exists:
            return

        stalkers = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.STALKER]
        priority_ids = {unit.COLOSSUS, unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE, unit.GHOST, unit.VIPER,
                    unit.MEDIVAC, unit.SIEGETANKSIEGED, unit.SIEGETANK, unit.LIBERATOR, unit.INFESTOR, unit.CORRUPTOR,
                        unit.MUTALISK, unit.VIKING, unit.THOR, unit.BUNKER, unit.QUEEN}
        dist = 9
        for stalker in stalkers:
            threats = enemy.filter(
                lambda unit_: ((unit_.can_attack_ground and unit_.distance_to(stalker.position) <= dist and
                              unit_.type_id not in self.ai.units_to_ignore) or unit_.type_id in priority_ids)
                              and not unit_.is_hallucination)
            if self.ai.attack:
                threats.extend(self.ai.enemy_structures().filter(lambda _x: _x.can_attack_ground or _x.type_id == unit.BUNKER))
            if threats.exists:
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

                # if target.distance_to(stalker) > dist:
                #     target = closest_enemy

                if stalker.shield_percentage < 0.4:
                    if stalker.health_percentage < 0.35:
                        stalker.move(self.find_back_out_position(stalker, closest_enemy.position))
                        continue
                    d = 4
                else:
                    d = 2

                if stalker.shield_percentage < 0.4 and upgrade.BLINKTECH in self.ai.state.upgrades and \
                        self.is_blink_available(stalker):
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

    async def is_blink_available(self, stalker):
        abilities = await self.ai.get_available_abilities(stalker)
        return ability.EFFECT_BLINK_STALKER in abilities

    async def blink(self, stalker, target):
        stalker(ability.EFFECT_BLINK_STALKER, target)


    def find_blink_out_position(self, stalker, closest_enemy_position):
        i = 8
        position = stalker.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 14:
            position = stalker.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                while not in_grid(self.ai, position) and k < 7:
                    k += 1
                    position = position.random_on_distance(j * 2)
                j += 1
        return position

    def find_back_out_position(self, stalker, closest_enemy_position):
        i = 6
        position = stalker.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 12:
            position = stalker.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                distance = j * 2
                while not in_grid(self.ai, position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position


class AdeptMicro(MicroABS):

    def __init__(self, ai):
        self.name = 'AdeptMicro'
        super().__init__(self.name, ai)
        self.enemy_base_idx = 0
        expansions = sorted(self.ai.expansion_locations,
                            key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        self.mineral_lines = [self.ai.mineral_field.closer_than(9, exp).center.towards(exp, -3)
                              for exp in expansions][:5]

    def select_target(self, targets, adept):
        if self.ai.enemy_race == Race.Protoss:
            a = targets[0].shield_percentage
        else:
            a = 1
        if targets[0].health_percentage * a == 1:
            target = targets.closest_to(adept)
        else:
            target = targets[0]
        return target

    async def do_micro(self, soldiers):
        enemy = self.ai.enemy_units()
        if not enemy.exists:
            return

        adepts = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.ADEPT]
        dist = 7
        if self.ai.attack:
            for ad in adepts:
                workers = self.ai.enemy_units().filter(lambda x: x.distance_to(ad) < 17 and x.type_id in
                                                                 self.ai.workers_ids)
                threats = self.ai.enemy_units().filter(lambda x: x.distance_to(ad) < 9 and x.type_id not in
                                                                 self.ai.workers_ids)
                if workers.amount < 3 or threats.amount > 3:
                    if ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT in await self.ai.get_available_abilities(ad):
                        self.ai.do(ad(ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT, ad.position))
                elif workers.amount > 2:
                    workers_in_range = workers.closer_than(5, ad)
                    if workers_in_range.exists:
                        workers_in_range = sorted(workers_in_range, key=lambda x: x.health + x.shield)
                        target3 = workers_in_range[0]
                    else:
                        target3 = workers.closest_to(ad)
                    if ad.weapon_cooldown == 0:
                        self.ai.do(ad.attack(target3))
            for shadow in self.ai.units(unit.ADEPTPHASESHIFT):
                workers = self.ai.enemy_units().filter(lambda x: x.distance_to(shadow) < 12 and x.type_id in
                                                                 self.ai.workers_ids)
                threats = self.ai.enemy_units().filter(lambda x: x.distance_to(shadow) < 9 and x.type_id not in
                                                                 self.ai.workers_ids)
                if workers.amount > 3 and threats.amount < 5:
                    workers = sorted(workers, key=lambda x: x.health + x.shield)
                    self.ai.do(shadow.move(workers[0]))
                else:
                    self.ai.do(shadow.move(self.mineral_lines[self.enemy_base_idx]))
                    if shadow.distance_to(self.mineral_lines[self.enemy_base_idx]) < 2:
                        self.enemy_base_idx += 1
                        if self.enemy_base_idx > 2:
                            self.enemy_base_idx = 0

        else:
            for adept in adepts:
                threats = enemy.filter(
                    lambda unit_: unit_.can_attack_ground and unit_.distance_to(adept.position) <= dist and
                                  unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination and
                not unit_.is_flying)
                if self.ai.attack:
                    threats.extend(self.ai.enemy_structures().filter(lambda _x: _x.can_attack_ground or _x.type_id == unit.BUNKER))
                if threats.exists:
                    closest_enemy = threats.closest_to(adept)
                    priority = threats.filter(lambda x1: x1.type_id in {unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                        unit.QUEEN})
                    if priority.exists:
                        targets = priority.sorted(lambda x1: x1.health + x1.shield)
                        target = self.select_target(targets, adept)
                    else:
                        targets = threats.filter(lambda x: x.is_light)
                        if not targets.exists:
                            targets = threats
                        targets = targets.sorted(lambda x1: x1.health + x1.shield)
                        target = self.select_target(targets, adept)

                    if adept.shield_percentage < 0.4:
                        if adept.health_percentage < 0.35:
                            adept.move(self.find_back_out_position(adept, closest_enemy.position))
                            continue
                        d = 4
                    else:
                        d = 2

                    back_out_position = self.find_back_out_position(adept, closest_enemy.position)
                    if back_out_position is not None and adept.weapon_cooldown > 0:
                        adept.move(adept.position.towards(back_out_position, d))
                    else:
                        adept.attack(target)

    def find_back_out_position(self, adept, closest_enemy_position):
        i = 6
        position = adept.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 12:
            position = adept.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                distance = j * 2
                while not in_grid(self.ai, position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position


class ArchonMicro(MicroABS):

    def __init__(self, ai):
        self.name = 'ArchonMicro'
        super().__init__(self.name, ai)

    def select_target(self, targets):
        total_hp_in_range_of_fire = {}
        _range = 1
        for target in targets:
            enemy_in_range = self.ai.enemy_units.filter(lambda x: x.distance_to(target) <= _range and\
                                                        x.type_id not in self.ai.units_to_ignore)
            total_hp_in_range_of_fire[target] = \
                (enemy_in_range.amount, sum([enemy.health + enemy.shield for enemy in enemy_in_range]))
        max_targets = max(total_hp_in_range_of_fire, key=lambda x: total_hp_in_range_of_fire[x][0])

        targets_with_max_count = {}
        for target in total_hp_in_range_of_fire:
            if total_hp_in_range_of_fire[target][0] == max_targets:
                targets_with_max_count[target] = total_hp_in_range_of_fire[target]

        min_hp = 99999999
        final_target = None
        for target in targets_with_max_count:
            if targets_with_max_count[target][1] < min_hp:
                min_hp = targets_with_max_count[target][1]
                final_target = target

        return final_target

    async def do_micro(self, soldiers):

        enemy = self.ai.enemy_units()
        if not enemy.exists:
            return

        archons = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.ARCHON]
        dist = 6
        for archon in archons:
            threats = enemy.filter(
                lambda unit_: unit_.can_attack_ground and unit_.distance_to(archon.position) <= dist and
                              unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination)
            if self.ai.attack:
                threats.extend(self.ai.enemy_structures().filter(lambda _x: _x.can_attack_ground or _x.type_id == unit.BUNKER))
            if threats.exists:
                closest_enemy = threats.closest_to(archon)
                priority = threats.filter(lambda x1: x1.type_id in {unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                    unit.QUEEN, unit.MUTALISK, unit.VIPER, unit.GHOST, unit.INFESTOR, unit.CORRUPTOR})
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets)
                else:
                    targets = threats.filter(lambda x: x.is_biological)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets)

                if archon.shield_percentage < 0.25:
                    archon.move(self.find_back_out_position(archon, closest_enemy.position))
                    continue

                # if self.ai.army().closer_than(5, archon).amount < 4:
                #     back_out_position = self.find_back_out_position(archon, closest_enemy.position)
                #     if back_out_position is not None and archon.weapon_cooldown > 0:
                #         archon.move(archon.position.towards(back_out_position, 4))
                #         continue
                if target is None:
                    target = closest_enemy
                archon.attack(target)

    def find_back_out_position(self, archon, closest_enemy_position):
        i = 6
        position = archon.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 12:
            position = archon.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                distance = j * 2
                while not in_grid(self.ai, position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position


class ImmortalMicro(MicroABS):

    def __init__(self, ai):
        self.name = 'ImmortalMicro'
        super().__init__(self.name, ai)

    def select_target(self, targets, immortal):
        if self.ai.enemy_race == Race.Protoss:
            a = targets[0].shield_percentage
        else:
            a = 1
        if targets[0].health_percentage * a == 1:
            target = targets.closest_to(immortal)
        else:
            target = targets[0]
        return target

    async def do_micro(self, soldiers):

        enemy = self.ai.enemy_units()
        if not enemy.exists:
            return

        immortals = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.IMMORTAL]
        dist = 8
        for immortal in immortals:
            threats = enemy.filter(
                lambda unit_: unit_.can_attack_ground and unit_.distance_to(immortal.position) <= dist and
                              unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination)
            if self.ai.attack:
                threats.extend(self.ai.enemy_structures().filter(lambda _x: _x.can_attack_ground or _x.type_id == unit.BUNKER))
            if threats.exists:
                closest_enemy = threats.closest_to(immortal)
                priority = threats.filter(lambda x1: x1.type_id in [unit.COLOSSUS, unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                    unit.MEDIVAC, unit.SIEGETANKSIEGED, unit.SIEGETANK, unit.LIBERATOR, unit.THOR, unit.BUNKER, unit.QUEEN])
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, immortal)
                else:
                    targets = threats.filter(lambda x: x.is_armored)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, immortal)

                # if target.distance_to(stalker) > dist:
                #     target = closest_enemy

                if immortal.shield_percentage < 0.4:
                    if immortal.health_percentage < 0.35:
                        immortal.move(self.find_back_out_position(immortal, closest_enemy.position))
                        continue
                    d = 4
                else:
                    d = 2

                back_out_position = self.find_back_out_position(immortal, closest_enemy.position)
                has_buff = immortal.has_buff(buff.IMMORTALOVERLOAD)
                if back_out_position is not None and immortal.weapon_cooldown > 0 and immortal.shield_percentage < 1 \
                        and not has_buff:
                    immortal.move(immortal.position.towards(back_out_position, d))
                else:
                    immortal.attack(target)

    def find_back_out_position(self, immortal, closest_enemy_position):
        i = 6
        position = immortal.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 12:
            position = immortal.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                distance = j * 2
                while not in_grid(self.ai, position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position


class ColossusMicro(MicroABS):
    def __init__(self, ai):
        self.name = 'ColossusMicro'
        super().__init__(self.name, ai)

    def select_target(self, targets):
        total_hp_in_range_of_fire = {}
        _range = 2.8
        for target in targets:
            enemy_in_range = self.ai.enemy_units.filter(lambda x: not x.is_flying and x.distance_to(target) <= _range and\
                                                        x.type_id not in self.ai.units_to_ignore)
            total_hp_in_range_of_fire[target] = \
                (enemy_in_range.amount, sum([enemy.health + enemy.shield for enemy in enemy_in_range]))
        max_targets = max(total_hp_in_range_of_fire, key=lambda x: total_hp_in_range_of_fire[x][0])

        targets_with_max_count = {}
        for target in total_hp_in_range_of_fire:
            if total_hp_in_range_of_fire[target][0] == max_targets:
                targets_with_max_count[target] = total_hp_in_range_of_fire[target]

        min_hp = 99999999
        final_target = None
        for target in targets_with_max_count:
            if targets_with_max_count[target][1] < min_hp:
                min_hp = targets_with_max_count[target][1]
                final_target = target

        return final_target

    async def do_micro(self, soldiers):

        enemy = self.ai.enemy_units()
        if not enemy.exists:
            return

        colossi = Units([soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.COLOSSUS], self.ai)
        dist = 10
        for colossus in colossi:
            threats = enemy.filter(
                lambda unit_: (unit_.can_attack_ground or unit_.can_attack_air) and unit_.distance_to(colossus.position) <= dist and
                              unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination)
            if self.ai.attack:
                threats.extend(self.ai.enemy_structures().filter(lambda _x: _x.can_attack_ground or _x.can_attack_air
                                                                            or _x.type_id == unit.BUNKER))
            if threats.exists:
                closest_enemy = threats.closest_to(colossus)
                priority = threats.filter(lambda x1: x1.type_id in {unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                                                                    unit.QUEEN, unit.GHOST})
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets)
                else:
                    targets = threats.filter(lambda x: x.is_light)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets)

                # if target.distance_to(stalker) > dist:
                #     target = closest_enemy

                if colossus.shield_percentage < 0.45:
                    if colossus.health_percentage < 0.45:
                        colossus.move(self.find_back_out_position(colossus, closest_enemy.position))
                        continue
                    d = 5
                else:
                    d = 3

                back_out_position = self.find_back_out_position(colossus, closest_enemy.position)
                if back_out_position is not None and colossus.weapon_cooldown > 0:
                    colossus.move(colossus.position.towards(back_out_position, d))
                elif target:
                    colossus.attack(target)


        stalkers = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.STALKER]
        priority_ids = {unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE, unit.VIPER,
                        unit.MEDIVAC, unit.SIEGETANKSIEGED, unit.SIEGETANK, unit.LIBERATOR, unit.INFESTOR,
                        unit.CORRUPTOR,unit.MUTALISK, unit.VIKING, unit.THOR, unit.BUNKER}

        colossi_threats_set = set()
        for colossus in colossi:
            threats = self.ai.enemy_units().filter(lambda x: x.type_id in priority_ids and
                            x.distance_to(colossus) <= 7)
            for threat in threats:
                colossi_threats_set.add(threat)

        colossi_threats = Units(colossi_threats_set, self.ai)
        dist = 6
        threats = None
        for stalker in stalkers:
            if colossi_threats:
                threats = colossi_threats
                # print(colossi_threats)
            elif colossi and not any([stalker.distance_to(colossus) < 4 for colossus in colossi]):
                if upgrade.BLINKTECH in self.ai.state.upgrades and \
                    await self.is_blink_available(stalker):
                    await self.blink(stalker, colossi.closest_to(stalker).position)
                else:
                    stalker.move(colossi.closest_to(stalker))
            else:
                threats = enemy.filter(
                    lambda unit_: (((unit_.can_attack_ground or unit_.can_attack_air)
                                    and unit_.distance_to(stalker.position) <= dist and
                                    unit_.type_id not in self.ai.units_to_ignore) or unit_.type_id in priority_ids)
                                  and not unit_.is_hallucination)
                if self.ai.attack:
                    threats.extend(
                        self.ai.enemy_structures().filter(lambda _x: _x.can_attack_ground or _x.type_id == unit.BUNKER))
            if threats:
                closest_enemy = threats.closest_to(stalker)
                priority = threats.filter(lambda x1: x1.type_id in priority_ids)
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_stalker_target(targets, stalker)
                else:
                    targets = threats.filter(lambda x: x.is_armored)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_stalker_target(targets, stalker)

                # if target.distance_to(stalker) > dist:
                #     target = closest_enemy

                if colossi_threats:
                    stalker.attack(target)
                    continue

                if stalker.shield_percentage < 0.3:
                    if stalker.health_percentage < 0.35:
                        stalker.move(self.find_stalker_back_out_position(stalker, closest_enemy.position))
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
                    back_out_position = self.find_stalker_back_out_position(stalker, closest_enemy.position)
                    if back_out_position is not None and stalker.weapon_cooldown > 0:
                        stalker.move(stalker.position.towards(back_out_position, d))
                    else:
                        stalker.attack(target)

    def select_stalker_target(self, targets, stalker):
        if targets[0].shield_health_percentage == 1:
            target = targets.closest_to(stalker)
        else:
            target = targets[0]
        return target

    async def is_blink_available(self, stalker):
        abilities = await self.ai.get_available_abilities(stalker)
        return ability.EFFECT_BLINK_STALKER in abilities

    async def blink(self, stalker, target):
        stalker(ability.EFFECT_BLINK_STALKER, target)

    def find_blink_out_position(self, stalker, closest_enemy_position):
        i = 8
        position = stalker.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 14:
            position = stalker.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                while not in_grid(self.ai, position) and k < 7:
                    k += 1
                    position = position.random_on_distance(j * 2)
                j += 1
        return position

    def find_stalker_back_out_position(self, stalker, closest_enemy_position):
        i = 6
        position = stalker.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 12:
            position = stalker.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                distance = j * 2
                while not in_grid(self.ai, position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position

    def find_back_out_position(self, colossus, closest_enemy_position):
        i = 6
        position = colossus.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 12:
            position = colossus.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                distance = j * 2
                while not in_grid(self.ai, position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position


class ZealotMicro(MicroABS):
    def __init__(self, ai):
        self.name = 'ZealotMicro'
        super().__init__(self.name, ai)

    async def do_micro(self, soldiers):
        zealots = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.ZEALOT]

        for zl in zealots:
            threats = self.ai.enemy_units().filter(lambda x2: x2.distance_to(zl.position) < 9 and not x2.is_flying and
                          x2.type_id not in self.ai.units_to_ignore and not x2.is_hallucination).sorted(lambda _x: _x.health + _x.shield)
            if threats.exists:
                closest = threats.closest_to(zl)
                if threats[0].health_percentage * threats[0].shield_percentage == 1 or threats[0].distance_to(zl.position) > \
                    closest.distance_to(zl.position) + 1 or not self.ai.in_pathing_grid(threats[0]):
                    target = closest
                else:
                    target = threats[0]
                if ability.EFFECT_CHARGE in await self.ai.get_available_abilities(zl):
                    zl(ability.EFFECT_CHARGE, target)
                    zl.attack(target, queue=True)
                else:
                    zl.attack(target)


class WallGuardZealotMicro(MicroABS):
    def __init__(self, ai):
        self.name = 'ZealotMicro'
        super().__init__(self.name, ai)

    async def do_micro(self, soldiers):
        zealots = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.ZEALOT]
        location = self.ai.main_base_ramp.protoss_wall_warpin
        for zl in zealots:
            if not any([zealot.distance_to(location) < 1 for zealot in zealots]):
                zl.move(location)
            if self.ai.enemy_units().closer_than(10, location):
                zl.hold_position(queue=True)


class SentryMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('SentryMicro', ai)

    async def do_micro(self, soldiers):
        #  Sentry region  #
        sentries = Units([soldiers[soldier_tag].unit for soldier_tag in soldiers if
               soldiers[soldier_tag].type_id == unit.SENTRY], self.ai)
        # sentries = self.ai.army(unit.SENTRY)
        if sentries.exists:
            m = -1
            sentry = None
            for se in sentries:
                close = sentries.closer_than(7, se.position).amount
                if close > m:
                    m = close
                    sentry = se
            force_fields = []
            guardian_shield_on = False
            for eff in self.ai.state.effects:
                if eff.id == FakeEffectID.get(unit.FORCEFIELD.value):
                    force_fields.append(eff)
                elif not guardian_shield_on and eff.id == effect.GUARDIANSHIELDPERSISTENT:
                    guardian_shield_on = True
            threats = self.ai.enemy_units().filter(
                lambda unit_: unit_.can_attack_ground or unit_.can_attack_air and unit_.distance_to(sentry.position) <= 9 and
                              unit_.type_id not in self.ai.units_to_ignore and unit_.type_id not in self.ai.workers_ids
            and not unit_.is_hallucination)
            has_energy_amount = sentries.filter(lambda x2: x2.energy >= 50).amount
            points = []

            if has_energy_amount > 0 and len(
                    force_fields) < 5 and threats.amount > 4:  # and self.ai.time - self.ai.force_field_time > 1:
                enemy_army_center = threats.center.towards(sentry, -1)
                gap = 3
                points.append(enemy_army_center)
                points.append(Point2((enemy_army_center.x - gap, enemy_army_center.y)))
                points.append(Point2((enemy_army_center.x + gap, enemy_army_center.y)))
                points.append(Point2((enemy_army_center.x, enemy_army_center.y - gap)))
                points.append(Point2((enemy_army_center.x, enemy_army_center.y + gap)))
            for se in self.ai.units(unit.SENTRY):
                abilities = await self.ai.get_available_abilities(se)
                if threats.amount > 4 and not guardian_shield_on and ability.GUARDIANSHIELD_GUARDIANSHIELD in abilities \
                        and se.distance_to(threats.closest_to(se).position) < 7:
                    se(ability.GUARDIANSHIELD_GUARDIANSHIELD)
                    guardian_shield_on = True
                if ability.FORCEFIELD_FORCEFIELD in abilities and len(points) > 0:
                    se(ability.FORCEFIELD_FORCEFIELD, points.pop(0))
                else:
                    army_nearby = self.ai.army.closer_than(9, se.position)
                    if army_nearby.exists:
                        if threats.exists:
                            se.move(army_nearby.center.towards(threats.closest_to(se), -4))


class WarpPrismMicro(MicroABS):
    def __init__(self, ai):
        super().__init__("WarpPrismMicro", ai)

    async def do_micro(self, soldiers):
        if self.ai.attack:
            dist = self.ai.enemy_start_locations[0].distance_to(self.ai.game_info.map_center) * 0.8
            for warp in self.ai.units(unit.WARPPRISM):
                if warp.distance_to(self.ai.enemy_start_locations[0]) <= dist:
                    abilities = await self.ai.get_available_abilities(warp)
                    if ability.MORPH_WARPPRISMPHASINGMODE in abilities:
                        warp(ability.MORPH_WARPPRISMPHASINGMODE)
        else:
            for warp in self.ai.units(unit.WARPPRISMPHASING):
                abilities = await self.ai.get_available_abilities(warp)
                if ability.MORPH_WARPPRISMTRANSPORTMODE in abilities:
                    warp(ability.MORPH_WARPPRISMTRANSPORTMODE)
            for warp in self.ai.units(unit.WARPPRISM):
                if warp.distance_to(self.ai.start_location) > 5:
                    warp.move(self.ai.start_location)


class DisruptorMicro(MicroABS):

    def __init__(self, ai):
        self.name = 'DisruptorMicro'
        super().__init__(self.name, ai)

    async def do_micro(self, soldiers):

        enemy = self.ai.enemy_units()
        if not enemy.exists:
            return

        disruptors = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.DISRUPTOR]
        # Disruptor
        # zealots = self.ai.army(unit.ZEALOT)
        for disruptor in disruptors:
            # Cast spells   ---> look for group of enemy
            abilities = await self.ai.get_available_abilities(disruptor)
            if ability.EFFECT_PURIFICATIONNOVA in abilities:
                spell_target = enemy.filter(
                    lambda unit_: unit_.distance_to(disruptor) < 12 and unit_.type_id not in self.ai.units_to_ignore
                                  and not unit_.is_flying)
                target = None
                if spell_target.amount > 2:
                    tanks = spell_target.filter(lambda x: x.type_id in {unit.SIEGETANKSIEGED, unit.SIEGETANK,
                                                                        unit.DISRUPTOR})
                    if tanks.amount > 1:
                        spell_target = tanks

                    maxNeighbours = 0
                    for en in spell_target:
                        neighbours = enemy.filter(lambda unit_: not unit_.is_flying and unit_.distance_to(en) <= 1.5
                                                  and unit_.type_id not in self.ai.units_to_ignore)
                        if neighbours.amount > maxNeighbours:
                            maxNeighbours = neighbours.amount
                            target = en
                    if target is not None and self.ai.army.closer_than(2, target).amount < 1:
                        dist = await self.ai._client.query_pathing(disruptor.position, target.position)
                        if dist is not None and dist <= 13:
                            # print("Casting Purification nova on " + str(maxNeighbours + 1) + " units.")
                            # self.ai.nova_wait = self.ai.time
                            disruptor(ability.EFFECT_PURIFICATIONNOVA, target.position)
            else:
                threat = enemy.filter(lambda x: x.distance_to(disruptor) < 10 and x.can_attack_ground)
                if threat.exists:
                    retreat_position = self.find_back_out_position(disruptor, threat.closest_to(disruptor))
                    disruptor.move(retreat_position)
        # Disruptor purification nova
        # if self.ai.time - self.ai.nova_wait > 0.4:
        for nova in self.ai.units(unit.DISRUPTORPHASED):
            spell_target = enemy.filter(lambda unit_: unit_.distance_to(nova) < 9
                                 and unit_.type_id not in self.ai.units_to_ignore and not unit_.is_flying)
            target = None
            if spell_target.amount > 0:
                tanks = spell_target.filter(lambda x: x.type_id in {unit.SIEGETANKSIEGED, unit.SIEGETANK})
                if tanks.amount > 0:
                    spell_target = tanks
                maxNeighbours = 0
                for en in spell_target:
                    neighbours = enemy.filter(
                        lambda unit_: unit_.distance_to(nova) <= 1.5
                                      and unit_.type_id not in self.ai.units_to_ignore and not unit_.is_flying)
                    if neighbours.amount > maxNeighbours:
                        maxNeighbours = neighbours.amount
                        target = en

                # ability.PURIFICATIONNOVAMORPHBACK_PURIFICATIONNOVA
                if target is not None and self.ai.army.closer_than(2, target).amount < 1:
                    # if self.ai.army.closer_than(3,target).amount < 2:
                    # print("Steering Purification nova to " + str(maxNeighbours + 1) + " units.")
                    nova.move(target.position.towards(nova, -1))

    def find_back_out_position(self, disruptor, closest_enemy_position):
        i = 6
        position = disruptor.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 12:
            position = disruptor.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                distance = j * 2
                while not in_grid(self.ai, position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position