from bot.enemy_data import EnemyInfo
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

    def __init__(self, enemy_info: EnemyInfo):
        self.enemy_info = enemy_info

    def get_strategy(self, strategy_name):
        return self.strategy_name_dict[strategy_name](self)