from bot.enemy_data import EnemyData
from strategy.adept_proxy import AdeptProxy
from strategy.adept_rush_defense import AdeptRushDefense
from strategy.air_oracle import AirOracle
from strategy.colossus import Colossus
from strategy.dts import DTs
from strategy.one_base_robo import OneBaseRobo
from strategy.stalker_proxy import StalkerProxy


class StrategyManager:
    strategy_name_dict = {
        'StalkerProxy': StalkerProxy,
        'AdeptProxy': AdeptProxy,
        'AdeptRushDefense': AdeptRushDefense,
        'OneBaseRobo': OneBaseRobo,
        'DTs': DTs,
        'Colossus': Colossus,
        'AirOracle': AirOracle
    }

    def __init__(self, enemy_info: EnemyData):
        self.enemy_info = enemy_info

    def get_strategy(self, strategy_name):
        return self.strategy_name_dict[strategy_name](self)

    def choose_strategy(self):
        self.enemy_info.load_enemy_data_dict()

        if self.enemy_info.enemy_info_dict['last_game']['result'] is 1:
            strategy_chosen = self.enemy_info.enemy_info_dict['last_game']['strategy']
        else:
            max_ = -1
            strategy_chosen = None
            for strategy in self.enemy_info.enemy_info_dict['scoreboard']:
                if strategy != self.enemy_info.enemy_info_dict['last_game']['strategy']:
                    win = self.enemy_info.enemy_info_dict['scoreboard'][strategy]['win']
                    total = self.enemy_info.enemy_info_dict['scoreboard'][strategy]['total']
                    if total == 0:
                        win_rate = 1
                    elif win == 0:
                        win_rate = 0.3 / total
                    else:
                        win_rate = win / total
                    if win_rate > max_:
                        max_ = win_rate
                        strategy_chosen = strategy
        try:
            strategy_obj = self.get_strategy(strategy_chosen)
        except KeyError as ex:
            strategy_obj = None
            print('Strategy "{}" not found.'.format(strategy_chosen))
            print(ex)
        return strategy_obj

    def update_enemy_data(self, score):
        if self.enemy_info.enemy_info_dict is None:
            self.enemy_info.enemy_info_dict = {
                'id': self.enemy_info.opponent_id,
                'last_game': {'strategy': '', 'result': 0},
                'scoreboard': {
                    'StalkerProxy': {'win': 0,'total': 0},
                    'AdeptRushDefense': {'win': 0, 'total': 0},
                    'AirOracle': {'win': 0, 'total': 0},
                    'Colossus': {'win': 0, 'total': 0,
                    'DTs': {'win': 0, 'total': 0},
                    'OneBaseRobo': {'win': 0,'total': 0},
                    'AdeptProxy': {'win': 0, 'total': 0}
                    }
                }
            }

        self.enemy_info.enemy_info_dict['scoreboard'][self.enemy_info.ai.starting_strategy]['total'] += 1
        self.enemy_info.enemy_info_dict['last_game']['strategy'] = self.enemy_info.ai.starting_strategy
        self.enemy_info.enemy_info_dict['last_game']['result'] = score

        general_stats = self.enemy_info.load_general_stats_dict()
        general_stats[self.enemy_info.ai.starting_strategy]['total'] += 1
        general_stats['total']['total'] += 1
        if score:
            self.enemy_info.enemy_info_dict['scoreboard'][self.enemy_info.ai.starting_strategy]['win'] += 1
            general_stats[self.enemy_info.ai.starting_strategy]['win'] += 1
            general_stats['total']['win'] += 1

        self.enemy_info.save_enemy_data_dict()
        self.enemy_info.save_general_stats_dict(general_stats)