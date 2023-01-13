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


class DarkTemplarMicro(MicroABS):
    def __init__(self, ai):
        self.name = 'DarkTemplarMicro'
        super().__init__(self.name, ai)
        self.enemy_base_idx = 0
        expansions = sorted(self.ai.expansion_locations,
                            key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        self.mineral_lines = [self.ai.mineral_field.closer_than(9, exp).center.towards(exp, 3)
                              for exp in expansions][:5]

    async def do_micro(self, soldiers):
        dts = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.DARKTEMPLAR]

        for dt in dts:
            detectors = self.ai.enemy_units().filter(lambda x: x.is_detector and
                            x.distance_to(dt.position) < x.detect_range + 1)
            detectors.extend(self.ai.enemy_structures().filter(lambda x: x.is_detector and
                            x.distance_to(dt.position) < x.detect_range + 1))
            threats = self.ai.enemy_units().filter(lambda x2: x2.distance_to(dt.position) < 9 and not x2.is_flying and
                          x2.type_id not in self.ai.units_to_ignore and not x2.is_hallucination)\
                                                                            .sorted(lambda _x: _x.health + _x.shield)
            workers = self.ai.enemy_units().filter(lambda x: x.type_id in self.ai.workers_ids
                                                and x.distance_to(dt) < 14).sorted(lambda _x: _x.health + _x.shield)
            if detectors.exists:
                position = self.find_back_out_position(dt, detectors.closest_to(dt))
                if position:
                    dt.move(position)
            elif workers.exists:
                closest = workers.closest_to(dt)
                if workers[0].health_percentage * workers[0].shield_percentage == 1 or workers[0].distance_to(
                        dt.position) > \
                        closest.distance_to(dt.position) + 1 or not self.ai.in_pathing_grid(workers[0]):
                    target = closest
                else:
                    target = workers[0]
                dt.attack(target)
            elif (self.ai.attack or self.ai.enemy_units().closer_than(15, self.ai.defend_position))and threats.exists:
                closest = threats.closest_to(dt)
                if threats[0].health_percentage * threats[0].shield_percentage == 1 or threats[0].distance_to(dt.position) > \
                    closest.distance_to(dt.position) + 1 or not self.ai.in_pathing_grid(threats[0]):
                    target = closest
                else:
                    target = threats[0]
                dt.attack(target)
            else:
                dt.move(self.mineral_lines[self.enemy_base_idx])
                if dt.distance_to(self.mineral_lines[self.enemy_base_idx]) < 3:
                    self.enemy_base_idx += 1
                    if self.enemy_base_idx > 2:
                        self.enemy_base_idx = 0

    def find_back_out_position(self, dt, closest_enemy_position):
        i = 6
        position = dt.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 12:
            position = dt.position.towards(closest_enemy_position, -i)
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

