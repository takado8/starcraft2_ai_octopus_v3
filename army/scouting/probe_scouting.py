from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2 import AbilityId
from economy.info.enemy_economy import *
from sc2.position import Point2

from main import OctopusV3

SCOUTING_COOLDOWN = 30


class ProbeScouting:
    def __init__(self, ai_object: OctopusV3, enemy_economy):
        self.ai = ai_object
        self.enemy_economy: EnemyEconomy = enemy_economy
        self.scout_tag = None
        self.number_of_scoutings_done = 0
        self.scouting_index = -1
        self.scouting_positions = []
        self.last_scouting_time = 0

    def assign_probe(self):
        distant_mining_workers_tags = self.ai.strategy.workers_distribution.get_distant_mining_workers_tags()
        scout = None
        if distant_mining_workers_tags:
            distant_mining_workers = self.ai.units().filter(lambda x: x.tag in distant_mining_workers_tags)
            if distant_mining_workers:
                scout = distant_mining_workers.closest_to(self.ai.enemy_start_locations[0])
        if not scout:
            mineral_workers_tags = self.ai.strategy.workers_distribution.get_mineral_workers_tags()
            if mineral_workers_tags:
                mineral_workers = self.ai.units().filter(lambda x: x.tag in mineral_workers_tags)
                if mineral_workers:
                    scout = mineral_workers.closest_to(self.ai.enemy_start_locations[0])
        if scout:
            self.scout_tag = scout.tag
        return scout
