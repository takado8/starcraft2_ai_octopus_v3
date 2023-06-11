from bot.constants import GAS_VALUE


class OwnEconomy:
    def __init__(self, ai):
        self.ai = ai

    @property
    def army_value(self):
        army_value = 0
        for unit in self.ai.army:
            try:
                unit_cost = self.ai.calculate_cost(unit.type_id)
                army_value += unit_cost.minerals + unit_cost.vespene * GAS_VALUE
            except:
                print('cannot get unit value: {}'.format(unit.type_id))
        return army_value

    @property
    def army_stats(self):
        army_value = 0
        total_own_ground_dps = 0
        total_own_hp = 0
        for unit in self.ai.army:
            total_own_ground_dps += unit.ground_dps
            total_own_hp += unit.health + unit.shield

            unit_cost = self.ai.calculate_cost(unit.type_id)
            army_value += unit_cost.minerals + unit_cost.vespene * GAS_VALUE

        return total_own_ground_dps, total_own_hp, army_value, self.ai.state.score.food_used_army

    @property
    def lost_minerals_army(self):
        return self.ai.state.score.lost_minerals_army

    @property
    def lost_gas_army(self):
        return self.ai.state.score.lost_vespene_army


    def print_own_economy_info(self):
        total_own_ground_dps, total_own_hp, value, supply = self.army_stats
        print("----------------------- own economy ----------------------------")
        print('army value: {}'.format(value))
        # print('total dps: {}\ntotal hp: {}'.format(total_own_ground_dps, total_own_hp))
        print('lost value army: {}'.format(self.lost_minerals_army + self.lost_gas_army * GAS_VALUE))
        # print('lost gas army: {}'.format(self.lost_gas_army))
        print("----------------------- end own economy ------------------------")
