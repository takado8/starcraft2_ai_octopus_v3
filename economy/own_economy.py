
class OwnEconomy:
    def __init__(self, ai):
        self.ai = ai
        self.total_own_ground_dps = 0
        self.total_own_hp = 0

    def calculate_units_report(self):
        self.total_own_ground_dps = 0
        self.total_own_hp = 0
        for unit in self.ai.army:
            self.total_own_ground_dps += unit.ground_dps
            self.total_own_hp += unit.health + unit.shield

    def print_own_economy_info(self):
        self.calculate_units_report()
        print("----------------------- own economy ----------------------------")
        print('total dps: {}\ntotal hp: {}'.format(self.total_own_ground_dps, self.total_own_hp))
        print("----------------------- end own economy ------------------------")
