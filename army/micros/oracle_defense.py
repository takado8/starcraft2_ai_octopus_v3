from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability
# from sc2.ids.effect_id import EffectId as effect
from sc2.ids.buff_id import BuffId as buff
# from main import OctopusV3
from bot.constants import ANTI_AIR_IDS, BURROWING_UNITS_IDS


class OracleDefenseMicro(MicroABS):
    REVELATION_DIAMETER = 6

    def __init__(self, ai):
        # self.ai: OctopusV3 = ai
        super().__init__('OracleDefenseMicro', ai)
        self.invisible_units_detected = False

    async def do_micro(self, division):
        enemy = self.ai.enemy_units()
        oracles = division.get_units(self.ai.iteration, unit.ORACLE)

        stasis = self.ai.structures(unit.ORACLESTASISTRAP)
        for oracle in oracles:
            abilities = await self.ai.get_available_abilities(oracle)
            # print(abilities)
            threats = enemy.filter(lambda x: x.can_attack_air and x.distance_to(oracle) < x.air_range + 4)
            invisible_threats = enemy.filter(lambda x: not x.has_buff(buff.ORACLEREVELATION) and
                          not x.has_buff(buff.STASIS) and
                (any(x.distance_to(townhall) < 25 for townhall in self.ai.townhalls)) if not self.ai.attack else True and
                                                       (x.cloak == 1 or x.type_id in BURROWING_UNITS_IDS))
            anti_air = self.ai.enemy_structures().filter(lambda x: x.type_id in ANTI_AIR_IDS and
                                            x.distance_to(oracle) < x.air_range + x.radius + 4)
            neural_parasites = self.ai.enemy_units().filter(lambda x: x.has_buff(buff.NEURALPARASITE))
            if neural_parasites.exists:
                affected_unit = neural_parasites.closest_to(oracle)
                infestors = enemy.filter(lambda x: x.type_id == unit.INFESTORBURROWED and
                                x.distance_to(affected_unit) <= 9 and not x.has_buff(buff.ORACLEREVELATION))
                if infestors.exists:
                    self.cast_revelation(oracle, infestors, abilities)
            elif anti_air:# or (oracle.health_percentage < 0.5 and oracle.shield_percentage < 0.35):
                oracle.move(oracle.position.towards(anti_air.closest_to(oracle), -12))
            elif invisible_threats:
                if not self.invisible_units_detected:
                    self.invisible_units_detected = True
                self.cast_revelation(oracle, invisible_threats, abilities)
            elif threats:
                if threats.amount > 5 and sum([threat.air_dps for threat in threats]) > 15 or\
                        oracle.shield_percentage < 0.75:
                    queue_command = False
                    if ability.BEHAVIOR_PULSARBEAMOFF in abilities:
                        oracle(ability.BEHAVIOR_PULSARBEAMOFF)
                        queue_command = True
                    if (not self.invisible_units_detected or oracle.energy >= 75) and self.cast_revelation(oracle, threats, abilities, queue_command):
                        queue_command = True
                    oracle.move(oracle.position.towards(threats.closest_to(oracle), -6), queue=queue_command)
                elif oracle.energy > 45 and ability.BEHAVIOR_PULSARBEAMON in abilities:
                    oracle(ability.BEHAVIOR_PULSARBEAMON)
                    oracle.attack(threats.closest_to(oracle), queue=True)

            elif not self.ai.attack and not self.invisible_units_detected and oracle.energy >= 75 and ability.BUILD_STASISTRAP in abilities:
                ramps = sorted(self.ai.game_info.map_ramps, key=lambda x: x.top_center.distance_to(self.ai.defend_position))
                for ramp in ramps:
                    if self.ai.townhalls.amount > 1 and (ramp.top_center == self.ai.main_base_ramp.top_center or
                                ramp.top_center.distance_to(self.ai.start_location.position) < 30 and
                                ramp.top_center.distance_to(self.ai.game_info.map_center) >
                                self.ai.main_base_ramp.top_center.distance_to(self.ai.game_info.map_center)):
                        continue
                    middle = self.ai.defend_position.towards(self.ai.townhalls.ready.closest_to(self.ai.defend_position),-5)
                    if not stasis.exists or not stasis.closer_than(6, middle).exists:
                        place = middle
                    else:
                        place = ramp.bottom_center.position.towards(ramp.top_center.position, -2)
                    if not stasis.exists or not stasis.closer_than(4, place).exists:
                        j=1
                        while not self.in_grid(place) and j < 5:
                            k = 0
                            while not self.in_grid(place) and k < 7:
                                k += 1
                                place = place.random_on_distance(j)
                            j += 1
                        oracle(ability.BUILD_STASISTRAP, place)
                        break
            elif self.ai.attack:
                targets = enemy.filter(lambda x: x.can_attack_air and not x.has_buff(buff.ORACLEREVELATION))
                if targets.amount > 3:
                    self.cast_revelation(oracle, targets, abilities, min_units=3)
        return 0


    def cast_revelation(self, oracle, targets, abilities, queue=False, min_units=None):
        if ability.ORACLEREVELATION_ORACLEREVELATION in abilities:
            revelation_target = None
            max_neighbours = -1
            for target in targets:
                neighbours = targets.closer_than(self.REVELATION_DIAMETER, target)
                if neighbours.amount > max_neighbours:
                    max_neighbours = neighbours.amount
                    revelation_target = target
            if min_units and max_neighbours < min_units:
                return False
            oracle(ability.ORACLEREVELATION_ORACLEREVELATION, revelation_target.position, queue=queue)
            return True