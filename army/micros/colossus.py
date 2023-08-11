from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit


class ColossusMicro(MicroABS):
    def __init__(self, ai, use_division_backout_position=None):
        self.name = 'ColossusMicro'
        super().__init__(self.name, ai, use_division_backout_position)

    def select_target(self, targets):
        total_hp_in_range_of_fire = {}
        _range = 2.8
        for target in targets:
            enemy_in_range = self.ai.enemy_units.filter(lambda x: not x.is_flying and x.distance_to(target) <= _range and\
                                                        x.type_id not in self.ai.units_to_ignore)
            total_hp_in_range_of_fire[target] = \
                (enemy_in_range.amount, sum([enemy.health + enemy.shield for enemy in enemy_in_range]))
        max_targets = max(total_hp_in_range_of_fire, key=lambda x: total_hp_in_range_of_fire[x][0])

        targets_with_max_count = {}
        for target in total_hp_in_range_of_fire:
            if total_hp_in_range_of_fire[target][0] == max_targets:
                targets_with_max_count[target] = total_hp_in_range_of_fire[target]

        min_hp = 99999999
        final_target = None
        for target in targets_with_max_count:
            if targets_with_max_count[target][1] < min_hp:
                min_hp = targets_with_max_count[target][1]
                final_target = target

        return final_target

    async def do_micro(self, division):
        enemy = self.ai.enemy_units()
        colossi = division.get_units(self.ai.iteration, unit.COLOSSUS)
        dist = 12
        units_in_position = 0
        attacking_friends = None
        division_position = None
        for colossus in colossi:
            if enemy.exists:
                threats = enemy.filter(
                    lambda unit_: (unit_.can_attack_ground or unit_.can_attack_air) and unit_.distance_to(colossus.position) <= dist and
                                  unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination)
                if self.ai.attack:
                    threats.extend(self.ai.enemy_structures().filter(lambda _x: (_x.can_attack_ground or _x.can_attack_air
                                                                                or _x.type_id == unit.BUNKER) and
                                                                     _x.distance_to(colossus) <= dist))
            else:
                threats = None
            if threats:
                close_threats = threats.closer_than(5, colossus)
                if close_threats.amount > 0:
                    threats = close_threats
                closest_enemy = threats.closest_to(colossus)
                priority = threats.filter(lambda x1: x1.type_id in {unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                                                                    unit.QUEEN, unit.GHOST})
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets)
                else:
                    targets = threats.filter(lambda x: x.is_light)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets)
                if colossus.shield_percentage < 0.6:
                    if colossus.health_percentage < 0.7:
                        colossus.move(self.find_back_out_position(colossus, closest_enemy.position, division))
                        continue
                    d = 5
                else:
                    d = 0

                back_out_position = self.find_back_out_position(colossus, closest_enemy.position, division)
                if back_out_position is not None and colossus.weapon_cooldown > 0:
                    colossus.move(colossus.position.towards(back_out_position, d))
                elif target:
                    colossus.attack(target)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(iteration=self.ai.iteration)
                    division_position = division.get_position(iteration=self.ai.iteration)
                if division_position and colossus.distance_to(division_position) > division.max_units_distance:
                    colossus.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    colossus.attack(enemy.closest_to(attacking_friends.closest_to(colossus)))
                else:
                    units_in_position += 1

        # stalkers = division.get_units(unit.STALKER)
        # priority_ids = {unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE, unit.VIPER,
        #                 unit.MEDIVAC, unit.SIEGETANKSIEGED, unit.SIEGETANK, unit.LIBERATOR, unit.INFESTOR,
        #                 unit.CORRUPTOR,unit.MUTALISK, unit.VIKING, unit.THOR, unit.BUNKER}
        #
        # colossi_threats_set = set()
        # for colossus in colossi:
        #     threats = self.ai.enemy_units().filter(lambda x: x.type_id in priority_ids and
        #                     x.distance_to(colossus) <= 7)
        #     for threat in threats:
        #         colossi_threats_set.add(threat)
        #
        # colossi_threats = Units(colossi_threats_set, self.ai)
        # dist = 6
        # threats = None
        # for stalker in stalkers:
        #     if colossi_threats:
        #         threats = colossi_threats
        #         # print(colossi_threats)
        #     elif colossi and not any([stalker.distance_to(colossus) < 4 for colossus in colossi]):
        #         if upgrade.BLINKTECH in self.ai.state.upgrades and \
        #             await self.is_blink_available(stalker):
        #             await self.blink(stalker, colossi.closest_to(stalker).position)
        #         else:
        #             stalker.move(colossi.closest_to(stalker))
        #     else:
        #         threats = enemy.filter(
        #             lambda unit_: (((unit_.can_attack_ground or unit_.can_attack_air)
        #                             and unit_.distance_to(stalker.position) <= dist and
        #                             unit_.type_id not in self.ai.units_to_ignore) or unit_.type_id in priority_ids)
        #                           and not unit_.is_hallucination)
        #         if self.ai.attack:
        #             threats.extend(
        #                 self.ai.enemy_structures().filter(lambda _x: _x.can_attack_ground or _x.type_id == unit.BUNKER))
        #     if threats:
        #         closest_enemy = threats.closest_to(stalker)
        #         priority = threats.filter(lambda x1: x1.type_id in priority_ids)
        #         if priority.exists:
        #             targets = priority.sorted(lambda x1: x1.health + x1.shield)
        #             target = self.select_stalker_target(targets, stalker)
        #         else:
        #             targets = threats.filter(lambda x: x.is_armored)
        #             if not targets.exists:
        #                 targets = threats
        #             targets = targets.sorted(lambda x1: x1.health + x1.shield)
        #             target = self.select_stalker_target(targets, stalker)
        #
        #         if colossi_threats:
        #             stalker.attack(target)
        #             continue
        #
        #         if stalker.shield_percentage < 0.3:
        #             if stalker.health_percentage < 0.35:
        #                 stalker.move(self.find_stalker_back_out_position(stalker, closest_enemy.position))
        #                 continue
        #             d = 4
        #         else:
        #             d = 2
        #
        #
        #         if stalker.shield_percentage < 0.4 and upgrade.BLINKTECH in self.ai.state.upgrades and \
        #                 await self.is_blink_available(stalker):
        #             back_out_position = self.find_blink_out_position(stalker, closest_enemy.position)
        #             if back_out_position is not None and stalker.weapon_cooldown > 0:
        #                 await self.blink(stalker, back_out_position)
        #             else:
        #                 stalker.attack(target)
        #         else:
        #             back_out_position = self.find_stalker_back_out_position(stalker, closest_enemy.position)
        #             if back_out_position is not None and stalker.weapon_cooldown > 0:
        #                 stalker.move(stalker.position.towards(back_out_position, d))
        #             else:
        #                 stalker.attack(target)
        #     else:
        #         attacking_friends = division.get_attacking_units()
        #         division_position = division.get_position()
        #         if attacking_friends.exists and enemy.exists:
        #             stalker.attack(enemy.closest_to(attacking_friends.closest_to(stalker)))
        #         elif division_position and stalker.distance_to(division_position) > division.max_units_distance:
        #             stalker.attack(division_position)
        #         else:
        #             units_in_position += 1
        return units_in_position

    def select_stalker_target(self, targets, stalker):
        if targets[0].shield_health_percentage == 1:
            target = targets.closest_to(stalker)
        else:
            target = targets[0]
        return target

    async def is_blink_available(self, stalker):
        abilities = await self.ai.get_available_abilities(stalker)
        return ability.EFFECT_BLINK_STALKER in abilities

    async def blink(self, stalker, target):
        stalker(ability.EFFECT_BLINK_STALKER, target)

    def find_blink_out_position(self, stalker, closest_enemy_position):
        i = 8
        position = stalker.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 14:
            position = stalker.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not self.in_grid(position) and j < 5:
                k = 0
                while not self.in_grid(position) and k < 7:
                    k += 1
                    position = position.random_on_distance(j * 2)
                j += 1
        return position

    def find_stalker_back_out_position(self, stalker, closest_enemy_position):
        i = 6
        position = stalker.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = stalker.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not self.in_grid(position) and j < 5:
                k = 0
                distance = j * 2
                while not self.in_grid(position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position

    def find_back_out_position(self, colossus, closest_enemy_position, division):
        if self.use_division_backout_position:
            backout_position = division.get_safety_backout_position(self.ai.iteration)
            if backout_position is not None:
                return backout_position
        i = 6
        position = colossus.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = colossus.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not self.in_grid(position) and j < 5:
                k = 0
                distance = j * 2
                while not self.in_grid(position) and k < 20:
                    k += 1
                    position = position.random_on_distance(distance)
                j += 1
        return position

