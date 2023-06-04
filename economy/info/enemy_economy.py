from sc2 import BotAI

# info categories
BASES = 'bases'
MILITARY = 'military'


class EnemyEconomy:
    def __init__(self, ai: BotAI):
        self.enemy_army_supply = 0
        self.enemy_army_value = 0
        self.ai = ai
        self.enemy_info = {}
        self.total_enemy_ground_dps = 0
        self.total_enemy_hp = 0
        self.lost_minerals_army = 0
        self.lost_gas_army = 0
        # self.killed_value_units = 0

    def lost_units_cost(self):
        self.lost_minerals_army = self.ai.state.score.killed_minerals_army
        self.lost_gas_army = self.ai.state.score.killed_vespene_army
        # self.killed_value_units = self.ai.state.score.killed_value_units

    def add_units_to_enemy_info(self, category, units):
        if units:
            if category not in self.enemy_info:
                self.enemy_info[category] = {}

            for unit in units:
                self.enemy_info[category][unit.tag] = unit

    def clear_category(self, category):
        if category in self.enemy_info:
            self.enemy_info.pop(category)

    def calculate_enemy_units_report(self):
        self.lost_units_cost()
        self.total_enemy_ground_dps = 0
        self.total_enemy_hp = 0
        self.enemy_army_value = 0
        self.enemy_army_supply = 0
        if MILITARY in self.enemy_info:
            for unit_tag in self.enemy_info[MILITARY]:
                unit = self.enemy_info[MILITARY][unit_tag]
                if unit:
                    self.total_enemy_ground_dps += unit.ground_dps
                    self.total_enemy_hp += unit.health + unit.shield
                    if unit.type_id:
                        try:
                            unit_cost = self.ai.calculate_cost(unit.type_id)
                            self.enemy_army_value += unit_cost.minerals + unit_cost.vespene * 3
                            unit_data = self.ai._game_data.units[unit.type_id.value]
                            unit_supply_cost = unit_data._proto.food_required
                            self.enemy_army_supply += unit_supply_cost
                        except:
                            print("cannot calculate cost of {}".format(unit.type_id))


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
            # for item in self.enemy_info[category]:
            #     print("   {}, {}".format(item, self.enemy_info[category][item]))
            print(" total: {}".format(len(self.enemy_info[category])))
        print('army value: {}'.format(self.enemy_army_value))
        print('army supply: {}'.format(self.enemy_army_supply))
        print('\ntotal dps: {}\ntotal hp: {}'.format(self.total_enemy_ground_dps, self.total_enemy_hp))
        print('lost value army: {}'.format(self.lost_minerals_army + self.lost_gas_army * 3))
        # print('lost gas army: {}'.format(self.lost_gas_army))
        print('-------------------- end of enemy info ----------------------')