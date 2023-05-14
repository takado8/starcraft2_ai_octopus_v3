from sc2.constants import UnitTypeId as unit_id
from sc2.ids.ability_id import AbilityId as ability



class WorkerRushDefense:
    FIGHTING_WORKERS_PERCENTAGE = 0.7

    def __init__(self, ai):
        self.ai = ai
        self.fighting_probes = set()

    async def worker_rush_defense(self):
        if self.ai.time < 360:
            enemy = self.ai.enemy_units()

            enemy_in_main_base = enemy.closer_than(10, self.ai.main_base_ramp.bottom_center)
            if not enemy_in_main_base:
                enemy_in_main_base = enemy.closer_than(25, self.ai.start_location.position)
            probes = self.ai.workers
            mineral_workers_tags = set()
            if enemy_in_main_base.amount > 2:
                own_army = self.ai.army
                total_hp = sum([unit.health + unit.shield for unit in own_army])
                enemy_dps = sum([unit.ground_dps for unit in enemy_in_main_base])
                if enemy_dps * 5 > total_hp:
                    # need probes
                    if self.ai.workers.amount < 18:
                        self.nexus_train_probes()

                    probes_to_remove = set()
                    for probe_tag in self.fighting_probes:
                        probe = probes.find_by_tag(probe_tag)
                        if probe and (probe.shield > 5 if probes.filter(lambda x: x.shield > 15).amount > len(probes) / 2
                            else probe.health_percentage > 0.5):
                            target = enemy_in_main_base.closest_to(probe)
                            if await self.ai._client.query_pathing(probe.position, target.position):
                                probe.attack(target)
                            else:
                                possible_targets = [x for x in enemy_in_main_base if await self.ai._client.query_pathing(probe.position, x.position)]


                                if possible_targets:
                                    possible_targets = sorted(possible_targets, key=lambda x: x.shield_health_percentage)
                                    probe.attack(possible_targets[0])
                                else:
                                    probe.move(target.position.towards(probe, 4))
                        else:
                            if probe:
                                probe.gather(self.ai.mineral_field.closer_than(10,
                                            self.ai.start_location.position).closest_to(probe.position))
                            probes_to_remove.add(probe_tag)
                    for probe_to_remove in probes_to_remove:
                        self.fighting_probes.remove(probe_to_remove)

                    if len(self.fighting_probes) < len(probes) * self.FIGHTING_WORKERS_PERCENTAGE:
                        probes = probes.sorted(lambda x: (x.shield, x.shield_health_percentage), reverse=True)
                        missing = int(len(probes) * self.FIGHTING_WORKERS_PERCENTAGE) - len(self.fighting_probes)
                        for probe in probes[:missing]:
                            self.fighting_probes.add(probe.tag)

                    for probe in probes:
                        if probe.tag not in self.fighting_probes:
                            mineral_workers_tags.add(probe.tag)
            dist = 55
            for probe in probes:
                if isinstance(probe.order_target, int) and probe.distance_to(self.ai.start_location) > dist:
                    probe.gather(self.ai.mineral_field.closer_than(10,
                        self.ai.start_location).closest_to(probe.position))
            return mineral_workers_tags



    def nexus_train_probes(self):
        nexus = self.ai.townhalls.ready
        if nexus and nexus.idle.exists:
            nexus = nexus.first
            nexus.train(unit_id.PROBE)
        elif nexus and not nexus.idle.exists:
            nexus = nexus.first
            if nexus.energy >= 50:
                nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
