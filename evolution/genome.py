import random
import time
from sc2.ids.unit_typeid import UnitTypeId as unit


class Genome:
    def __init__(self, build_order=None, units_ratio=None):
        self.build_order = [] if build_order is None else build_order
        self.units_ratio = {unit.ZEALOT: None, unit.ADEPT: None, unit.STALKER: None, unit.IMMORTAL: None,
                            unit.ARCHON: None, unit.SENTRY: None} if units_ratio is None else units_ratio

    def __str__(self):
        return 'build_order={} units_ratio={}'.format(self.build_order, self.units_ratio)

    @staticmethod
    def create_random_genome():
        def generate_build_order():
            order_queue = []
            gates = random.randint(3, 12)
            cybernetics = 1# random.randint(0, 1)
            forge = random.randint(0, 3)
            nexus = random.randint(0, 5)
            robotics = random.randint(0, 3)
            twilight = random.randint(0, 3)
            templar_archives = random.randint(0, 3)
            army_priority_checkpoints_nb = 4

            for i in range(gates):
                order_queue.append(unit.GATEWAY)
            for i in range(forge):
                order_queue.append(unit.FORGE)
            for i in range(cybernetics):
                order_queue.append(unit.CYBERNETICSCORE)
            for i in range(nexus):
                order_queue.append(unit.NEXUS)
            for i in range(robotics):
                order_queue.append(unit.ROBOTICSFACILITY)
            for i in range(twilight):
                order_queue.append(unit.TWILIGHTCOUNCIL)
            for i in range(templar_archives):
                order_queue.append(unit.TEMPLARARCHIVE)
            random.shuffle(order_queue)
            army_priority_checkpoints = []
            indexes = []
            for i in range(army_priority_checkpoints_nb):
                army_priority_checkpoints.append(random.randint(2, 24))
                indexes.append(random.randint(2,len(order_queue)-1))

            army_priority_checkpoints = sorted(army_priority_checkpoints)
            indexes = sorted(indexes)
            for i in range(len(indexes)):
                order_queue.insert(indexes[i], army_priority_checkpoints[i])
            return order_queue

        buildings = generate_build_order()

        while not Genome.is_correct_order(buildings):
            buildings = generate_build_order()

        buildings = Genome.filter_double_tech_buildings(buildings)

        zealots = random.uniform(1, 30)
        adepts = random.uniform(0, 80)
        stalkers = random.uniform(5, 80)
        immortals = random.uniform(5, 23)
        archons = random.uniform(5, 23)
        sentry = random.uniform(0, 5)
        units_ratio = {unit.ZEALOT: zealots, unit.ADEPT: adepts, unit.STALKER: stalkers,
                       unit.IMMORTAL: immortals, unit.ARCHON: archons, unit.SENTRY: sentry}

        return Genome(build_order=buildings, units_ratio=units_ratio)

    @staticmethod
    def filter_double_tech_buildings(build_order: list):
        Genome.filter_double_buildings(build_order, structure=unit.CYBERNETICSCORE)
        Genome.filter_double_buildings(build_order, structure=unit.TWILIGHTCOUNCIL)
        Genome.filter_double_buildings(build_order, structure=unit.TEMPLARARCHIVE)
        return build_order


    @staticmethod
    def filter_double_buildings(build_order, structure):
        if structure in build_order:
            n=0
            i=0
            idx=0
            for building in build_order:
                if building == structure:
                    n+=1
                idx=i
                i+=1
            if n > 1:
                build_order.pop(idx)

    @staticmethod
    def is_correct_order(build_order: list):
        for i in range(2):
            if isinstance(build_order[i], int):
                return False
        for i in range(len(build_order)-1):
            if isinstance(build_order[i], int) and isinstance(build_order[i+1], int):
                return False

        if unit.CYBERNETICSCORE in build_order:
            n=0
            i=0
            idx=0
            for building in build_order:
                if building == unit.CYBERNETICSCORE:
                    n+=1
                idx=i
                i+=1
            if n > 1:
                build_order.pop(idx)
            if build_order.index(unit.CYBERNETICSCORE) < build_order.index(unit.GATEWAY):
                return False
        if unit.FORGE in build_order:
            if build_order.index(unit.FORGE) < build_order.index(unit.GATEWAY):
                return False
        if unit.TEMPLARARCHIVE in build_order:
            n = 0
            i = 0
            idx = 0
            for building in build_order:
                if building == unit.TEMPLARARCHIVE:
                    n += 1
                idx = i
                i += 1
            if n > 1:
                build_order.pop(idx)
            if unit.TWILIGHTCOUNCIL not in build_order or\
                build_order.index(unit.TEMPLARARCHIVE) < build_order.index(unit.TWILIGHTCOUNCIL):
                return False
        if unit.TWILIGHTCOUNCIL in build_order:
            n = 0
            i = 0
            idx = 0
            for building in build_order:
                if building == unit.TWILIGHTCOUNCIL:
                    n += 1
                idx = i
                i += 1
            if n > 1:
                build_order.pop(idx)
            if unit.CYBERNETICSCORE not in build_order or\
                build_order.index(unit.TWILIGHTCOUNCIL) < build_order.index(unit.CYBERNETICSCORE):
                return False
        if unit.ROBOTICSFACILITY in build_order:
            if unit.CYBERNETICSCORE not in build_order or\
                build_order.index(unit.ROBOTICSFACILITY) < build_order.index(unit.CYBERNETICSCORE):
                return False
        return True

    def save_genome(self, directory='genomes'):
        import uuid
        import json
        import os
        random_name = str(uuid.uuid4())
        # print('saving genome: {}' .format(random_name))
        if not os.path.isdir(directory):
            os.mkdir(directory)
        with open(os.path.join(directory, random_name + '_units.json'), 'w+') as file:
            str_dict = {}
            for key in self.units_ratio:
                str_dict[str(key)] = self.units_ratio[key]
            json.dump(str_dict, file)

        with open(os.path.join(directory, random_name + '_build.json'), 'w+') as file:
            json.dump([str(x) for x in self.build_order], file)

    def load_genome(self, genome_path):
        import json

        with open(genome_path + '_build.json') as file:
            build_order = json.load(file)

        with open(genome_path + '_units.json') as file:
            units = json.load(file)

        buildings = [unit.NEXUS, unit.GATEWAY, unit.CYBERNETICSCORE, unit.TWILIGHTCOUNCIL, unit.ROBOTICSFACILITY,
                     unit.TEMPLARARCHIVE, unit.FORGE]
        buildings_dict = {}
        for building in buildings:
            buildings_dict[str(building)] = building
        build_order_units = []
        for b in build_order:
            if b in buildings_dict:
                build_order_units.append(buildings_dict[b])
            else:
                build_order_units.append(int(b))
        self.build_order = build_order_units
        units_unit_type = {}
        units_dict = {}
        units_unit = [unit.ZEALOT, unit.STALKER, unit.ADEPT, unit.ARCHON, unit.IMMORTAL, unit.SENTRY]
        for unit_unit in units_unit:
            units_dict[str(unit_unit)] = unit_unit

        for u in units:
            units_unit_type[units_dict[u]] = units[u]
        self.units_ratio = units_unit_type