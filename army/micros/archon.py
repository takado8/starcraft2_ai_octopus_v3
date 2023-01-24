from army.micros.microABS import MicroABS
from sc2.ids.unit_typeid import UnitTypeId as unit


class ArchonMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('ArchonMicro', ai)


    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        archons = division.get_units(self.ai.iteration, unit.ARCHON)
        attacking_friends = None
        division_position = None
        dist = 4
        units_in_position = 0
        for archon in archons:
            if enemy.exists:
                threats = enemy.filter(
                    lambda unit_: unit_.can_attack_ground and unit_.distance_to(archon.position) <= dist and
                                  unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination)
                if self.ai.attack:
                    threats.extend(self.ai.enemy_structures().filter(
                        lambda _x:(_x.can_attack_ground or _x.type_id == unit.BUNKER) and _x.distance_to(archon) <= dist))
            else:
                threats = None
            if threats:
                close_threats = threats.closer_than(2, archon)
                if close_threats.amount > 0:
                    threats = close_threats
                closest_enemy = threats.closest_to(archon)
                priority = threats.filter(lambda x1: x1.type_id in {unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                    unit.QUEEN, unit.MUTALISK, unit.VIPER, unit.GHOST, unit.INFESTOR, unit.CORRUPTOR})
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets)
                else:
                    targets = threats.filter(lambda x: x.is_biological)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets)

                if archon.shield_percentage < 0.25:
                    archon.move(self.find_back_out_position(archon, closest_enemy.position))
                    continue

                if target is None:
                    target = closest_enemy
                archon.attack(target)
            else:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(iteration=self.ai.iteration)
                    division_position = division.get_position(iteration=self.ai.iteration)
                if division_position and archon.distance_to(division_position) > division.max_units_distance:
                    archon.attack(division_position)
                elif attacking_friends.exists and enemy.exists:
                    archon.attack(enemy.closest_to(attacking_friends.closest_to(archon)))
                else:
                    units_in_position += 1
        return units_in_position

    def select_target(self, targets):
        total_hp_in_range_of_fire = {}
        _range = 1
        for target in targets:
            enemy_in_range = self.ai.enemy_units.filter(lambda x: x.distance_to(target) <= _range and\
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

    def find_back_out_position(self, archon, closest_enemy_position):
        i = 6
        position = archon.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = archon.position.towards(closest_enemy_position, -i)
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

