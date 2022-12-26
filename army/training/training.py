from typing import Dict, List
from ..soldier import Soldier
from sc2.unit import UnitTypeId as unit
from bot.constants import ARMY_IDS, SPECIAL_UNITS_IDS


class Training:
    def __init__(self, ai, trainer, divisions):
        self.ai = ai
        self.trainer = trainer
        self.divisions = divisions
        self.unassigned_soldiers: List[Soldier] = []
        self.all_soldiers: Dict[str, Soldier] = {}

    def create_training_order(self):
        all_missing_units = {}
        divisions_to_delete = []
        for division_name in self.divisions:
            division = self.divisions[division_name]
            if division.lifetime:
                if 0 < division.lifetime < self.ai.time:
                    divisions_to_delete.append(division_name)
                    continue
                elif -division.lifetime > self.ai.time:
                    continue
            missing_units = division.get_dict_of_missing_units()
            for unit_id in missing_units:
                unit_amount = 0
                assigned_soldiers = []
                for soldier in self.unassigned_soldiers:
                    if unit_amount < missing_units[unit_id]:
                        if unit_id == soldier.type_id:
                            unit_amount += 1
                            division.add_soldier(soldier)
                            soldier.division_name = division_name
                            assigned_soldiers.append(soldier)
                            missing_units[unit_id] -= 1
                    else:
                        break
                for soldier in assigned_soldiers:
                    self.unassigned_soldiers.remove(soldier)
            for unit_id in missing_units:
                if unit_id in all_missing_units:
                    all_missing_units[unit_id] += missing_units[unit_id]
                else:
                    all_missing_units[unit_id] = missing_units[unit_id]

        units_id_to_remove = []
        for unit_id in all_missing_units:
            all_missing_units[unit_id] -= self.ai.already_pending(unit_id)
            if all_missing_units[unit_id] < 1:
                units_id_to_remove.append(unit_id)

        for unit_id in units_id_to_remove:
            all_missing_units.pop(unit_id)
        # exceptions for warpprism
        if unit.WARPPRISM in all_missing_units:
            all_missing_units[unit.WARPPRISM] -= self.ai.units(unit.WARPPRISMPHASING).amount
            if all_missing_units[unit.WARPPRISM] < 1:
                all_missing_units.pop(unit.WARPPRISM)
        for division_name in divisions_to_delete:
            if not self.divisions[division_name].soldiers:
                self.divisions.pop(division_name)
        self.unassigned_soldiers.clear()
        # print('all missing units: ')
        # print(all_missing_units)
        return all_missing_units

    def order_units_training(self, units_ids_dict):
        list_of_units = []
        for unit_id in units_ids_dict:
            # for _ in range(units_ids_dict[unit_id]):
            if unit_id == unit.ARCHON:
                list_of_units.append(unit.HIGHTEMPLAR)
            else:
                list_of_units.append(unit_id)
        self.trainer.add_units_to_training_queue(list_of_units)

    def refresh_all_soldiers(self):
        all_units = self.ai.units().filter(lambda x: (x.type_id in ARMY_IDS or x.type_id in SPECIAL_UNITS_IDS)
                                                      and x.is_ready)
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
        dead_units_tags = set()
        for unit_tag in self.all_soldiers:
            if unit_tag not in living_units_tags:
                dead_units_tags.add(unit_tag)
        for dead_unit_tag in dead_units_tags:
            dead_soldier = self.all_soldiers.pop(dead_unit_tag)
            if dead_soldier.division_name and dead_soldier.division_name in self.divisions:
                self.divisions[dead_soldier.division_name].remove_soldier(dead_unit_tag)
            else:
                print('soldier: {} not in division.'.format(str(dead_soldier)))

    async def train(self):
        await self.trainer.train()

    def debug(self):
        print('\n----------------------------------------------------')
        print('all soldiers:')
        for soldier_tag in self.all_soldiers:
            soldier = self.all_soldiers[soldier_tag]
            print('{} {} {} {}'.format(soldier_tag,  soldier.type_id, soldier.unit.type_id, soldier.division_name))
        print('\ndivisions:')
        for division_name in self.divisions:
            print(self.divisions[division_name])