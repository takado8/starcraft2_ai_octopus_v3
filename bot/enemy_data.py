from typing import Dict
import argparse
import json
import os
import sys


class EnemyInfo:
    def __init__(self, ai):
        self.ai = ai
        self.opponent_id = None
        self.dir_path = None
        self.opponent_file_path = None
        self.enemy_info_dict: Dict[str] = None

    async def get_opponent_id(self):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument('--OpponentId',type=str,nargs="?",help='Opponent Id')
            args,unknown = parser.parse_known_args()
            if args.OpponentId:
                return str(args.OpponentId)
            else:
                await self.ai.chat_send('opponent id is none.')
                return None
        except Exception as ex:
            await self.ai.chat_send('Cannot read opponent id.')
            print(ex)
            return None

    async def pre_analysis(self):
        try:
            self.opponent_id = await self.get_opponent_id()
            if self.opponent_id:
                dir_ = os.path.realpath(sys.argv[0]) if sys.argv[0] else None
                if dir_:
                    self.dir_path = os.path.dirname(os.path.abspath(dir_))
                else:
                    await self.ai.chat_send('dir error')
                    return
                print('opponent id: '+ str(self.opponent_id))
                await self.ai.chat_send('opponent id: '+ str(self.opponent_id))
                self.opponent_file_path = os.path.join(self.dir_path,'data','enemy_info',self.opponent_id + '.json')
                if os.path.isfile(self.opponent_file_path):
                    # enemy = None
                    with open(self.opponent_file_path, 'r') as file:
                        self.enemy_info_dict = json.load(file)
                    # await self.ai.chat_send(str(self.enemy))
                    if self.enemy_info_dict['last_game']['result'] is 1:
                        strategy_chosen = self.enemy_info_dict['last_game']['strategy']
                    else:
                        max_ = -1
                        strategy_chosen = None
                        for strategy in self.enemy_info_dict['scoreboard']:
                            if strategy != self.enemy_info_dict['last_game']['strategy']:
                                win = self.enemy_info_dict['scoreboard'][strategy]['win']
                                total = self.enemy_info_dict['scoreboard'][strategy]['total']
                                if total == 0:
                                    win_rate = 1
                                elif win == 0:
                                    win_rate = 0.3 / total
                                else:
                                    win_rate = win / total
                                if win_rate > max_:
                                    max_ = win_rate
                                    strategy_chosen = strategy
                    return strategy_chosen
                else:
                    await self.ai.chat_send("new opponent.")
            else:
                await self.ai.chat_send("opponent_id is None")
        except Exception as ex:
            print('error.')
            await self.ai.chat_send('recognition error')
            print(ex)

    def post_analysis(self, score):
        if self.enemy_info_dict is None:
            self.enemy_info_dict = {
                'id': self.opponent_id,
                'last_game': {'strategy': '', 'result': 0},
                'scoreboard': {
                    'StalkerProxy': {'win': 0,'total': 0},
                    'AdeptProxy': {'win': 0,'total': 0},
                    'OneBaseRobo': {'win': 0,'total': 0},
                    'AdeptRushDefense': {'win': 0,'total': 0},
                    'DTs': {'win': 0,'total': 0},
                    'Colossus': {'win': 0,'total': 0},
                    'AirOracle': {'win': 0,'total': 0}
                }
            }
        # load general stats file
        general_stats_path = os.path.join(self.dir_path,'data','enemy_info','general_stats.json')
        if os.path.isfile(general_stats_path):
            with open(general_stats_path,'r') as file:
                general_stats = json.load(file)
        else:
            general_stats = {
                    'total': {'win': 0,'total': 0},
                    'StalkerProxy': {'win': 0,'total': 0},
                    'AdeptProxy': {'win': 0,'total': 0},
                    'OneBaseRobo': {'win': 0,'total': 0},
                    'AdeptRushDefense': {'win': 0,'total': 0},
                    'DTs': {'win': 0,'total': 0},
                    'Colossus': {'win': 0,'total': 0},
                    'AirOracle': {'win': 0,'total': 0}
            }
        # update scoreboard
        self.enemy_info_dict['scoreboard'][self.ai.starting_strategy]['total'] += 1
        general_stats[self.ai.starting_strategy]['total'] += 1
        general_stats['total']['total'] += 1
        if score:
            self.enemy_info_dict['scoreboard'][self.ai.starting_strategy]['win'] += 1
            general_stats[self.ai.starting_strategy]['win'] += 1
            general_stats['total']['win'] += 1

        self.enemy_info_dict['last_game']['strategy'] = self.ai.starting_strategy
        self.enemy_info_dict['last_game']['result'] = score

        with open(self.opponent_file_path,'w+') as file:
            json.dump(self.enemy_info_dict, file)

        with open(general_stats_path,'w+') as file:
            json.dump(general_stats, file)
