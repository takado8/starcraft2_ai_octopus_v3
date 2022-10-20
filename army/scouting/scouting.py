from sc2.ids.unit_typeid import UnitTypeId as Unit
from sc2 import AbilityId, BotAI
import time
# from evolution.main import OctopusEvo


# scouting categories
BASES = 'bases'
MILITARY = 'military'


class Scouting:
    def __init__(self, ai_object):
        self.number_of_scoutings_done = 0
        self.ai = ai_object
        self.enemy_info = {}
        self.total_enemy_ground_dps = 0
        self.total_enemy_hp = 0
        self.total_enemy_cost_minerals = 0
        self.total_enemy_cost_gas = 0
        self.total_enemy_supply = 0
        self.scouting_index = -1
        self.scouting_positions = []

    def scan_middle_game(self):
        scouts = self.ai.units(Unit.PHOENIX).filter(lambda z: z.is_hallucination)
        if scouts.exists:
            if BASES not in self.enemy_info or len(self.scouting_positions) < len(self.enemy_info[BASES]) + 2:
                self.scouting_positions.clear()
                self.scouting_positions = self.create_scouting_positions_list()

            for scout in scouts.filter(lambda x: x.is_idle or
                                                 x.distance_to(self.scouting_positions[self.scouting_index]) < 5):
                self.scouting_index += 1
                if self.scouting_index >= len(self.scouting_positions):
                    self.scouting_index = 0
                self.ai.do(scout.move(self.scouting_positions[self.scouting_index]))
        else:
            self.create_scout()

    def gather_enemy_info(self):
        # bases
        enemy_bases = self.ai.enemy_structures().filter(lambda x: x.type_id in self.ai.bases_ids and x.is_visible)
        self.add_units_to_enemy_info(BASES, enemy_bases)
        # military units
        excluded = [Unit.BROODLING]
        enemy_military_units = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.workers_ids and
                                                                      x.type_id not in self.ai.units_to_ignore
                                                                      and x.type_id not in excluded)
        self.add_units_to_enemy_info(MILITARY, enemy_military_units)

    def add_units_to_enemy_info(self, category, units):
        if units:
            if category not in self.enemy_info:
                self.enemy_info[category] = {}

            for unit in units:
                self.enemy_info[category][unit.tag] = unit

    def calculate_enemy_units_report(self):
        self.total_enemy_ground_dps = 0
        self.total_enemy_hp = 0
        if MILITARY in self.enemy_info:
            for unit_tag in self.enemy_info[MILITARY]:
                unit = self.enemy_info[MILITARY][unit_tag]
                self.total_enemy_ground_dps += unit.ground_dps
                self.total_enemy_hp += unit.health + unit.shield

    def remove_unit_from_enemy_info(self, unit_tag):
        for category in self.enemy_info:
            if unit_tag in self.enemy_info[category]:
                self.enemy_info[category].pop(unit_tag)

    def create_scouting_positions_list(self):
        scouting_positions = []
        for exp in self.ai.expansion_locations_list:
            if not self.ai.structures().closer_than(7, exp).exists:
                scouting_positions.append(exp)

        scouting_positions = sorted(scouting_positions, key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        if BASES in self.enemy_info:
            most_distant_base_idx = len(self.enemy_info[BASES]) + 2
        else:
            most_distant_base_idx = 3

        while most_distant_base_idx >= len(scouting_positions):
            most_distant_base_idx -= 1

        scouting_positions = scouting_positions[:most_distant_base_idx]
        return scouting_positions

    def create_scout(self):
        sentries = self.ai.army(Unit.SENTRY)
        if sentries.exists:
            sentries = sorted(sentries.filter(lambda z: z.energy >= 75), key=lambda sent: sent.energy, reverse=True)
            if self.number_of_scoutings_done > 3:
                if len(sentries) < 2:
                    return
            for sentry in sentries:
                sentry_energy = sentry.energy_percentage
                self.ai.do(sentry(AbilityId.HALLUCINATION_PHOENIX))
                self.number_of_scoutings_done += 1
                if sentry_energy < 1:
                    break

    def print_enemy_info(self):
        print('-------------------- enemy info -----------------------------')
        self.calculate_enemy_units_report()
        for category in self.enemy_info:
            print("{}:".format(category))
            for item in self.enemy_info[category]:
                print("   {}, {}".format(item, self.enemy_info[category][item]))
            print(" total: {}".format(len(self.enemy_info[category])))
        print('\ntotal dps: {}\ntotal hp: {}'.format(self.total_enemy_ground_dps, self.total_enemy_hp))
        print('-------------------- end of enemy info ----------------------')

    def on_unit_destroyed(self, unit_tag):
        self.remove_unit_from_enemy_info(unit_tag)

    def get_enemy_bases_amount(self):
        return len(self.enemy_info[BASES])
