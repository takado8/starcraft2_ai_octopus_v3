from sc2.position import Point2
from sc2.unit import UnitTypeId as unit
from bot.constants import GROUND_AOE_IDS, AIR_AOE_IDS
import random


class Defense:
    def __init__(self, ai):
        self.ai = ai

    def defend(self, army_status):
        if army_status.status == army_status.DEFENDING_SIEGE:
            self.defend_siege()
        elif army_status.status == army_status.ENEMY_SCOUT:
            self.defend_scout()
        elif army_status.status == army_status.DEFENSE_POSITION:
            self.take_defense_position()

    def assign_defend_position(self):
        nexuses = self.ai.structures(unit.NEXUS).ready
        enemy = self.ai.enemy_units()
        walloff_on_second = self.ai.structures({unit.PYLON, unit.PHOTONCANNON, unit.GATEWAY, unit.FORGE})
        if walloff_on_second.exists:
            walloff_on_second = walloff_on_second.closer_than(8, self.ai.main_base_ramp.bottom_center.towards(
                    self.ai.main_base_ramp.top_center, -8).towards(self.ai.game_info.map_center, 8))
        if nexuses.amount < 2:
            if walloff_on_second.exists:
                self.ai.defend_position = self.ai.main_base_ramp.bottom_center.towards(
                    self.ai.main_base_ramp.top_center, -8).towards(self.ai.game_info.map_center, 3)
            else:
                self.ai.defend_position = self.ai.main_base_ramp.top_center.towards(self.ai.main_base_ramp.bottom_center,
                                                                                -5)
        elif enemy.exists:
            for nexus in nexuses:
                if enemy.closer_than(35, nexus).amount > 1:
                    self.ai.defend_position = nexus.position.towards(self.ai.game_info.map_center, 5)
        elif 4 > nexuses.amount > 1:
            if self.ai.structures(unit.TEMPLARARCHIVE).ready.exists and walloff_on_second:
                second_nexus = nexuses.closest_to(self.ai.game_info.map_center)
            else:
                second_nexus = nexuses.closest_to(self.ai.main_base_ramp.bottom_center.towards(
                    self.ai.main_base_ramp.top_center, -8))
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
        enemy_structures = self.ai.enemy_structures().closer_than(20, self.ai.defend_position)
        if enemy_structures:
            target = None
            pylons = enemy_structures(unit.PYLON)
            cannons = enemy_structures(unit.PHOTONCANNON)
            if pylons:
                if cannons:
                    if self.ai.army.amount >= cannons.amount * 2:
                        target = pylons.closest_to(self.ai.main_base_ramp.bottom_center)
                else:
                    target = pylons.closest_to(self.ai.main_base_ramp.bottom_center)
            elif cannons:
                target = cannons.closest_to(self.ai.main_base_ramp.bottom_center)
            else:
                target = enemy_structures.closest_to(self.ai.main_base_ramp.bottom_center)
            if target:
                for man in self.ai.army:
                    man.attack(target)
        else:
            dist = 7
            for man in self.ai.army:
                if man.type_id == unit.PHOENIX and man.is_hallucination or\
                        man.type_id == unit.OBSERVER:
                    continue
                position = Point2(self.ai.defend_position).towards(self.ai.game_info.map_center, 5) if \
                    man.type_id == unit.ZEALOT else Point2(self.ai.defend_position)
                if man.distance_to(self.ai.defend_position) > dist and man.type_id != unit.DARKTEMPLAR:
                    man.move(position.random_on_distance(random.randint(1, 2)))

    def avoid_aoe(self):
        purification_novas = self.ai.enemy_units(unit.DISRUPTORPHASED)
        purification_novas.extend(self.ai.units(unit.DISRUPTORPHASED))
        for man in self.ai.army:
            if man.is_flying:
                aoe_ids = AIR_AOE_IDS
            else:
                if purification_novas.exists and purification_novas.closer_than(3, man).exists:
                    man.move(man.position.towards(purification_novas.closest_to(man), -4))
                    continue
                aoe_ids = GROUND_AOE_IDS
            for eff in self.ai.state.effects:
                if eff.id in aoe_ids:
                    positions = eff.positions
                    for position in positions:
                        if man.distance_to(position) < eff.radius + 2:
                            man.move(man.position.towards(position, -3))
