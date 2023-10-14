from sc2 import Race

from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.unit_typeid import UnitTypeId as unit


class HandleProxy(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai
        self.last_scout_time = -10
        self.scout_every_n_seconds = 30
        self.workers_amount = 5 #if self.ai.enemy_race == Race.Protoss else 3
        self.is_reported = False
        self.is_active = True


    async def execute(self):
        if self.ai.time < 360 and self.is_active:
            if self.ai.time < 240 and self.ai.time - self.last_scout_time > self.scout_every_n_seconds:
                workers_tags = self.ai.strategy.workers_distribution.get_distant_mining_workers_tags()
                if not workers_tags:
                    workers_tags = self.ai.strategy.workers_distribution.get_mineral_workers_tags()
                if workers_tags:
                    workers = self.ai.workers.filter(lambda x: x.tag in workers_tags)
                    scout = workers.closer_than(50, self.ai.start_location).furthest_to(self.ai.start_location)
                    nearby_expansions = sorted(self.ai.expansion_locations_list,
                                               key=lambda x: self.ai.start_location.distance_to(x))[1:3]
                    scout.stop()
                    for exp in nearby_expansions:
                        scout.move(exp, queue=True)
                    self.last_scout_time = self.ai.time

            enemy_proxy = self.ai.enemy_structures().filter(
                lambda x: x.type_id in {unit.BUNKER, unit.BARRACKS, unit.PYLON, unit.PHOTONCANNON} and
                          x.distance_to(self.ai.main_base_ramp.bottom_center) < 45)
            if enemy_proxy.exists:
                if not self.is_reported:
                    self.is_reported = True
                    await self.ai.chat_send("Tag:2_handle proxy")
                # barracs = enemy_proxy(unit.BARRACKS)
                # bunkers = enemy_proxy(unit.BUNKER)

                enemy_units = self.ai.enemy_units().closer_than(55, self.ai.main_base_ramp.bottom_center)
                enemy_workers = enemy_units().filter(lambda x: x.type_id in {unit.SCV, unit.PROBE})

                if enemy_workers and enemy_units.amount - enemy_workers.amount <= 2:
                    closest_enemy = enemy_workers.closest_to(self.ai.main_base_ramp.bottom_center)
                    probes = self.ai.workers.closest_n_units(closest_enemy, self.workers_amount)
                    for probe in probes:
                        if probe.distance_to(self.ai.main_base_ramp.bottom_center) > 60 or probe.shield_percentage < 0.1:
                            probe.gather(self.ai.mineral_field.closest_to(self.ai.start_location))
                        else:
                            probe.attack(closest_enemy)
                elif not enemy_units:
                    barracks = enemy_proxy(unit.BARRACKS)
                    if barracks:
                        enemy_proxy = barracks
                    else:
                        cannons = enemy_proxy(unit.PHOTONCANNON)
                        if cannons:
                            ready_cannons = cannons.ready
                            if not ready_cannons:
                                enemy_proxy = cannons
                            else:
                                self.is_active = False
                elif enemy_units:
                    self.is_active = False

                closest_enemy = enemy_proxy.closest_to(self.ai.main_base_ramp.bottom_center)
                probes = self.ai.workers.closest_n_units(closest_enemy, self.workers_amount)
                for probe in probes:
                    probe.attack(closest_enemy)
