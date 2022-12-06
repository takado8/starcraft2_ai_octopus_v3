# from sc2.units import Units
from sc2.unit import UnitTypeId as unit
from sc2.position import Point2
from typing import Dict, Set, List


class DistributeWorkers:
    def __init__(self, ai):
        self.ai = ai
        self.all_workers: Dict[int, int] = {} # [worker.tag, target.tag]
        self.minerals_dict: Dict[int, List[int]] = {} # [mineral.tag, [workers.tags, ...]]
        self.gas_dict: Dict[int, List[int]] = {} # [gas.tag, [workers.tags, ...]]

    def distribute_workers_new(self):
        self.refresh_mining_places_dicts()
        self.remove_dead_bases()
        self.assign_workers()
        self.distribute_idle_workers()
        # print("all:")
        # print(self.all_workers)
        # print("minerals:")
        # print(self.minerals_dict)
        # print("gas:")
        # print(self.gas_dict)
        # print("-------------------------------------------------------")

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
            # try:
            self.all_workers.pop(local_worker)
            # except:
            #     pass
            #
    def remove_dead_mineral(self, mineral_tag):
        local_workers = self.minerals_dict.pop(mineral_tag)
        for worker_tag in local_workers:
            # try:
            self.all_workers.pop(worker_tag)
            # except KeyError:
            #     pass

    def assign_workers(self):
        workers = self.ai.workers.filter(lambda worker: worker.tag not in self.all_workers and worker.is_ready)
        mineral_tags_to_remove = []
        for j in range(1,3):
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

        for j in range(1,4):
            for gas_tag in self.gas_dict:
                while len(self.gas_dict[gas_tag]) < j and workers:
                    gas = self.ai.structures(unit.ASSIMILATOR).by_tag(gas_tag)
                    closest_worker = workers.closest_to(gas)
                    self.gas_dict[gas_tag].append(closest_worker.tag)
                    workers.remove(closest_worker)
                    closest_worker.gather(gas)
                    self.all_workers[closest_worker.tag] = gas_tag

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



    def distribute_workers(self, minerals_to_gas_ratio=2):
        bases = self.ai.townhalls.ready

        if not self.ai.mineral_field or not self.ai.workers or not bases:
            return
        workers_idle = self.ai.workers.idle
        gas_buildings = self.ai.gas_buildings.ready
        # surplus_workers = {}
        bases_with_deficit = {}
        gas_buildings_with_deficit = {}
        for base in bases:
            local_minerals_tags = {mineral.tag for mineral in self.ai.mineral_field
                                   if mineral.distance_to(base) <= 12}
            local_workers = self.ai.workers.filter(
                lambda unit: unit.order_target in local_minerals_tags
                             or (unit.is_carrying_minerals and unit.order_target == base.tag) or
                             (unit.distance_to(base) < 12 and unit.is_moving and not isinstance(unit.order_target, int)
                              and not unit.is_carrying_vespene))
            surplus_harvesters = local_workers.amount - base.ideal_harvesters
            if surplus_harvesters == 0:
                continue
            elif surplus_harvesters > 0:
                workers_idle.extend(local_workers[:surplus_harvesters])
            else:
                bases_with_deficit[base] = -surplus_harvesters

        for gas_building in gas_buildings:
            surplus_harvesters = gas_building.surplus_harvesters

            if surplus_harvesters == 0:
                continue
            elif surplus_harvesters > 0:
                closest_base = bases.closest_to(gas_building)
                local_workers = self.ai.workers.filter(
                    lambda unit: unit.order_target == gas_building.tag
                                 or (unit.is_carrying_vespene and unit.order_target == closest_base.tag))

                workers_idle.extend(local_workers[:surplus_harvesters])
            else:
                gas_buildings_with_deficit[gas_building] = -surplus_harvesters
        prefer_minerals = self.ai.minerals / (self.ai.vespene + 1) < minerals_to_gas_ratio
        if prefer_minerals:
            for worker in workers_idle:
                if len(bases_with_deficit) > 0:
                    self.assign_minerals_mining(bases_with_deficit, worker)
                elif len(gas_buildings_with_deficit) > 0:
                    self.assign_gas_mining(gas_buildings_with_deficit, worker)
            #
            # if len(bases_with_deficit) > 0:
            #     for base in bases_with_deficit:
            #         close_gas_buildings = self.ai.gas_buildings.ready.closest_n_units(base, 2)
            #         close_gas_buildings_tags = {b.tag for b in close_gas_buildings}
            #         local_workers = self.ai.workers.filter(
            #             lambda unit: unit.order_target in close_gas_buildings_tags
            #                          or (unit.is_carrying_vespene and unit.order_target == base.tag))
            #         if not local_workers:
            #             continue
            #         for _ in range(bases_with_deficit[base]):
            #             worker = local_workers.closest_to(base)
            #             if worker.is_carrying_vespene:
            #                 worker.smart(base)
            #                 worker.gather(self.ai.mineral_field.closest_to(worker), queue=True)
            #             else:
            #                 worker.gather(self.ai.mineral_field.closest_to(worker))
        else:
            for worker in workers_idle:
                if len(gas_buildings_with_deficit) > 0:
                    self.assign_gas_mining(gas_buildings_with_deficit, worker)
                elif len(bases_with_deficit) > 0:
                    self.assign_minerals_mining(bases_with_deficit, worker)
            # if len(gas_buildings_with_deficit) > 0:
            #     for gas_building in gas_buildings_with_deficit:
            #         closest_base = bases.closest_to(gas_building)
            #         local_minerals_tags = {mineral.tag for mineral in self.ai.mineral_field
            #                                if mineral.distance_to(closest_base) <= 12}
            #         local_workers = self.ai.workers.filter(
            #             lambda unit: unit.order_target in local_minerals_tags
            #                          or (unit.is_carrying_minerals and unit.order_target == closest_base.tag))
            #         if not local_workers:
            #             continue
            #         for _ in range(gas_buildings_with_deficit[gas_building]):
            #             worker = local_workers.closest_to(gas_building)
            #             if worker.is_carrying_minerals:
            #                 worker.smart(closest_base)
            #                 worker.gather(gas_building, queue=True)
            #             else:
            #                 worker.gather(gas_building)
            # else:
            #     self.assign_minerals_mining({self.ai.structures(unit.NEXUS).ready.closest_to(worker): 10},
            #                                 worker)
        # for base in bases_with_deficit:
        #     if len(surplus_workers) > 0:
        #         while bases_with_deficit[base] >= 0:
        #             closest_workers_position = min(surplus_workers, key=lambda position: position.distance_to(base))
        #             while surplus_workers[closest_workers_position].amount >= 0:

    def assign_minerals_mining(self, bases_with_deficit, worker):
        closest_base = min(bases_with_deficit, key=lambda place: place.distance_to(worker))

        local_minerals = self.ai.mineral_field.filter(lambda mineral: mineral.distance_to(closest_base) <= 12)
        # local_minerals can be empty if townhall is misplaced
        # target_mineral = max(local_minerals, key=lambda mineral: mineral.mineral_contents, default=None)
        target_mineral = local_minerals.closest_to(worker)
        if target_mineral:
            worker.gather(target_mineral)
            bases_with_deficit[closest_base] -= 1
            if bases_with_deficit[closest_base] <= 0:
                bases_with_deficit.pop(closest_base)

    def assign_gas_mining(self, gas_buildings_with_deficit, worker):
        closest_place = min(gas_buildings_with_deficit, key=lambda place: place.distance_to(worker))
        nexuses = self.ai.structures(unit.NEXUS).ready
        if nexuses.exists and nexuses.closer_than(12, closest_place).exists:
            worker.gather(closest_place)
            gas_buildings_with_deficit[closest_place] -= 1
            if gas_buildings_with_deficit[closest_place] <= 0:
                gas_buildings_with_deficit.pop(closest_place)

    def distribute_workers_on_first_step(self):
        mineral_fields = self.ai.mineral_field.closer_than(12, self.ai.start_location.position)
        fields_workers_dict = {}
        for worker in self.ai.workers:
            closest_field = mineral_fields.closest_to(worker)
            if closest_field in fields_workers_dict:
                fields_workers_dict[closest_field].append(worker)
            else:
                fields_workers_dict[closest_field] = [worker]
        empty_fields = mineral_fields.filter(lambda field: field not in fields_workers_dict)
        for field in fields_workers_dict:
            if len(fields_workers_dict[field]) > 2:
                worker = fields_workers_dict[field].pop(-1)
                worker.gather(empty_fields.closest_to(worker))
            for worker in fields_workers_dict[field]:
                worker.gather(field)
