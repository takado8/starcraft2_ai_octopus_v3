from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.units import Units


class SecureExpansionLocations(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai
        self.units_tags = set()
        self.locations = []
        self.index = 0

    async def execute(self):
        units = Units([], self.ai)

        for unit_tag in self.units_tags:
            u = self.ai.units.find_by_tag(unit_tag)
            if u:
                if u.is_idle:
                    units.append(u)
            else:
                self.units_tags.remove(unit_tag)


        if len(units) < 3:
            new_units = self.ai.army().filter(lambda x: x.type_id == unit.STALKER and x.tag not in
                                                        self.units_tags and x.is_idle)
            new_units = new_units[:3-len(units)]
            units.extend(new_units)

        observer = self.ai.units(unit.OBSERVER).ready.idle
        if observer:
            observer = observer.closest_to(self.ai.defend_position)
            if units:
                locations = sorted(self.ai.expansion_locations_list, key=lambda x: x.distance_to(self.ai.start_location))
                locations = locations[:len(self.ai.townhalls) + 3]
                locations = [x for x in locations if not self.ai.townhalls.closer_than(10, x).exists]

                if observer.distance_to(locations[self.index]) < 5 and not (self.ai.enemy_units.exists or
                                                    self.ai.enemy_units.closer_than(12, observer).exists):
                    self.index += 1
                    if self.index >= len(locations):
                        self.index = 0
                observer.move(locations[self.index])
                for u in units:
                    u.move(locations[self.index])
                    self.ai.army.remove(u)