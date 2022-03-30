import random
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
            buildings = []
            gates = random.randint(3, 10)
            cybernetics = 1# random.randint(0, 1)
            forge = random.randint(0, 1)
            nexus = random.randint(0, 3)
            robotics = random.randint(0, 2)
            twilight = random.randint(0, 1)
            templar_archives = random.randint(0, 1)
            for i in range(gates):
                buildings.append(unit.GATEWAY)
            for i in range(forge):
                buildings.append(unit.FORGE)
            for i in range(cybernetics):
                buildings.append(unit.CYBERNETICSCORE)
            for i in range(nexus):
                buildings.append(unit.NEXUS)
            for i in range(robotics):
                buildings.append(unit.ROBOTICSFACILITY)
            for i in range(twilight):
                buildings.append(unit.TWILIGHTCOUNCIL)
            for i in range(templar_archives):
                buildings.append(unit.TEMPLARARCHIVE)
            random.shuffle(buildings)
            return buildings

        buildings = generate_build_order()

        while not Genome.is_correct_order(buildings):
            buildings = generate_build_order()

        buildings = Genome.filter_double_tech_buildings(buildings)

        zealots = random.uniform(1, 20)
        adepts = random.uniform(0, 40)
        stalkers = random.uniform(5, 40)
        immortals = random.uniform(5, 16)
        archons = random.uniform(5, 16)
        sentry = random.uniform(0, 3)
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
        with open(os.path.join(directory, random_name + '_units'), 'w+') as file:
            json.dump(str(self.units_ratio), file)

        with open(os.path.join(directory, random_name + '_build'), 'w+') as file:
            json.dump(str(self.build_order), file)