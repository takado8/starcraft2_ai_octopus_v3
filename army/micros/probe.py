

class ProbeMicro:
    def __init__(self, ai):
        self.ai = ai

    async def do_micro(self):
        for probe in self.ai.workers:
            enemy = self.ai.enemy_units().filter(lambda x: x.can_attack_ground and not x.is_flying and
                                                           x.distance_to(probe) < x.ground_range + 3)
            if 0 < enemy.amount < 3:
                damaged_probes = self.ai.workers.filter(lambda x: x.distance_to(probe) < 6
                            and probe.shield_percentage < 1)
                if damaged_probes:
                    if any([probe.distance_to(nexus) < 14 for nexus in self.ai.townhalls.ready]):
                        probe.attack(enemy.closest_to(probe))
                    else:
                        probe.gather(self.ai.mineral_field.closest_to(probe))
            # elif enemy.amount > 2 and self.ai.time > 360 and \
            #         probe.distance_to(self.ai.start_location.position) > 12:
            #     probe.gather(self.ai.mineral_field.closest_to(self.ai.start_location.position))