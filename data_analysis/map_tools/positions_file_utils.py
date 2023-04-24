import sys
import os


class PositionsFileUtils:
    def __init__(self, ai):
        self.ai = ai

    @property
    def directory(self):
        directory = os.path.realpath(sys.argv[0]) if sys.argv[0] else ''
        if directory:
            directory = os.path.dirname(os.path.abspath(directory))
        if 'data_analysis' in directory:
            return os.path.join(directory, 'saved_positions')
        return os.path.join(directory, 'data_analysis', 'map_tools', 'saved_positions')

    def get_filename(self, locations_name):
        map_name = self.ai.game_info.map_name
        return os.path.join(self.directory, '{}_{}.json'.format(map_name, locations_name))

    @property
    def start_location(self):
        return str((self.ai.start_location.x, self.ai.start_location.y))
