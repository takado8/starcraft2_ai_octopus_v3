from sc2.unit import UnitTypeId as unit
from typing import Dict, List


class DistributeWorkers:
    def __init__(self, ai):
        self.ai = ai
        self.all_workers: Dict[int, int] = {} # [worker.tag, target.tag]
        self.minerals_dict: Dict[int, List[int]] = {} # [mineral.tag, [worker.tag, ...]]
        self.gas_dict: Dict[int, List[int]] = {} # [gas.tag, [worker.tag, ...]]

    def distribute_workers(self, minerals_to_gas_ratio=2):
        self.refresh_mining_places_dicts()
        self.remove_dead_bases()
        self.assign_workers(minerals_to_gas_ratio)
        self.distribute_idle_workers()

    def refresh_mining_places_dicts(self):
        for base in self.ai.townhalls.ready:
            minerals = self.ai.mineral_field.closer_than(12, base)
            for mineral in minerals:
                if mineral.tag not in self.minerals_dict:
                    self.minerals_dict[mineral.tag] = []

            gas = self.ai.structures(unit.ASSIMILATOR).ready
            if gas.exists:
                gas = gas.closer_than(14, base)
                for g in gas:
                    if g.tag not in self.gas_dict:
                        self.gas_dict[g.tag] = []

    def distribute_idle_workers(self):
        for worker in self.ai.units(unit.PROBE).filter(lambda x: x.is_gathering or x.is_idle):
            if worker.tag in self.all_workers:
                target_tag = self.all_workers[worker.tag]
                target = None
                if target_tag in self.gas_dict:
                    try:
                        target = self.ai.structures(unit.ASSIMILATOR).by_tag(target_tag)
                    except KeyError:
                        self.remove_dead_gas(target_tag)
                elif target_tag in self.minerals_dict:
                    try:
                        target = self.ai.mineral_field.by_tag(target_tag)
                    except KeyError:
                        self.remove_dead_mineral(target_tag)
                if target:
                    if worker.is_carrying_minerals or worker.is_carrying_vespene:
                        worker.smart(self.ai.structures(unit.NEXUS).ready.closest_to(worker))
                        worker.gather(target, queue=True)
                    else:
                        worker.gather(target)

    def assign_workers(self, minerals_to_gas_ratio=2):
        prefer_minerals = self.ai.minerals / (self.ai.vespene + 1) < minerals_to_gas_ratio
        workers = self.ai.workers.filter(lambda worker: worker.tag not in self.all_workers and worker.is_ready)
        if prefer_minerals:
            self.assign_mineral_mining(workers)
            if workers:
                self.assign_gas_mining(workers)
        else:
            self.assign_gas_mining(workers)
            if workers:
                self.assign_mineral_mining(workers)

    def assign_mineral_mining(self, workers):
        mineral_tags_to_remove = []
        for j in range(1, 3):
            for mineral_tag in self.minerals_dict:
                while len(self.minerals_dict[mineral_tag]) < j and workers:
                    try:
                        mineral = self.ai.mineral_field.by_tag(mineral_tag)
                        closest_worker = workers.closest_to(mineral)
                        self.minerals_dict[mineral_tag].append(closest_worker.tag)
                        workers.remove(closest_worker)
                        closest_worker.gather(mineral)
                        self.all_workers[closest_worker.tag] = mineral_tag
                    except KeyError:
                        mineral_tags_to_remove.append(mineral_tag)

        for mineral_tag in mineral_tags_to_remove:
            self.remove_dead_mineral(mineral_tag)

    def assign_gas_mining(self, workers):
        for j in range(1,4):
            for gas_tag in self.gas_dict:
                while len(self.gas_dict[gas_tag]) < j and workers:
                    gas = self.ai.structures(unit.ASSIMILATOR).by_tag(gas_tag)
                    closest_worker = workers.closest_to(gas)
                    self.gas_dict[gas_tag].append(closest_worker.tag)
                    workers.remove(closest_worker)
                    closest_worker.gather(gas)
                    self.all_workers[closest_worker.tag] = gas_tag

    def on_unit_destroyed(self, tag):
        try:
            worker_tag = self.all_workers[tag]
        except KeyError:
            return
        if worker_tag in self.minerals_dict:
            self.minerals_dict[worker_tag].remove(tag)
        elif worker_tag in self.gas_dict:
            self.gas_dict[worker_tag].remove(tag)

    def remove_dead_bases(self):
        minerals_to_remove = []
        for mineral_tag in self.minerals_dict:
            try:
                mineral = self.ai.mineral_field.by_tag(mineral_tag)
                if not self.ai.townhalls.ready.closer_than(12, mineral).exists:
                    minerals_to_remove.append(mineral_tag)
            except KeyError:
                minerals_to_remove.append(mineral_tag)

        for mineral_tag in minerals_to_remove:
            self.remove_dead_mineral(mineral_tag)

        gas_to_remove = []
        for gas_tag in self.gas_dict:
            try:
                gas = self.ai.structures().by_tag(gas_tag)
                if not self.ai.townhalls.ready.closer_than(12, gas).exists:
                    gas_to_remove.append(gas_tag)
            except KeyError:
                gas_to_remove.append(gas_tag)

        for gas_tag in gas_to_remove:
            self.remove_dead_gas(gas_tag)

    def remove_dead_gas(self, gas_tag):
        local_workers = self.gas_dict.pop(gas_tag)
        for local_worker in local_workers:
            self.all_workers.pop(local_worker)

    def remove_dead_mineral(self, mineral_tag):
        local_workers = self.minerals_dict.pop(mineral_tag)
        for worker_tag in local_workers:
            self.all_workers.pop(worker_tag)

    def get_mineral_workers_tags(self):
        mineral_workers_tags = set()
        for mineral_tag in self.minerals_dict:
            for worker_tag in self.minerals_dict[mineral_tag]:
                mineral_workers_tags.add(worker_tag)

        return mineral_workers_tags