from typing import Dict
import argparse
import json
import os
import sys


class EnemyData:
    def __init__(self, ai):
        self.ai = ai
        self.opponent_id = None
        self.dir_path = None
        self.opponent_file_path = None
        self.general_stats_filepath = None
        self.enemy_data_dict: Dict[str] = None

    async def get_opponent_id(self):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument('--OpponentId',type=str,nargs="?",help='Opponent Id')
            args,unknown = parser.parse_known_args()
            if args.OpponentId:
                return str(args.OpponentId)
            else:
                print('opponent id is none.')
                return None
        except Exception as ex:
            await self.ai.chat_send('Error 020')
            print(ex)
            return None

    async def load_enemy_data_dict(self):
        try:
            self.opponent_id = await self.get_opponent_id()
            if self.opponent_id:
                dir_ = os.path.realpath(sys.argv[0]) if sys.argv[0] else None
                if dir_:
                    self.dir_path = os.path.dirname(os.path.abspath(dir_))
                else:
                    print('dir error')
                    return
                print('opponent id: '+ str(self.opponent_id))
                self.opponent_file_path = os.path.join(self.dir_path,'data','enemy_info',self.opponent_id + '.json')
                if os.path.isfile(self.opponent_file_path):
                    with open(self.opponent_file_path, 'r') as file:
                        self.enemy_data_dict = json.load(file)
                        return self.enemy_data_dict
                else:
                    print("new opponent.")
                    return False
            else:
                print("opponent_id is None")
        except Exception as ex:
            print('load_enemy_data_dict error')
            print(ex)

    def create_enemy_data_dict(self, scoreboard: Dict):
        self.enemy_data_dict = {
            'id': self.opponent_id,
            'last_game': {'strategy': '', 'result': 0},
            'scoreboard': scoreboard}

    def save_enemy_data_dict(self):
        with open(self.opponent_file_path, 'w+') as file:
            json.dump(self.enemy_data_dict, file)

    def load_general_stats_dict(self):
        self.general_stats_filepath = os.path.join(self.dir_path, 'data', 'enemy_info', 'general_stats2.json')
        if os.path.isfile(self.general_stats_filepath):
            with open(self.general_stats_filepath, 'r') as file:
                general_stats = json.load(file)
                return general_stats

    def save_general_stats_dict(self, general_stats):
        with open(self.general_stats_filepath, 'w+') as file:
            json.dump(general_stats, file)
