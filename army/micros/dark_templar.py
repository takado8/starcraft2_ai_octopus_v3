from sc2.ids.unit_typeid import UnitTypeId as unit
from .microABS import MicroABS


class DarkTemplarMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('DarkTemplarMicro', ai)
        self.enemy_base_idx = 0
        expansions = sorted(self.ai.expansion_locations,
                            key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        self.mineral_lines = [self.ai.mineral_field.closer_than(9, exp).center.towards(exp, 3)
                              for exp in expansions][:5]

    async def do_micro(self, division):
        dts = division.get_units(self.ai.iteration, unit.DARKTEMPLAR)
        for dt in dts:
            detectors = self.ai.enemy_units().filter(lambda x: x.is_detector and
                            x.distance_to(dt.position) < x.detect_range + 1)
            detectors.extend(self.ai.enemy_structures().filter(lambda x: x.is_detector and
                            x.distance_to(dt.position) < x.detect_range + 1))
            threats = self.ai.enemy_units().filter(lambda x2: x2.distance_to(dt.position) < 9 and not x2.is_flying and
                          x2.type_id not in self.ai.units_to_ignore and not x2.is_hallucination)\
                                                                            .sorted(lambda _x: _x.health + _x.shield)
            workers = self.ai.enemy_units().filter(lambda x: x.type_id in self.ai.workers_ids
                                                and x.distance_to(dt) < 14).sorted(lambda _x: _x.health + _x.shield)
            if detectors.exists:
                position = self.find_back_out_position(dt, detectors.closest_to(dt))
                if position:
                    dt.move(position)
            elif workers.exists:
                closest = workers.closest_to(dt)
                if workers[0].health_percentage * workers[0].shield_percentage == 1 or workers[0].distance_to(
                        dt.position) > \
                        closest.distance_to(dt.position) + 1 or not self.ai.in_pathing_grid(workers[0]):
                    target = closest
                else:
                    target = workers[0]
                dt.attack(target)
            elif (self.ai.attack or self.ai.enemy_units().closer_than(17, self.ai.defend_position))and threats.exists:
                closest = threats.closest_to(dt)
                if threats[0].health_percentage * threats[0].shield_percentage == 1 or threats[0].distance_to(dt.position) > \
                    closest.distance_to(dt.position) + 1 or not self.ai.in_pathing_grid(threats[0]):
                    target = closest
                else:
                    target = threats[0]
                dt.attack(target)
            else:
                dt.move(self.mineral_lines[self.enemy_base_idx])
                if dt.distance_to(self.mineral_lines[self.enemy_base_idx]) < 3:
                    self.enemy_base_idx += 1
                    if self.enemy_base_idx > 2:
                        self.enemy_base_idx = 0
        return dts.amount

    def find_back_out_position(self, dt, closest_enemy_position):
        i = 6
        position = dt.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = dt.position.towards(closest_enemy_position, -i)
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
