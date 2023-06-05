from bot.enemy_data import EnemyData
from strategy.air_oracle import AirOracle
from strategy.cannon_rush_defense import CannonRushDefense
from strategy.fortress_skytoss import FortressSkyToss
from strategy.fortress_toss import FortressToss
from strategy.oracle_defense import OracleDefenseUpdated
from strategy.skytoss import SkyToss
from strategy.skytoss_carriers import SkytossCarriers
from strategy.stalker_defense import StalkerDefenseUpdated
from strategy.stalker_proxy import StalkerProxy
from strategy.worker_rush_defense import WorkerRushDefenseStrategy
from strategy.zealot_rush_defense import ZealotRushDefense
from sc2 import Race


class StrategyManager:
    def __init__(self, enemy_data: EnemyData, ai):
        if ai.enemy_race == Race.Terran:
            self.strategy_name_dict = {
                'StalkerProxy': StalkerProxy,
                'AirOracle': AirOracle,
                'FortressSkyToss': FortressSkyToss,
                'SkytossCarriers': SkytossCarriers
            }
        elif ai.enemy_race == Race.Protoss:
            self.strategy_name_dict = {
                'StalkerProxy': StalkerProxy,
                'CannonRushDefense': CannonRushDefense,
                'FortressSkyToss': FortressSkyToss,
                'SkytossCarriers': SkytossCarriers

            }
        elif ai.enemy_race == Race.Zerg:
            self.strategy_name_dict = {
                'ZealotRushDefense': ZealotRushDefense,
                'FortressSkyToss': FortressSkyToss,
                'StalkerProxy': StalkerProxy,
                'SkytossCarriers': SkytossCarriers
            }
        else:
            self.strategy_name_dict = {
                'StalkerProxy': StalkerProxy,
                'FortressSkyToss': FortressSkyToss,
                'SkytossCarriers': SkytossCarriers
            }

        self.enemy_data = enemy_data
        self.default_strategy = SkytossCarriers

    def get_strategy(self, strategy_name):
        return self.strategy_name_dict[strategy_name]

    async def choose_get_strategy(self):
        enemy_data_dict = await self.enemy_data.load_enemy_data_dict()
        strategy_chosen = None
        if enemy_data_dict is False:
            self.enemy_data.create_enemy_data_dict(self.create_enemy_data_scoreboard_dict())
        elif enemy_data_dict:
            self.update_strategies()
            if self.enemy_data.enemy_data_dict['last_game']['result'] is 1:
                strategy_chosen = self.enemy_data.enemy_data_dict['last_game']['strategy']
            else:
                max_ = -1
                for strategy in self.enemy_data.enemy_data_dict['scoreboard']:
                    if strategy != self.enemy_data.enemy_data_dict['last_game']['strategy']:
                        win = self.enemy_data.enemy_data_dict['scoreboard'][strategy]['win']
                        total = self.enemy_data.enemy_data_dict['scoreboard'][strategy]['total']
                        if total == 0:
                            win_rate = 0.75
                        elif win == 0:
                            win_rate = 0.3 / total
                        else:
                            win_rate = win / total
                        if win_rate > max_:
                            max_ = win_rate
                            strategy_chosen = strategy
        if strategy_chosen:
            try:
                strategy_obj = self.get_strategy(strategy_chosen)
            except KeyError as ex:
                print('Strategy "{}" not found. Setting default: {}'.format(strategy_chosen, self.default_strategy))
                strategy_obj = self.default_strategy
                print(ex)
        else:
            strategy_obj = self.default_strategy
            print('Strategy is "{}". Setting default: {}'.format(strategy_chosen, self.default_strategy))

        return strategy_obj

    def update_strategies(self):
        for strategy_name in self.strategy_name_dict:
            if strategy_name not in self.enemy_data.enemy_data_dict['scoreboard']:
                self.enemy_data.enemy_data_dict['scoreboard'][strategy_name] = {'win': 0, 'total': 0}

        strategies_to_remove = []
        for strategy_name in self.enemy_data.enemy_data_dict['scoreboard']:
            if strategy_name not in self.strategy_name_dict:
                strategies_to_remove.append(strategy_name)
        for strategy_name in strategies_to_remove:
            self.enemy_data.enemy_data_dict['scoreboard'].pop(strategy_name)


    def update_general_stats_strategies(self, general_stats_dict):
        for strategy_name in self.strategy_name_dict:
            if strategy_name not in general_stats_dict:
                general_stats_dict[strategy_name] = {'win': 0, 'total': 0}

    def create_general_stats_dict(self):
        general_stats_dict = {'total': {'win': 0, 'total': 0}}
        for strategy_name in self.strategy_name_dict:
            general_stats_dict[strategy_name] = {'win': 0, 'total': 0}
        return general_stats_dict

    def create_enemy_data_scoreboard_dict(self):
        scoreboard = {}
        for strategy_name in self.strategy_name_dict:
            scoreboard[strategy_name] = {'win': 0, 'total': 0}
        return scoreboard

    def update_and_save_enemy_data(self, score):
        if self.enemy_data.enemy_data_dict is None:
            self.enemy_data.create_enemy_data_dict(self.create_enemy_data_scoreboard_dict())

        self.enemy_data.enemy_data_dict['scoreboard'][self.enemy_data.ai.starting_strategy]['total'] += 1
        self.enemy_data.enemy_data_dict['last_game']['strategy'] = self.enemy_data.ai.starting_strategy
        self.enemy_data.enemy_data_dict['last_game']['result'] = score

        general_stats = self.enemy_data.load_general_stats_dict()
        if general_stats:
            self.update_general_stats_strategies(general_stats)
        else:
            general_stats = self.create_general_stats_dict()

        general_stats[self.enemy_data.ai.starting_strategy]['total'] += 1
        general_stats['total']['total'] += 1
        if score:
            self.enemy_data.enemy_data_dict['scoreboard'][self.enemy_data.ai.starting_strategy]['win'] += 1
            general_stats[self.enemy_data.ai.starting_strategy]['win'] += 1
            general_stats['total']['win'] += 1

        self.enemy_data.save_enemy_data_dict()
        self.enemy_data.save_general_stats_dict(general_stats)