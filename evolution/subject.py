from evolution.genome import Genome


class Subject:
    def __init__(self, genome: Genome=None):
        self.genome: Genome = genome
        self.fitness = -1
