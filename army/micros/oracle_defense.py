from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability
# from sc2.ids.effect_id import EffectId as effect
from sc2.ids.buff_id import BuffId as buff
# from main import OctopusV3


class OracleDefenseMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('OracleDefenseMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units()
        oracles = division.get_units(self.ai.iteration, unit.ORACLE)
        revelation_range = 6
        stasis = self.ai.structures(unit.ORACLESTASISTRAP)
        for oracle in oracles:
            abilities = await self.ai.get_available_abilities(oracle)
            # print(abilities)
            threats = enemy.filter(lambda x: x.can_attack_air and x.distance_to(oracle) < x.air_range + 4)
            invisible_threats = enemy.filter(lambda x: not x.has_buff(buff.ORACLEREVELATION) and
                                                       (x.cloak == 1 or x.type_id == unit.ROACH))

            if invisible_threats:
                # print('invisible threats!')
                if ability.ORACLEREVELATION_ORACLEREVELATION in abilities:
                    # print('wtc')
                    revelation_target = None
                    max_neighbours = -1
                    for target in invisible_threats:
                        neighbours = invisible_threats.closer_than(revelation_range, target)
                        if neighbours.amount > max_neighbours:
                            max_neighbours = neighbours.amount
                            revelation_target = target
                    # print('casting on: {}'.format(revelation_target))
                    oracle(ability.ORACLEREVELATION_ORACLEREVELATION, revelation_target.position)

            elif threats:
                if sum([threat.air_dps for threat in threats]) > 20 or oracle.shield_percentage < 0.4:
                    queue_command = False
                    if ability.BEHAVIOR_PULSARBEAMOFF in abilities:
                        oracle(ability.BEHAVIOR_PULSARBEAMOFF)
                        queue_command = True
                    oracle.move(oracle.position.towards(threats.closest_to(oracle), -6), queue=queue_command)
                elif ability.BEHAVIOR_PULSARBEAMON in abilities:
                    oracle(ability.BEHAVIOR_PULSARBEAMON)
                    oracle.attack(threats.closest_to(oracle), queue=True)
            elif not self.ai.attack and oracle.energy > 100 and ability.BUILD_STASISTRAP in abilities:
                if self.ai.townhalls.ready.amount < 3:
                    place = self.ai.main_base_ramp.bottom_center.towards(self.ai.main_base_ramp.top_center, -2)
                else:
                    place = self.ai.defend_position.towards(self.ai.townhalls.ready.closest_to(self.ai.defend_position), -5)

                if not stasis.exists or not stasis.closer_than(6, place).exists:
                    j=1
                    while not self.in_grid(place) and j < 5:
                        k = 0
                        while not self.in_grid(place) and k < 7:
                            k += 1
                            place = place.random_on_distance(j)
                        j += 1
                    oracle(ability.BUILD_STASISTRAP, place)
        return oracles.amount