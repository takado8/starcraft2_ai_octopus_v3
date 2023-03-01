from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit


class DisruptorMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('DisruptorMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        disruptors = division.get_units(self.ai.iteration, unit.DISRUPTOR)
        units_in_position = 0
        novas_casted = self.ai.units(unit.DISRUPTORPHASED).amount
        for disruptor in disruptors:
            abilities = await self.ai.get_available_abilities(disruptor)
            close_enemy = enemy.closer_than(20, disruptor)
            if novas_casted < 2 and ability.EFFECT_PURIFICATIONNOVA in abilities\
                    and enemy and close_enemy.exists:
                spell_target = enemy.filter(
                    lambda unit_: unit_.distance_to(disruptor) < 15 and unit_.type_id not in self.ai.units_to_ignore
                                  and not unit_.is_flying)
                target = None
                if spell_target.amount > 2:
                    tanks = spell_target.filter(lambda x: x.type_id in {unit.SIEGETANKSIEGED, unit.SIEGETANK,
                                                                        unit.DISRUPTOR})
                    if tanks.amount > 1:
                        spell_target = tanks

                    maxNeighbours = 0
                    for en in spell_target:
                        neighbours = enemy.filter(lambda unit_: not unit_.is_flying and unit_.distance_to(en) <= 1.5
                                                  and unit_.type_id not in self.ai.units_to_ignore)
                        if neighbours.amount > maxNeighbours:
                            maxNeighbours = neighbours.amount
                            target = en
                    if target is not None and self.ai.army.closer_than(2, target).amount < 1:
                        dist = await self.ai._client.query_pathing(disruptor.position, target.position)
                        if dist is not None and dist <= 13:
                            # print("Casting Purification nova on " + str(maxNeighbours + 1) + " units.")
                            # self.ai.nova_wait = self.ai.time
                            disruptor(ability.EFFECT_PURIFICATIONNOVA, target.position)
                            novas_casted += 1
                elif close_enemy.amount > 3:
                    disruptor.move(disruptor.position.towards(close_enemy.closest_to(disruptor), 2))
            else:
                threat = enemy.filter(lambda x: x.distance_to(disruptor) < 10 and x.can_attack_ground)
                division_position = division.get_position(self.ai.iteration)
                if division_position and disruptor.distance_to(division_position) > division.max_units_distance:
                    disruptor.move(division_position)
                else:
                    units_in_position += 1
                    if threat.exists:
                        retreat_position = self.find_back_out_position(disruptor, threat.closest_to(disruptor))
                        disruptor.move(disruptor.position.towards(retreat_position, 2))
                # else:


        # Disruptor purification nova
        # if self.ai.time - self.ai.nova_wait > 0.4:
        for nova in self.ai.units(unit.DISRUPTORPHASED):
            spell_target = enemy.filter(lambda unit_: unit_.distance_to(nova) < 10
                                 and unit_.type_id not in self.ai.units_to_ignore and not unit_.is_flying)
            target = None
            if spell_target.amount > 0:
                tanks = spell_target.filter(lambda x: x.type_id in {unit.SIEGETANKSIEGED, unit.SIEGETANK})
                if tanks.amount > 0:
                    spell_target = tanks
                maxNeighbours = 0
                for en in spell_target:
                    neighbours = enemy.filter(
                        lambda unit_: unit_.distance_to(nova) <= 1.5
                                      and unit_.type_id not in self.ai.units_to_ignore and not unit_.is_flying)
                    if neighbours.amount > maxNeighbours:
                        maxNeighbours = neighbours.amount
                        target = en

                # ability.PURIFICATIONNOVAMORPHBACK_PURIFICATIONNOVA
                if target is not None and self.ai.army.closer_than(2, target).amount < 1:
                    # if self.ai.army.closer_than(3,target).amount < 2:
                    # print("Steering Purification nova to " + str(maxNeighbours + 1) + " units.")
                    nova.move(target.position.towards(nova, -1))

        return units_in_position

    def find_back_out_position(self, disruptor, closest_enemy_position):
        i = 6
        position = disruptor.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = disruptor.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not self.in_grid(position) and j < 5:
                k = 0
                distance = j * 2
                while not self.in_grid(position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position