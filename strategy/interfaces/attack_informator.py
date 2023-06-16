from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade


class AttackInformant(InterfaceABS):

    def __init__(self, ai):
        self.ai = ai
        self.previous_attack_state = False

    async def execute(self):
        if self.ai.attack != self.previous_attack_state or (self.ai.attack and self.ai.iteration % 100 == 0) or \
                (self.ai.iteration % 500 == 0 and self.ai.iteration > 0):

            self.previous_attack_state = self.ai.attack
            if self.ai.iteration % 500 == 0:
                word = 'Chillin\''
            else:
                if self.ai.attack:
                    word = 'Attacking'
                else:
                    word = 'Retreating'
            fitness = self.ai.strategy.army_fitness.get_army_fitness()
            msg = "{} with army value {} vs {}, fit -{} vs -{}".format(word, round(self.ai.strategy.own_economy.army_value),
                                round(self.ai.strategy.enemy_economy.army_value), round(fitness[0]), round(fitness[1]))
            print(msg)
            await self.ai.chat_send(msg)