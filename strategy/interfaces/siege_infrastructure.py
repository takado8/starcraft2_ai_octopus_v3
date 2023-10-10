from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.unit import UnitTypeId as unit


class SiegeInfrastructure(InterfaceABS):

    def __init__(self, ai, min_minerals=500, min_army_supply=60):
        self.ai = ai
        self.previous_attack_state = False
        self.siege_location = None
        self.min_minerals = min_minerals
        self.min_army_supply = min_army_supply

    async def execute(self):
        if self.ai.attack:
            if not self.siege_location:
                self.siege_location = self.ai.game_info.map_center.towards(self.ai.enemy_start_locations[0], 10)
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
                if builder.distance_to(self.siege_location) > 20:
                    builder.move(self.siege_location)
                elif isinstance(builder.order_target, int):
                    builder.move(self.siege_location)
                if self.ai.supply_army >= self.min_army_supply and builder.is_moving and self.ai.minerals > self.min_minerals and (not self.ai.enemy_units() or
                        not self.ai.enemy_units().closer_than(10, self.siege_location).exists):
                    pylons = self.ai.structures().filter(lambda x: x.type_id == unit.PYLON
                                                                 and x.distance_to(self.siege_location) <= 14)
                    if pylons.amount < 2 and self.ai.already_pending(unit.PYLON) < 2:
                        await self.ai.build(unit.PYLON, near=self.siege_location, build_worker=builder, queue=True)
                    pylons_rdy = pylons.ready
                    if pylons_rdy:
                        if self.ai.structures().filter(lambda x: x.type_id == unit.SHIELDBATTERY and x.distance_to(
                                self.siege_location) < 16).amount < 9 and self.ai.already_pending(unit.SHIELDBATTERY) < 3:
                            await self.ai.build(unit.SHIELDBATTERY, near=pylons_rdy.closest_to(self.siege_location),
                                                build_worker=builder, queue=True)
                        if self.ai.structures().filter(lambda x: x.type_id == unit.PHOTONCANNON and x.distance_to(
                                self.siege_location) < 16).amount < 3 and self.ai.already_pending(unit.PHOTONCANNON) < 2:
                            await self.ai.build(unit.PHOTONCANNON, near=pylons_rdy.closest_to(self.siege_location),
                                                build_worker=builder, queue=True)
