from sc2.unit import UnitTypeId as unit
from .division import Division
from .soldier import Soldier
from typing import Dict, List
from bot.constants import ARMY_IDS, SPECIAL_UNITS_IDS


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

    async def attack(self):
        target = self.select_targets_to_attack()
        await self.move_army(target)

    def select_targets_to_attack(self):
        enemy_units = self.ai.enemy_units()
        enemy = enemy_units.filter(lambda x: x.type_id not in self.ai.units_to_ignore
                                             and (x.can_attack_ground or x.can_attack_air))
        enemy.extend(self.ai.enemy_structures().filter(lambda b: b.type_id in self.ai.bases_ids
                        or b.can_attack_ground or b.can_attack_air or b.type_id == unit.BUNKER))
        if self.ai.enemy_main_base_down or (
                self.ai.army.closer_than(20, self.ai.enemy_start_locations[0]).amount > 17 and
                not self.ai.enemy_structures().exists):
            if not self.ai.enemy_main_base_down:
                # await self.ai.chat_send('enemy main base down.')
                print('enemy main base down.')
                self.ai.enemy_main_base_down = True
            # self.ai.scan()
            enemy_units.extend(self.ai.enemy_structures())
            if enemy_units.exists:
                for man in self.ai.army.exclude_type(unit.OBSERVER):
                    self.ai.do(man.attack(enemy_units.closest_to(man)))

        if enemy.amount > 4:
            if enemy.closer_than(35, self.ai.start_location).amount > 5:
                destination = enemy.closest_to(self.ai.start_location).position
            else:
                destination = enemy.further_than(25, self.ai.start_location)
                if destination:
                    destination = destination.closest_to(self.ai.start_location).position
                elif self.ai.enemy_structures().exists:
                    enemy = self.ai.enemy_structures()
                    destination = enemy.closest_to(self.ai.start_location).position
                else:
                    destination = self.ai.enemy_start_locations[0].position
        elif self.ai.enemy_structures().exists:
            enemy = self.ai.enemy_structures()
            destination = enemy.closest_to(self.ai.start_location).position
        else:
            if self.ai.enemy_main_base_down:
                if len(self.ai.observer_scouting_points) == 0:
                    for exp in self.ai.expansion_locations:
                        if not self.ai.structures().closer_than(7, exp).exists:
                            self.ai.observer_scouting_points.append(exp)
                    self.ai.observer_scouting_points = sorted(self.ai.observer_scouting_points,
                                                              key=lambda x: self.ai.enemy_start_locations[
                                                                  0].distance_to(x))
                if self.ai.army() and self.ai.army().closer_than(12, self.ai.observer_scouting_points[
                    self.ai.observer_scouting_index]).amount > 12 \
                        and self.ai.enemy_structures().amount < 1:
                    self.ai.observer_scouting_index += 1
                    if self.ai.observer_scouting_index == len(self.ai.observer_scouting_points):
                        self.ai.observer_scouting_index = 0
                destination = self.ai.observer_scouting_points[self.ai.observer_scouting_index]
            else:
                destination = self.ai.enemy_start_locations[0].position
        return destination

    def create_division(self, division_name, units_ids_dict, micros: List, movements):
        if division_name in self.divisions:
            print('Division "{}" already exists.'.format(division_name))
        else:
            new_division = Division(self.ai, division_name, units_ids_dict, micros, movements)
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
            if dead_soldier.division_name:
                self.divisions[dead_soldier.division_name].remove_soldier(dead_unit_tag)
            else:
                print('soldier: {} not in division.'.format(str(dead_soldier)))


    async def move_army(self, destination):
        for division_name in self.divisions:
            await self.divisions[division_name].move_division(destination)

    def print_divisions_info(self):
        for division_name in self.divisions:
            print(self.divisions[division_name])


class ArmyStatus:
    DEFENSE_POSITION = 'DEFENSE_POSITION'
    ENEMY_SCOUT = 'ENEMY_SCOUT'
    DEFENDING_SIEGE = 'DEFENDING_SIEGE'
    MOVING = 'MOVING'
    ATTACKING = 'ATTACKING'
