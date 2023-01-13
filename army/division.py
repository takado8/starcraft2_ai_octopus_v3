from typing import Dict, List

from army.movements import Movements
from army.soldier import Soldier
from sc2.unit import UnitTypeId
from sc2.units import Units


class Division:
    def __init__(self, ai, name, units_ids_dict, micros: List, movements: Movements, max_units_distance=12,
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

    def get_units(self, unit_type_id=None):
        if unit_type_id:
            return Units([self.soldiers[soldier_tag].unit for soldier_tag in self.soldiers
                          if self.soldiers[soldier_tag].type_id == unit_type_id], self.ai)
        return Units([self.soldiers[soldier_tag].unit for soldier_tag in self.soldiers], self.ai)

    def get_attacking_units(self):
        return Units([self.soldiers[soldier_tag].unit for soldier_tag in self.soldiers
                          if self.soldiers[soldier_tag].unit.is_attacking], self.ai)

    def get_position(self):
        max_neighbours = -1
        position = None
        division_units = self.get_units()
        if division_units.amount > 1:
            for unit in division_units:
                neighbours = division_units.closer_than(self.max_units_distance, unit.position)
                if neighbours.amount > max_neighbours:
                    max_neighbours = neighbours.amount
                    position = unit.position
        elif division_units.amount == 1:
            position = division_units.first.position

        return position

    def get_units_amount(self):
        return len(self.soldiers)

    def __str__(self):
        return 'Division "{}" of count {} with micros "{}":\n{}'.format(self.name, len(self.soldiers),
        [str(m) for m in self.micros], ['{}: {}'.format(s, str(self.soldiers[s])) for s in self.soldiers])

    def __repr__(self):
        return str(self)
