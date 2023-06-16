from bot.constants import GAS_VALUE
from economy.info.enemy_economy import MILITARY
from sc2.unit import UnitTypeId as unit


class ArmyFitness:
    def __init__(self, ai):
        self.ai = ai
        self.last_iteration = 0
        self.last_result = 0, 0

    def get_army_fitness(self):
        if self.last_iteration == self.ai.iteration:
            return self.last_result
        enemy_armored_value = 0
        enemy_light_value = 0
        # enemy_other_value = 0
        enemy_bonus_armored_value = 0
        enemy_bonus_light_value = 0
        # enemy_bonus_other_value = 0

        if MILITARY in self.ai.strategy.enemy_economy.enemy_info:
            for unit_tag in self.ai.strategy.enemy_economy.enemy_info[MILITARY]:
                unit_ = self.ai.strategy.enemy_economy.enemy_info[MILITARY][unit_tag]
                try:
                    unit_cost = self.ai.calculate_cost(unit_.type_id)
                    unit_value = unit_cost.minerals + unit_cost.vespene * GAS_VALUE
                    if unit_.is_armored:
                        enemy_armored_value += unit_value
                    elif unit_.is_light:
                        enemy_light_value += unit_value
                    # else:
                    #     enemy_other_value += unit_value
                    if unit_.bonus_damage:
                        bonus_dmg_type = unit_.bonus_damage[1]
                    else:
                        bonus_dmg_type = None
                    if bonus_dmg_type == 'Armored':
                        enemy_bonus_armored_value += unit_value
                    elif bonus_dmg_type == 'Light':
                        enemy_bonus_light_value += unit_value
                    # else:
                    #     # print('unit bonus is: {} of type: {}'.format(bonus_dmg_type, type(bonus_dmg_type)))
                    #     enemy_bonus_other_value += unit_value
                except:
                    print("cannot calculate cost of {}".format(unit_.type_id))

        own_armored_value = 0
        own_light_value = 0
        # own_other_value = 0
        own_bonus_armored_value = 0
        own_bonus_light_value = 0
        # own_bonus_other_value = 0
        excluded = {unit.WARPPRISM, unit.WARPPRISMPHASING, unit.OBSERVER}
        for unit_ in self.ai.army().filter(lambda x: x.type_id not in excluded):
            # try:
            unit_cost = self.ai.calculate_cost(unit_.type_id)
            unit_value = unit_cost.minerals + unit_cost.vespene * GAS_VALUE
            if unit_.is_armored:
                own_armored_value += unit_value
            elif unit_.is_light:
                own_light_value += unit_value
            # else:
            #     own_other_value += unit_value
            if unit_.bonus_damage:
                bonus_dmg_type = unit_.bonus_damage[1]
            else:
                bonus_dmg_type = None
            if bonus_dmg_type == 'Armored':
                own_bonus_armored_value += unit_value
            elif bonus_dmg_type == 'Light':
                own_bonus_light_value += unit_value
            # else:
            #     # print('unit bonus is: {} of type: {}'.format(bonus_dmg_type, type(bonus_dmg_type)))
            #     own_bonus_other_value += unit_value
            # except:
            #     print("cannot calculate cost of {}".format(unit_.type_id))

        own_armored_fitness = abs(enemy_armored_value - own_bonus_armored_value)
        own_light_fitness = abs(enemy_light_value - own_bonus_light_value)
        # own_other_fitness = abs(enemy_other_value - own_bonus_other_value)

        enemy_armored_fitness = abs(own_armored_value - enemy_bonus_armored_value)
        enemy_light_fitness = abs(own_light_value - enemy_bonus_light_value)
        # enemy_other_fitness = abs(own_other_value - enemy_bonus_other_value)

        self.last_iteration = self.ai.iteration
        self.last_result = (own_armored_fitness + own_light_fitness) * 0.33, \
                           (enemy_armored_fitness + enemy_light_fitness) * 0.33
        return self.last_result
