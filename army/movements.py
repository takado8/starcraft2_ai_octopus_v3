from sc2.ids.unit_typeid import UnitTypeId as unit


class Movements:
    def __init__(self, ai, units_ratio_before_next_step=0.7):
        self.ai = ai
        self.position = None
        self.units_ratio_before_next_step = units_ratio_before_next_step

    async def move_division(self, division, destination):
        if destination is None:
            return
        division_units = division.get_units()

        if self.position is None:
            division_position = division.get_position()
            if division_position is None:
                return
            distance = division_position.distance_to(destination)
            step = 35
            if distance > step:
                point = division_position.towards(destination, step)
            else:
                point = destination

            self.position = await self.find_placement_for_army(point)

        # if everybody's here, we can go
        _range = 7 if division_units.amount < 27 else 14
        units_in_position_count = 0

        enemy = None
        division_position = division.get_position()
        if division_position:
            enemy = self.ai.enemy_units().filter(
                    lambda unit_: unit_.can_attack_ground and
                                  unit_.distance_to(division_position) <= division.max_units_distance and
                                  unit_.type_id not in self.ai.units_to_ignore)
        for man in division_units:
            if man.distance_to(self.position) <= _range:  # in position
                units_in_position_count += 1
                if enemy and not enemy.closer_than(man.ground_range + man.radius, man.position).exists:
                    # go help someone who is fighting
                    attacking_friend = division_units.filter(lambda x: x.is_attacking)
                    if attacking_friend.exists:
                        man.attack(enemy.closest_to(attacking_friend.closest_to(man.position).position).position)
            elif man.type_id not in {unit.ZEALOT, unit.DARKTEMPLAR} or not man.is_attacking:  # away. join army
                man.attack(self.position)

        if units_in_position_count > len(division_units) * self.units_ratio_before_next_step:  # take next position
            self.position = None

    def find_placement_for_unit(self, position):
        i = 3
        while not self.ai.in_pathing_grid(position) and i < 6:
            position = position.random_on_distance(i)
            i += 1
            j = 1
            while not self.ai.in_pathing_grid(position) and j < 3:
                # print('func j: ' + str(j))
                position = position.random_on_distance(j)
                j += 1

    async def find_placement_for_army(self, point):
        position = None
        i = 0
        while position is None:
            i += 1
            position = await self.ai.find_placement(unit.PYLON, near=point.random_on_distance(i * 2), max_distance=5,
                                                    placement_step=2, random_alternative=False)
            if i > 7:
                print("can't find position for army.")
        return position