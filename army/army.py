from .soldier import Soldier
from .division import Division
from typing import Dict


class Army:
    # TODO try genetic algo to calc army composition accordingly to enemy army type
    def __init__(self, ai_object):
        self.ai = ai_object
        self.status: ArmyStatus = ArmyStatus.DEFENSE_POSITION
        self.divisions: Dict[str, Division] = {}

    def add_soldier_to_division(self, division_name: str, soldier: Soldier):
        if division_name in self.divisions:
            self.divisions[division_name].add_soldier(soldier)
        else:
            new_division = Division(division_name)
            new_division.add_soldier(soldier)
            self.divisions[division_name] = new_division

    def remove_soldier_form_division(self, soldier):
        for division in self.divisions:
            self.divisions[division].remove_soldier(soldier)


class ArmyStatus:
    DEFENSE_POSITION = 'DEFENSE_POSITION'
    ENEMY_SCOUT = 'ENEMY_SCOUT'
    DEFENDING_SIEGE = 'DEFENDING_SIEGE'
    MOVING = 'MOVING'
    ATTACKING = 'ATTACKING'