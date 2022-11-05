from sc2.ids.unit_typeid import UnitTypeId as Unit
from sc2 import AbilityId
from economy.info.enemy_economy import BASES, MILITARY


class Scouting:
    def __init__(self, ai_object, enemy_economy):
        self.number_of_scoutings_done = 0
        self.ai = ai_object
        self.scouting_index = -1
        self.scouting_positions = []
        self.enemy_economy = enemy_economy

    def scan_middle_game(self):
        scouts = self.ai.units(Unit.PHOENIX).filter(lambda z: z.is_hallucination)
        if scouts.exists:
            if BASES not in self.enemy_economy.enemy_info or len(self.scouting_positions) <\
                    len(self.enemy_economy.enemy_info[BASES]) + 2:
                self.scouting_positions.clear()
                self.scouting_positions = self.create_scouting_positions_list()

            for scout in scouts.filter(lambda x: x.is_idle or
                                                 x.distance_to(self.scouting_positions[self.scouting_index]) < 5):
                self.scouting_index += 1
                if self.scouting_index >= len(self.scouting_positions):
                    self.scouting_index = 0
                self.ai.do(scout.move(self.scouting_positions[self.scouting_index]))
        else:
            self.create_scout()

    def gather_enemy_info(self):
        # bases
        enemy_bases = self.ai.enemy_structures().filter(lambda x: x.type_id in self.ai.bases_ids and x.is_visible)
        self.enemy_economy.add_units_to_enemy_info(BASES, enemy_bases)
        # military units
        excluded = [Unit.BROODLING, Unit.OVERLORD, Unit.OVERSEER, Unit.ADEPTPHASESHIFT, Unit.OVERLORDCOCOON,
                    Unit.OVERLORDTRANSPORT]
        enemy_military_units = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.workers_ids and
                                                                      x.type_id not in self.ai.units_to_ignore
                                                                      and x.type_id not in excluded and x.is_visible
                                                            and not x.is_snapshot and not x.is_hallucination)
        self.enemy_economy.add_units_to_enemy_info(MILITARY, enemy_military_units)


    def create_scouting_positions_list(self):
        scouting_positions = []
        for exp in self.ai.expansion_locations_list:
            if not self.ai.structures().closer_than(7, exp).exists:
                scouting_positions.append(exp)

        scouting_positions = sorted(scouting_positions, key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        if BASES in self.enemy_economy.enemy_info:
            most_distant_base_idx = len(self.enemy_economy.enemy_info[BASES]) + 2
        else:
            most_distant_base_idx = 3

        while most_distant_base_idx >= len(scouting_positions):
            most_distant_base_idx -= 1

        scouting_positions = scouting_positions[:most_distant_base_idx]
        return scouting_positions

    def create_scout(self):
        sentries = self.ai.army(Unit.SENTRY)
        if sentries.exists:
            sentries = sorted(sentries.filter(lambda z: z.energy >= 75), key=lambda sent: sent.energy, reverse=True)
            if self.number_of_scoutings_done > 3:
                if len(sentries) < 2:
                    return
            for sentry in sentries:
                sentry_energy = sentry.energy_percentage
                self.ai.do(sentry(AbilityId.HALLUCINATION_PHOENIX))
                self.number_of_scoutings_done += 1
                if sentry_energy < 1:
                    break

    def scan_on_end(self):
        scouts = self.ai.units(Unit.PHOENIX).filter(lambda z: z.is_hallucination)
        if scouts.amount < 3:
            snts = self.ai.army(Unit.SENTRY)
            if snts.exists and self.ai.time < 1800:
                snts = self.ai.army(Unit.SENTRY).filter(lambda z: z.energy >= 75)
                if snts:
                    for se in snts:
                        self.ai.do(se(AbilityId.HALLUCINATION_PHOENIX))
                    scouts = self.ai.units(Unit.PHOENIX).filter(lambda z: z.is_hallucination)
            else:
                scouts = self.ai.units({Unit.WARPPRISM, Unit.OBSERVER})
                if not scouts.exists:
                    scouts = self.ai.army.filter(lambda z: z.is_flying)
                    if not scouts.exists:
                        scouts = self.ai.units(Unit.PROBE).closest_n_units(self.ai.enemy_start_locations[0], 3)
                        if not scouts.exists:
                            scouts = self.ai.units().closest_n_units(self.ai.enemy_start_locations[0], 3)
        if scouts.exists:
            if len(self.scouting_positions) == 0:
                for exp in self.ai.expansion_locations_list:
                    if not self.ai.structures().closer_than(7, exp).exists:
                        self.scouting_positions.append(exp)
                self.scouting_positions = sorted(self.scouting_positions,
                                                       key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
            for px in scouts.idle:
                self.ai.do(px.move(self.scouting_positions[self.scouting_index]))
                self.scouting_index += 1
                if self.scouting_index == len(self.scouting_positions):
                    self.scouting_index = 0