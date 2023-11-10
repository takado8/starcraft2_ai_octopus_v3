from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2 import BotAI
from sc2.position import Point2


class BuildingSpotValidator:
    def __init__(self, ai: BotAI):
        self.ai = ai

        self.building_pylon_max_dist = 25
        self.building_pylon_max_dist_increment = 5

        # linear function coefficients for build spot validation
        self.validation_coefficients = {}

    def is_valid_location(self, x, y):
        """
        :return: True if location is outside of minerals and gas transport area in the closest base, False otherwise.
        """
        point = Point2((x,y))
        expansion_location = min(self.ai.expansion_locations_list, key=lambda x: x.distance_to(point))
        if expansion_location in self.validation_coefficients:
            coe_a1, coe_b1, coe_a2, coe_b2, r, linear_function = self.validation_coefficients[expansion_location]
        else:
            coe_a1, coe_b1, coe_a2, coe_b2, r, linear_function = self.compute_coefficients(expansion_location)
            self.validation_coefficients[expansion_location] = coe_a1, coe_b1, coe_a2, coe_b2, r, linear_function

        condition1 = self.in_circle(x, y, expansion_location, r)
        if not condition1:
            return True  # outside of circle is a valid location for sure
        condition2 = linear_function(x, y, coe_a1, coe_b1)
        if not condition2:
            return True
        condition3 = linear_function(x, y, coe_a2, coe_b2)
        if not condition3:
            return True
        return False

    def compute_coefficients(self, expansion_location):
        n = expansion_location
        vespenes = self.ai.vespene_geyser.closer_than(9, n)
        g1 = vespenes.pop(0).position
        g2 = vespenes.pop(0).position

        delta1 = (g1.x - n.x)
        if delta1 == 0:
            print('delta == 0 !')
            delta1 = 1
        coe_a1 = (g1.y - n.y) / delta1
        coe_b1 = n.y - coe_a1 * n.x

        delta2 = (g2.x - n.x)
        if delta2 == 0:
            print('delta == 0 !')
            delta2 = 1
        coe_a2 = (g2.y - n.y) / delta2
        coe_b2 = n.y - coe_a2 * n.x

        max_ = 0
        minerals = self.ai.mineral_field.closer_than(9, n)
        minerals.append(g1)
        minerals.append(g2)
        for field in minerals:
            d = n.distance_to(field)
            if d > max_:
                max_ = d
        r = int(max_) ** 2

        if self.line_less_than(minerals[0].position.x, minerals[0].position.y, coe_a1, coe_b1):
            linear_function = self.line_less_than
        else:
            linear_function = self.line_bigger_than

        return coe_a1, coe_b1, coe_a2, coe_b2, r, linear_function

    @staticmethod
    def in_circle(x, y, n, r):
        return (x - n.x) ** 2 + (y - n.y) ** 2 < r

    @staticmethod
    def line_less_than(x, y, a, b):
        return y < a * x + b

    @staticmethod
    def line_bigger_than(x, y, a, b):
        return y > a * x + b

    def get_pylon_with_least_neighbours(self):
        properPylons = self.ai.structures().filter(lambda unit_: unit_.type_id == unit.PYLON
                        and unit_.is_ready and unit_.distance_to(self.ai.start_location.position) <
                                                                 self.building_pylon_max_dist)
        max_neighbours = 6
        if properPylons.exists:
            min_neighbours = 99
            pylon = None
            for pyl in properPylons:
                neighbours = self.ai.structures().filter(lambda unit_: unit_.type_id != unit.PYLON and
                                                                       unit_.distance_to(pyl) <= 6).amount
                if neighbours < min_neighbours:
                    min_neighbours = neighbours
                    pylon = pyl

            if min_neighbours > max_neighbours:
                self.building_pylon_max_dist += self.building_pylon_max_dist_increment
                return self.get_pylon_with_least_neighbours()

            return pylon
        else:
            print('No pylons in range {} from main base.'.format(self.building_pylon_max_dist))
            return None

    def get_super_pylon(self):
        pylons = self.ai.structures(unit.PYLON).ready
        if pylons.exists:
            pylons = pylons.closer_than(45, self.ai.start_location)
            if pylons.exists:
                pylons = pylons.sorted_by_distance_to(self.ai.enemy_start_locations[0])
                warps = self.ai.structures().filter(lambda x: x.type_id in {unit.WARPGATE, unit.NEXUS} and x.is_ready)
                if warps.exists:
                    for pylon in pylons:
                        if warps.closer_than(6.5, pylon).exists:
                            return pylon
                return pylons[-1]