from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.unit import UnitTypeId as unit


class EmergencyExpansion(InterfaceABS):

    def __init__(self, ai):
        self.ai = ai
        self.msg_send_on_nexuses_amount = 0
        self.lock_condition_cached = None
        self.excess_expansion_was_created_recently = False
        self.mineral_threshold1 = 2000
        self.mineral_threshold2 = 1500
        self.excess_expansion_threshold = 2000

    async def execute(self):
        nexuses = self.ai.structures(unit.NEXUS)
        if len(self.ai.strategy.workers_distribution.distant_mining_workers) >= (16 if self.ai.attack else 9) and not \
                nexuses.filter(lambda x: not x.is_ready) and not self.ai.already_pending(unit.NEXUS)\
                and (not self.ai.enemy_units() or not self.ai.enemy_units().closer_than(20, self.ai.defend_position)):
            if self.msg_send_on_nexuses_amount != nexuses.amount and not self.excess_expansion_was_created_recently:
                await self.ai.chat_send("Spending lock for expansion.")
                self.msg_send_on_nexuses_amount = nexuses.amount
                self.lock_condition_cached = self.ai.strategy.lock_spending_condition
                self.ai.strategy.lock_spending_condition = self.lock_condition_overwrite
            elif self.excess_expansion_was_created_recently:
                self.excess_expansion_was_created_recently = False
            await self.ai.strategy.builder.expander.expand()
        elif self.lock_condition_cached:
            self.ai.strategy.lock_spending_condition = self.lock_condition_cached
            self.lock_condition_cached = None
            await self.ai.chat_send("End of spending lock for expansion.")
        elif (self.ai.workers.amount < 80 and (self.ai.minerals > self.mineral_threshold1 or
                                               self.ai.minerals > self.mineral_threshold2 and self.ai.vespene < 50)
                or self.ai.minerals > self.excess_expansion_threshold) and not self.ai.already_pending(unit.NEXUS):
            await self.ai.strategy.builder.expander.expand()
            if self.msg_send_on_nexuses_amount != nexuses.amount:
                self.excess_expansion_was_created_recently = True
                await self.ai.chat_send("Excess expansion.")
                self.msg_send_on_nexuses_amount = nexuses.amount

    async def lock_condition_overwrite(self):
        return True