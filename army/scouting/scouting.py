from sc2.ids.unit_typeid import UnitTypeId as Unit
from sc2 import AbilityId
from economy.info.enemy_economy import BASES, MILITARY, EnemyEconomy
from sc2.position import Point2


class Scouting:
    SCOUTING_COOLDOWN = 30

    def __init__(self, ai_object, enemy_economy):
        self.number_of_scoutings_done = 0
        self.ai = ai_object
        self.scouting_index = -1
        self.scouting_positions = []
        self.scouting_positions_on_end = []
        self.enemy_economy: EnemyEconomy = enemy_economy
        self.last_scouting_time = 0
        self.last_print_time = 0
        self.visited_positions_count = {}

    def scan_middle_game(self):
        self.gather_enemy_info()
        # time = int(self.ai.time)
        # if time % 5 == 0 and self.last_print_time != time:
            # print()
            # for pos in self.visited_positions_count:
            #     print("{}: {}".format(pos, self.visited_positions_count[pos]))
            # print()
            # self.enemy_economy.print_enemy_info()
            # self.last_print_time = time

        if self.ai.time - self.last_scouting_time > self.SCOUTING_COOLDOWN:
            if self.create_scout():
                self.last_scouting_time = self.ai.time

        scouts = self.ai.units(Unit.PHOENIX).filter(lambda z: z.is_hallucination)
        if scouts.exists:
            # if BASES not in self.enemy_economy.enemy_info or len(self.scouting_positions) <\
            #         len(self.enemy_economy.enemy_info[BASES]) + 2:
            self.scouting_positions.clear()
            self.scouting_positions = self.create_scouting_positions_list()
            enemy = self.ai.enemy_units()
            if enemy:
                threats = enemy.filter(lambda x: x.can_attack_air)
                if threats:
                    for scout in scouts:
                        threats = threats.closer_than(12, scout)
                        if threats:
                            center1 = Point2.center([t.position for t in threats] + [scout.position,
                                                            self.scouting_positions[self.scouting_index]])
                            center2 = Point2.center([scout.position, self.scouting_positions[self.scouting_index]])
                            dodge_position = center1.position.towards(center2, 9)
                            scout.move(dodge_position)

            for scout in scouts.filter(lambda x: x.is_idle or
                    (x.distance_to(self.scouting_positions[self.scouting_index]) < 6)
            if self.scouting_index < len(self.scouting_positions) else False):
                if self.scouting_index < len(self.scouting_positions):
                    position = self.scouting_positions[self.scouting_index]
                    if scout.distance_to(position) < 6:
                        if position not in self.visited_positions_count:
                            self.visited_positions_count[position] = 1
                        else:
                            self.visited_positions_count[position] += 1
                        self.scouting_index += 1
                        self.number_of_scoutings_done += 1
                else:
                    self.scouting_index = 0
                if len(self.scouting_positions) > 0 and self.scouting_index < len(self.scouting_positions):
                    scout.move(self.scouting_positions[self.scouting_index])
                else:
                    self.scouting_index = 0

    def gather_enemy_info(self):
        if self.number_of_scoutings_done % 3 == 0:
            self.enemy_economy.clear_category(MILITARY)
        # bases
        enemy_bases = self.ai.enemy_structures().filter(lambda x: x.type_id in self.ai.bases_ids and x.is_visible)
        self.enemy_economy.add_units_to_enemy_info(BASES, enemy_bases)
        # military units
        excluded = {Unit.BROODLING, Unit.OVERLORD, Unit.OVERSEER, Unit.ADEPTPHASESHIFT, Unit.OVERLORDCOCOON,
                    Unit.OVERLORDTRANSPORT}
        enemy_military_units = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.workers_ids and
                                                                      x.type_id not in self.ai.units_to_ignore
                                                                      and x.type_id not in excluded and x.is_visible
                                                            and not x.is_snapshot and not x.is_hallucination)
        self.enemy_economy.add_units_to_enemy_info(MILITARY, enemy_military_units)


    def create_scouting_positions_list(self):
        scouting_positions = []
        for exp in self.ai.expansion_locations_list:
            if not self.ai.structures().closer_than(7, exp).exists:
                scouting_positions.append(exp)

        scouting_positions = sorted(scouting_positions, key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        if BASES in self.enemy_economy.enemy_info:
            most_distant_base_idx = len(self.enemy_economy.enemy_info[BASES]) + 2
        else:
            most_distant_base_idx = 3

        while most_distant_base_idx >= len(scouting_positions):
            most_distant_base_idx -= 1

        scouting_positions = scouting_positions[:most_distant_base_idx]
        return sorted(scouting_positions, key=lambda x: (self.visited_positions_count[x]
                                    if x in self.visited_positions_count else 0, scouting_positions.index(x)))

    def create_scout(self):
        sentries = self.ai.army(Unit.SENTRY).ready
        if sentries.exists:
            sentries = sorted(sentries.filter(lambda z: z.energy >= (75 if self.number_of_scoutings_done < 5 else 150)),
                              key=lambda sent: sent.energy, reverse=True)

            for sentry in sentries:
                sentry(AbilityId.HALLUCINATION_PHOENIX)
                # self.number_of_scoutings_done += 1
                return True

    def scan_on_end(self):
        scouts = self.ai.units(Unit.PHOENIX).filter(lambda z: z.is_hallucination)
        if scouts.amount < 3:
            snts = self.ai.army(Unit.SENTRY)
            if snts.exists:
                snts = self.ai.army(Unit.SENTRY).filter(lambda z: z.energy >= 75)
                if snts:
                    for se in snts:
                        se(AbilityId.HALLUCINATION_PHOENIX)
            else:
                scouts = self.ai.units({Unit.WARPPRISM, Unit.OBSERVER})
                if not scouts.exists:
                    scouts = self.ai.army.filter(lambda z: z.is_flying and int(str(z.tag)[-1]) % 3 == 0)
                    if not scouts.exists:
                        scouts = self.ai.units(Unit.PROBE).closest_n_units(self.ai.enemy_start_locations[0], 3)
                        if not scouts.exists:
                            scouts = self.ai.units().closest_n_units(self.ai.enemy_start_locations[0], 3)
        if scouts.exists:
            self.scouting_positions_on_end.clear()
            for exp in self.ai.expansion_locations_list:
                if not self.ai.structures().closer_than(7, exp).exists:
                    self.scouting_positions_on_end.append(exp)
            if len(self.scouting_positions_on_end) < 2:
                self.scouting_positions_on_end.extend(self.ai.expansion_locations_list)
            self.scouting_positions_on_end = sorted(self.scouting_positions_on_end,
                                                    key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
            for px in scouts.idle:
                if self.scouting_index >= len(self.scouting_positions_on_end):
                    self.scouting_index = 0
                if self.scouting_index < len(self.scouting_positions_on_end):
                    px.move(self.scouting_positions_on_end[self.scouting_index])
                    self.scouting_index += 1
                else:
                    self.scouting_positions_on_end.extend(self.ai.expansion_locations_list)