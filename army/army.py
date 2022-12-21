import random

from sc2.position import Point2
from sc2.unit import UnitTypeId as unit

from .division import Division
from .soldier import Soldier
from typing import Dict, List
from bot.constants import ARMY_IDS, SPECIAL_UNITS_IDS, AOE_IDS



class Army:
    def __init__(self, ai_object, scouting, trainer):
        self.ai = ai_object
        self.scouting = scouting
        self.trainer = trainer
        self.status: ArmyStatus = ArmyStatus.DEFENSE_POSITION
        self.divisions: Dict[str, Division] = {}
        self.unassigned_soldiers: List[Soldier] = []
        self.all_soldiers: Dict[str, Soldier] = {}
        self.enemy_main_base_down = False
        self.assign_defend_position()

    def debug(self):
        print('\n----------------------------------------------------')
        print('all soldiers:')
        for soldier_tag in self.all_soldiers:
            soldier = self.all_soldiers[soldier_tag]
            print('{} {} {} {}'.format(soldier_tag,  soldier.type_id, soldier.unit.type_id, soldier.division_name))
        print('\ndivisions:')
        for division_name in self.divisions:
            print(self.divisions[division_name])

    async def execute(self):
        try:
            self.establish_army_status()
            self.refresh_all_soldiers()
            training_order = self.create_training_order()
            self.order_units_training(training_order)
            await self.trainer.train()

            if self.status == ArmyStatus.ATTACKING:
                await self.attack()
            else:
                self.assign_defend_position()
                self.defend()

            await self.execute_micro()
            self.avoid_aoe()
            if self.enemy_main_base_down:
                self.scouting.scan_on_end()
            # self.debug()

        except Exception as ex:
            self.debug()
            raise ex

    async def execute_micro(self):
        for division in self.divisions:
            await self.divisions[division].do_micro()

    def establish_army_status(self):
        enemy = self.ai.enemy_units()
        if (not self.ai.retreat_condition()) and (
                self.ai.counter_attack_condition() or self.ai.attack_condition() or self.ai.attack):
            self.status = ArmyStatus.ATTACKING
        elif enemy.closer_than(40, self.ai.defend_position).amount > 1:
            self.status = ArmyStatus.DEFENDING_SIEGE
        elif self.status != ArmyStatus.ATTACKING and any([3 > enemy.closer_than(30, townhall).amount > 0 for townhall in self.ai.townhalls.ready]):
            self.status = ArmyStatus.ENEMY_SCOUT
        elif self.ai.retreat_condition() or self.status in {ArmyStatus.ENEMY_SCOUT, ArmyStatus.DEFENDING_SIEGE}:
            self.status = ArmyStatus.DEFENSE_POSITION

    def defend(self):
        if self.status == ArmyStatus.DEFENDING_SIEGE:
            self.defend_siege()
        elif self.status == ArmyStatus.ENEMY_SCOUT:
            self.defend_scout()
        elif self.status == ArmyStatus.DEFENSE_POSITION:
            self.take_defense_position()

    def assign_defend_position(self):
        nexuses = self.ai.structures(unit.NEXUS).ready
        enemy = self.ai.enemy_units()
        if enemy.exists:
            for nexus in nexuses:
                if enemy.closer_than(35, nexus).amount > 1:
                    self.ai.defend_position = nexus.position.towards(self.ai.game_info.map_center, 5)
        elif nexuses.amount < 2:
            self.ai.defend_position = self.ai.main_base_ramp.top_center.towards(self.ai.main_base_ramp.bottom_center, -2)
        elif 4 > nexuses.amount > 1:
            second_nexus = nexuses.furthest_to(self.ai.start_location.position)
            self.ai.defend_position = second_nexus.position.towards(
                self.ai.game_info.map_center, 5)
        else:
            closest_nexuses = nexuses.closest_n_units(self.ai.enemy_start_locations[0].position, n=2)
            nexus_with_most_workers = max(closest_nexuses, key=lambda x: self.ai.workers.closer_than(15, x).amount)
            current_position_workers = self.ai.workers.closer_than(15, self.ai.defend_position)
            if self.ai.workers.closer_than(15, nexus_with_most_workers).amount - current_position_workers.amount > 3:
                self.ai.defend_position = nexus_with_most_workers.position.towards(
                    self.ai.game_info.map_center, 5)

    def defend_siege(self):
        enemy = self.ai.enemy_units()
        for man in self.ai.army.idle:
            man.attack(enemy.closest_to(man))

    def defend_scout(self):
        enemy = self.ai.enemy_units()
        if enemy:
            high_mobility = []
            high_mobility_ids = {unit.STALKER, unit.ADEPT, unit.ZEALOT}
            for man in self.ai.army:
                if man.is_flying or man.type_id in high_mobility_ids:
                    high_mobility.append(man)

            high_mobility = high_mobility[:5]
            observer = self.ai.units(unit.OBSERVER).ready
            if observer.exists:
                high_mobility.append(observer.random)
            for unit_ in high_mobility:
                unit_.attack(enemy.closest_to(unit_))

    def take_defense_position(self):
        dist = 7
        for man in self.ai.army:
            position = Point2(self.ai.defend_position).towards(self.ai.game_info.map_center, 5) if \
                man.type_id == unit.ZEALOT else Point2(self.ai.defend_position)
            if man.distance_to(self.ai.defend_position) > dist:
                man.move(position.random_on_distance(random.randint(1, 2)))

    async def attack(self):
        target = self.select_targets_to_attack()
        await self.move_army(target)

    def select_targets_to_attack(self):
        enemy_units = self.ai.enemy_units()
        enemy = enemy_units.filter(lambda x: x.type_id not in self.ai.units_to_ignore and not x.is_hallucination
                                             and (x.can_attack_ground or x.can_attack_air))
        enemy.extend(self.ai.enemy_structures().filter(lambda b: #b.type_id in self.ai.bases_ids or
                         b.can_attack_ground or b.can_attack_air or b.type_id == unit.BUNKER))
        if self.enemy_main_base_down or (
                self.ai.army.closer_than(15, self.ai.enemy_start_locations[0]).amount > 7 and
                (not self.ai.enemy_structures().exists or self.ai.enemy_structures().closer_than(15,
                                                                    self.ai.enemy_start_locations[0]).amount < 1)):
            if not self.enemy_main_base_down:
                # await self.ai.chat_send('enemy main base down.')
                print('enemy main base down.')
                self.enemy_main_base_down = True
            enemy.extend(self.ai.enemy_structures())

        if enemy.amount > 4 or self.enemy_main_base_down and enemy.exists:
            if enemy.closer_than(50, self.ai.start_location).amount > 3:
                destination = enemy.closest_to(self.ai.start_location).position
            else:
                destination = enemy.further_than(30, self.ai.start_location)
                if destination:
                    destination = destination.closest_to(self.ai.start_location).position
                # elif self.ai.enemy_structures().exists:
                #     enemy = self.ai.enemy_structures()
                #     destination = enemy.closest_to(self.ai.start_location).position
                else:
                    destination = self.ai.enemy_start_locations[0].position
        elif not self.enemy_main_base_down:
            destination = self.ai.enemy_start_locations[0].position
        else:
            destination = None

        return destination

    def create_division(self, division_name, units_ids_dict, micros: List, movements, lifetime=None):
        if division_name in self.divisions:
            print('Division "{}" already exists.'.format(division_name))
        else:
            new_division = Division(self.ai, division_name, units_ids_dict, micros, movements, lifetime=lifetime)
            self.divisions[division_name] = new_division
            print("division created: {}".format(new_division))
            return new_division

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
        print('all missing units: ')
        print(all_missing_units)
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

    async def move_army(self, destination):
        for division_name in self.divisions:
            await self.divisions[division_name].move_division(destination)

    def avoid_aoe(self):
        purification_novas = self.ai.enemy_units(unit.DISRUPTORPHASED)
        purification_novas.extend(self.ai.units(unit.DISRUPTORPHASED))
        for man in self.ai.army:
            if purification_novas.exists and purification_novas.closer_than(3, man).exists:
                man.move(man.position.towards(purification_novas.closest_to(man), -4))
                continue
            for eff in self.ai.state.effects:
                if eff.id in AOE_IDS:
                    positions = eff.positions
                    for position in positions:
                        if man.distance_to(position) < eff.radius + 2:
                            man.move(man.position.towards(position, -3))

    def print_divisions_info(self):
        for division_name in self.divisions:
            print(self.divisions[division_name])


class ArmyStatus:
    DEFENSE_POSITION = 'DEFENSE_POSITION'
    ENEMY_SCOUT = 'ENEMY_SCOUT'
    DEFENDING_SIEGE = 'DEFENDING_SIEGE'
    ATTACKING = 'ATTACKING'
