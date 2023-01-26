import random
from datetime import datetime
import sc2
from sc2 import run_game, maps, Race, Difficulty, AIBuild, Result
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2, Point3
from bot.building_spot_validator import BuildingSpotValidator
from typing import Optional, Union
from bot.constants import ARMY_IDS, BASES_IDS, WORKERS_IDS, UNITS_TO_IGNORE
from bot.enemy_data import EnemyInfo
from strategy.adept_proxy import AdeptProxy
from strategy.adept_rush_defense import AdeptRushDefense
from strategy.air_oracle import AirOracle
from strategy.colossus import Colossus
from strategy.dts import DTs
from strategy.one_base_robo import OneBaseRobo
from strategy.stalker_proxy import StalkerProxy


class OctopusV3(sc2.BotAI):
    army_ids = ARMY_IDS
    bases_ids = BASES_IDS
    units_to_ignore = UNITS_TO_IGNORE
    workers_ids = WORKERS_IDS
    lost_minerals = 0
    lost_gas = 0
    killed_minerals = 0
    killed_gas = 0
    structures_amount = 0

    def __init__(self):
        super().__init__()
        self.spot_validator = BuildingSpotValidator(self)
        self.attack = False
        self.first_attack = False
        self.retreat = False
        self.after_first_attack = False
        self.defend_position = None
        self.army_priority = False
        self.army = None
        self.strategy = None
        self.coords = None
        self.enemy_info: EnemyInfo = None
        self.starting_strategy = None
        self.iteration = -2
        self.enemy_main_base_ramp = None

    # async def on_unit_created(self, unit: Unit):
    #     if unit.is_mine and unit.type_id in self.army_ids:
    #         self.strategy.army.add_unassigned_soldier(unit)

    async def on_unit_destroyed(self, unit_tag: int):
        try:
            self.strategy.enemy_economy.on_unit_destroyed(unit_tag)
            self.strategy.workers_distribution.on_unit_destroyed(unit_tag)
        except Exception as ex:
            try:
                await self.chat_send('Error 11')
            except:
                pass
            print(ex)

    async def on_start(self):
        print('----------------------- new game ---------------------------------')
        try:
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print(current_time)
            print('getting enemy info...')
            self.enemy_info = EnemyInfo(self)
            strategy_name = await self.enemy_info.pre_analysis()
            print('getting enemy info done.')
            if not strategy_name:
                print('enemy is None. default strategy')
                strategy_name = 'StalkerProxy'
            print('setting strategy: ' + str(strategy_name))
            self.starting_strategy = strategy_name
            self.set_strategy(strategy_name)
            map_name = str(self.game_info.map_name)
            print('map_name: ' + map_name)
            print('start location: ' + str(self.start_location.position))
            # if map_name in coords and self.start_location.position in coords[map_name]:
            #     self.coords = coords[map_name][self.start_location.position]
            #     print('getting coords successful.')
            # else:
            #     print('getting coords failed')
            #     # await self.chat_send('getting coords failed')
            for worker in self.workers:
                worker.stop()

            self.enemy_main_base_ramp = min(self.game_info.map_ramps, key=lambda ramp:
                        self.enemy_start_locations[0].position.distance_to(ramp.top_center))

        except Exception as ex:
            try:
                await self.chat_send('Error 10')
            except:
                pass
            print(ex)

    async def on_end(self, game_result: Result):
        try:
            print('starting post-analysis...')
            if game_result == Result.Victory:
                score = 1
            else:
                score = 0
            # plot(self.times,self.y1,self.y2)
            self.enemy_info.post_analysis(score)
            print('done.')
        except Exception as ex:
            try:
                await self.chat_send('Error 09')
            except:
                pass
            print(ex)

    async def on_step(self, iteration: int):
        if self.iteration == 10:
            await self.chat_send('{}{}'.format(self.strategy.name[0], self.strategy.name[-1]))

        try:
            self.iteration = iteration
            # self.save_stats()
            self.set_game_step()
            self.army = self.units().filter(lambda x: x.type_id in self.army_ids and x.is_ready)
        except Exception as ex:
            await self.chat_send('Error 00')
            print(ex)
        try:
            await self.strategy.morphing()
        except Exception as ex:
            await self.chat_send('Error 01')
            print(ex)
        try:
            await self.strategy.army_execute()
        except Exception as ex:
            await self.chat_send('Error 02')
            print(ex)
        try:
            self.strategy.handle_workers()
        except Exception as ex:
            await self.chat_send('Error 03')
            print(ex)
        try:
            await self.strategy.nexus_abilities()
        except Exception as ex:
            await self.chat_send('Error 04')
            print(ex)
        try:
            await self.strategy.build_pylons()
        except Exception as ex:
            await self.chat_send('Error 05')
            print(ex)
        try:
            self.strategy.train_probes()
            self.strategy.build_assimilators()
        except Exception as ex:
            await self.chat_send('Error 06')
            print(ex)
        try:
            await self.strategy.do_upgrades()
        except Exception as ex:
            await self.chat_send('Error 07')
            print(ex)

        if (not self.attack) and (not self.retreat_condition()) and (
                self.counter_attack_condition() or self.attack_condition()):
            self.first_attack = True
            self.attack = True
            self.retreat = False
            self.army_priority = True
        # retreat
        if self.attack and self.retreat_condition():
            self.army_priority = False
            self.retreat = True
            self.attack = False
            self.after_first_attack = True
        #
        ## build
        try:
            current_building = self.strategy.builder.get_current_building()
            # print('current building: {}'.format(current_building))
            if not isinstance(current_building, unit):
                min_army_supply = current_building
                if self.state.score.food_used_army >= min_army_supply:
                    self.strategy.builder.increment_build_queue_index()
                    self.army_priority = False
                else:
                    self.army_priority = True
            lock_spending = await self.lock_spending_condition()
            # print('army priority: {}'.format(self.army_priority))
            if (not self.army_priority or (self.minerals > 700 and self.vespene > 200)) and not lock_spending:
                # print('build from main.')
                await self.strategy.build_from_queue()
        except Exception as ex:
            await self.chat_send('Error 08')
            print(ex)

    async def build(self, building: unit, near: Union[Unit, Point2, Point3], max_distance: int = 20, block=False,
                    build_worker: Optional[Unit] = None, random_alternative: bool = True,
                    placement_step: int = 3, ) -> bool:
        return await self.strategy.builder.build(building=building, near=near, max_distance=max_distance, block=block,
                                                 build_worker=build_worker, random_alternative=random_alternative)

    def set_strategy(self, strategy_name):
        strategy_name_dict = {
            'StalkerProxy': StalkerProxy,
            'AdeptProxy': AdeptProxy,
            'AdeptRushDefense': AdeptRushDefense,
            'OneBaseRobo': OneBaseRobo,
            'DTs': DTs,
            'Colossus': Colossus,
            'AirOracle': AirOracle
        }
        self.strategy = strategy_name_dict[strategy_name](self)


    def in_pathing_grid(self, pos: Union[Point2, Unit]):
        if isinstance(pos, Unit):
            pos = pos.position
        if not self.in_map_bounds(pos):
            return
        return super().in_pathing_grid(pos)

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
            self._client.game_step = 8

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

    def save_stats(self):
        self.killed_minerals = self.state.score.killed_minerals_army
        self.killed_gas = self.state.score.killed_vespene_army
        self.lost_minerals = self.state.score.lost_minerals_army
        self.lost_gas = self.state.score.lost_vespene_army
        self.structures_amount = self.structures.amount


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
    computer_builds = [AIBuild.Power]
    # computer_builds = [AIBuild.Macro]
    build = random.choice(computer_builds)

    # map_index = random.randint(0, 5)
    # race_index = random.randint(0, 2)
    # CheatMoney   VeryHard CheatInsane VeryEasy CheatMoney
    result = run_game(map_settings=maps.get(random.choice(maps_list)), players=[
        Bot(race=Race.Protoss, ai=ai, name='Octopus'),
        Computer(race=races[2], difficulty=Difficulty.CheatMoney, ai_build=build)
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
    return win, ai.killed_minerals, ai.killed_gas, ai.lost_minerals, ai.lost_gas


if __name__ == '__main__':
    import time
    results = []
    for i in range(1, 11):
        print('\n---------------------- game {} -----------------------------\n'.format(i))
        start = time.time()
        win, killed_minerals, killed_gas, lost_minerals, lost_gas = test(real_time=0)
        stop = time.time()
        results.append((win, killed_minerals, killed_gas, lost_minerals, lost_gas))
        print('result: {} time elapsed: {} s'.format('win' if win else 'lost', int(stop - start)))
        print('killed minerals: {}\nkilled gas: {}\n\nlost minerals: {}\nlost gas {}\n'.format(
            killed_minerals, killed_gas, lost_minerals, lost_gas))

    avg_killed_minerals = sum([result[1] for result in results]) / len(results)
    avg_killed_gas = sum([result[2] for result in results]) / len(results)
    avg_lost_minerals = sum([result[3] for result in results]) / len(results)
    avg_lost_gas = sum([result[4] for result in results]) / len(results)
    wins = sum([result[0] for result in results])

    print('\n----------------------------- results ---------------------------\n')
    print('wins: {}/{}\navg killed minerals: {}\navg killed gas: {}\n\navg lost minerals: {}\navg lost gas {}\n'.format(
        wins, len(results), avg_killed_minerals, avg_killed_gas, avg_lost_minerals, avg_lost_gas))