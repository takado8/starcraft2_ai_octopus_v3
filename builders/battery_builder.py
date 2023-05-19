from sc2.ids.unit_typeid import UnitTypeId as unit


class BatteryBuilder:
    def __init__(self, ai):
        self.ai = ai

    async def build_batteries(self, when_minerals_more_than=600, amount=2):
        nexuses = self.ai.structures(unit.NEXUS)
        if nexuses.amount > 2 and self.ai.minerals > when_minerals_more_than:
            start_nexus = nexuses.closest_to(self.ai.start_location.position)
            nexuses.remove(start_nexus)
            second_nexus = self.ai.townhalls.closest_to(self.ai.main_base_ramp.bottom_center.towards(
                self.ai.main_base_ramp.top_center, -5))
            nexuses.remove(second_nexus)
            for nexus in nexuses:
                pylon = self.ai.structures(unit.PYLON).ready.closer_than(14, nexus)
                if pylon.exists:
                    pylon = pylon.furthest_to(self.ai.start_location.position)
                    batteries = self.ai.structures(unit.SHIELDBATTERY).closer_than(14, pylon.position)
                    if batteries.amount < amount \
                            and self.ai.already_pending(unit.SHIELDBATTERY) < amount:
                        await self.ai.build(unit.SHIELDBATTERY, pylon.position.towards(self.ai.game_info.map_center, 3),
                                            max_distance=8,
                                         random_alternative=False, placement_step=2,
                        validate_location=True if batteries.amount < amount / 2 else False)
                elif self.ai.already_pending(unit.PYLON) < 1:
                    minerals = self.ai.mineral_field.closest_to(nexus.position)
                    if minerals.distance_to(nexus.position) < 12:
                        pylon_spot = nexus.position.towards(minerals, -7)
                        await self.ai.build(unit.PYLON, pylon_spot)