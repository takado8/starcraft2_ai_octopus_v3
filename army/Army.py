from .soldier import Soldier


class Army:
    def __init__(self, ai_object):
        self.ai = ai_object
        self.status: ArmyStatus = ArmyStatus.PEACE
        self.divisions = {}

    def add_soldier_to_division(self, division, soldier: Soldier):
        if division in self.divisions:
            self.divisions[division].add(soldier)
        else:
            self.divisions[division] = {soldier}

    def remove_soldier_form_division(self, soldier):
        for division in self.divisions:
            if soldier in self.divisions[division]:
                self.divisions[division].pop(soldier)


class Division:
    MAIN_ARMY = 'main'
    RAPID_RESPONSE = 'rapid'


class ArmyStatus:
    PEACE = 'peace'
    ENEMY_SCOUT = 'enemy_scout'
    DEFENSE = 'defense'
    MOVING = 'moving'
    ATTACKING = 'attacking'