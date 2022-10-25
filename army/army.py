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

    def execute_divisions_orders(self):
        for division in self.divisions:
            self.divisions[division].do_micro()

    def establish_army_status(self):
        pass

    def select_targets(self):
        pass

    def create_division(self, division_name, units_ids_list, micro):
        if division_name not in self.divisions:
            new_division = Division(division_name, units_ids_list, micro)
            self.divisions[division_name] = new_division
            return new_division
        else:
            print('Division "{}" already exists'.format(division_name))

    def train_divisions(self):
        for division in self.divisions:
            missing_units = self.divisions[division].get_list_of_missing_units()
            for unit_id in missing_units:
                present = False
                for soldier in self.unassigned_soldiers:
                    if unit_id == soldier.type_id:
                        self.divisions[division].add_soldier(soldier)
                        soldier.division_name = division
                        self.unassigned_soldiers.remove(soldier)
                        present = True
                        break
                if not present:
                    self.order_unit_training(unit_id)

    def order_unit_training(self, unit_id):
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



class ArmyStatus:
    DEFENSE_POSITION = 'DEFENSE_POSITION'
    ENEMY_SCOUT = 'ENEMY_SCOUT'
    DEFENDING_SIEGE = 'DEFENDING_SIEGE'
    MOVING = 'MOVING'
    ATTACKING = 'ATTACKING'