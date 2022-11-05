
class OwnEconomy:
    def __init__(self, ai):
        self.ai = ai
        self.total_own_ground_dps = 0
        self.total_own_hp = 0
        self.lost_minerals_army = 0
        self.lost_gas_army = 0

    def calculate_units_report(self):
        self.lost_units_cost()
        self.total_own_ground_dps = 0
        self.total_own_hp = 0
        for unit in self.ai.army:
            self.total_own_ground_dps += unit.ground_dps
            self.total_own_hp += unit.health + unit.shield

    def lost_units_cost(self):
        self.lost_minerals_army = self.ai.state.score.lost_minerals_army
        self.lost_gas_army = self.ai.state.score.lost_vespene_army

    def print_own_economy_info(self):
        print("----------------------- own economy ----------------------------")
        print('total dps: {}\ntotal hp: {}'.format(self.total_own_ground_dps, self.total_own_hp))
        print('lost minerals army: {}'.format(self.lost_minerals_army))
        print('lost gas army: {}'.format(self.lost_gas_army))
        print("----------------------- end own economy ------------------------")
