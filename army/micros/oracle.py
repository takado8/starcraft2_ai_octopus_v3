from army.micros.microABS import MicroABS
from bot.constants import ANTI_AIR_IDS, BURROWING_UNITS_IDS
from sc2.unit import UnitTypeId as unit
from sc2.position import Point2
from sc2.ids.ability_id import AbilityId as ability
from sc2 import Race
from sc2.ids.buff_id import BuffId as buff


class OracleMicro(MicroABS):
    revelation_range = 6
    locked_oracle_tags = {}

    def __init__(self, ai):
        super().__init__('OracleMicro', ai)
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

    async def do_micro(self, division):
        # Oracle
        oracles = division.get_units(self.ai.iteration, unit.ORACLE)
        all_oracles = self.ai.units(unit.ORACLE).ready
        multiple_oracles = all_oracles.amount > 1
        for oracle in oracles:
            abilities = await self.ai.get_available_abilities(oracle)
            if self.oracle_on_harassment:
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
                shield_min = 0.35 if threats.amount > 7 else 0.15
                condition = oracle.energy > 45 and\
                            oracle.shield_percentage > shield_min
                # if multiple_oracles:
                #     condition = all([(oracle2.energy > 45 or ability.BEHAVIOR_PULSARBEAMOFF in
                #                 await self.ai.get_available_abilities(oracle2)) and oracle2.shield_percentage > shield_min
                #                      for oracle2 in all_oracles])

                if condition:
                    # queens = self.ai.enemy_units(unit.QUEEN).ready
                    # if queens:
                    #     queens = queens.closer_than(12, oracle)

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
                    elif workers.amount > 1 and oracle.is_idle:# or queens.amount == 1:
                        self.oracle_first_position_visited = False
                        # target = None
                        # if self.ai.enemy_race == Race.Terran:
                        #     anti_air_in_build = self.ai.enemy_structures().filter(
                        #     lambda x: x.distance_to(oracle) < 15 and x.type_id in ANTI_AIR_IDS and not x.is_ready)
                        #     if anti_air_in_build.exists:
                        #         print('anti_air_in_build.exists!')
                        #         min_dist = 999
                        #         for anti_air in anti_air_in_build:
                        #             closest_worker = workers.closest_to(anti_air)
                        #             dist = closest_worker.distance_to(anti_air)
                        #             if dist < min_dist:
                        #                 min_dist = dist
                        #                 target = closest_worker
                        #         print('target {}'.format(target))
                        # # if queens.amount == 1:
                        #     target = queens.first
                        # if target is None:
                        workers_in_range = workers.closer_than(7, oracle.position)
                        if workers_in_range.exists:
                            max_neighbours = -1
                            target = None
                            for worker in workers_in_range:
                                neighbours = workers.closer_than(4, worker)
                                if neighbours.amount > max_neighbours:
                                    max_neighbours = neighbours.amount
                                    target = worker.position
                        else:
                            target = self.mineral_lines[self.enemy_base_idx].towards(self.ai.enemy_start_locations[0], 5)
                        # if target.distance_to(oracle) <= 5:
                        if ability.BUILD_STASISTRAP in abilities and oracle.energy >= 50:

                            j = 1
                            while (workers.closer_than(1.2, target).exists or not self.in_grid(target)) and j < 2:
                                k = 0
                                while (workers.closer_than(1.2, target).exists or not self.in_grid(target)) and k < 2500 * j:
                                    k += 1
                                    target = target.random_on_distance(j)
                                j += 1
                            if workers.closer_than(1.2, target).exists or not self.in_grid(target):
                                target = self.mineral_lines[self.enemy_base_idx].towards(self.ai.enemy_start_locations[0], 5)

                            # target = self.mineral_lines[self.enemy_base_idx]

                            oracle(ability.BUILD_STASISTRAP, target)
                            continue
                        #     oracle.attack(target, queue=True)
                        # else:
                        #     oracle.attack(target)
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
                        if oracle.health_percentage < 0.40:
                            self.oracle_on_harassment = False
                        self.oracle_first_position_visited = False
            else:       # end of harassment
                enemy = self.ai.enemy_units()
                stasis = self.ai.structures(unit.ORACLESTASISTRAP)
                # print(abilities)
                threats = enemy.filter(lambda x: x.can_attack_air and x.distance_to(oracle) < x.air_range + 4)
                invisible_threats = enemy.filter(lambda x: not x.has_buff(buff.ORACLEREVELATION) and
                                                           (x.cloak == 1 or x.type_id in BURROWING_UNITS_IDS))
                anti_air = self.ai.enemy_structures().filter(lambda x: x.type_id in ANTI_AIR_IDS and
                                                                       x.distance_to(
                                                                           oracle) < x.air_range + x.radius + 4)
                neural_parasites = self.ai.enemy_units().filter(lambda x: x.has_buff(buff.NEURALPARASITE))
                if neural_parasites.exists:
                    affected_unit = neural_parasites.closest_to(oracle)
                    infestors = enemy.filter(lambda x: x.type_id == unit.INFESTORBURROWED and
                                                       x.distance_to(affected_unit) <= 9 and not x.has_buff(
                        buff.ORACLEREVELATION))
                    if infestors.exists:
                        self.cast_revelation(oracle, infestors, abilities)
                elif anti_air:  # or (oracle.health_percentage < 0.5 and oracle.shield_percentage < 0.35):
                    oracle.move(oracle.position.towards(anti_air.closest_to(oracle), -6))
                elif invisible_threats:
                    self.cast_revelation(oracle, invisible_threats, abilities)
                elif threats:
                    if threats.amount > 5 and sum([threat.air_dps for threat in threats]) > 10 or \
                            oracle.shield_percentage < 0.85:
                        queue_command = False
                        if ability.BEHAVIOR_PULSARBEAMOFF in abilities:
                            oracle(ability.BEHAVIOR_PULSARBEAMOFF)
                            queue_command = True
                        if self.cast_revelation(oracle, threats, abilities, queue_command):
                            queue_command = True
                        oracle.move(oracle.position.towards(threats.closest_to(oracle), -6), queue=queue_command)
                    elif oracle.energy > 45 and ability.BEHAVIOR_PULSARBEAMON in abilities:
                        oracle(ability.BEHAVIOR_PULSARBEAMON)
                        oracle.attack(threats.closest_to(oracle), queue=True)

                elif not self.ai.attack and oracle.energy >= 75 and ability.BUILD_STASISTRAP in abilities:
                    ramps = sorted(self.ai.game_info.map_ramps,
                                   key=lambda x: x.top_center.distance_to(self.ai.defend_position))
                    for ramp in ramps:
                        if self.ai.townhalls.amount > 1 and (ramp.top_center == self.ai.main_base_ramp.top_center or
                                                             ramp.top_center.distance_to(
                                                                 self.ai.start_location.position) < 30 and
                                                             ramp.top_center.distance_to(
                                                                 self.ai.game_info.map_center) >
                                                             self.ai.main_base_ramp.top_center.distance_to(
                                                                 self.ai.game_info.map_center)):
                            continue
                        middle = self.ai.defend_position.towards(
                            self.ai.townhalls.ready.closest_to(self.ai.defend_position), -5)
                        if not stasis.exists or not stasis.closer_than(6, middle).exists:
                            place = middle
                        else:
                            place = ramp.bottom_center.position.towards(ramp.top_center.position, -2)
                        if not stasis.exists or not stasis.closer_than(4, place).exists:
                            j = 1
                            while not self.in_grid(place) and j < 5:
                                k = 0
                                while not self.in_grid(place) and k < 7:
                                    k += 1
                                    place = place.random_on_distance(j)
                                j += 1
                            oracle(ability.BUILD_STASISTRAP, place)
                            break
                elif self.ai.attack:
                    targets = enemy.filter(lambda x: x.can_attack_air and not x.has_buff(buff.ORACLEREVELATION))
                    if targets.amount > 3:
                        self.cast_revelation(oracle, targets, abilities, min_units=3)
        return oracles.amount

    def cast_revelation(self, oracle, targets, abilities, queue=False, min_units=None):
        if ability.ORACLEREVELATION_ORACLEREVELATION in abilities:
            revelation_target = None
            max_neighbours = -1
            for target in targets:
                neighbours = targets.closer_than(self.revelation_range, target)
                if neighbours.amount > max_neighbours:
                    max_neighbours = neighbours.amount
                    revelation_target = target
            if min_units and max_neighbours < min_units:
                return False
            oracle(ability.ORACLEREVELATION_ORACLEREVELATION, revelation_target.position, queue=queue)
            return True