from sc2.unit import Unit
from typing import Optional, Union
from sc2.position import Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.building_spot_validator import BuildingSpotValidator


class Builder:
    def __init__(self, ai, build_queue, expander, special_building_locations=None):
        self.ai = ai
        self.expander = expander
        self.validator = BuildingSpotValidator(ai)
        self.build_queue = build_queue
        self.build_queue_index = 0
        self.special_building_locations = special_building_locations

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
                        (2 if building == unit.GATEWAY else 1):
                    if building == unit.NEXUS:
                        await self.expander.expand()
                        return
                    elif self.special_building_locations and building in self.special_building_locations:
                        all_building_types = None
                        if building == unit.GATEWAY:
                            all_building_types = {unit.GATEWAY, unit.WARPGATE}
                        location = self.special_building_locations[building]
                        if not self.ai.structures(all_building_types if all_building_types else building)\
                                .closer_than(1, location).exists:
                            await self.ai.build(building, near=location,
                                            placement_step=1, max_distance=1,
                                            random_alternative=False)
                            return

                    pylon = self.ai.get_pylon_with_least_neighbours()
                    if pylon:
                        await self.ai.build(building, near=pylon, placement_step=3, max_distance=45,
                                        random_alternative=True)
                        # else:
                            # print("pylon is none")
        if all_done:
            # print('all done.')
            if self.build_queue_index + 1 < len(self.build_queue):
                self.build_queue_index += 1

    def get_current_building(self):
        return self.build_queue[self.build_queue_index]

    async def build(self, building: unit, near: Union[Unit, Point2, Point3], max_distance: int = 20, block=False,
                    build_worker: Optional[Unit] = None, random_alternative: bool = True,
                    placement_step: int = 3, ) -> bool:
        assert isinstance(near, (Unit, Point2, Point3))
        if isinstance(near, Unit):
            near = near.position
        near = near.to2
        if not self.ai.can_afford(building, check_supply_cost=not block):
            # print('cant afford')
            return False

        p = await self.ai.find_placement(building, near, max_distance, random_alternative, placement_step)
        if p is None:
            # print('position none')
            return False
        # validate
        if self.validator.is_valid_location(p.x, p.y):
            # print("valid location for " + str(building) + ": "+ str(p))
            builder = build_worker or self.ai.select_build_worker(p)
            if builder is None:
                return False
            builder.build(building, p)
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