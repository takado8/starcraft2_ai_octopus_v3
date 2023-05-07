import sc2

from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2 import run_game, maps, Race
from sc2.player import Bot
from data_analysis.test_bots.worker_rush import WorkerRushZergBot


class TerranStalkerDefense(sc2.BotAI):
    def __init__(self):
        super().__init__()
        self.depots_pos = None
        self.second_depot_place = None

    async def on_start(self):
        self.depots_pos = [x for x in self.main_base_ramp.corner_depots]

    async def on_step(self, iteration):
        self.train_workers()
        await self.distribute_workers()
        await self.build_depots()
        await self.build_barracks()
        await self.build_factory()
        await self.build_bunker()
        await self.build_refinery()
        self.train_marines()
        self.train_tank()



    async def build_refinery(self):
        if self.can_afford(unit.REFINERY) and self.structures(unit.REFINERY).amount < 2 and not self.already_pending(
            unit.REFINERY):
            await self.build(unit.REFINERY, near=self.vespene_geyser.closer_than(10, self.start_location.position).random)

    def train_marines(self):
        if self.can_afford(unit.MARINE) and self.structures(unit.BARRACKS).ready.idle.exists:
            self.train(unit.MARINE)

    def train_tank(self):
        if self.can_afford(unit.SIEGETANK) and self.structures(unit.FACTORY).ready.idle.exists:
            self.train(unit.SIEGETANK)

    async def build_bunker(self):
        if self.can_afford(unit.BUNKER) and self.structures(unit.BARRACKS).ready.exists and\
            self.structures(unit.BUNKER).amount < 1 and not self.already_pending(unit.BUNKER):
            natural_location = min([(self.main_base_ramp.bottom_center.distance_to(x), x) for x in self.expansion_locations_list],
                       key=lambda x: x[0])[1]
            bunker_location = self.mineral_field.closest_to(natural_location).position.towards(natural_location, 10)
            await self.build(unit.BUNKER, bunker_location)

    async def build_factory(self):
        if self.can_afford(unit.FACTORY) and not self.already_pending(unit.FACTORY) \
            and self.structures(unit.FACTORY).amount < 1 and self.structures(unit.BARRACKS).ready.exists:
            await self.build(unit.FACTORY, self.start_location.position.random_on_distance(20))

    async def build_barracks(self):
        barracks = self.structures(unit.BARRACKS)
        if self.can_afford(unit.BARRACKS)and not self.already_pending(unit.BARRACKS):
            if not barracks:
                await self.build(unit.BARRACKS, self.main_base_ramp.barracks_correct_placement)
            elif 2 > barracks.amount > 0:
                await self.build(unit.BARRACKS, self.start_location.position.random_on_distance(16))


    def train_workers(self):
        if self.can_afford(unit.SCV) and self.workers.amount < self.townhalls.amount * 16 + self.structures(unit.REFINERY).amount * 3\
                and self.townhalls.ready.idle.exists:
            self.train(unit.SCV)

    async def build_depots(self):
        depots = self.structures(unit.SUPPLYDEPOT)
        if self.can_afford(unit.SUPPLYDEPOT) and not self.already_pending(unit.SUPPLYDEPOT) and\
                (depots.amount < 2 or self.supply_left < 5):

            if not depots or not depots.closer_than(1, self.depots_pos[0]).exists:
                place = self.depots_pos[0]
            elif not depots or not depots.closer_than(1, self.depots_pos[1]).exists:
                place = self.depots_pos[1]
            else:
                place = self.start_location.position.random_on_distance(17)
            await self.build(unit.SUPPLYDEPOT, place)


def run(real_time=0):
    if real_time:
        real_time = True
    else:
        real_time = False

    maps_list = ["BerlingradAIE", "HardwireAIE", "InsideAndOutAIE", "MoondanceAIE", "StargazersAIE",
                 "WaterfallAIE"]

    run_game(map_settings=maps.get(maps_list[5]), players=[
        Bot(race=Race.Terran, ai=TerranStalkerDefense(), name='PositionsSetup'),
        Bot(race=Race.Zerg, ai=WorkerRushZergBot(), name='ZergRush')

    ], realtime=real_time)


if __name__ == '__main__':
    run(real_time=0)