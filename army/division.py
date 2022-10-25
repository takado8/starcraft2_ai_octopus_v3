from typing import Dict, List
from army.soldier import Soldier


class Division:
    def __init__(self, name, units_ids_list, micro):
        self.name = name
        self.units_ids_list = units_ids_list
        self.soldiers: Dict[str, Soldier] = {}
        self.policy = None
        self.micro = micro

    def do_micro(self):
        self.micro()

    def add_soldier(self, soldier):
        # if soldier.tag not in self.soldiers:
        self.soldiers[soldier.tag] = soldier

    def remove_soldier(self, soldier_tag):
        if soldier_tag in self.soldiers:
            self.soldiers.pop(soldier_tag)

    def get_list_of_missing_units(self):
        desired = [x for x in self.units_ids_list]
        for soldier_tag in self.soldiers:
            desired.remove(self.soldiers[soldier_tag].type_id)
        return desired