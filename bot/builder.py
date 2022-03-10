from sc2.unit import Unit
from typing import Optional, Union
from sc2.position import Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.building_spot_validator import BuildingSpotValidator


class Builder:
    def __init__(self, ai):
        self.ai = ai
        self.validator = BuildingSpotValidator(ai)

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
            self.ai.do(builder.build(building, p), subtract_cost=True)
            return True
        else:
            return False