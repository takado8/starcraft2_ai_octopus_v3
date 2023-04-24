from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit


class SecondWallGuardZealotMicro(MicroABS):
    def __init__(self, ai, defend_position=None):
        super().__init__('ZealotMicro', ai)
        self.defend_position = defend_position

    async def do_micro(self, division):
        zealots = division.get_units(self.ai.iteration, unit.ZEALOT)
        # if self.ai.time < 480:
        cannons = self.ai.structures(unit.PHOTONCANNON)
        if self.defend_position:
            location = self.defend_position
        else:
            if cannons.amount > 1:
                cannons = cannons.closest_n_units(self.ai.main_base_ramp.bottom_center, 2)
                location = cannons.center
            else:
                location = self.ai.defend_position
        for zealot in zealots:
            try:
                self.ai.army.remove(zealot)
            except:
                pass
            near_enemy = self.ai.enemy_units().closer_than(10, location)
            if not any([zealot.distance_to(location) < (3 if not near_enemy and
                    self.ai.units.closer_than(3, location).exists else 1) for zealot in zealots]):
                zealot.move(location)
            if near_enemy and zealot.distance_to(location) < 1:
                zealot.hold_position()
            elif self.ai.units().closer_than(3, location) and zealot.is_using_ability(ability.HOLDPOSITION):
                zealot.stop()

        return zealots.amount
