import random
from sc2.ids.unit_typeid import UnitTypeId as unit


class Genome:
    def __init__(self, build_order=None, units_ratio=None):
        self.build_order = [] if build_order is None else build_order
        self.units_ratio = {'zealot': None, 'adept': None, 'stalker': None, 'immortal': None, 'archon': None,
                            'sentry': None} if \
            units_ratio is None else units_ratio

    @staticmethod
    def create_random_genome():
        buildings = []
        gates = random.randint(1, 10)
        cybernetics = random.randint(0, 1)
        forge = random.randint(0, 1)
        nexus = random.randint(0, 5)
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
            buildings.append(unit.ROBOTICSBAY)
        for i in range(twilight):
            buildings.append(unit.TWILIGHTCOUNCIL)
        for i in range(templar_archives):
            buildings.append(unit.TEMPLARARCHIVE)

        random.shuffle(buildings)

        zealots = random.uniform(0, 12)
        adepts = random.uniform(0, 20)
        stalkers = random.uniform(0, 20)
        immortals = random.uniform(0, 12)
        archons = random.uniform(0, 12)
        sentry = random.uniform(0,3)
        units_ratio = {'zealot': zealots, 'adept': adepts, 'stalker': stalkers,
                       'immortal': immortals, 'archon': archons, 'sentry': sentry}

        return Genome(build_order=buildings, units_ratio=units_ratio)