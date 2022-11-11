from sc2.ids.unit_typeid import UnitTypeId as unit


class BatteryBuilder:
    def __init__(self, ai):
        self.ai = ai

    async def build_batteries(self):
        nexuses = self.ai.structures(unit.NEXUS).ready
        if nexuses.amount > 1:
            start_nexus = nexuses.closest_to(self.ai.start_location.position)
            nexuses.remove(start_nexus)
            for nexus in nexuses:
                pylon = self.ai.structures(unit.PYLON).ready.closer_than(11, nexus)
                if pylon.exists:
                    pylon = pylon.furthest_to(nexus)
                    if self.ai.structures(unit.SHIELDBATTERY).closer_than(5, pylon.position).amount < 2 \
                            and self.ai.already_pending(unit.SHIELDBATTERY) < 2:
                        await self.ai.build(unit.SHIELDBATTERY, pylon.position, max_distance=5,
                                         random_alternative=False, placement_step=2)
                elif self.ai.already_pending(unit.PYLON) < 1:
                    minerals = self.ai.mineral_field.closest_to(nexus.position)
                    if minerals.distance_to(nexus.position) < 12:
                        pylon_spot = nexus.position.towards(minerals, -7)
                        await self.ai.build(unit.PYLON, pylon_spot)