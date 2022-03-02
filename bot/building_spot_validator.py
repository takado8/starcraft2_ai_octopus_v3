from sc2.unit import Unit
from typing import Optional, Union
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2, Point3


class BuildingSpotValidator:
    def __init__(self, ai):
        self.ai = ai
        # linear function coefficients for build spot validation
        self.coe_a1 = None
        self.coe_a2 = None
        self.coe_b1 = None
        self.coe_b2 = None
        self.n = None
        self.g1 = None
        self.g2 = None
        self.r = None
        self.linear_func = None

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
        if self.is_valid_location(p.x, p.y):
            # print("valid location for " + str(building) + ": "+ str(p))
            builder = build_worker or self.ai.select_build_worker(p)
            if builder is None:
                return False
            self.ai.do(builder.build(building, p), subtract_cost=True)
            return True
        else:
            return False

    def compute_coefficients_for_building_validation(self):
        print('compute_coefficients_for_building_validation...')
        self.n = self.ai.structures(unit.NEXUS).closest_to(self.ai.start_location).position
        vespenes = self.ai.vespene_geyser.closer_than(9, self.n)
        self.g1 = vespenes.pop(0).position
        self.g2 = vespenes.pop(0).position

        delta1 = (self.g1.x - self.n.x)
        if delta1 == 0:
            print('delta == 0 !')
            delta1 = 1
        self.coe_a1 = (self.g1.y - self.n.y) / delta1
        self.coe_b1 = self.n.y - self.coe_a1 * self.n.x

        delta2 = (self.g2.x - self.n.x)
        if delta2 == 0:
            print('delta == 0 !')
            delta2 = 1
        self.coe_a2 = (self.g2.y - self.n.y) / delta2
        self.coe_b2 = self.n.y - self.coe_a2 * self.n.x

        max_ = 0
        minerals = self.ai.mineral_field.closer_than(9, self.n)
        minerals.append(self.g1)
        minerals.append(self.g2)
        for field in minerals:
            d = self.n.distance_to(field)
            if d > max_:
                max_ = d
        self.r = int(max_) ** 2
        if self.ai.start_location.position.y < self.ai.enemy_start_locations[0].position.y:
            self.linear_func = self.line_less_than
        else:
            self.linear_func = self.line_bigger_than
        print('done.')

    def is_valid_location(self, x, y):
        if self.linear_func is None:
            self.compute_coefficients_for_building_validation()

        condition1 = self.in_circle(x, y)
        if not condition1:
            return True  # outside of circle is a valid location for sure
        condition2 = self.linear_func(x, y, self.coe_a1, self.coe_b1)
        if not condition2:
            return True
        condition3 = self.linear_func(x, y, self.coe_a2, self.coe_b2)
        if not condition3:
            return True
        return False

    def in_circle(self, x, y):
        return (x - self.n.x) ** 2 + (y - self.n.y) ** 2 < self.r

    @staticmethod
    def line_less_than(x, y, a, b):
        return y < a * x + b

    @staticmethod
    def line_bigger_than(x, y, a, b):
        return y > a * x + b

    def get_proper_pylon(self):
        properPylons = self.ai.structures().filter(lambda unit_: unit_.type_id == unit.PYLON and unit_.is_ready and
                                                              unit_.distance_to(self.ai.start_location.position) < 27)
        if properPylons.exists:
            min_neighbours = 99
            pylon = None
            for pyl in properPylons:
                neighbours = self.ai.structures().filter(lambda unit_: unit_.distance_to(pyl) < 6).amount
                if neighbours < min_neighbours:
                    min_neighbours = neighbours
                    pylon = pyl
            return pylon
        else:
            print('cant find proper pylon')
            return None
