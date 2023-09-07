from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.unit import UnitTypeId as unit


class SiegeInfrastructure(InterfaceABS):

    def __init__(self, ai):
        self.ai = ai
        self.previous_attack_state = False
        self.siege_location = None

    async def execute(self):
        if self.ai.attack and self.ai.supply_army > 60:
            if not self.siege_location:
                self.siege_location = self.ai.game_info.map_center.towards(self.ai.enemy_start_locations[0], 20)
                self.siege_location = await self.ai.find_placement(unit.PYLON, near=self.siege_location)


            workers_tags = self.ai.strategy.workers_distribution.get_distant_mining_workers_tags()
            if not workers_tags:
                workers_tags = self.ai.strategy.workers_distribution.get_mineral_workers_tags()
            if not workers_tags:
                workers = self.ai.workers
                if not workers:
                    workers = self.ai.units(unit.PROBE)
            else:
                workers = self.ai.workers.filter(lambda x: x.tag in workers_tags)
            if workers:
                builder = workers.closest_to(self.siege_location)
                if builder.distance_to(self.siege_location) > 25:
                    builder.move(self.siege_location)
                elif isinstance(builder.order_target, int):
                    builder.move(self.siege_location)
                if builder.is_moving and self.ai.minerals > 500:
                    pylons = self.ai.structures().filter(lambda x: x.type_id == unit.PYLON
                                                                 and x.distance_to(self.siege_location) <= 14)
                    if pylons.amount < 3 and self.ai.already_pending(unit.PYLON) < 2:
                        await self.ai.build(unit.PYLON, near=self.siege_location, build_worker=builder, queue=True)
                    pylons_rdy = pylons.ready
                    if pylons_rdy:
                        if self.ai.structures().filter(lambda x: x.type_id == unit.SHIELDBATTERY and x.distance_to(
                                self.siege_location) < 16).amount < 9 and self.ai.already_pending(unit.SHIELDBATTERY) < 3:
                            await self.ai.build(unit.SHIELDBATTERY, near=pylons_rdy.closest_to(self.siege_location),
                                                build_worker=builder, queue=True)
                        if self.ai.structures().filter(lambda x: x.type_id == unit.PHOTONCANNON and x.distance_to(
                                self.siege_location) < 16).amount < 4 and self.ai.already_pending(unit.PHOTONCANNON) < 2:
                            await self.ai.build(unit.PHOTONCANNON, near=pylons_rdy.closest_to(self.siege_location),
                                                build_worker=builder, queue=True)
