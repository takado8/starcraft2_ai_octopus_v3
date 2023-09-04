from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability
from strategy.one_base_blink import OneBaseBlink


class DetectBunkerContain(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai
        self.last_scout_time = -30
        self.scout_every_n_seconds = 60

    async def execute(self):
        if self.ai.time < 360:
            if self.ai.time < 240 and self.ai.time - self.last_scout_time > self.scout_every_n_seconds:
                workers_tags = self.ai.strategy.workers_distribution.get_distant_mining_workers_tags()
                if not workers_tags:
                    workers_tags = self.ai.strategy.workers_distribution.get_mineral_workers_tags()
                if workers_tags:
                    workers = self.ai.workers.filter(lambda x: x.tag in workers_tags)
                    scout = workers.closer_than(50, self.ai.start_location).furthest_to(self.ai.start_location)
                    nearby_expansions = sorted(self.ai.expansion_locations_list,
                                               key=lambda x: self.ai.start_location.distance_to(x))[1:5]
                    scout.stop()
                    for exp in nearby_expansions:
                        scout.move(exp, queue=True)
                    self.last_scout_time = self.ai.time

            enemy_proxy = self.ai.enemy_structures({unit.BUNKER, unit.BARRACKS})
            if enemy_proxy.exists and enemy_proxy.closer_than(30, self.ai.main_base_ramp.bottom_center).exists:
                barracs = enemy_proxy(unit.BARRACKS)
                bunkers = enemy_proxy(unit.BUNKER)
                if barracs and bunkers:
                    proxy_type = 'barracks and bunker'
                elif barracs:
                    proxy_type = 'barracks'
                else:
                    proxy_type = 'bunker'
                await self.ai.chat_send(f'Tag:Proxy {proxy_type} detected.')
                self.ai.strategy = OneBaseBlink(self.ai)
                for build in self.ai.structures().filter(lambda x: not x.is_ready and x.type_id == unit.NEXUS):
                    build(ability.CANCEL_BUILDINPROGRESS)
