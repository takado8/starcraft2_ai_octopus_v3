from sc2.ids.unit_typeid import UnitTypeId as unit


class AssimilatorBuilder:
    def __init__(self, ai):
        self.ai = ai

    def max_vespene(self):
        if self.ai.structures().filter(lambda x: x.type_id in [unit.GATEWAY, unit.WARPGATE]).amount < 1:
            return
        if self.ai.can_afford(unit.ASSIMILATOR) and self.ai.structures(unit.PYLON).exists:
            nexuses = self.ai.structures(unit.NEXUS)
            if nexuses.amount < 3:
                nexuses = nexuses.ready
            for nexus in nexuses:
                vaspenes = self.ai.vespene_geyser.closer_than(12, nexus)
                for vaspene in vaspenes:
                    if not (self.ai.already_pending(unit.ASSIMILATOR) or self.ai.already_pending(unit.ASSIMILATORRICH)) \
                            and (not self.ai.structures(unit.ASSIMILATOR).exists or not (self.ai.structures(
                        unit.ASSIMILATOR).closer_than(3, vaspene).exists) or
                                 self.ai.structures(unit.ASSIMILATORRICH).closer_than(3, vaspene).exists):
                        worker = self.ai.select_build_worker(vaspene.position)
                        if worker is None:
                            break
                        worker.build(unit.ASSIMILATOR, vaspene)
                        worker.move(worker.position.random_on_distance(1), queue=True)

    def absolute_max_vespene(self):
        if self.ai.structures().filter(lambda x: x.type_id in [unit.PYLON]).amount < 1:
            return
        if self.ai.can_afford(unit.ASSIMILATOR) and self.ai.structures(unit.PYLON).exists:
            nexuses = self.ai.structures(unit.NEXUS)
            if nexuses.amount < 3:
                nexuses = nexuses.ready
            for nexus in nexuses:
                vaspenes = self.ai.vespene_geyser.closer_than(12, nexus)
                for vaspene in vaspenes:
                    if not (self.ai.already_pending(unit.ASSIMILATOR) or self.ai.already_pending(unit.ASSIMILATORRICH)) \
                            and (not self.ai.structures(unit.ASSIMILATOR).exists or not (self.ai.structures(
                        unit.ASSIMILATOR).closer_than(3, vaspene).exists) or
                                 self.ai.structures(unit.ASSIMILATORRICH).closer_than(3, vaspene).exists):
                        worker = self.ai.select_build_worker(vaspene.position)
                        if worker is None:
                            break
                        worker.build(unit.ASSIMILATOR, vaspene)
                        worker.move(worker.position.random_on_distance(1), queue=True)

    def more_vespene(self):
        if self.ai.structures().filter(lambda x: x.type_id in [unit.GATEWAY, unit.WARPGATE]).amount == 0 or \
                (self.ai.structures(unit.NEXUS).ready.amount > 1 and self.ai.vespene > self.ai.minerals):
            return
        nexuses = self.ai.structures(unit.NEXUS)
        if nexuses.amount < 4:
            nexuses = nexuses.ready
        probes = self.ai.units(unit.PROBE)
        if probes.exists:
            for nexus in nexuses:
                vespenes = self.ai.vespene_geyser.closer_than(9, nexus)
                workers = probes.closer_than(12, nexus)
                if workers.amount > 14 or nexuses.amount > 3:
                    for vespene in vespenes:
                        if not (self.ai.already_pending(unit.ASSIMILATOR) or self.ai.already_pending(
                                unit.ASSIMILATORRICH)) \
                                and (not self.ai.structures(unit.ASSIMILATOR).exists or not (self.ai.structures(
                            unit.ASSIMILATOR).closer_than(3, vespene).exists) or
                                     self.ai.structures(unit.ASSIMILATORRICH).closer_than(3, vespene).exists):
                            if not self.ai.can_afford(unit.ASSIMILATOR):
                                return
                            worker = self.ai.select_build_worker(vespene.position)
                            if worker is None:
                                break
                            worker.build(unit.ASSIMILATOR, vespene)
                            worker.move(worker.position.random_on_distance(1), queue=True)

    def standard(self, minerals_to_gas_ratio=2):
        if self.ai.structures().filter(lambda x: x.type_id in [unit.GATEWAY, unit.WARPGATE]).amount < 1:
            return
        if (self.ai.minerals + 50) / (self.ai.vespene + 50) < minerals_to_gas_ratio:
            return

        nexuses = self.ai.structures(unit.NEXUS)
        if nexuses.amount < 4:
            nexuses = nexuses.ready
        probes = self.ai.units(unit.PROBE)
        if probes.exists:
            for nexus in nexuses:
                vespenes = self.ai.vespene_geyser.closer_than(9, nexus)
                workers = probes.closer_than(12, nexus)
                if workers.amount > 14 or nexuses.amount > 3:
                    for vespene in vespenes:
                        if not (self.ai.already_pending(unit.ASSIMILATOR) or self.ai.already_pending(
                                unit.ASSIMILATORRICH)) \
                                and (not self.ai.structures(unit.ASSIMILATOR).exists or not (self.ai.structures(
                            unit.ASSIMILATOR).closer_than(3, vespene).exists) or
                                     self.ai.structures(unit.ASSIMILATORRICH).closer_than(3, vespene).exists):
                            if not self.ai.can_afford(unit.ASSIMILATOR):
                                return
                            worker = self.ai.select_build_worker(vespene.position)
                            if worker is None:
                                break
                            worker.build(unit.ASSIMILATOR, vespene)
                            worker.move(worker.position.random_on_distance(1), queue=True)
                            # print("building assimilator.")
                            break

    def one_vespene(self):
        if self.ai.structures().filter(lambda x: x.type_id in {unit.GATEWAY, unit.WARPGATE}).ready.amount < 1 or\
                self.ai.structures(unit.ASSIMILATOR).exists or self.ai.already_pending(unit.ASSIMILATOR):
            return


        nexuses = self.ai.structures(unit.NEXUS)
        probes = self.ai.units(unit.PROBE)
        if probes.exists:
            for nexus in nexuses:
                vespenes = self.ai.vespene_geyser.closer_than(9, nexus)

                for vespene in vespenes:
                    if not (self.ai.already_pending(unit.ASSIMILATOR) or self.ai.already_pending(
                            unit.ASSIMILATORRICH)) \
                            and (not self.ai.structures(unit.ASSIMILATOR).exists or not (self.ai.structures(
                        unit.ASSIMILATOR).closer_than(3, vespene).exists) or
                                 self.ai.structures(unit.ASSIMILATORRICH).closer_than(3, vespene).exists):
                        if not self.ai.can_afford(unit.ASSIMILATOR):
                            return
                        worker = self.ai.select_build_worker(vespene.position)
                        if worker is None:
                            return
                        worker.build(unit.ASSIMILATOR, vespene)
                        worker.move(worker.position.random_on_distance(1), queue=True)
                        # print("building assimilator.")
                        return