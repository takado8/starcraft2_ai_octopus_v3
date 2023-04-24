import os
import json
from sc2.position import Point2
from sc2.unit import UnitTypeId as unit
from data_analysis.map_tools.positions_file_utils import PositionsFileUtils


class PositionsLoader(PositionsFileUtils):
    def __init__(self, ai):
        super().__init__(ai)

    def load_positions_dict(self, positions_name, load_opposite_start_location=False):
        filename = self.get_filename(positions_name)
        if os.path.isfile(filename):
            with open(filename) as file:
                positions_dict = json.load(file)

            result_positions_dict = {}
            for start_location in positions_dict:
                if not load_opposite_start_location and start_location != self.start_location:
                    continue
                result_positions_dict[start_location] = {}
                for id in positions_dict[start_location]:
                    result_positions_dict[start_location][unit(int(id))] = [Point2(position) for position in
                                                                            positions_dict[start_location][id]]

            if self.start_location not in result_positions_dict:

                print('No locations for start location {} at map {}'.format(self.start_location,
                                                                            self.ai.game_info.map_name))
        else:
            print('No locations file for map {} at {}'.format(self.ai.game_info.map_name,
                                                              filename))
            return {}
        result = result_positions_dict if load_opposite_start_location else result_positions_dict[self.start_location]
        print('loading locations file done:')
        print(result)
        return result
