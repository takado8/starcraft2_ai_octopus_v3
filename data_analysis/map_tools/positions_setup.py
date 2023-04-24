import time
from sc2 import BotAI
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2 import run_game, maps, Race
from sc2.player import Bot
from builders.builder import Builder
from data_analysis.map_tools.map_positions_service import MapPositionsService
from data_analysis.worker_rush import WorkerRushZergBot


class PositionsSetup(BotAI):
    def __init__(self):
        super().__init__()
        self.map_service: MapPositionsService = None
        self.builder: Builder = None

    async def on_start(self):
        self.map_service = MapPositionsService(self, "test101")
        try:
            locations_dict = self.map_service.positions_dict[self.map_service.start_location]
        except:
            locations_dict = {}

        build_queue = []
        for unit_id in locations_dict:
            for _ in locations_dict[unit_id]:
                build_queue.append(unit_id)
        special_locations = [locations_dict]
        self.builder = Builder(self, build_queue=build_queue, expander=None,
                               special_building_locations=special_locations)

        print('map_name: ' + str(self.game_info.map_name))
        print('start location: ' + str(self.start_location.position))
        print('build queue:')
        print(build_queue)

    async def on_step(self, iteration: int):
        try:
            await self.builder.build_from_queue()
        except:
            pass
        if iteration > 5:
            self.map_service.get_structures_positions()
            if self.structures(unit.ASSIMILATOR).amount > 1:
                self.map_service.save_positions_json()
                time.sleep(1)
                exit(12)




def run(real_time=0):
    if real_time:
        real_time = True
    else:
        real_time = False

    maps_list = ["BerlingradAIE", "HardwireAIE", "InsideAndOutAIE", "MoondanceAIE", "StargazersAIE",
                 "WaterfallAIE"]

    run_game(map_settings=maps.get(maps_list[1]), players=[
        Bot(race=Race.Protoss, ai=PositionsSetup(), name='PositionsSetup'),
        Bot(race=Race.Zerg, ai=WorkerRushZergBot(), name='ZergRush')

    ], realtime=real_time)


if __name__ == '__main__':
    run(real_time=1)