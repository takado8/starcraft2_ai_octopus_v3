from sc2.position import Point2
from sc2.unit import UnitTypeId as unit
from bot.constants import GROUND_AOE_IDS, AIR_AOE_IDS, BURROWING_UNITS_IDS
import random


class Defense:
    def __init__(self, ai):
        self.ai = ai
        self.units_tags_to_defend_scout = set()
        self.scout_defense_units_amount = 7

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
        walloff_on_second = self.ai.structures({unit.PHOTONCANNON, unit.GATEWAY, unit.WARPGATE,
                                                unit.FORGE, unit.CYBERNETICSCORE})
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
            if self.units_tags_to_defend_scout:
                scout_defense_units = self.ai.army.filter(lambda x: x.tag in self.units_tags_to_defend_scout)
                if len(scout_defense_units) < len(self.units_tags_to_defend_scout) or\
                        len(scout_defense_units) < self.scout_defense_units_amount:
                    self.units_tags_to_defend_scout = {unit_.tag for unit_ in scout_defense_units}
                    scout_defense_units = self.assign_units_to_defend_scout()
            else:
                scout_defense_units = self.assign_units_to_defend_scout()

            ground_units = enemy.filter(lambda x: not x.is_flying)
            flying_units = enemy.filter(lambda x: x.is_flying)
            cloacked_or_burrowing_units = enemy.filter(lambda x: x.cloak in {1,2} or x.type_id in BURROWING_UNITS_IDS
                                                       or x.is_burrowed)
            for unit_ in scout_defense_units:
                if flying_units and unit_.can_attack_air:
                    unit_.attack(flying_units.closest_to(unit_))
                elif ground_units and unit_.can_attack_ground:
                    unit_.attack(ground_units.closest_to(unit_))
                elif unit_.type_id == unit.OBSERVER and cloacked_or_burrowing_units:
                    unit_.move(cloacked_or_burrowing_units.closest_to(unit_))

        elif self.ai.iteration % 50 == 0:
            self.units_tags_to_defend_scout = set()

    def take_defense_position(self):
        dist = 7
        for man in self.ai.army:
            if man.type_id == unit.PHOENIX and man.is_hallucination or\
                    man.type_id in {unit.OBSERVER}:
                continue
            position = Point2(self.ai.defend_position).towards(self.ai.game_info.map_center, 5) if \
                man.type_id == unit.ZEALOT else Point2(self.ai.defend_position)
            if man.distance_to(self.ai.defend_position) > dist and man.type_id != unit.DARKTEMPLAR:
                man.move(position.random_on_distance(random.randint(1, 2)))

    def avoid_aoe(self):
        purification_novas = self.ai.enemy_units(unit.DISRUPTORPHASED)
        purification_novas.extend(self.ai.units(unit.DISRUPTORPHASED))
        autoturrets = self.ai.enemy_units(unit.AUTOTURRET)
        autoturrets.extend(self.ai.enemy_structures(unit.AUTOTURRET))
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
            for turret in autoturrets:
                if man.distance_to(turret) <= 8:
                    man.move(man.position.towards(turret, -3))

    def assign_units_to_defend_scout(self):
        selected_units = self.ai.army.filter(lambda x: x.is_flying and x.can_attack_ground
                                                       and x.tag not in self.units_tags_to_defend_scout)
        deficit = self.scout_defense_units_amount - len(self.units_tags_to_defend_scout)
        if selected_units.amount < deficit:
            stalkers = self.ai.army.filter(lambda x: x.type_id == unit.STALKER
                                                     and x.tag not in self.units_tags_to_defend_scout)
            if stalkers.amount + selected_units.amount < deficit:
                anybody = self.ai.army.filter(lambda x: x.type_id in {unit.ADEPT, unit.ZEALOT}
                                                        and x.tag not in self.units_tags_to_defend_scout)
                if not anybody:
                    anybody = self.ai.army.filter(lambda x: x.can_attack_ground
                                                            and x.tag not in self.units_tags_to_defend_scout)
                if stalkers.amount + selected_units.amount + anybody.amount > deficit:
                    selected_units.extend(stalkers)
                    selected_units.extend(anybody[:deficit-selected_units.amount])
                else:
                    selected_units.extend(stalkers)
                    selected_units.extend(anybody)
            else:
                selected_units.extend(stalkers[:deficit-selected_units.amount])
        else:
            selected_units = selected_units[:deficit]

        observer = self.ai.units(unit.OBSERVER).ready
        if observer.exists:
            selected_units.append(observer.random)

        self.units_tags_to_defend_scout = {unit_.tag for unit_ in selected_units}
        return selected_units