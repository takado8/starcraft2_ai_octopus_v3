from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability

from bot.constants import BURROWING_UNITS_IDS
from bot.math import points_on_circumference_sorted
from sc2.ids.buff_id import BuffId as buff


class ObserverMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('ObserverMicro', ai)

    async def do_micro(self, division):
        all_observers = self.ai.units(unit.OBSERVER)
        observers = division.get_units(self.ai.iteration, unit.OBSERVER)
        all_enemy = self.ai.enemy_units()
        for observer in observers:
            if self.ai.attack:
                detectors = self.ai.enemy_units().filter(lambda x: x.is_detector and
                                                    x.distance_to(observer.position) < x.detect_range + x.radius + 3)
                detectors.extend(self.ai.enemy_structures().filter(lambda x: x.is_detector and
                                 x.distance_to(observer.position) < x.detect_range + x.radius))

                if detectors.exists:
                    detector = detectors.closest_to(observer)
                    observer.move(observer.position.towards(detector, -7))
                    continue

            if all_enemy.exists:
                invisible_threats = all_enemy.filter(lambda x: not x.has_buff(buff.ORACLEREVELATION) and
                                        (x.cloak in {1, 2} or x.type_id in BURROWING_UNITS_IDS) and
                                                               (all_observers.closer_than(7, x).amount == 0 or
                                                                all_observers.closest_to(x).tag == observer.tag))
                if invisible_threats:
                    observer.move(invisible_threats.closest_to(observer.position))
                    continue
            division_position = division.get_position(self.ai.iteration)
            if division_position and observer.is_idle:
                observer.move(division_position)
        return observers.amount
