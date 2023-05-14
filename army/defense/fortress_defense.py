from army.defense.defense import Defense
from sc2.unit import UnitTypeId as unit


class FortressDefense(Defense):
    def __init__(self, ai):
        super().__init__(ai)

    def defend_siege(self):
        enemy = self.ai.enemy_units().closer_than(10, self.ai.defend_position)
        if enemy:
            for man in self.ai.army.idle:
                man.attack(enemy.closest_to(man))

    def assign_defend_position(self):
        nexuses = self.ai.structures(unit.NEXUS).ready
        enemy = self.ai.enemy_units()
        walloff_on_second = self.ai.structures({unit.PYLON, unit.PHOTONCANNON, unit.GATEWAY, unit.FORGE})
        if walloff_on_second.exists:
            walloff_on_second = walloff_on_second.closer_than(8, self.ai.main_base_ramp.bottom_center.towards(
                self.ai.main_base_ramp.top_center, -8).towards(self.ai.game_info.map_center, 8))
        if nexuses.amount <= 2:
            if walloff_on_second.exists:
                self.ai.defend_position = self.ai.main_base_ramp.bottom_center.towards(
                    self.ai.main_base_ramp.top_center, -8).towards(self.ai.game_info.map_center, 3)
            else:
                self.ai.defend_position = self.ai.main_base_ramp.top_center.towards(
                    self.ai.main_base_ramp.bottom_center,
                    -5)
        elif enemy.exists:
            for nexus in nexuses:
                if enemy.closer_than(35, nexus).amount > 1 and self.ai.structures(unit.SHIELDBATTERY).exists and \
                        self.ai.structures(unit.SHIELDBATTERY).closer_than(12, nexus).amount > 3:
                    self.ai.defend_position = nexus.position.towards(self.ai.game_info.map_center, 5)
        elif nexuses.amount > 2:
            nexuses_fortified = nexuses.filter(lambda nexus: self.ai.structures().filter(lambda y:
                         y.type_id == unit.SHIELDBATTERY and y.is_ready and y.distance_to(nexus) < 14).amount > 3)
            if nexuses_fortified:
                nexus = nexuses_fortified.furthest_to(self.ai.start_location)
                self.ai.defend_position = nexus.position.towards(self.ai.game_info.map_center, 5)