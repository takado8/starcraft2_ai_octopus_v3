from typing import Dict, List
from army.soldier import Soldier
from sc2.unit import UnitTypeId
from sc2.units import Units



class Division:
    def __init__(self, ai, name, units_ids_dict, micros: List, movements, max_units_distance=20):
        self.ai = ai
        self.name = name
        self.units_ids_dict: Dict[UnitTypeId, int] = units_ids_dict
        self.soldiers: Dict[str, Soldier] = {}
        self.policy = None
        self.micros = micros
        self.movements = movements
        self.max_units_distance = max_units_distance

    async def do_micro(self):
        for micro in self.micros:
            await micro.do_micro(self.soldiers)

    def add_soldier(self, soldier):
        # if soldier.tag not in self.soldiers:
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

    def get_units(self):
        return Units([self.soldiers[soldier_tag].unit for soldier_tag in self.soldiers], self.ai)

    def get_position(self):
        max_neighbours = -1
        biggest_group = None
        division_units = self.get_units()
        for unit in division_units:
            neighbours = division_units.closer_than(self.max_units_distance, unit)
            if neighbours.amount > max_neighbours:
                max_neighbours = neighbours.amount
                biggest_group = neighbours

        center = biggest_group.center if biggest_group else None
        return center

    def __str__(self):
        return 'Division "{}" of count {} with micros "{}":\n{}'.format(self.name, len(self.soldiers),
        [str(m) for m in self.micros], ['{}: {}'.format(s, str(self.soldiers[s])) for s in self.soldiers])

    async def move_division(self, destination):
        await self.movements.move_division(self, destination)
