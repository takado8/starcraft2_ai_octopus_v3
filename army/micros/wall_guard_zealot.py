from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit


class WallGuardZealotMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('ZealotMicro', ai)

    async def do_micro(self, division):
        zealots = division.get_units(self.ai.iteration, unit.ZEALOT)
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        units_in_position = 0
        attacking_friends = None
        division_position = None
        if self.ai.time < 480:
            location = self.ai.main_base_ramp.protoss_wall_warpin
            for zealot in zealots:
                if not any([zealot.distance_to(location) < 1 for zealot in zealots]):
                    zealot.move(location)
                if self.ai.enemy_units().closer_than(10, location) and zealot.distance_to(location) < 1:
                    zealot.hold_position(queue=False)
                elif self.ai.units().closer_than(3, location) and zealot.is_using_ability(ability.HOLDPOSITION):
                    zealot.stop()

        else:
            for zealot in zealots:
                if enemy.exists:
                    threats = self.ai.enemy_units().filter(
                        lambda x2: x2.distance_to(zealot.position) < 9 and not x2.is_flying and
                                   x2.type_id not in self.ai.units_to_ignore and not x2.is_hallucination).sorted(
                        lambda _x: _x.health + _x.shield)
                else:
                    threats = None
                if threats:
                    close_threats = threats.closer_than(4, zealot)
                    if close_threats.exists:
                        threats = close_threats
                    closest = threats.closest_to(zealot)
                    if threats[0].health_percentage * threats[0].shield_percentage == 1 or threats[0].distance_to(
                            zealot.position) > \
                            closest.distance_to(zealot.position) + 1 or not self.ai.in_pathing_grid(threats[0]):
                        target = closest
                    else:
                        target = threats[0]
                    if ability.EFFECT_CHARGE in await self.ai.get_available_abilities(zealot):
                        zealot(ability.EFFECT_CHARGE, target)
                        zealot.attack(target, queue=True)
                    else:
                        zealot.attack(target)
                else:
                    if attacking_friends is None:
                        attacking_friends = division.get_attacking_units(self.ai.iteration)
                        division_position = division.get_position(self.ai.iteration)
                    if division_position and zealot.distance_to(division_position) > division.max_units_distance:
                        zealot.attack(division_position)
                    elif attacking_friends.exists and enemy.exists:
                        zealot.attack(enemy.closest_to(attacking_friends.closest_to(zealot)))
                    else:
                        units_in_position += 1

        return units_in_position