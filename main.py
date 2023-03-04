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
from bot.enemy_data import EnemyData
from bot.strategy_manager import StrategyManager
from bot.cancel_build import cancel_damaged_build
import traceback

from data_analysis.test_bot_zerg_roach import RoachBurrowBot
from data_analysis.test_bot_zerg_rush import SimpleZergBot
from data_analysis.worker_rush import WorkerRushZergBot


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
        self.strategy_manager: StrategyManager = None
        self.enemy_data: EnemyData = None
        self.starting_strategy = None
        self.iteration = -2
        self.enemy_main_base_ramp = None



    # async def on_unit_created(self, unit: Unit):
        # print('unit: {} created'.format(unit.type_id))

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
            print('getting enemy data...')
            self.enemy_data = EnemyData(self)
            self.strategy_manager = StrategyManager(self.enemy_data)

            strategy = await self.strategy_manager.choose_get_strategy()
            self.strategy = strategy(self)
            print('getting enemy data done.')
            print('setting strategy: ' + str(self.strategy.name))
            self.starting_strategy = self.strategy.name
            map_name = str(self.game_info.map_name)
            print('map_name: ' + map_name)
            print('start location: ' + str(self.start_location.position))

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
            self.strategy_manager.update_and_save_enemy_data(score)
            print('done.')
        except Exception as ex:
            try:
                await self.chat_send('Error 09')
            except:
                pass
            print(ex)

    async def on_step(self, iteration: int):
        if self.iteration == 10:
            strategy_tag = 'Tag:' + ''.join([a for a in self.strategy.name if a.isupper()])
            await self.chat_send(strategy_tag)
        try:
            self.iteration = iteration
            self.save_stats()
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
        except:
            await self.chat_send('Error 02')
            print(traceback.print_exc())
        try:
            self.strategy.handle_workers()
        except Exception:
            await self.chat_send('Error 03')
            print(traceback.print_exc())
        try:
            await self.strategy.nexus_abilities()
        except Exception:
            await self.chat_send('Error 04')
            print(traceback.print_exc())
        try:
            await self.strategy.build_pylons()
        except Exception as ex:
            await self.chat_send('Error 05')
            print(ex)
        try:
            self.strategy.train_probes()
            self.strategy.build_assimilators()
        except:
            await self.chat_send('Error 06')
            print(traceback.print_exc())
        try:
            await self.strategy.do_upgrades()
        except:
            await self.chat_send('Error 07')
            print(traceback.print_exc())

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
            if (not self.army_priority or (self.minerals > 700 and self.vespene > 350)) and not lock_spending:
                # print('build from main.')
                await self.strategy.build_from_queue()
        except:
            await self.chat_send('Error 08')
            print(traceback.print_exc())
        try:
            await cancel_damaged_build(self)
        except:
            await self.chat_send('Error 12')
            print(traceback.print_exc())



    async def build(self, building: unit, near: Union[Unit, Point2, Point3], max_distance: int = 20, block=False,
                    build_worker: Optional[Unit] = None, random_alternative: bool = True,
                    placement_step: int = 3, validate_location=True, ) -> bool:
        return await self.strategy.builder.build(building=building, near=near, max_distance=max_distance, block=block,
                                                 build_worker=build_worker, random_alternative=random_alternative,
                                                 validate_location=validate_location)

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
            self._client.game_step = 6
        else:
            self._client.game_step = 4

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

    computer_builds = [AIBuild.Rush]
    # computer_builds = [AIBuild.Timing, AIBuild.Rush, AIBuild.Power, AIBuild.Macro]
    # computer_builds = [AIBuild.Timing]
    # computer_builds = [AIBuild.Air]
    # computer_builds = [AIBuild.Power]
    # computer_builds = [AIBuild.Macro]
    build = random.choice(computer_builds)

    # map_index = random.randint(0, 5)
    # race_index = random.randint(0, 2)
    # CheatMoney   VeryHard CheatInsane VeryEasy CheatMoney
    result = run_game(map_settings=maps.get(random.choice(maps_list)), players=[
        Bot(race=Race.Protoss, ai=ai, name='Octopus'),
        # Bot(race=Race.Zerg, ai=WorkerRushZergBot(), name='ZergRush')
        Computer(race=races[2], difficulty=Difficulty.VeryHard, ai_build=build)
    ], realtime=real_time)
    return result, ai  # , build, races[race_index]


def test(real_time=0):
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
    for i in range(1, 6):
        print('\n---------------------- game {} -----------------------------\n'.format(i))
        start = time.time()
        win, killed_minerals, killed_gas, lost_minerals, lost_gas = test(real_time=0)
        stop = time.time()
        results.append((win, killed_minerals, killed_gas, lost_minerals, lost_gas))
        print('result: {} time elapsed: {} s'.format('win' if win else 'lost', int(stop - start)))
        print('killed minerals: {}\nkilled gas: {}\n\nlost minerals: {}\nlost gas {}\n'.format(
            killed_minerals, killed_gas, lost_minerals, lost_gas))

    avg_killed_minerals = sum([result[1] for result in results if result[0]]) / len(results)
    avg_killed_gas = sum([result[2] for result in results if result[0]]) / len(results)
    avg_lost_minerals = sum([result[3] for result in results if result[0]]) / len(results)
    avg_lost_gas = sum([result[4] for result in results if result[0]]) / len(results)
    wins = sum([result[0] for result in results])

    print('\n----------------------------- results ---------------------------\n')
    print('wins: {}/{}\navg killed minerals: {}\navg killed gas: {}\n\navg lost minerals: {}\navg lost gas {}\n'.format(
        wins, len(results), avg_killed_minerals, avg_killed_gas, avg_lost_minerals, avg_lost_gas))