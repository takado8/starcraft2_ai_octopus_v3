from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2 import Race


class AdeptShieldMicro(MicroABS):

    def __init__(self, ai):
        super().__init__('AdeptMicro', ai)
        self.enemy_base_idx = 0
        expansions = sorted(self.ai.expansion_locations,
                            key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        self.mineral_lines = [self.ai.mineral_field.closer_than(9, exp).center.towards(exp, -2)
                              for exp in expansions][:5]


    async def do_micro(self, division):
        enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in self.ai.units_to_ignore)
        adepts = division.get_units(self.ai.iteration, unit.ADEPT)
        attacking_friends = None
        division_position = None
        division_units = division.get_units(self.ai.iteration)
        division_low_shield = division_units.filter(lambda x: x.shield_percentage < 0.5)
        adepts_low_shield = adepts.filter(lambda x: x.shield_percentage < 0.5)
        units_in_position = 0
        if adepts_low_shield.amount > adepts.amount * 0.65 or division_low_shield.amount > division_units.amount * 0.65:
            shield_regen_pause = True
        else:
            shield_regen_pause = False
        for adept in adepts:
            abilities = await self.ai.get_available_abilities(adept)

            if adept.shield_percentage < 0.45 or shield_regen_pause:
                if ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT in abilities:
                    adept(ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT, adept.position)
                    continue
                batteries = self.ai.structures.filter(lambda x: x.type_id == unit.SHIELDBATTERY and
                                                                x.is_ready and x.energy_percentage >= 0.1)
                if batteries.exists:
                    adept.move(batteries.closest_to(adept))
                    continue
                elif adept.distance_to(self.ai.defend_position) > 20:
                    adept.move(self.ai.defend_position)
                    continue
            workers = self.ai.enemy_units().filter(lambda x: x.distance_to(adept) < 17 and x.type_id in
                                                             self.ai.workers_ids)
            threats = enemy.filter(
                lambda unit_: unit_.can_attack_ground and unit_.distance_to(adept.position) <= 9 and
                              unit_.type_id not in self.ai.units_to_ignore and not unit_.is_hallucination and
                              not unit_.is_flying)
            if threats.amount > 3 and ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT in abilities:
                adept(ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT, adept.position)
            if workers.amount < 3 or threats.amount > 0:
                queue = False
                if ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT in abilities and \
                        adept.distance_to(self.ai.enemy_start_locations[0]) < \
                    self.ai.start_location.position.distance_to(self.ai.enemy_start_locations[0]) * 0.15:
                    adept(ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT, adept.position)
                    queue = True
                if threats.exists:
                    closer_enemy = threats.closer_than(3, adept)
                    if closer_enemy:
                        threats = closer_enemy
                    closest_enemy = threats.closest_to(adept)
                    priority = threats.filter(
                        lambda x1: x1.type_id in {unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                                                  unit.QUEEN})
                    if priority.exists:
                        targets = priority.sorted(lambda x1: x1.health + x1.shield)
                        target = self.select_target(targets, adept)
                    else:
                        targets = threats.filter(lambda x: x.is_light)
                        if not targets.exists:
                            targets = threats
                        targets = targets.sorted(lambda x1: x1.health + x1.shield)
                        target = self.select_target(targets, adept)

                    if adept.shield_percentage < 0.4:
                        if adept.health_percentage < 0.35:
                            adept.move(self.find_back_out_position(adept, closest_enemy.position), queue=queue)
                            continue
                        d = 4
                    else:
                        d = 2

                    back_out_position = self.find_back_out_position(adept, closest_enemy.position)
                    if back_out_position is not None and adept.weapon_cooldown > 0:
                        adept.move(adept.position.towards(back_out_position, d), queue=queue)
                    else:
                        adept.attack(target, queue=queue)
            elif workers.amount > 1:
                workers_in_range = workers.closer_than(5, adept)
                if workers_in_range.exists:
                    workers_in_range = sorted(workers_in_range, key=lambda x: x.health + x.shield)
                    target3 = workers_in_range[0]
                else:
                    target3 = workers.closest_to(adept)
                if adept.weapon_cooldown == 0:
                    adept.attack(target3)
            if not threats:
                if attacking_friends is None:
                    attacking_friends = division.get_attacking_units(iteration=self.ai.iteration)
                    division_position = division.get_position(iteration=self.ai.iteration)
                if division_position and adept.distance_to(division_position) > division.max_units_distance:
                    adept.move(division_position)
                elif attacking_friends.exists and enemy.exists:
                    adept.move(attacking_friends.closest_to(adept))
                else:
                    units_in_position += 1

        for shadow in self.ai.units(unit.ADEPTPHASESHIFT):
            batteries = self.ai.structures.filter(lambda x: x.type_id == unit.SHIELDBATTERY and
                                                            x.is_ready and x.energy_percentage >= 0.1)
            if batteries.exists:
                shadow.move(batteries.closest_to(shadow))
                continue
            elif shadow.distance_to(self.ai.defend_position) > 20:
                shadow.move(self.ai.defend_position)
                continue
            else:
                shadow.move(self.ai.start_location.position)
                continue
        if not self.ai.attack and self.ai.enemy_units:
            enemy = self.ai.enemy_units().filter(lambda x: x.distance_to(self.ai.start_location) < 35 and
                                              not x.is_flying and x.type_id in {unit.REAPER, unit.SCV, unit.HELLION})

            if enemy and enemy.amount <= 2:
                for adept in adepts:
                    closest_enemy = enemy.closest_to(adept)
                    bunker = self.ai.enemy_structures(unit.BUNKER)
                    if bunker and bunker.closer_than(8, closest_enemy):
                        return adepts.amount
                    adept.attack(closest_enemy)
                    if ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT in await self.ai.get_available_abilities(adept):
                        adept(ability.ADEPTPHASESHIFT_ADEPTPHASESHIFT, closest_enemy.position)

                for shadow in self.ai.units(unit.ADEPTPHASESHIFT):
                    enemy_shadows = enemy(unit.ADEPTPHASESHIFT)
                    if enemy_shadows:
                        enemy = enemy_shadows
                    shadow.move(enemy.closest_to(shadow))
        return adepts.amount

    def select_target(self, targets, adept):
        if self.ai.enemy_race == Race.Protoss:
            a = targets[0].shield_percentage
        else:
            a = 1
        if targets[0].health_percentage * a == 1:
            target = targets.closest_to(adept)
        else:
            target = targets[0]
        return target

    def find_back_out_position(self, adept, closest_enemy_position):
        i = 6
        position = adept.position.towards(closest_enemy_position, -i)
        while not self.in_grid(position) and i < 12:
            position = adept.position.towards(closest_enemy_position, -i)
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

