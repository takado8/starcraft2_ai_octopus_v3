import random
import sc2
from sc2 import run_game, maps, Race, Difficulty, AIBuild, Result
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2, Point3
from bot.building_spot_validator import BuildingSpotValidator
from typing import Optional, Union
from bot.coords import coords
from bot.constants import ARMY_IDS, BASES_IDS, WORKERS_IDS, UNITS_TO_IGNORE
from strategy.air_oracle import AirOracle
from economy.workers.speed_mining import SpeedMining
from strategy.blinkers import Blinkers
from strategy.colossus import Colossus
from strategy.one_base_robo import OneBaseRobo
from strategy.stalker_proxy import StalkerProxy


class OctopusV3(sc2.BotAI):
    army_ids = ARMY_IDS
    bases_ids = BASES_IDS
    units_to_ignore = UNITS_TO_IGNORE
    workers_ids = WORKERS_IDS

    destination = None
    lost_cost = 0
    killed_cost = 0

    def __init__(self):
        super().__init__()
        self.structures_amount = 0
        self.spot_validator = BuildingSpotValidator(self)
        self.attack = False
        self.first_attack = False
        self.retreat = False
        self.after_first_attack = False
        self.defend_position = None
        self.army_priority = False
        self.army = None
        self.strategy: OneBaseRobo = None
        self.coords = None
        self.speed_mining: SpeedMining = None

    # async def on_unit_created(self, unit: Unit):
    #     if unit.is_mine and unit.type_id in self.army_ids:
    #         self.strategy.army.add_unassigned_soldier(unit)

    async def on_unit_destroyed(self, unit_tag: int):
        self.strategy.enemy_economy.on_unit_destroyed(unit_tag)

    async def on_start(self):
        self.strategy = Colossus(self)
        self.speed_mining = SpeedMining(self)
        self.speed_mining.calculate_targets()
        map_name = str(self.game_info.map_name)
        print('map_name: ' + map_name)
        print('start location: ' + str(self.start_location.position))
        if map_name in coords and self.start_location.position in coords[map_name]:
            self.coords = coords[map_name][self.start_location.position]
            print('getting coords successful.')
        else:
            print('getting coords failed')
            # await self.chat_send('getting coords failed')
        self.strategy.workers_distribution.distribute_workers_on_first_step()
        # for worker in self.workers:
        #     worker.gather(self.mineral_field.closest_to(worker))

    async def on_step(self, iteration: int):
        # self.save_stats()
        self.set_game_step()
        self.army = self.units().filter(lambda x: x.type_id in self.army_ids and x.is_ready)
        await self.strategy.morphing()
        await self.strategy.army_execute()
        self.strategy.distribute_workers()
        self.speed_mining.execute()
        self.strategy.chronoboost()
        await self.strategy.build_pylons()
        self.strategy.train_probes()
        self.strategy.build_assimilators()
        await self.strategy.do_upgrades()
        #
        ## scan
        # self.strategy.scouting.scan_middle_game()
        # self.strategy.scouting.gather_enemy_info()
        # self.strategy.own_economy.calculate_units_report()
        # self.strategy.enemy_economy.calculate_enemy_units_report()
        # if iteration % 30 == 0:
        #     self.strategy.enemy_economy.print_enemy_info()
        #     self.strategy.own_economy.print_own_economy_info()
        ##

        #
        ## attack
        # army_priority = False
        if (not self.attack) and (not self.retreat_condition()) and (
                self.counter_attack_condition() or self.attack_condition()):
            # await self.chat_send('Attack!  army len: ' + str(len(self.army)))
            self.first_attack = True
            self.attack = True
            self.retreat = False
            self.army_priority = True
        # retreat
        if self.retreat_condition():
            self.army_priority = False
            # await self.chat_send('Retreat! army len: ' + str(len(self.army)))
            self.retreat = True
            self.attack = False
            self.after_first_attack = True
        #
        ## build
        current_building = self.strategy.builder.get_current_building()

        if not isinstance(current_building, unit):
            min_army_supply = current_building
            if self.state.score.food_used_army >= min_army_supply:
                self.strategy.builder.increment_build_queue_index()
                self.army_priority = False
            else:
                self.army_priority = True
        lock_spending = await self.lock_spending_condition()

        if not self.army_priority and not lock_spending:
            await self.strategy.build_from_queue()

    async def build(self, building: unit, near: Union[Unit, Point2, Point3], max_distance: int = 20, block=False,
                    build_worker: Optional[Unit] = None, random_alternative: bool = True,
                    placement_step: int = 3, ) -> bool:
        return await self.strategy.builder.build(building=building, near=near, max_distance=max_distance, block=block,
                                                 build_worker=build_worker, random_alternative=random_alternative)

    def is_build_in_progress(self):
        return self.strategy.builder.is_build_in_progress()

    def is_build_finished(self):
        return self.strategy.builder.is_build_finished()

    def get_pylon_with_least_neighbours(self):
        return self.spot_validator.get_pylon_with_least_neighbours()

    def set_game_step(self):
        if self.enemy_units().exists:
            self._client.game_step = 4
        else:
            self._client.game_step = 6

    def get_super_pylon(self):
        return self.spot_validator.get_super_pylon()

    def attack_condition(self):
        return self.strategy.attack_condition()

    def retreat_condition(self):
        return self.strategy.retreat_condition()

    def counter_attack_condition(self):
        return self.strategy.counter_attack_condition()

    async def lock_spending_condition(self):
        return await self.strategy.lock_spending_condition()


def botVsComputer(ai, real_time=0):
    if real_time:
        real_time = True
    else:
        real_time = False

    maps_list = ["BerlingradAIE", "HardwireAIE", "InsideAndOutAIE", "MoondanceAIE", "StargazersAIE",
                 "WaterfallAIE"]
    races = [Race.Protoss, Race.Zerg, Race.Terran]

    # computer_builds = [AIBuild.Rush]
    # computer_builds = [AIBuild.Timing, AIBuild.Rush, AIBuild.Power, AIBuild.Macro]
    # computer_builds = [AIBuild.Timing]
    # computer_builds = [AIBuild.Air]
    # computer_builds = [AIBuild.Power]
    computer_builds = [AIBuild.Macro]
    build = random.choice(computer_builds)

    # map_index = random.randint(0, 5)
    # race_index = random.randint(0, 2)
    # CheatMoney   VeryHard CheatInsane VeryEasy
    result = run_game(map_settings=maps.get(random.choice(maps_list)), players=[
        Bot(race=Race.Protoss, ai=ai, name='Octopus'),
        Computer(race=races[1], difficulty=Difficulty.VeryHard, ai_build=build)
    ], realtime=real_time)
    return result, ai  # , build, races[race_index]


def test(real_time=1):
    ai = OctopusV3()
    result, ai = botVsComputer(ai, real_time)
    print('Result: {}'.format(result))

    if result == Result.Victory:
        win = 1
    elif result == Result.Defeat:
        win = 0
    elif ai.structures_amount > 5:
        win = 1
    else:
        win = 0
    return win, ai.killed_cost, ai.lost_cost


if __name__ == '__main__':
    import time

    start = time.time()
    win, killed, lost = test(real_time=0)
    stop = time.time()
    print('result: {} time elapsed: {} s'.format('win' if win else 'lost', int(stop - start)))
