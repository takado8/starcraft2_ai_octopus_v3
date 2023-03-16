
class OwnEconomy:
    def __init__(self, ai):
        self.ai = ai

    @property
    def total_own_ground_dps_and_hp(self):
        total_own_ground_dps = 0
        total_own_hp = 0
        for unit in self.ai.army:
            total_own_ground_dps += unit.ground_dps
            total_own_hp += unit.health + unit.shield
        return total_own_ground_dps, total_own_hp

    @property
    def lost_minerals_army(self):
        return self.ai.state.score.lost_minerals_army

    @property
    def lost_gas_army(self):
        return self.ai.state.score.lost_vespene_army

    def print_own_economy_info(self):
        total_own_ground_dps, total_own_hp = self.total_own_ground_dps_and_hp
        print("----------------------- own economy ----------------------------")
        print('total dps: {}\ntotal hp: {}'.format(total_own_ground_dps, total_own_hp))
        print('lost minerals army: {}'.format(self.lost_minerals_army))
        print('lost gas army: {}'.format(self.lost_gas_army))
        print("----------------------- end own economy ------------------------")
