from evolution.subject import Subject
from evolution.genome import Genome
from sc2.ids.unit_typeid import UnitTypeId as unit
import random
import os

MUTATION_RATE = 0.1
TECH_STRUCTURES = [unit.CYBERNETICSCORE, unit.TWILIGHTCOUNCIL, unit.TEMPLARARCHIVE]


class Evolution:
    def __init__(self, population_count=100, reproduction_rate=0.8, load_population_directory=None):
        self.population_count = population_count
        self.population = []
        self.reproduction_rate = reproduction_rate
        self.generate_random_population()
        if load_population_directory:
            if os.path.isdir(load_population_directory):
                files = os.listdir(load_population_directory)
                files_set = set([x[:-11] for x in files])
                if len(self.population) < len(files_set):
                    self.population_count = len(files_set)
                    self.generate_random_population()
                i=0
                for file_name in files_set:
                    self.population[i].genome.load_genome(os.path.join(load_population_directory,
                                                                       file_name))
                    i+=1



    def evolve(self):
        print('start population count: {}'.format(len(self.population)))
        new_generation = self.reproduce()
        print('new generation count: {}'.format(len(new_generation)))
        self.delete_subjects()
        print('population count after deletion: {}'.format(len(self.population)))
        self.population.extend(new_generation)
        print('population count after merge: {}'.format(len(self.population)))

    def reproduce(self):
        reproduction_pool = self.select_to_reproduction()
        new_subjects = []
        while len(new_subjects) < len(reproduction_pool):
            parents = random.sample(reproduction_pool, 2)
            new_subject = self.cross_over(parents)
            k=0
            while not Genome.is_correct_order(new_subject.genome.build_order) and k < 60000:
                k+=1
                new_subject = self.cross_over(parents)
            new_subject.genome.build_order = Genome.filter_double_tech_buildings(new_subject.genome.build_order)
            new_subjects.append(new_subject)
        return new_subjects

    @staticmethod
    def cross_over(parents):
        def mutate(gene):
            if random.uniform(0, 1) < MUTATION_RATE:
                gene = gene - (2 if gene > 1 and random.uniform(0, 1) < 0.5 else -2)
            return gene

        def mutate_build_order(build_order: list):
            if random.uniform(0, 1) < MUTATION_RATE * 5:
                i = random.randint(0, len(build_order)-1)
                r = random.uniform(0,1)
                if r < 0.33 and len(build_order) - 1 > i:
                    temp = build_order[i+1]
                    build_order[i+1] = build_order[i]
                    build_order[i] = temp
                elif r > 0.66:
                    if build_order[i] != unit.CYBERNETICSCORE:
                        build_order.pop(i)
                else:
                    if build_order[i] not in TECH_STRUCTURES:
                        build_order.append(build_order[i])
            return build_order
        new_subject = Subject()
        new_subject.genome = Genome.create_random_genome()
        new_subject.genome.build_order.clear()
        new_subject.genome.units_ratio.clear()
        longer = parents[0] if len(parents[0].genome.build_order) > len(parents[1].genome.build_order)\
            else parents[1]
        shorter = parents[0] if longer == parents[1] else parents[1]

        for i in range(len(longer.genome.build_order)):
            if random.uniform(0,1) < 0.5:
                gene = longer.genome.build_order[i]
                if gene in TECH_STRUCTURES and gene in new_subject.genome.build_order:
                    continue
                new_subject.genome.build_order.append(gene)
            elif i < len(shorter.genome.build_order):
                gene = shorter.genome.build_order[i]
                if gene in TECH_STRUCTURES and gene in new_subject.genome.build_order:
                    continue
                new_subject.genome.build_order.append(gene)

        for unit_ratio in parents[0].genome.units_ratio:
            if random.uniform(0, 1) < 0.5:
                new_subject.genome.units_ratio[unit_ratio] = mutate(parents[0].genome.units_ratio[unit_ratio])
            else:
                new_subject.genome.units_ratio[unit_ratio] = mutate(parents[1].genome.units_ratio[unit_ratio])

        new_subject.genome.build_order = mutate_build_order(new_subject.genome.build_order)
        return new_subject

    def select_to_reproduction(self):
        selected = []
        n = int(len(self.population) * self.reproduction_rate)
        while len(selected) < n:
            subjects = random.sample(self.population, 2)
            selected.append(subjects[0] if subjects[0].fitness > subjects[1].fitness else subjects[1])
        return selected

    def delete_subjects(self):
        selected = []
        n = int(len(self.population) * (1 - self.reproduction_rate))
        while len(selected) < n:
            subjects = random.sample(self.population, 2)
            selected.append(subjects[0] if subjects[0].fitness > subjects[1].fitness else subjects[1])
        self.population = selected

    def generate_random_population(self):
        while len(self.population) < self.population_count:
            s = Subject()
            s.genome = Genome.create_random_genome()
            self.population.append(s)




if __name__ == '__main__':
    from sc2.ids.unit_typeid import UnitTypeId as unit
    evo = Evolution(population_count=16, reproduction_rate=0.75)
    target = 17
    generations_nb = 10
    for i in range(generations_nb):
        evo.evolve()
        for subject in evo.population:
            # print(subject.genome)
            total = subject.genome.units_ratio[unit.STALKER]
            fitness = 100 - abs(target - total)
            if fitness <= 0:
                fitness = 1
            subject.fitness = fitness
        print('i: {} avg fit: {} best fit: {}'.format(i, round(
            sum([s.fitness for s in evo.population]) / len(evo.population), 4),
                                                      round(max([s.fitness for s in evo.population]), 4)))

    for s in evo.population:
        print(s.genome)
        print('fit: {}'.format( s.fitness))
        s.genome.save_genome()

