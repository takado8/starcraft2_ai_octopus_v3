from sc2.unit import Unit
from typing import Optional, Union
from sc2.position import Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.building_spot_validator import BuildingSpotValidator
from bot.constants import STRUCTURES_RADIUS


class Builder:
    GAP_SIZE = 0.6

    def __init__(self, ai, build_queue, expander, special_building_locations=None):
        self.ai = ai
        self.expander = expander
        self.validator = BuildingSpotValidator(ai)
        self.build_queue = build_queue
        self.build_queue_index = 0
        self.special_building_locations = special_building_locations
        self.structures_max_radius = sorted(STRUCTURES_RADIUS, key=lambda x: STRUCTURES_RADIUS[x], reverse=True)[1]


    async def build_from_queue(self):
        order_dict = {}
        for i in range(self.build_queue_index + 1):
            building = self.build_queue[i]
            if isinstance(building, unit):
                if building in order_dict:
                    order_dict[building][1] += 1
                else:
                    amount = self.ai.structures(building).amount
                    order_dict[building] = [amount, 1]
        if unit.GATEWAY in order_dict:
            warpgate_amount = self.ai.structures(unit.WARPGATE).amount
            order_dict[unit.GATEWAY][0] += warpgate_amount
        if unit.NEXUS in order_dict:
            order_dict[unit.NEXUS][1] += 1
        # print('order dict: {}'.format(order_dict))
        all_done = True
        for building in order_dict:
            if order_dict[building][0] < order_dict[building][1]:
                all_done = False
                # print('need to build: {}'.format(building))
                if self.ai.can_afford(building) and self.ai.already_pending(building) < \
                        (2 if building in {unit.GATEWAY, unit.PHOTONCANNON, unit.SHIELDBATTERY} else 1):
                    if building == unit.NEXUS:
                        await self.expander.expand()
                        return
                    elif self.special_building_locations and\
                            any([building in locations for locations in self.special_building_locations]):
                        all_building_types = None
                        if building == unit.GATEWAY:
                            all_building_types = {unit.GATEWAY, unit.WARPGATE}
                        locations = []
                        for location_list in self.special_building_locations:
                            if building in location_list:
                                locations.extend(location_list[building])

                        for location in locations:
                            if not self.ai.structures(all_building_types if all_building_types else building)\
                                    .closer_than(1, location).exists:
                                await self.ai.build(building, near=location,
                                                placement_step=1, max_distance=1,
                                                random_alternative=False, validate_location=False)
                                return

                    pylon = self.ai.get_pylon_with_least_neighbours()
                    if pylon:
                        await self.ai.build(building, near=pylon, placement_step=4, max_distance=47,
                                        random_alternative=True)
                        # else:
                            # print("pylon is none")
        if all_done:
            # print('all done.')
            if self.build_queue_index + 1 < len(self.build_queue):
                self.build_queue_index += 1

    def get_current_building(self):
        return self.build_queue[self.build_queue_index]

    async def build(self, building: unit, near: Union[Unit, Point2, Point3], max_distance: int = 45, block=False,
                    build_worker: Optional[Unit] = None, random_alternative: bool = True,
                    placement_step: int = 3, validate_location=True, ) -> bool:
        assert isinstance(near, (Unit, Point2, Point3))
        near_pylon = None
        if isinstance(near, Unit):
            if near.type_id == unit.PYLON:
                near_pylon = near
            near = near.position
        near = near.to2
        if not self.ai.can_afford(building, check_supply_cost=not block):
            # print('cant afford')
            return False
        if validate_location:
            place = None
            loops = 5 if near_pylon else 1
            try:
                radius = STRUCTURES_RADIUS[building]
            except:
                radius = self.structures_max_radius
            distance = self.GAP_SIZE + radius
            for k in range(loops):
                i=0
                while place is None and i < 50:
                    i+=1
                    place = await self.ai.find_placement(building, near, max_distance, random_alternative, placement_step)

                    if place:
                        neighbours = self.ai.structures().filter(lambda x: x.distance_to(place) < x.radius + distance)
                        if neighbours.amount == 0:
                            break
                        else:
                            if i < 50:
                                place = None
                if near_pylon and i == 50 and k < loops - 1:
                    print('changing pylon...')
                    place = None
                    pylons = self.ai.structures().filter(lambda x: x.is_ready and x.type_id == unit.PYLON
                                                                   and x.tag != near_pylon.tag)

                    pylons = sorted(pylons, key=lambda x: self.ai.structures().filter(lambda y:
                                                        y.type_id != unit.PYLON and y.distance_to(x) <= 6).amount)
                    if pylons:
                        near_pylon = pylons[0]
                        near = near_pylon.position.to2
        else:
            place = await self.ai.find_placement(building, near, max_distance, random_alternative, placement_step)

        if place is None:
            # print('position none')
            return False
        # validate
        if self.validator.is_valid_location(place.x, place.y):
            # print("valid location for " + str(building) + ": "+ str(p))
            builder = build_worker or self.ai.select_build_worker(place)
            if builder is None:
                return False
            builder.build(building, place)
            return True
        else:
            return False

    def is_build_finished(self):
        return self.build_queue_index + 1 == len(self.build_queue)

    def is_build_in_progress(self):
        for building in self.build_queue:
            if isinstance(building, unit):
                if self.ai.already_pending(building):
                    return True
        return False

    def increment_build_queue_index(self):
        self.build_queue_index += 1