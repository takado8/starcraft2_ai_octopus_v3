from sc2.unit import Unit
from .division import Division
from .soldier import Soldier
from typing import Dict, List
from bot.constants import ARMY_IDS


class Army:
    # TODO try genetic algo to calc army composition accordingly to enemy army type
    def __init__(self, ai_object):
        self.ai = ai_object
        self.status: ArmyStatus = ArmyStatus.DEFENSE_POSITION
        self.divisions: Dict[str, Division] = {}
        self.unassigned_soldiers: List[Soldier] = []
        self.all_soldiers: Dict[str, Soldier] = {}

    async def execute_divisions_orders(self):
        for division in self.divisions:
            await self.divisions[division].do_micro()

    def establish_army_status(self):
        pass

    def select_targets(self):
        pass

    def create_division(self, division_name, units_ids_dict, micros: List):
        if division_name in self.divisions:
            print('Division "{}" already exists.'.format(division_name))
        else:
            new_division = Division(division_name, units_ids_dict, micros)
            self.divisions[division_name] = new_division
            return new_division

    def train_divisions(self):
        all_missing_units = {}
        for division in self.divisions:
            missing_units = self.divisions[division].get_dict_of_missing_units()
            for unit_id in missing_units:
                unit_amount = 0
                for soldier in self.unassigned_soldiers:
                    if unit_amount < missing_units[unit_id]:
                        if unit_id == soldier.type_id:
                            unit_amount += 1
                            self.divisions[division].add_soldier(soldier)
                            soldier.division_name = division
                            self.unassigned_soldiers.remove(soldier)
                            missing_units[unit_id] -= 1
                    else:
                        break
            for unit_id2 in missing_units:
                if unit_id2 in all_missing_units:
                    all_missing_units[unit_id2] += missing_units[unit_id2]
                else:
                    all_missing_units[unit_id2] = missing_units[unit_id2]

        self.order_unit_training(all_missing_units)

    def order_unit_training(self, units_ids_dict):
        pass

    def refresh_all_soldiers(self):
        all_units = self.ai.units().filter(lambda x: x.type_id in ARMY_IDS and x.is_ready)
        for unit in all_units:
            if unit.tag in self.all_soldiers:
                soldier = self.all_soldiers[unit.tag]
                soldier.unit = unit
                if soldier.division_name is None:
                    self.unassigned_soldiers.append(soldier)
            else:
                soldier = Soldier(unit)
                self.all_soldiers[unit.tag] = soldier
                self.unassigned_soldiers.append(soldier)
        living_units_tags = {u.tag for u in all_units}
        for unit_tag in self.all_soldiers:
            if unit_tag not in living_units_tags:
                dead_soldier = self.all_soldiers.pop(unit_tag)
                self.divisions[dead_soldier.division_name].remove_soldier(unit_tag)

    def print_divisions_info(self):
        for division_name in self.divisions:
            print(self.divisions[division_name])


class ArmyStatus:
    DEFENSE_POSITION = 'DEFENSE_POSITION'
    ENEMY_SCOUT = 'ENEMY_SCOUT'
    DEFENDING_SIEGE = 'DEFENDING_SIEGE'
    MOVING = 'MOVING'
    ATTACKING = 'ATTACKING'