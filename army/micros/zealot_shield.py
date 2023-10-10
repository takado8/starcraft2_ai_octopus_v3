from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit


class ZealotShieldMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('ZealotShieldMicro', ai)

    async def do_micro(self, division):
        zealots = division.get_units(self.ai.iteration, unit.ZEALOT)
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        units_in_position = 0
        dist = 9
        attacking_friends = None
        division_position = None
        division_units = division.get_units(self.ai.iteration)
        division_low_shield = division_units.filter(lambda x: x.shield_percentage < 0.5)
        zealots_low_shield = zealots.filter(lambda x: x.shield_percentage < 0.5)
        if zealots_low_shield.amount > zealots.amount * 0.65 or division_low_shield.amount > division_units.amount * 0.65:
            shield_regen_pause = True
        else:
            shield_regen_pause = False
        for zealot in zealots:
            if zealot.shield_percentage < 0.5 or shield_regen_pause:
                batteries = self.ai.structures.filter(lambda x: x.type_id == unit.SHIELDBATTERY and
                                                      x.is_ready and x.energy_percentage >= 0.1)
                if batteries.exists:
                    zealot.move(batteries.closest_to(zealot))
                    continue
                elif zealot.distance_to(self.ai.defend_position) > 20:
                    zealot.move(self.ai.defend_position)
                    continue

            if enemy.exists:
                threats = self.ai.enemy_units().filter(lambda x2: x2.distance_to(zealot.position) < dist and not x2.is_flying and
                              x2.type_id not in self.ai.units_to_ignore and not x2.is_hallucination).sorted(lambda _x: _x.health + _x.shield)
                if self.ai.attack:
                    threats.extend(
                        self.ai.enemy_structures().filter(lambda _x: (_x.can_attack_ground or _x.type_id == unit.BUNKER) and
                                                          _x.distance_to(zealot.position) <= dist))
            else:
                threats = None
            if threats:
                close_threats = threats.closer_than(4, zealot)
                if close_threats.exists:
                    threats = close_threats
                closest = threats.closest_to(zealot)
                if threats[0].health_percentage * threats[0].shield_percentage == 1 or threats[0].distance_to(zealot.position) > \
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
                    attacking_friends = division.get_attacking_units(iteration=self.ai.iteration)
                    division_position = division.get_position(iteration=self.ai.iteration)
                if division_position and zealot.distance_to(division_position) > division.max_units_distance:
                    zealot.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    zealot.attack(enemy.closest_to(attacking_friends.closest_to(zealot)))
                else:
                    units_in_position += 1

        return units_in_position