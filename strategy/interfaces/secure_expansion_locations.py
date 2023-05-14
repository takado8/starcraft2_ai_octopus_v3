from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.unit_typeid import UnitTypeId as unit


class SecureExpansionLocations(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai
        self.locations = []
        self.index = 0

    async def execute(self):
        observers = self.ai.units(unit.OBSERVER).ready
        locations = [x for x in sorted(self.ai.expansion_locations_list,
                                       key=lambda x: x.distance_to(self.ai.start_location))
                     if not self.ai.townhalls.closer_than(10, x).exists and
        (not self.ai.enemy_structures().exists or not self.ai.enemy_structures().closer_than(10, x).exists)]
        locations = locations[:3]

        for observer in observers:

            if (observer.distance_to(locations[self.index]) < 6 or observer.is_idle) and not (self.ai.enemy_units.exists or
                                                self.ai.enemy_units.closer_than(12, observer).exists):
                self.index += 1
                if self.index >= len(locations):
                    self.index = 0

                observer.move(locations[self.index])