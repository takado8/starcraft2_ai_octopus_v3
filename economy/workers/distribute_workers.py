# from sc2.units import Units
from sc2.unit import UnitTypeId as unit
from sc2.position import Point2
from typing import Dict, Set


class DistributeWorkers:
    def __init__(self, ai):
        self.ai = ai

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
