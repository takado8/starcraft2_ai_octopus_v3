from .soldier import Soldier
from .division import Division
from typing import Dict


class Army:
    # TODO try genetic algo to calc army composition accordingly to enemy army type
    def __init__(self, ai_object):
        self.ai = ai_object
        self.status: ArmyStatus = ArmyStatus.DEFENSE_POSITION
        self.divisions: Dict[str, Division] = {}

    def create_division(self, division_name, micro):
        if division_name not in self.divisions:
            new_division = Division(division_name, micro)
            self.divisions[division_name] = new_division

    def add_soldier_to_division(self, division_name: str, soldier: Soldier):
        if division_name in self.divisions:
            self.divisions[division_name].add_soldier(soldier)
        else:
            print('division of name \'{}\' does not exist.'.format(division_name))

    def remove_soldier_form_division(self, soldier: Soldier):
        self.divisions[soldier.division_name].remove_soldier(soldier)


class ArmyStatus:
    DEFENSE_POSITION = 'DEFENSE_POSITION'
    ENEMY_SCOUT = 'ENEMY_SCOUT'
    DEFENDING_SIEGE = 'DEFENDING_SIEGE'
    MOVING = 'MOVING'
    ATTACKING = 'ATTACKING'