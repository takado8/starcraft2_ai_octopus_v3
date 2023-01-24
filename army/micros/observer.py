from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability
from bot.math import points_on_circumference_sorted


class ObserverMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('ObserverMicro', ai)

    async def do_micro(self, division):
        observers = division.get_units(self.ai.iteration, unit.OBSERVER)
        for observer in observers:
            detectors = self.ai.enemy_units().filter(lambda x: x.is_detector and
                                                x.distance_to(observer.position) < x.detect_range + x.radius + 3)
            detectors.extend(self.ai.enemy_structures().filter(lambda x: x.is_detector and
                             x.distance_to(observer.position) < x.detect_range + x.radius))

            if detectors.exists:
                detector = detectors.closest_to(observer)
                observer.move(observer.position.towards(detector, -4))
                continue

            enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore
                                                           and x.distance_to(observer) < 10)

            if enemy.exists:
                enemy_center = enemy.center
                radius = enemy_center.distance_to(enemy.furthest_to(enemy_center)) + 3
                points = points_on_circumference_sorted(enemy_center, observer.position, radius, n=12)
                for point in points:
                    observer.move(point, queue=True)
        return observers.amount