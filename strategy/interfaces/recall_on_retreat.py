from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.ability_id import AbilityId as ability


class RecallOnRetreat(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai
        self.previous_attack_state = False

    async def execute(self):
        if self.previous_attack_state is True and self.ai.attack is False:
            nexuses = self.ai.townhalls().filter(lambda x: x.energy >= 50)
            if nexuses:
                nexus = nexuses.closest_to(self.ai.start_location)
                abilities = await self.ai.get_available_abilities(nexus)
                if ability.EFFECT_MASSRECALL_NEXUS in abilities:
                    target = max(self.ai.army, key=lambda x: self.ai.army.closer_than(6.5, x).amount)
                    if any(townhall.distance_to(target) < 18 for townhall in self.ai.townhalls):
                        return
                    nexus(ability.EFFECT_MASSRECALL_NEXUS, target.position)
        self.previous_attack_state = self.ai.attack
