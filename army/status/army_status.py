from sc2.ids.unit_typeid import UnitTypeId as unit


class ArmyStatus:
    DEFENSE_POSITION = 'DEFENSE_POSITION'
    ENEMY_SCOUT = 'ENEMY_SCOUT'
    DEFENDING_SIEGE = 'DEFENDING_SIEGE'
    ATTACKING = 'ATTACKING'

    def __init__(self, ai):
        self.ai = ai
        self.status = ArmyStatus.DEFENSE_POSITION

    def establish_army_status(self):
        enemy = self.ai.enemy_units()
        if (not self.ai.retreat_condition()) and (
                self.ai.counter_attack_condition() or self.ai.attack_condition() or self.ai.attack):
            self.status = ArmyStatus.ATTACKING
        elif enemy.closer_than(40, self.ai.defend_position).amount > 1:
            self.status = ArmyStatus.DEFENDING_SIEGE
        elif self.status != ArmyStatus.ATTACKING and any([3 > enemy().filter(lambda x: x.type_id != unit.OVERSEER and
                                        x.distance_to(townhall) < 30).amount > 0 for townhall in
                                                        [y for y in self.ai.townhalls] + sorted(self.ai.expansion_locations_list,
            key=lambda x: x.distance_to(self.ai.start_location))[len(self.ai.townhalls):len(self.ai.townhalls) + 3]]):
            self.status = ArmyStatus.ENEMY_SCOUT
        elif self.ai.retreat_condition() or self.status in {ArmyStatus.ENEMY_SCOUT, ArmyStatus.DEFENDING_SIEGE}:
            self.status = ArmyStatus.DEFENSE_POSITION
