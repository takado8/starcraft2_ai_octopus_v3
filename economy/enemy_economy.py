from sc2 import BotAI

# info categories
BASES = 'bases'
MILITARY = 'military'


class EnemyEconomy:
    def __init__(self, ai: BotAI):
        self.ai = ai
        self.enemy_info = {}
        self.total_enemy_ground_dps = 0
        self.total_enemy_hp = 0
        self.killed_minerals_army = 0
        self.killed_gas_army = 0
        # self.killed_value_units = 0

    def lost_units_cost(self):
        self.killed_minerals_army = self.ai.state.score.killed_minerals_army
        self.killed_gas_army = self.ai.state.score.killed_vespene_army
        # self.killed_value_units = self.ai.state.score.killed_value_units

    def add_units_to_enemy_info(self, category, units):
        if units:
            if category not in self.enemy_info:
                self.enemy_info[category] = {}

            for unit in units:
                self.enemy_info[category][unit.tag] = unit

    def calculate_enemy_units_report(self):
        self.lost_units_cost()
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
                # print('unit {} removed from info.'.format(u))

    def on_unit_destroyed(self, unit_tag):
        # print('unit of tag {} destroyed.'.format(unit_tag))
        self.remove_unit_from_enemy_info(unit_tag)

    def get_enemy_bases_amount(self):
        return len(self.enemy_info[BASES])

    def print_enemy_info(self):
        print('-------------------- enemy info -----------------------------')
        self.calculate_enemy_units_report()
        for category in self.enemy_info:
            print("{}:".format(category))
            for item in self.enemy_info[category]:
                print("   {}, {}".format(item, self.enemy_info[category][item]))
            print(" total: {}".format(len(self.enemy_info[category])))
        print('\ntotal dps: {}\ntotal hp: {}'.format(self.total_enemy_ground_dps, self.total_enemy_hp))
        print('killed minerals army: {}'.format(self.killed_minerals_army))
        print('killed gas army: {}'.format(self.killed_gas_army))
        print('-------------------- end of enemy info ----------------------')