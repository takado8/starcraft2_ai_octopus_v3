from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.unit import UnitTypeId as unit


class SetNexusResp(InterfaceABS):

    def __init__(self, ai):
        self.ai = ai

    async def execute(self):
        if 60 < self.ai.time < 360:
            workers = self.ai.workers
            if self.ai.townhalls.exists:
                first_nexus = self.ai.townhalls.closer_than(5, self.ai.start_location)
                if first_nexus:
                    first_nexus = first_nexus.first
                    if workers.amount >= 16 and (not self.ai.enemy_units or not self.ai.enemy_units.closer_than(40,
                                                                                        self.ai.start_location)):

                        position = first_nexus.position.towards(self.ai.mineral_field.closest_to(first_nexus), -5)
                        if workers.amount < 20 and first_nexus.is_idle:
                            first_nexus.train(unit.PROBE)
                    else:
                        position = first_nexus.position.towards(self.ai.mineral_field.closest_to(first_nexus), 3)

                    first_nexus(ability.SMART, position)