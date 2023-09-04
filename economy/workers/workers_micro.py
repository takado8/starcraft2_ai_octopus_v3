from sc2.ids.unit_typeid import UnitTypeId as unit


class WorkersMicro:
    def __init__(self, ai):
        self.ai = ai

    def execute(self):
        workers = self.ai.workers
        enemy = self.ai.enemy_units()
        enemy.extend(self.ai.enemy_structures(unit.BUNKER))
        if enemy:
            for worker in workers:
                if worker.shield_percentage < 1:
                    if self.ai.townhalls.amount == 1:
                        worker.move(enemy.closest_to(worker, -6))
                    else:
                        safe_townhall = self.ai.townhalls.filter(lambda x: not enemy.closer_than(12, x).exists)
                        worker.move(safe_townhall.closest_to(worker))
