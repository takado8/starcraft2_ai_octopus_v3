from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.buff_id import BuffId as buff
from sc2 import Race


class ImmortalMicro(MicroABS):
    def __init__(self, ai, use_division_backout_position=None):
        super().__init__('ImmortalMicro', ai, use_division_backout_position)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        immortals = division.get_units(self.ai.iteration, unit.IMMORTAL)
        dist = 10
        units_in_position = 0
        attacking_friends = None
        division_position = None
        for immortal in immortals:

            if enemy.exists:
                threats = enemy.filter(
                    lambda unit_: unit_.can_attack_ground and unit_.distance_to(immortal.position) <= dist and
                                  unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination)
                if self.ai.attack:
                    threats.extend(
                        self.ai.enemy_structures().filter(lambda _x: (_x.can_attack_ground or _x.type_id == unit.BUNKER) and
                                                          _x.distance_to(immortal) <= dist))
                    enemy_main_ramp = self.ai.enemy_main_base_ramp.top_center
                    wall_buildings = self.ai.enemy_structures().filter(lambda x: x.type_id in {unit.SUPPLYDEPOT,
                            unit.BARRACKS, unit.BARRACKSREACTOR} and x.distance_to(enemy_main_ramp) < 5 and
                                                                                 x.distance_to(immortal) < dist)
                    workers = enemy.filter(lambda x: x.type_id == unit.SCV)

                    if wall_buildings:
                        workers_near_wall = workers.filter(lambda x:
                                                     any([x.distance_to(building) < 3 for building in wall_buildings]))
                        threats.extend(workers_near_wall)
                        threats.extend(wall_buildings)

                    bunkers = enemy().filter(lambda x: x.type_id == unit.BUNKER and x.distance_to(immortal) < dist)
                    if bunkers:
                        workers_near_bunkers = workers.filter(lambda x:
                                                     any([x.distance_to(building) < 3 for building in bunkers]))
                        threats.extend(workers_near_bunkers)
            else:
                threats = None
            if immortal.shield_percentage < 0.5:
                batteries = self.ai.structures().filter(lambda x: x.type_id == unit.SHIELDBATTERY and
                                                                  x.energy_percentage >= 0.2 and x.is_ready)
                if threats:
                    immortal.move(self.find_back_out_position(immortal,
                                                              threats.closest_to(immortal).position, division))
                elif batteries:
                    immortal.move(batteries.closest_to(immortal))

                continue
            if threats:
                close_threats = threats.closer_than(4, immortal)
                if close_threats.amount > 0:
                    threats = close_threats
                closest_enemy = threats.closest_to(immortal)
                priority = threats.filter(
                    lambda x1: x1.type_id in [unit.COLOSSUS, unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                                              unit.MEDIVAC, unit.SIEGETANKSIEGED, unit.SIEGETANK, unit.LIBERATOR,
                                              unit.THOR, unit.BUNKER, unit.QUEEN])
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, immortal)
                else:
                    targets = threats.filter(lambda x: x.is_armored)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, immortal)

                if immortal.shield_percentage < 0.4:
                    if immortal.health_percentage < 0.35:
                        immortal.move(self.find_back_out_position(immortal, closest_enemy.position, division))
                        continue
                    d = 4
                else:
                    d = 2

                back_out_position = self.find_back_out_position(immortal, closest_enemy.position, division)
                has_buff = immortal.has_buff(buff.IMMORTALOVERLOAD)
                if back_out_position is not None and immortal.weapon_cooldown > 0 and immortal.shield_percentage < 1 \
                        and not has_buff:
                    immortal.move(immortal.position.towards(back_out_position, d))
                else:
                    immortal.attack(target)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(iteration=self.ai.iteration)
                    division_position = division.get_position(iteration=self.ai.iteration)
                if division_position and immortal.distance_to(division_position) > division.max_units_distance:
                    immortal.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    immortal.attack(enemy.closest_to(attacking_friends.closest_to(immortal)))
                else:
                    units_in_position += 1
        return units_in_position

    def find_back_out_position(self, immortal, closest_enemy_position, division):
        if self.use_division_backout_position:
            backout_position = division.get_safety_backout_position(self.ai.iteration)
            if backout_position is not None:
                return backout_position
        i = 6
        position = immortal.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = immortal.position.towards(closest_enemy_position, -i)
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

    def select_target(self, targets, immortal):
        if self.ai.enemy_race == Race.Protoss:
            a = targets[0].shield_percentage
        else:
            a = 1
        if targets[0].health_percentage * a == 1:
            target = targets.closest_to(immortal)
        else:
            target = targets[0]
        return target