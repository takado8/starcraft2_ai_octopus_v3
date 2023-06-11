from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade



class AttackInformant(InterfaceABS):

    def __init__(self, ai):
        self.ai = ai
        self.previous_attack_state = False

    async def execute(self):
        if self.ai.attack != self.previous_attack_state or self.ai.attack and self.ai.iteration % 100 == 0:
            self.previous_attack_state = self.ai.attack
            if self.ai.attack:
                word = 'Attacking'
            else:
                word = 'Retreating'
            msg = "{} with army value {} vs {}".format(word, self.ai.strategy.own_economy.army_value,
                                self.ai.strategy.enemy_economy.army_value)
            print(msg)
            await self.ai.chat_send(msg)