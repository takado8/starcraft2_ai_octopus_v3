class Movements:
    def __init__(self, ai, units_ratio_before_next_step=0.7, movements_step=25):
        self.ai = ai
        self.units_ratio_before_next_step = units_ratio_before_next_step
        self.movements_step = movements_step

    def move_division(self, division, destination, units_in_position):
        if destination and units_in_position:
            division_position = division.get_position()
            if units_in_position > division.get_units_amount() * self.units_ratio_before_next_step:
                if division_position and division_position.distance_to(destination) > self.movements_step:
                    position = self.find_placement_for_units(division_position.towards(destination, self.movements_step))
                elif destination:
                    position = self.find_placement_for_units(destination)
                else:
                    position = None
                if position:
                    division_units = division.get_units()
                    for soldier in division_units:
                        soldier.attack(position)

    def find_placement_for_units(self, position):
        i = 3
        while not self.ai.in_pathing_grid(position) and i < 6:
            position = position.random_on_distance(i)
            i += 1
            j = 1
            while not self.ai.in_pathing_grid(position) and j < 5:
                k = 0
                while not self.ai.in_pathing_grid(position) and k < 12:
                    position = position.random_on_distance(j * 2)
                    k+=1
                j += 1
        return position if self.ai.in_pathing_grid(position) else None