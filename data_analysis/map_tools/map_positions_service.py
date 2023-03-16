import os
import sys
import json
from sc2.unit import UnitTypeId as unit
from sc2.position import Point2


class MapPositionsService:
    def __init__(self, ai):
        self.ai = ai
        self.positions_dict = {}

        directory = os.path.realpath(sys.argv[0]) if sys.argv[0] else ''
        if directory:
            directory = os.path.dirname(os.path.abspath(directory))
        self.saved_positions_dir = os.path.join(directory, 'data_analysis', 'map_tools', 'saved_positions')

    def get_positions(self, start_location):
        for structure in self.ai.structures().filter(lambda x: x.type_id not in self.ai.bases_ids and
                                                     x.type_id != unit.ASSIMILATOR):
            type_id_int = structure.type_id.value
            if type_id_int not in self.positions_dict[start_location]:
                self.positions_dict[start_location][type_id_int] = [structure.position_tuple]
            else:
                self.positions_dict[start_location][type_id_int].append(structure.position_tuple)

    def save_positions_json(self, locations_name):
        self._load_positions_to_edit(locations_name)
        start_location = self._get_start_location()
        self.positions_dict[start_location] = {}
        self.get_positions(start_location)
        filename = self._get_filename(locations_name)
        with open(filename, 'w+') as file:
            json.dump(self.positions_dict, file)

    def _load_positions_to_edit(self, locations_name):
        filename = self._get_filename(locations_name)
        if os.path.isfile(filename):
            with open(filename) as file:
                positions_dict = json.load(file)

            for start_location in positions_dict:
                self.positions_dict[start_location] = {}

                for id in positions_dict[start_location]:
                    self.positions_dict[start_location][id] = [Point2(position) for position in positions_dict[start_location][id]]

    def load_positions_dict(self, locations_name):
        print('loading locations for map...')
        filename = self._get_filename(locations_name)
        if os.path.isfile(filename):
            with open(filename) as file:
                positions_dict = json.load(file)

            start_location = self._get_start_location()
            if start_location in positions_dict:
                self.positions_dict[start_location] = {}
                for id in positions_dict[start_location]:
                    self.positions_dict[start_location][unit(int(id))] = [Point2(position) for position in
                                                               positions_dict[start_location][id]]
            else:
                print('No locations for start location {} at map {}'.format(start_location,
                                                                                 self.ai.game_info.map_name))
                return False
        else:
            print('No locations file for map {} at {}'.format(self.ai.game_info.map_name,
                                                              filename))
            return False
        print('Done')
        print(self.positions_dict[start_location])
        return self.positions_dict[start_location]

    def _get_filename(self, locations_name):
        map_name = self.ai.game_info.map_name
        return os.path.join(self.saved_positions_dir, '{}_{}.json'.format(map_name, locations_name))

    def _get_start_location(self):
        return str((self.ai.start_location.x, self.ai.start_location.y))
