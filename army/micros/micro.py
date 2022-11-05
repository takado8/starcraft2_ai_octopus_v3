from sc2.constants import FakeEffectID
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.position import Point2
from sc2.ids.effect_id import EffectId as effect
from sc2.units import Units
from sc2 import Race
from .microABS import MicroABS
from bot.constants import ANTI_AIR_IDS


def in_grid(ai, pos):
    try:
        return ai.in_pathing_grid(pos)
    except:
        return False




class AirMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('air', ai)
        self.enemy_base_idx = 0
        expansions = sorted(self.ai.expansion_locations,
                                 key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))
        self.mineral_lines = [self.ai.mineral_field.closer_than(9, exp).center.towards(exp, -3) for exp in expansions][:5]

        enemy_position = self.ai.enemy_start_locations[0]
        self.max_dist = min(self.ai.game_info.map_size) - 5
        short_dist = self.max_dist
        min_dist = 999999
        corners = [Point2((5,5)), Point2((5,self.max_dist)), Point2((self.max_dist, 5)),
                   Point2((self.max_dist,self.max_dist))]
        for position in corners:
            dist = enemy_position.distance_to(position)
            if dist < min_dist:
                self.oracle_safe_position = position
                min_dist = dist
        if self.ai.start_location.y < enemy_position.y:
            if self.ai.start_location.x < enemy_position.x:
                self.oracle_first_position = Point2((5, short_dist))
            else:
                self.oracle_first_position = Point2((short_dist, short_dist))
        else:
            if self.ai.start_location.x < enemy_position.x:
                self.oracle_first_position = Point2((5, 5))
            else:
                self.oracle_first_position = Point2((short_dist, 5))
        self.oracle_safe_position = Point2(self.oracle_safe_position.towards(self.oracle_first_position,self.max_dist/2))
        self.oracle_first_position = self.oracle_safe_position
        self.oracle_first_position_visited = False
        self.oracle_safe_position_visited = False
        self.oracle_last_dist = None
        self.oracle_on_harassment = True
        self.set_new_first_pos = False

    async def do_micro(self, soldiers):
        # Oracle
        all_units = Units([soldiers[soldier_tag].unit for soldier_tag in soldiers], self.ai)
        oracles = all_units(unit.ORACLE)
        for oracle in oracles:
            if self.oracle_on_harassment:
                abilities = await self.ai.get_available_abilities(oracle)
                workers = self.ai.enemy_units().filter(lambda x: x.distance_to(oracle) < 15 and x.type_id in
                                                                 self.ai.workers_ids)
                threats = self.ai.enemy_units().filter(lambda x: x.distance_to(oracle) < 10 and (x.can_attack_air or
                                                 x.type_id in [unit.SENTRY,unit.WIDOWMINE,unit.VOIDRAY]))
                threats.extend(self.ai.enemy_structures().filter(
                    lambda x: x.distance_to(oracle) < 11 and x.can_attack_air and x.is_ready))
                if threats.amount > 0 and threats.filter(lambda x: x.type_id in ANTI_AIR_IDS).amount > 0 and \
                        oracle.distance_to(self.mineral_lines[self.enemy_base_idx]) < 19:
                    print('anti-air detected')
                    if len(self.mineral_lines) > 1:
                        print('removing mineral line: ' + str(self.mineral_lines[self.enemy_base_idx]))
                        self.mineral_lines.remove(self.mineral_lines[self.enemy_base_idx])
                    self.enemy_base_idx += 1
                    if self.enemy_base_idx >= len(self.mineral_lines):
                        self.enemy_base_idx = 0
                    self.set_new_first_pos = True
                    # x2 = self.oracle_first_position.x
                    # y2 = self.oracle_first_position.y
                    # if y2 == 5:
                    #     y2 = self.max_dist
                    # else:
                    #     y2 = 5
                    # self.oracle_first_position = Point2((y2,x2))
                    self.oracle_first_position_visited = False
                if (oracle.energy > 45 or ability.BEHAVIOR_PULSARBEAMOFF in abilities) and oracle.shield_percentage > 0.75:
                    if workers.amount < 1:
                        if self.enemy_base_idx >= len(self.mineral_lines):
                            self.enemy_base_idx = 0
                        if oracle.distance_to(self.mineral_lines[self.enemy_base_idx]) < 7:
                            # print('close!')
                            if self.ai.enemy_structures().filter(lambda x1: x1.type_id in self.ai.bases_ids and
                                                                 x1.distance_to(oracle) < 10).amount < 1:
                                # print('no base here')
                                if len(self.mineral_lines) > 1:
                                    self.mineral_lines.remove(self.mineral_lines[self.enemy_base_idx])
                                self.enemy_base_idx += 1
                                if self.enemy_base_idx == len(self.mineral_lines):
                                    self.enemy_base_idx = 0
                        if not self.oracle_first_position_visited:
                            dist = oracle.distance_to(self.oracle_first_position)
                            if dist > 60 or (self.oracle_last_dist and dist < self.oracle_last_dist):
                                # print('going first pos dist: ' + str(dist) + '  pos: ' + str(self.oracle_first_position))
                                self.ai.do(oracle.move(self.oracle_first_position))
                                self.oracle_last_dist = dist
                            else:
                                self.oracle_first_position_visited = True
                        else:
                            # print('attack lines')
                            if len(self.mineral_lines) <= self.enemy_base_idx:
                                self.enemy_base_idx = 0
                            attack_position = self.mineral_lines[self.enemy_base_idx].towards(self.oracle_first_position, 3)
                            if oracle.distance_to(attack_position) > 17 and\
                                    self.mineral_lines[self.enemy_base_idx].distance_to(self.ai.enemy_start_locations[0]) < 7:
                                self.ai.do(oracle.move(self.mineral_lines[self.enemy_base_idx].towards(self.ai.enemy_start_locations[0], -22)))
                            else:
                                self.ai.do(oracle.move(attack_position))
                    elif workers.amount > 1 and oracle.is_idle:
                        self.oracle_first_position_visited = False
                        workers_in_range = workers.closer_than(5,oracle)
                        if workers_in_range.exists:
                            workers_in_range = sorted(workers_in_range,key=lambda x1: x1.health + x1.shield)
                            target3 = workers_in_range[0]
                        else:
                            target3 = workers.closest_to(oracle)
                        if target3.distance_to(oracle) < 5:
                            if ability.BEHAVIOR_PULSARBEAMON in abilities:
                                self.ai.do(oracle(ability.BEHAVIOR_PULSARBEAMON))
                                self.ai.do(oracle.attack(target3, queue=True))
                            else:
                                self.ai.do(oracle.attack(target3))
                        else:
                            self.ai.do(oracle.move(oracle.position.towards(target3,5)))
                else:  # go safe
                    dist = oracle.distance_to(self.oracle_first_position)
                    # print('want go safe')
                    if dist > 30 or dist < self.oracle_last_dist:
                        # print('go safe')
                        if ability.BEHAVIOR_PULSARBEAMOFF in abilities:
                            self.ai.do(oracle(ability.BEHAVIOR_PULSARBEAMOFF))
                            self.ai.do(oracle.move(self.oracle_first_position, queue=True))
                        else:
                            self.ai.do(oracle.move(self.oracle_first_position))
                        self.oracle_last_dist = dist
                    else:     # is in safe
                        if self.set_new_first_pos:
                            self.set_new_first_pos = False
                            x2 = self.oracle_first_position.x
                            y2 = self.oracle_first_position.y
                            if y2 == 5:
                                y2 = self.max_dist
                            else:
                                y2 = 5
                            self.oracle_first_position = Point2((y2,x2))
                        if oracle.health_percentage < 0.15:
                            self.oracle_on_harassment = False
                        self.oracle_first_position_visited = False
            else:       # end of harassment
                self.ai.do(oracle.move(self.ai.defend_position))
        # Carrier
        carriers = all_units.filter(lambda x: x.type_id in [unit.CARRIER, unit.TEMPEST] and not x.is_attacking)
        for cr in carriers:
            threats = self.ai.enemy_units().filter(
                lambda z: z.distance_to(cr) < 15 and z.type_id not in self.ai.units_to_ignore)
            threats.extend(
                self.ai.enemy_structures().filter(lambda z: z.distance_to(cr) < 15 and z.can_attack_air))
            if threats.exists:
                priority = threats.filter(lambda z: z.can_attack_air or z.type_id in [unit.VOIDRAY, unit.WIDOWMINE, unit.BUNKER]).sorted(
                    lambda z: z.health + z.shield,reverse=False)
                if priority.exists:
                    queens = priority.filter(lambda z: z.type_id == unit.QUEEN)
                    if queens.exists:
                        target2 = queens[0]
                    else:
                        target2 = priority[0]
                else:
                    target2 = threats.sorted(lambda z: z.health + z.shield)[0]
                if target2 is not None:
                    self.ai.do(cr.attack(target2))

        void_rays = all_units.filter(lambda x: x.type_id == unit.VOIDRAY and not x.is_attacking)
        for vr in void_rays:
            threats = self.ai.enemy_units().filter(
                lambda z: z.distance_to(vr) < 12 and z.type_id not in self.ai.units_to_ignore or z.type_id in [unit.VOIDRAY, unit.WIDOWMINE, unit.BUNKER])
            threats.extend(
                self.ai.enemy_structures().filter(lambda z: z.distance_to(vr) < 15 and z.can_attack_air))
            if threats.exists:
                # target2 = None
                priority = threats.filter(lambda z: z.can_attack_air).sorted(lambda z: z.health + z.shield,reverse=False)
                if priority.exists:
                    # closest = priority.closest_to(cr)
                    # if cr.distance_to(closest) < 7:
                    #     self.ai.do(cr.move(cr.position.towards(closest,-3)))
                    # else:
                    # if priority.amount > 2:
                    #     priority = sorted(priority[:int(len(priority) / 2)],key=lambda z: z.health + z.shield)
                    target2 = priority[0]
                else:
                    target2 = threats.sorted(lambda z: z.health + z.shield)[0]
                if target2 is not None:
                    queue = False
                    if target2.is_armored and target2.distance_to(vr) < 7:
                        abilities = await self.ai.get_available_abilities(vr)
                        if ability.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities:
                            self.ai.do(vr(ability.EFFECT_VOIDRAYPRISMATICALIGNMENT))
                            queue = True
                    self.ai.do(vr.attack(target2, queue=queue))


class StalkerMicro(MicroABS):

    def __init__(self, ai):
        self.name = 'StalkerMicro'
        super().__init__(self.name, ai)

    def select_target(self, targets, stalker):
        if self.ai.enemy_race == Race.Protoss:
            a = targets[0].shield_percentage
        else:
            a = 1
        if targets[0].health_percentage * a == 1:
            target = targets.closest_to(stalker)
        else:
            target = targets[0]
        return target

    async def do_micro(self, soldiers):

        enemy = self.ai.enemy_units()
        if not enemy.exists:
            return

        stalkers = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.STALKER]
        # print('doing micro with {} units: {}'.format(len(stalkers), stalkers))
        dist = 6
        for stalker in stalkers:
            threats = enemy.filter(
                lambda unit_: unit_.can_attack_ground and unit_.distance_to(stalker) <= dist and
                              unit_.type_id not in self.ai.units_to_ignore)
            if self.ai.attack:
                threats.extend(self.ai.enemy_structures().filter(lambda _x: _x.can_attack_ground or _x.type_id == unit.BUNKER))
            if threats.exists:
                closest_enemy = threats.closest_to(stalker)
                priority = threats.filter(lambda x1: x1.type_id in [unit.COLOSSUS, unit.DISRUPTOR, unit.HIGHTEMPLAR, unit.WIDOWMINE,
                    unit.MEDIVAC, unit.SIEGETANKSIEGED, unit.SIEGETANK, unit.LIBERATOR, unit.THOR, unit.BUNKER, unit.QUEEN])
                if priority.exists:
                    targets = priority.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, stalker)
                else:
                    targets = threats.filter(lambda x: x.is_armored)
                    if not targets.exists:
                        targets = threats
                    targets = targets.sorted(lambda x1: x1.health + x1.shield)
                    target = self.select_target(targets, stalker)

                # if target.distance_to(stalker) > dist:
                #     target = closest_enemy

                if stalker.shield_percentage < 0.4:
                    if stalker.health_percentage < 0.35:
                        self.ai.do(stalker.move(self.find_back_out_position(stalker, closest_enemy.position)))
                        continue
                    d = 4
                else:
                    d = 2

                if stalker.shield_percentage < 0.4 and upgrade.BLINKTECH in self.ai.state.upgrades and \
                        self.is_blink_available(stalker):
                    back_out_position = self.find_blink_out_position(stalker, closest_enemy.position)
                    if back_out_position is not None and stalker.weapon_cooldown > 0:
                        await self.blink(stalker, back_out_position)
                    else:
                        self.ai.do(stalker.attack(target))
                else:
                    back_out_position = self.find_back_out_position(stalker, closest_enemy.position)
                    if back_out_position is not None and stalker.weapon_cooldown > 0:
                        self.ai.do(stalker.move(stalker.position.towards(back_out_position, d)))
                    else:
                        self.ai.do(stalker.attack(target))

    async def is_blink_available(self, stalker):
        abilities = await self.ai.get_available_abilities(stalker)
        return ability.EFFECT_BLINK_STALKER in abilities

    async def blink(self, stalker, target):
        self.ai.do(stalker(ability.EFFECT_BLINK_STALKER, target))


    def find_blink_out_position(self, stalker, closest_enemy_position):
        i = 8
        position = stalker.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 14:
            position = stalker.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 5:
                k = 0
                while not in_grid(self.ai, position) and k < 7:
                    k += 1
                    position = position.random_on_distance(j * 2)
                j += 1
        return position

    def find_back_out_position(self, stalker, closest_enemy_position):
        i = 3
        position = stalker.position.towards(closest_enemy_position, -i)
        while not in_grid(self.ai, position) and i < 12:
            position = stalker.position.towards(closest_enemy_position, -i)
            i += 1
            j = 1
            while not in_grid(self.ai, position) and j < 3:
                k = 0
                while not in_grid(self.ai, position) and k < 7:
                    k += 1
                    position = position.random_on_distance(j * 2)
                j += 1
        return position


class ZealotMicro(MicroABS):
    def __init__(self, ai):
        self.name = 'ZealotMicro'
        super().__init__(self.name, ai)

    async def do_micro(self, soldiers):
        zealots = [soldiers[tag].unit for tag in soldiers if soldiers[tag].unit.type_id == unit.ZEALOT]

        for zl in zealots:
            threats = self.ai.enemy_units().filter(lambda x2: x2.distance_to(zl.position) < 9 and not x2.is_flying and
                          x2.type_id not in self.ai.units_to_ignore).sorted(lambda _x: _x.health + _x.shield)
            if threats.exists:
                closest = threats.closest_to(zl)
                if threats[0].health_percentage * threats[0].shield_percentage == 1 or threats[0].distance_to(zl) > \
                    closest.distance_to(zl) + 5 or not self.ai.in_pathing_grid(threats[0]):
                    target = closest
                else:
                    target = threats[0]
                if ability.EFFECT_CHARGE in await self.ai.get_available_abilities(zl):
                    self.ai.do(zl(ability.EFFECT_CHARGE, target))
                self.ai.do(zl.attack(target))


class SentryMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('SentryMicro', ai)

    async def do_micro(self, soldiers):
        #  Sentry region  #
        sentries = Units([soldiers[soldier_tag].unit for soldier_tag in soldiers if
               soldiers[soldier_tag].type_id == unit.SENTRY], self.ai)
        # sentries = self.ai.army(unit.SENTRY)
        if sentries.exists:
            m = -1
            sentry = None
            for se in sentries:
                close = sentries.closer_than(7, se).amount
                if close > m:
                    m = close
                    sentry = se
            force_fields = []
            guardian_shield_on = False
            for eff in self.ai.state.effects:
                if eff.id == FakeEffectID.get(unit.FORCEFIELD.value):
                    force_fields.append(eff)
                elif not guardian_shield_on and eff.id == effect.GUARDIANSHIELDPERSISTENT:
                    guardian_shield_on = True
            threats = self.ai.enemy_units().filter(
                lambda unit_: unit_.can_attack_ground or unit_.can_attack_air and unit_.distance_to(sentry) <= 9 and
                              unit_.type_id not in self.ai.units_to_ignore and unit_.type_id not in self.ai.workers_ids)
            has_energy_amount = sentries.filter(lambda x2: x2.energy >= 50).amount
            points = []

            if has_energy_amount > 0 and len(
                    force_fields) < 5 and threats.amount > 4:  # and self.ai.time - self.ai.force_field_time > 1:
                enemy_army_center = threats.center.towards(sentry, -1)
                gap = 3
                points.append(enemy_army_center)
                points.append(Point2((enemy_army_center.x - gap, enemy_army_center.y)))
                points.append(Point2((enemy_army_center.x + gap, enemy_army_center.y)))
                points.append(Point2((enemy_army_center.x, enemy_army_center.y - gap)))
                points.append(Point2((enemy_army_center.x, enemy_army_center.y + gap)))
            for se in self.ai.units(unit.SENTRY):
                abilities = await self.ai.get_available_abilities(se)
                if threats.amount > 4 and not guardian_shield_on and ability.GUARDIANSHIELD_GUARDIANSHIELD in abilities \
                        and se.distance_to(threats.closest_to(se)) < 7:
                    self.ai.do(se(ability.GUARDIANSHIELD_GUARDIANSHIELD))
                    guardian_shield_on = True
                if ability.FORCEFIELD_FORCEFIELD in abilities and len(points) > 0:
                    self.ai.do(se(ability.FORCEFIELD_FORCEFIELD, points.pop(0)))
                else:
                    army_nearby = self.ai.army.closer_than(9, se)
                    if army_nearby.exists:
                        if threats.exists:
                            self.ai.do(se.move(army_nearby.center.towards(threats.closest_to(se), -4)))


class WarpPrismMicro(MicroABS):
    def __init__(self, ai):
        super().__init__("WarpPrismMicro", ai)

    async def do_micro(self, soldiers):
        if self.ai.attack:
            dist = self.ai.enemy_start_locations[0].distance_to(self.ai.game_info.map_center) * 0.8
            for warp in self.ai.units(unit.WARPPRISM):
                if warp.distance_to(self.ai.enemy_start_locations[0]) <= dist:
                    abilities = await self.ai.get_available_abilities(warp)
                    if ability.MORPH_WARPPRISMPHASINGMODE in abilities:
                        self.ai.do(warp(ability.MORPH_WARPPRISMPHASINGMODE))
        else:
            for warp in self.ai.units(unit.WARPPRISMPHASING):
                abilities = await self.ai.get_available_abilities(warp)
                if ability.MORPH_WARPPRISMTRANSPORTMODE in abilities:
                    self.ai.do(warp(ability.MORPH_WARPPRISMTRANSPORTMODE))