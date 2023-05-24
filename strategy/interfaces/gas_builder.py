from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.unit import UnitTypeId as unit


class GasBuilder(InterfaceABS):

    def __init__(self, ai):
        self.ai = ai

    async def execute(self):
        if 60 < self.ai.time < 360 and (not self.ai.enemy_units.exists or not self.ai.enemy_units
                .closer_than(40, self.ai.start_location).exists):
            if self.ai.structures(unit.ASSIMILATOR).amount < 2 and self.ai.structures(unit.GATEWAY).exists:
                geysers = self.ai.vespene_geyser.filter(lambda x: x.distance_to(self.ai.start_location) < 12
                                            and (not self.ai.structures(unit.ASSIMILATOR).exists or
                                not self.ai.structures(unit.ASSIMILATOR).closer_than(2,x).exists))
                geyser = geysers.closest_to(self.ai.start_location)
                worker = self.ai.workers.furthest_to(self.ai.start_location)
                worker.build(unit.ASSIMILATOR, geyser)