from evolution.subject import Subject
import random

GENOME_LEN = 3
MUTATION_RATE = 0.05


class Evolution:
    def __init__(self, population_count=100, reproduction_rate=0.6):
        self.population_count = population_count
        self.population = []
        self.reproduction_rate = reproduction_rate
        self.generate_random_population()

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
            new_subjects.append(new_subject)
        return new_subjects

    @staticmethod
    def cross_over(parents):
        def mutate(gene):
            if random.uniform(0, 1) < MUTATION_RATE:
                gene = gene - (1 if gene > 0 and random.uniform(0, 1) < 0.5 else -1)
            return gene

        new_subject = Subject()
        new_genome = []
        for i in range(len(parents[0].genome)):
            chromosome0 = parents[0].genome[i]
            chromosome1 = parents[1].genome[i]
            new_chromosome = []
            for j in range(len(chromosome0)):
                new_chromosome.append(mutate(chromosome0[j] if random.uniform(0, 1) > 0.5 else chromosome1[j]))
            new_genome.append(new_chromosome)
        new_subject.genome = new_genome
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
        n = int(len(self.population) * self.reproduction_rate)
        while len(selected) < n:
            subjects = random.sample(self.population, 2)
            selected.append(subjects[0] if subjects[0].fitness > subjects[1].fitness else subjects[1])
        self.population = selected

    def generate_random_population(self):
        while len(self.population) < self.population_count:
            s = Subject()
            s.genome = self.generate_random_genome(GENOME_LEN)
            self.population.append(s)

    @staticmethod
    def generate_random_genome(length):
        genome = []
        while len(genome) < length:
            gates_count = random.randint(0, 7)
            stalkers_count = random.randint(0, 80)
            zealots_count = random.randint(0, 80)
            attack = random.randint(0, 1)
            chromosome = [gates_count, stalkers_count, zealots_count, attack]
            genome.append(chromosome)
        return genome


if __name__ == '__main__':
    evo = Evolution(population_count=10, reproduction_rate=0.6)
    target = 23
    generations_nb = 500
    for i in range(generations_nb):
        evo.evolve()
        for subject in evo.population:
            total = sum(subject.genome[0])
            fitness = 100 - abs(target - total)
            if fitness <= 0:
                fitness = 1
            subject.fitness = fitness
        print('i: {} avg fit: {} best fit: {}'.format(i, round(
            sum([s.fitness for s in evo.population]) / len(evo.population), 4),
                                                      round(max([s.fitness for s in evo.population]), 4)))

    for s in evo.population:
        print(s.genome)
        print('sum: {} fit: {}'.format(sum(s.genome[0]), s.fitness))
