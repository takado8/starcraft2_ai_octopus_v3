from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit


class SecondWallGuardZealotMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('ZealotMicro', ai)

    async def do_micro(self, division):
        zealots = division.get_units(self.ai.iteration, unit.ZEALOT)
        # if self.ai.time < 480:
        cannons = self.ai.structures(unit.PHOTONCANNON)
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
            if not any([zealot.distance_to(location) < 1 for zealot in zealots]):
                zealot.move(location)
            if self.ai.enemy_units().closer_than(10, location) and zealot.distance_to(location) < 1:
                zealot.hold_position(queue=False)
            elif self.ai.units().closer_than(3, location) and zealot.is_using_ability(ability.HOLDPOSITION):
                zealot.stop()

        return zealots.amount
