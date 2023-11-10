
from sc2.ids.unit_typeid import UnitTypeId as unit

from bot.constants import WORKERS_IDS
from bot.math import points_on_circumference_sorted


class ProbeScouting:
    def __init__(self, ai, start_time=20):
        self.ai = ai
        self.scout_tag = None
        self.points_to_visit = points_on_circumference_sorted(self.ai.enemy_start_locations[0],
                                                self.ai.start_location, 11, n=14)
        self.enabled = True
        self.start_time = start_time

    def scout(self):
        if self.enabled and self.ai.time > self.start_time:
            scouting_probe = self.get_scouting_probe()
            if not scouting_probe:
                scouting_probe = self.assign_scouting_probe()
                if not scouting_probe:
                    return
            if self.ai.enemy_units and self.ai.enemy_units.filter(lambda x: x.can_attack_ground and x.type_id
                                                           not in WORKERS_IDS):
                self.enabled = False
                scouting_probe.gather(self.ai.mineral_field.closest_to(self.ai.start_location))
                return

            if not scouting_probe.is_moving:
                for point in self.points_to_visit:
                    scouting_probe.move(point, queue=True)
            self.ai.workers.remove(scouting_probe)
            self.ai.units.remove(scouting_probe)

    def assign_scouting_probe(self):
        workers_tags = self.ai.strategy.workers_distribution.get_distant_mining_workers_tags()
        if not workers_tags:
            workers_tags = self.ai.strategy.workers_distribution.get_mineral_workers_tags()
        if workers_tags:
            workers = self.ai.workers.filter(lambda x: x.tag in workers_tags)
        else:
            workers = self.ai.units(unit.PROBE)
        if workers:
            scout = workers.closest_to(self.ai.start_location)
            self.scout_tag = scout.tag
            return scout

    def get_scouting_probe(self):
        if self.scout_tag:
            scouting_probe = self.ai.workers.find_by_tag(self.scout_tag)
            return scouting_probe
