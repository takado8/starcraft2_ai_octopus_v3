from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.unit_typeid import UnitTypeId as unit


class SecureMineralLines(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai

    async def execute(self):
        if self.ai.structures(unit.FORGE).ready.exists:
            for base in self.ai.townhalls:
                minerals = self.ai.mineral_field.closer_than(12, base.position)
                if minerals:
                    mineral = minerals.furthest_to(base.position)
                    pylon_position = mineral.position.towards(base.position, -2)
                    pylons = self.ai.structures(unit.PYLON).ready.closer_than(5, pylon_position)
                    if pylons:
                        pylon = pylons.closest_to(mineral.position)
                        cannons = self.ai.structures(unit.PHOTONCANNON)
                        if cannons:
                            cannons = cannons.closer_than(6, pylon.position)
                        if cannons.amount < 1 and not self.ai.already_pending(unit.PHOTONCANNON):
                            position = pylon_position#(minerals + [base]).center.towards(base.position, -2)
                            await self.ai.build(unit.PHOTONCANNON, near=position, max_distance=4, random_alternative=False,
                                            placement_step=1, validate_location=False)
                    elif not self.ai.already_pending(unit.PYLON):

                        await self.ai.build(unit.PYLON, near=pylon_position, max_distance=5, random_alternative=False,
                                            placement_step=1, validate_location=False)
        if self.ai.structures(unit.CYBERNETICSCORE).ready.exists:
            for base in self.ai.townhalls:
                minerals = self.ai.mineral_field.closer_than(12, base.position)
                if minerals:
                    mineral = minerals.furthest_to(base.position)
                    pylon_position = mineral.position.towards(base.position, -2)
                    pylons = self.ai.structures(unit.PYLON).ready.closer_than(5, pylon_position)
                    if pylons:
                        pylon = pylons.closest_to(mineral.position)
                        batteries = self.ai.structures(unit.SHIELDBATTERY)
                        if batteries:
                            batteries = batteries.closer_than(5, pylon.position)
                        if batteries.amount < 1 and not self.ai.already_pending(unit.SHIELDBATTERY):

                            position = (minerals + [base]).center.towards(base.position, 1)

                            await self.ai.build(unit.SHIELDBATTERY, near=position, max_distance=3, random_alternative=False,
                                            placement_step=1, validate_location=False)
                    elif not self.ai.already_pending(unit.PYLON):
                        position = mineral.position.towards(base.position, -2)
                        await self.ai.build(unit.PYLON, near=position, max_distance=5, random_alternative=False,
                                            placement_step=1, validate_location=False)