from army.micros.microABS import MicroABS
from sc2.unit import UnitTypeId as unit
from sc2.ids.buff_id import BuffId as buff
from sc2 import Race


class ImmortalMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('ImmortalMicro', ai)

    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        immortals = division.get_units(unit.IMMORTAL)
        dist = 7
        units_in_position = 0
        for immortal in immortals:
            threats = enemy.filter(
                lambda unit_: unit_.can_attack_ground and unit_.distance_to(immortal.position) <= dist and
                              unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination)
            if self.ai.attack:
                threats.extend(
                    self.ai.enemy_structures().filter(lambda _x: (_x.can_attack_ground or _x.type_id == unit.BUNKER) and
                                                      _x.distance_to(immortal) <= dist))
            if threats.exists:
                closest_enemy = threats.closest_to(immortal)
                priority = threats.filter(
                    lambda x1: x1.type_id in [unit.COLOSSUS, unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                                              unit.MEDIVAC, unit.SIEGETANKSIEGED, unit.SIEGETANK, unit.LIBERATOR,
                                              unit.THOR, unit.BUNKER, unit.QUEEN])
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, immortal)
                else:
                    targets = threats.filter(lambda x: x.is_armored)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, immortal)

                if immortal.shield_percentage < 0.4:
                    if immortal.health_percentage < 0.35:
                        immortal.move(self.find_back_out_position(immortal, closest_enemy.position))
                        continue
                    d = 4
                else:
                    d = 2

                back_out_position = self.find_back_out_position(immortal, closest_enemy.position)
                has_buff = immortal.has_buff(buff.IMMORTALOVERLOAD)
                if back_out_position is not None and immortal.weapon_cooldown > 0 and immortal.shield_percentage < 1 \
                        and not has_buff:
                    immortal.move(immortal.position.towards(back_out_position, d))
                else:
                    immortal.attack(target)
            else:
                attacking_friends = division.get_attacking_units()
                division_position = division.get_position()
                if attacking_friends.exists and enemy.exists:
                    immortal.attack(enemy.closest_to(attacking_friends.closest_to(immortal)))
                elif division_position and immortal.distance_to(division_position) > division.max_units_distance:
                    immortal.attack(division_position)
                else:
                    units_in_position += 1
        return units_in_position

    def find_back_out_position(self, immortal, closest_enemy_position):
        i = 6
        position = immortal.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = immortal.position.towards(closest_enemy_position, -i)
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

    def select_target(self, targets, immortal):
        if self.ai.enemy_race == Race.Protoss:
            a = targets[0].shield_percentage
        else:
            a = 1
        if targets[0].health_percentage * a == 1:
            target = targets.closest_to(immortal)
        else:
            target = targets[0]
        return target