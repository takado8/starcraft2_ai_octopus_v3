from typing import Dict, List

from army.movements import Movements
from army.soldier import Soldier
from sc2.unit import UnitTypeId
from sc2.units import Units


class Division:
    def __init__(self, ai, name, units_ids_dict, micros: List, movements: Movements, max_units_distance=10,
                 lifetime=None):
        self.ai = ai
        self.name = name
        self.movements = movements
        self.units_ids_dict: Dict[UnitTypeId, int] = units_ids_dict
        self.soldiers: Dict[str, Soldier] = {}
        self.policy = None
        self.micros = micros
        self.max_units_distance = max_units_distance
        self.lifetime = lifetime
        self.attacking_units = None
        self.attacking_units_last_fetch = -1
        self.position = None
        self.position_last_fetch = -1
        self.units = None
        self.units_last_fetch = -1
        self.safety_backout_position = None
        self.safety_backout_position_last_fetch = -1

    async def do_micro(self, destination):
        units_in_position = 0
        for micro in self.micros:
            units_in_position += await micro.do_micro(self)
        self.movements.move_division(self, destination, units_in_position)

    def add_soldier(self, soldier):
        self.soldiers[soldier.tag] = soldier

    def remove_soldier(self, soldier_tag):
        if soldier_tag in self.soldiers:
            self.soldiers.pop(soldier_tag)

    def get_dict_of_missing_units(self):
        missing_units = {}
        for unit_id in self.units_ids_dict:
            unit_amount = 0
            for soldier_tag in self.soldiers:
                soldier = self.soldiers[soldier_tag]
                if soldier.type_id == unit_id:
                    unit_amount += 1
            desired_amount = self.units_ids_dict[unit_id]
            if unit_amount < desired_amount:
                missing_units[unit_id] = desired_amount - unit_amount
        return missing_units

    def get_units(self, iteration: int, unit_type_id: UnitTypeId=None):
        if unit_type_id:
            return Units([self.soldiers[soldier_tag].unit for soldier_tag in self.soldiers
                          if self.soldiers[soldier_tag].type_id == unit_type_id], self.ai)
        if self.units_last_fetch != iteration:
            self.units = Units([self.soldiers[soldier_tag].unit for soldier_tag in self.soldiers], self.ai)
            self.units_last_fetch = iteration
        return self.units

    def get_attacking_units(self, iteration):
        if self.attacking_units_last_fetch != iteration:
            self.attacking_units = Units([self.soldiers[soldier_tag].unit for soldier_tag in self.soldiers
                                          if self.soldiers[soldier_tag].unit.is_attacking], self.ai)
            self.attacking_units_last_fetch = iteration

        return self.attacking_units

    def get_position(self, iteration):
        if self.position_last_fetch != iteration:
            max_neighbours = -1
            position = None
            division_units = self.get_units(iteration)
            if division_units.amount > 1:
                for unit in division_units:
                    neighbours = division_units.closer_than(self.max_units_distance, unit.position)
                    if neighbours.amount > max_neighbours:
                        max_neighbours = neighbours.amount
                        position = unit.position
            elif division_units.amount == 1:
                position = division_units.first.position
            self.position = position
            self.position_last_fetch = iteration
        return self.position

    def get_safety_backout_position(self, iteration):
        if self.safety_backout_position_last_fetch != iteration:
            division_position = self.get_position(iteration)
            if division_position:
                enemies = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore and
                                        (x.can_attack_ground or x.can_attack_air)
                                                and x.distance_to(division_position) < 16)
                if enemies:
                    max_neighbours = -1
                    position = None
                    for enemy in enemies:
                        neighbours = enemies.closer_than(6, enemy)
                        if neighbours.amount > max_neighbours:
                            max_neighbours = neighbours.amount
                            position = enemy.position
                    safety_position = division_position.towards(position, -10)
                    self.safety_backout_position = self._find_back_out_position(safety_position)

        return self.safety_backout_position

    def _find_back_out_position(self, position):
        j = 1
        while not self.ai.in_pathing_grid(position) and j < 5:
            k = 0
            distance = j * 2
            while not self.ai.in_pathing_grid(position) and k < 20:
                k += 1
                position = position.random_on_distance(distance)
            j += 1
        return position

    def get_units_amount(self):
        return len(self.soldiers)

    def __str__(self):
        return 'Division "{}" of count {} with micros "{}":\n{}'.format(self.name, len(self.soldiers),
        [str(m) for m in self.micros], ['{}: {}'.format(s, str(self.soldiers[s])) for s in self.soldiers])

    def __repr__(self):
        return str(self)
