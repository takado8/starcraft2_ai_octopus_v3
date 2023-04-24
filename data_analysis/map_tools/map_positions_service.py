import json
from sc2.unit import UnitTypeId as unit

from bot.constants import BASES_IDS
from data_analysis.map_tools.positions_file_utils import PositionsFileUtils
from data_analysis.map_tools.positions_loader import PositionsLoader


class MapPositionsService(PositionsFileUtils):
    def __init__(self, ai, positions_name):
        super().__init__(ai)
        self.added_positions = set()
        self.positions_name = positions_name
        positions_loader = PositionsLoader(ai)
        self.positions_dict = positions_loader.load_positions_dict(positions_name,
                                                                   load_opposite_start_location=True)
        for start_location in self.positions_dict:
            for unit_id in self.positions_dict[start_location]:
                for position in self.positions_dict[start_location][unit_id]:
                    self.added_positions.add(position)

    def get_structures_positions(self):
        start_location = self.start_location
        if start_location not in self.positions_dict:
            self.positions_dict[start_location] = {}
        for structure in self.ai.structures().filter(lambda x: x.type_id not in BASES_IDS and
                                                     x.type_id != unit.ASSIMILATOR):
            if structure.position not in self.added_positions:
                self.added_positions.add(structure.position)
                type_id = structure.type_id
                if type_id not in self.positions_dict[start_location]:
                    self.positions_dict[start_location][type_id] = [structure.position]
                else:
                    self.positions_dict[start_location][type_id].append(structure.position)

    def get_units_position(self):
        start_location = self.start_location
        if start_location not in self.positions_dict:
            self.positions_dict[start_location] = {}
        for unit_ in self.ai.units().filter(lambda x: x.type_id == unit.ZEALOT):
            if unit_.position not in self.added_positions:
                self.added_positions.add(unit_.position)
                type_id = unit_.type_id
                if type_id not in self.positions_dict[start_location]:
                    self.positions_dict[start_location][type_id] = [unit_.position]
                else:
                    self.positions_dict[start_location][type_id].append(unit_.position)

    def save_positions_json(self):
        self.get_structures_positions()
        self.get_units_position()
        filename = self.get_filename(self.positions_name)
        positions_dict_to_save = {}
        for start_location in self.positions_dict:
            positions_dict_to_save[start_location] = {}
            for unit_id in self.positions_dict[start_location]:
                positions_dict_to_save[start_location][unit_id.value] =\
                    [(round(position.x,2), round(position.y,2)) for position in self.positions_dict[start_location][unit_id]]

        with open(filename, 'w+') as file:
            json.dump(positions_dict_to_save, file)
