from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2 import AbilityId, BotAI



class Scouting:
    def __init__(self, ai_object: BotAI):
        self.ai = ai_object
        self.enemy_info = {}
        self.observer_scouting_index = -1
        self.observer_scouting_points = []

    def scan_middle_game(self):
        scouts = self.ai.units(unit.PHOENIX).filter(lambda z: z.is_hallucination)
        if scouts.amount < 1:
            sentries = self.ai.army(unit.SENTRY)
            if sentries.exists:
                sentries = sorted(sentries.filter(lambda z: z.energy >= 75), key=lambda sent: sent.energy, reverse=True)
                for sentry in sentries:
                    sentry_energy = sentry.energy_percentage
                    self.ai.do(sentry(AbilityId.HALLUCINATION_PHOENIX))
                    if sentry_energy < 1:
                        break
                scouts = self.ai.units(unit.PHOENIX).filter(lambda z: z.is_hallucination)

        if scouts.exists:
            if len(self.observer_scouting_points) < len(self.enemy_info['bases']) + 2 if 'bases' in self.enemy_info \
                else True:
                self.observer_scouting_points.clear()
                for exp in self.ai.expansion_locations_list:
                    if not self.ai.structures().closer_than(7, exp).exists:
                        self.observer_scouting_points.append(exp)
                self.observer_scouting_points = sorted(self.observer_scouting_points,
                                    key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
                if 'bases' in self.enemy_info:
                    most_distant_base_idx = len(self.enemy_info['bases']) + 2
                else:
                    most_distant_base_idx = 3
                while most_distant_base_idx >= len(self.observer_scouting_points):
                    most_distant_base_idx -= 1

                self.observer_scouting_points = self.observer_scouting_points[:most_distant_base_idx]

            print('sct idx: {}'.format(self.observer_scouting_index))
            for scout in scouts.filter(lambda x: x.is_idle or
                     x.distance_to(self.observer_scouting_points[self.observer_scouting_index]) < 7):
                self.observer_scouting_index += 1
                if self.observer_scouting_index >= len(self.observer_scouting_points):
                    self.observer_scouting_index = 0
                self.ai.do(scout.move(self.observer_scouting_points[self.observer_scouting_index]))

    def gather_enemy_info(self):
        # bases
        enemy_bases = self.ai.enemy_structures().filter(lambda x: x.type_id in self.ai.bases_ids and x.is_visible)
        if enemy_bases:
            if 'bases' in self.enemy_info:
                for base in enemy_bases:
                    if base.tag not in self.enemy_info['bases']:
                        self.enemy_info['bases'][base.tag] = base.type_id
            else:
                self.enemy_info['bases'] = {}
                for base in enemy_bases:
                    self.enemy_info['bases'][base.tag] = base.type_id
        # workers
        # workers = self.ai.enemy_units().filter(lambda x: x.type_id in self.ai.workers_ids)

    def print_enemy_info(self):
        print('-------------------- enemy info -----------------------------')
        for category in self.enemy_info:
            print("{}:".format(category))
            for item in self.enemy_info[category]:
                print("   {}, {}".format(item, self.enemy_info[category][item]))
            print(" total: {}".format(len(self.enemy_info[category])))
        print('-------------------- end of enemy info ----------------------')
