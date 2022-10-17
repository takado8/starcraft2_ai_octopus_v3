from sc2.ids.unit_typeid import UnitTypeId as Unit
from sc2 import AbilityId, BotAI

# scouting categories
BASES = 'bases'


class Scouting:
    def __init__(self, ai_object: BotAI):
        self.ai = ai_object
        self.enemy_info = {}
        self.scouting_index = -1
        self.scouting_positions = []

    def scan_middle_game(self):
        scouts = self.ai.units(Unit.PHOENIX).filter(lambda z: z.is_hallucination)
        if scouts.exists:
            if BASES not in self.enemy_info or len(self.scouting_positions) < len(self.enemy_info[BASES]) + 2:
                self.scouting_positions.clear()
                self.scouting_positions = self.create_scouting_positions_list()

            print('sct idx: {}'.format(self.scouting_index))
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

    def add_units_to_enemy_info(self, category, units):
        if units:
            if category in self.enemy_info:
                for unit in units:
                    self.enemy_info[category][unit.tag] = unit.type_id
            else:
                self.enemy_info[category] = {}
                for unit in units:
                    self.enemy_info[category][unit.tag] = unit.type_id

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
            for sentry in sentries:
                sentry_energy = sentry.energy_percentage
                self.ai.do(sentry(AbilityId.HALLUCINATION_PHOENIX))
                if sentry_energy < 1:
                    break

    def print_enemy_info(self):
        print('-------------------- enemy info -----------------------------')
        for category in self.enemy_info:
            print("{}:".format(category))
            for item in self.enemy_info[category]:
                print("   {}, {}".format(item, self.enemy_info[category][item]))
            print(" total: {}".format(len(self.enemy_info[category])))
        print('-------------------- end of enemy info ----------------------')
