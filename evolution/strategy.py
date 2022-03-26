from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.constants import FakeEffectID
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2
from sc2.ids.effect_id import EffectId as effect
from sc2.units import Units
from sc2 import Race
from builders.expander import Expander
from bot.chronobooster import Chronobooster


class EvolutionStrategy:
    def __init__(self, ai):
        self.ai = ai
        self.type = 'macro'
        self.name = 'evo'
        self.expander = Expander(ai)
        self.chronobooster = Chronobooster(ai)

    # =======================================================  Builders
    async def build_from_queue(self):
        order_dict = {}
        for i in range(self.ai.build_order_index + 1):
            building = self.ai.build_order[i]
            if building in order_dict:
                order_dict[building][1] += 1
            else:
                amount = self.ai.structures(building).amount
                order_dict[building] = [amount, 1]
        if unit.GATEWAY in order_dict:
            warpgate_amount = self.ai.structures(unit.WARPGATE).amount
            order_dict[unit.GATEWAY][0] += warpgate_amount
        if unit.NEXUS in order_dict:
            order_dict[unit.NEXUS][1] += 1
        print('order dict: {}'.format(order_dict))
        all_done = True
        for building in order_dict:
            if order_dict[building][0] < order_dict[building][1]:
                all_done = False
                print('need to build: {}'.format(building))
                if self.ai.can_afford(building) and self.ai.already_pending(building) < 1:
                    pylon = self.ai.get_pylon_with_least_neighbours()
                    if pylon:
                        if building == unit.NEXUS:
                            await self.expander.evo()
                        else:
                            await self.ai.build(building, near=pylon, placement_step=3, max_distance=40,
                                            random_alternative=True)
        if all_done:
            print('all done.')
            if self.ai.build_order_index + 1 < len(self.ai.build_order):
                self.ai.build_order_index += 1

    async def build_pylons(self):
        if self.ai.supply_cap < 200:
            # if self.ai.structures(unit.PYLON).amount < 1:
            #     if not self.ai.already_pending(unit.PYLON):
            #         placement = self.ai.main_base_ramp.protoss_wall_pylon
            #
            #         await self.ai.build(unit.PYLON, near=placement, placement_step=0, max_distance=0,
            #                             random_alternative=False)
            # else:
            if self.ai.supply_cap < 80:
                pos = self.ai.start_location.position.towards(self.ai.main_base_ramp.top_center, 5)
                max_d = 23
                pending = 2 if self.ai.time > 180 else 1
                left = 5
                step = 7
            else:
                pos = self.ai.structures(unit.NEXUS).ready.random.position
                max_d = 35
                pending = 3
                left = 9
                step = 5
            if self.ai.supply_left < left:  # or (pylons.amount < 1 and self.ai.structures(unit.GATEWAY).exists):
                if self.ai.already_pending(unit.PYLON) < pending:
                    result = await self.ai.build(unit.PYLON, max_distance=max_d, placement_step=step, near=pos)
                    i = 0
                    while not result and i < 12:
                        i += 1
                        pos = pos.random_on_distance(2)
                        result = await self.ai.build(unit.PYLON, max_distance=max_d, placement_step=step, near=pos)

    # =======================================================  Upgraders
    def forge_upgrades(self):
        for forge in self.ai.structures(unit.FORGE).ready.idle:
            if upgrade.PROTOSSGROUNDWEAPONSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDWEAPONSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSGROUNDWEAPONSLEVEL1):
                self.ai.do(forge.research(upgrade.PROTOSSGROUNDWEAPONSLEVEL1))
            elif upgrade.PROTOSSGROUNDWEAPONSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDWEAPONSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSGROUNDWEAPONSLEVEL2):
                self.ai.do(forge.research(upgrade.PROTOSSGROUNDWEAPONSLEVEL2))
            elif self.ai.already_pending_upgrade(upgrade.PROTOSSGROUNDWEAPONSLEVEL2) or \
                    upgrade.PROTOSSGROUNDWEAPONSLEVEL2 in self.ai.state.upgrades:
                if upgrade.PROTOSSGROUNDWEAPONSLEVEL2 in \
                        self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDWEAPONSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSGROUNDWEAPONSLEVEL3):
                    self.ai.do(forge.research(upgrade.PROTOSSGROUNDWEAPONSLEVEL3))
                elif upgrade.PROTOSSGROUNDARMORSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSGROUNDARMORSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSGROUNDARMORSLEVEL1):
                    self.ai.do(forge.research(upgrade.PROTOSSGROUNDARMORSLEVEL1))
                elif upgrade.PROTOSSSHIELDSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSSHIELDSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL1):
                    self.ai.do(forge.research(upgrade.PROTOSSSHIELDSLEVEL1))
                elif upgrade.PROTOSSGROUNDARMORSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSGROUNDARMORSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSGROUNDARMORSLEVEL2):
                    self.ai.do(forge.research(upgrade.PROTOSSGROUNDARMORSLEVEL2))
                elif upgrade.PROTOSSGROUNDARMORSLEVEL2 in \
                        self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDARMORSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSGROUNDARMORSLEVEL3):
                    self.ai.do(forge.research(upgrade.PROTOSSGROUNDARMORSLEVEL3))
                elif upgrade.PROTOSSSHIELDSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSSHIELDSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL2) and \
                        upgrade.PROTOSSSHIELDSLEVEL1 in self.ai.state.upgrades and self.ai.structures(
                    unit.TWILIGHTCOUNCIL).ready.exists:
                    self.ai.do(forge.research(upgrade.PROTOSSSHIELDSLEVEL2))
                elif upgrade.PROTOSSSHIELDSLEVEL3 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSSHIELDSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL3) and \
                        upgrade.PROTOSSSHIELDSLEVEL2 in self.ai.state.upgrades:
                    self.ai.do(forge.research(upgrade.PROTOSSSHIELDSLEVEL3))

    def cybernetics_upgrade(self):
        cyber = self.ai.structures(unit.CYBERNETICSCORE).ready.idle
        if cyber.exists:
            if upgrade.WARPGATERESEARCH not in self.ai.state.upgrades and \
                    not self.ai.already_pending_upgrade(upgrade.WARPGATERESEARCH) and \
                    self.ai.can_afford(upgrade.WARPGATERESEARCH):
                self.ai.do(cyber.random.research(upgrade.WARPGATERESEARCH))

    async def twilight_upgrades(self):
        if upgrade.CHARGE not in self.ai.state.upgrades and self.ai.structures(unit.TWILIGHTCOUNCIL).ready.exists and \
                self.ai.army(unit.ZEALOT).amount > 4:
            tc = self.ai.structures(unit.TWILIGHTCOUNCIL).ready.idle
            if tc.exists:
                tc = tc.random
                abilities = await self.ai.get_available_abilities(tc)
                if ability.RESEARCH_CHARGE in abilities:
                    self.ai.do(tc(ability.RESEARCH_CHARGE))

    # =======================================================  Trainers
    async def train_units(self):
        await self.gate_train(3,1,0)
        await self.warp_units(max_archons=14,max_sentry=2,max_stalkers=7,max_adepts=0,max_zealots=12)
        self.robotics_train(12)

    
    async def warp_units(self, max_archons, max_sentry, max_stalkers, max_adepts, max_zealots):
        if self.ai.attack:
            prisms = self.ai.units(unit.WARPPRISMPHASING)
            if prisms.exists:
                pos = prisms.furthest_to(self.ai.start_location).position
            else:
                furthest_pylon = self.ai.structures(unit.PYLON).ready.furthest_to(self.ai.start_location.position)
                pos = furthest_pylon.position
        else:
            if (self.ai.structures(unit.ROBOTICSFACILITY).ready.idle.exists and
                self.ai.army(unit.IMMORTAL).amount < 5) or self.ai.forge_upg_priority() or not self.ai.structures(
                unit.WARPGATE).exists:
                return
            pos = self.ai.get_super_pylon().position
        placement = None
        i = 0
        while placement is None:
            i += 1
            placement = await self.ai.find_placement(ability.TRAINWARP_ADEPT, near=pos.random_on_distance(5),
                                                     max_distance=5, placement_step=2, random_alternative=False)
            if i > 5:
                print("can't find position for warpin.")
                return

        for warpgate in self.ai.structures(unit.WARPGATE).ready:
            abilities = await self.ai.get_available_abilities(warpgate)
            if ability.WARPGATETRAIN_ZEALOT in abilities:
                if self.ai.can_afford(unit.HIGHTEMPLAR) and self.ai.army(unit.ARCHON).amount < max_archons \
                        and self.ai.structures(unit.TEMPLARARCHIVE).ready.exists:
                    self.ai.do(warpgate.warp_in(unit.HIGHTEMPLAR, placement))
                elif self.ai.can_afford(unit.SENTRY) and self.ai.structures(unit.CYBERNETICSCORE).ready.exists \
                        and self.ai.units(unit.SENTRY).amount < max_sentry:
                    self.ai.do(warpgate.warp_in(unit.SENTRY, placement))
                elif self.ai.can_afford(unit.STALKER) and self.ai.army(unit.STALKER).amount < max_stalkers:
                    self.ai.do(warpgate.warp_in(unit.STALKER, placement))
                elif self.ai.can_afford(unit.ADEPT) and self.ai.structures(unit.CYBERNETICSCORE).ready.exists \
                        and self.ai.units(unit.ADEPT).amount < max_adepts:
                    self.ai.do(warpgate.warp_in(unit.ADEPT, placement))
                elif self.ai.minerals > 350 and \
                        self.ai.supply_left > 1 and self.ai.units(unit.ZEALOT).amount < max_zealots:
                    self.ai.do(warpgate.warp_in(unit.ZEALOT, placement))

    async def gate_train(self, max_stalkers, max_zealots, max_adepts):
        gateway = self.ai.structures(unit.GATEWAY).ready
        if gateway.idle.exists:
            if self.ai.can_afford(unit.STALKER) and self.ai.structures(unit.CYBERNETICSCORE).ready.exists and \
                    self.ai.army(unit.STALKER).amount < max_stalkers:
                u = unit.STALKER
            elif self.ai.minerals > 155 and self.ai.units(unit.ZEALOT).amount < max_zealots:
                u = unit.ZEALOT
            elif self.ai.can_afford(unit.ADEPT) and self.ai.structures(unit.CYBERNETICSCORE).ready.exists and \
                    self.ai.army(unit.ADEPT).amount < max_adepts:
                u = unit.ADEPT
            else:
                return
            gateway = gateway.ready.idle.random
            self.ai.do(gateway.train(u))

    def train_probes(self):
        workers = self.ai.workers.amount
        nex = self.ai.structures(unit.NEXUS).amount
        if not self.ai.structures(unit.PYLON).exists and workers == 14:
            return
        if workers < 20 * nex and workers < 55:
            for nexus in self.ai.structures(unit.NEXUS).ready:
                if nexus.is_idle and self.ai.can_afford(unit.PROBE):
                    self.ai.do(nexus.train(unit.PROBE))
        elif 54 < workers < 74:
            if self.ai.can_afford(unit.PROBE) and not self.ai.already_pending(unit.PROBE):
                if self.ai.structures(unit.NEXUS).idle.amount < nex:
                    return
                nexus = self.ai.structures(unit.NEXUS).ready.idle.random
                self.ai.do(nexus.train(unit.PROBE))

    def robotics_train(self, max_immortals):
        robotics = self.ai.structures(unit.ROBOTICSFACILITY).ready.idle
        if robotics.exists:
            immortals = self.ai.units(unit.IMMORTAL)
            if self.ai.units(unit.OBSERVER).amount + self.ai.units(unit.OBSERVERSIEGEMODE).amount < 1 and \
                    self.ai.can_afford(unit.OBSERVER):
                for factory in robotics:
                    self.ai.do(factory.train(unit.OBSERVER))
                    break
            elif self.ai.units(unit.WARPPRISMPHASING).amount + self.ai.units(unit.WARPPRISM).amount < 1 \
                    and self.ai.can_afford(unit.WARPPRISM) and not self.ai.already_pending(
                unit.WARPPRISM) and (immortals.amount > 1 or self.ai.attack):
                for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
                    self.ai.do(factory.train(unit.WARPPRISM))
                    break
            # elif self.ai.can_afford(unit.COLOSSUS) and self.ai.supply_left > 5 and self.ai.structures(
            #         unit.ROBOTICSBAY).ready.exists \
            #         and self.ai.units(unit.COLOSSUS).amount < 3:
            #     for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
            #         self.ai.do(factory.train(unit.COLOSSUS))
            # elif self.ai.can_afford(unit.DISRUPTOR) and self.ai.supply_left > 3 and self.ai.structures(
            #         unit.ROBOTICSBAY).ready.exists \
            #         and self.ai.units(unit.DISRUPTOR).amount < 3:
            #     for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
            #         self.ai.do(factory.train(unit.DISRUPTOR))
            else:
                for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
                    if self.ai.can_afford(unit.IMMORTAL) and immortals.amount < max_immortals:
                        self.ai.do(factory.train(unit.IMMORTAL))

    # =======================================================  Army

    async def micro(self):
        def __in_grid(self, pos):
            try:
                return self.ai.in_pathing_grid(pos)
            except:
                return False

        enemy = self.ai.enemy_units()
        if not enemy.exists:
            return

        def chunk(lst, n):
            for k in range(0, len(lst), n):
                yield lst[k:k + n]

        # stalkers // mixed
        whole_army = self.ai.army.exclude_type({unit.ZEALOT, unit.DARKTEMPLAR, unit.WARPPRISM, unit.WARPPRISMPHASING})
        dist = 7
        group_size = 5
        c = int(len(whole_army) / group_size)
        chunks = c if c > 0 else 1
        part_army = chunk(whole_army, chunks)
        for army_l in part_army:
            army = Units(army_l, self.ai)
            if army.exists:
                # leader = self.ai.leader
                # if leader is None:
                if self.ai.destination is not None:
                    leader = army.closest_to(self.ai.destination)
                else:
                    leader = army.random
                threats = enemy.filter(
                    lambda unit_: (unit_.can_attack_ground or unit_.type_id == unit.DISRUPTOR)
                                  and unit_.distance_to(leader) <= dist and
                                  unit_.type_id not in self.ai.units_to_ignore)
                if self.ai.attack:
                    threats.extend(
                        self.ai.enemy_structures().filter(lambda _x: _x.can_attack_ground or _x.can_attack_air or
                                                                     _x.type_id == unit.BUNKER))
                if threats.exists:
                    closest_enemy = threats.closest_to(leader)
                    priority = threats.filter(lambda x1: x1.type_id in [unit.COLOSSUS, unit.DISRUPTOR, unit.HIGHTEMPLAR,
                                                                        unit.MEDIVAC, unit.SIEGETANKSIEGED,
                                                                        unit.SIEGETANK, unit.THOR, unit.BUNKER,
                                                                        unit.QUEEN, unit.LIBERATOR])
                    if priority.exists:
                        targets = priority.sorted(lambda x1: x1.health + x1.shield)
                        if self.ai.enemy_race == Race.Protoss:
                            a = targets[0].shield_percentage
                        else:
                            a = 1
                        if targets[0].health_percentage * a == 1:
                            target = priority.closest_to(leader)
                        else:
                            target = targets[0]
                    else:
                        targets = threats.sorted(lambda x1: x1.health + x1.shield)
                        if self.ai.enemy_race == Race.Protoss:
                            a = targets[0].shield_percentage
                        else:
                            a = 1
                        if targets[0].health_percentage * a == 1:
                            target = closest_enemy
                        else:
                            target = targets[0]
                    if target.distance_to(leader) > leader.distance_to(closest_enemy) + 4:
                        target = closest_enemy

                    i = 3
                    pos = leader.position.towards(closest_enemy.position, -i)
                    while not __in_grid(self, pos) and i < 12:
                        # print('func i: ' + str(i))
                        pos = leader.position.towards(closest_enemy.position, -i)
                        i += 1
                        j = 1
                        while not __in_grid(self, pos) and j < 9:
                            # print('func j: ' + str(j))
                            pos = pos.random_on_distance(j)
                            j += 1
                    for st in army:
                        if st.shield_percentage < 0.25:
                            if st.health_percentage < 0.35:
                                self.ai.do(st.move(pos))
                                continue
                            else:
                                d = 4
                        else:
                            d = 2

                        if pos is not None and st.weapon_cooldown > 0:
                            if not await self.ai.blink(st, pos):
                                self.ai.do(st.move(st.position.towards(pos, d)))
                        elif not st.is_attacking:
                            self.ai.do(st.attack(target))

        #  Sentry region  #
        sents = self.ai.army(unit.SENTRY)
        if sents.exists:
            m = -1
            sentry = None
            for se in sents:
                close = sents.closer_than(7, se).amount
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
            has_energy_amount = sents.filter(lambda x2: x2.energy >= 50).amount
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

        # Carrier
        for cr in self.ai.army(unit.CARRIER):
            threats = self.ai.enemy_units().filter(
                lambda z: z.distance_to(cr) < 12 and z.type_id not in self.ai.units_to_ignore)
            threats.extend(
                self.ai.enemy_structures().filter(lambda z: z.can_attack_air or z.type_id in self.ai.bases_ids))
            if threats.exists:
                # target2 = None
                priority = threats.filter(lambda z: z.can_attack_air).sorted(lambda z: z.air_dps, reverse=True)
                if priority.exists:
                    # closest = priority.closest_to(cr)
                    # if cr.distance_to(closest) < 7:
                    #     self.ai.do(cr.move(cr.position.towards(closest,-3)))
                    # else:
                    if priority.amount > 2:
                        priority = sorted(priority[:int(len(priority) / 2)], key=lambda z: z.health + z.shield)
                    target2 = priority[0]
                else:
                    target2 = threats.sorted(lambda z: z.health + z.shield)[0]
                if target2 is not None:
                    self.ai.do(cr.attack(target2))

            # high templar
        for ht in whole_army(unit.HIGHTEMPLAR):
            # if enemy.exists:
            _enemy = enemy.closer_than(9, ht)
            if _enemy.amount > 5:
                # if low energy, go behind army, else to front
                army = whole_army.closer_than(7, ht)
                if ht.energy < 50 or ht.is_idle:
                    en = _enemy.closest_to(ht)
                    place = army.furthest_to(en).position.towards(en, -7)
                    if ht.distance_to(place) > 3:
                        self.ai.do(ht.move(place))
                # Cast spells   ---> look for group of enemy
                spell_target = _enemy.filter(
                    lambda unit_: not unit_.is_structure and unit_.type_id not in self.ai.workers and
                                  unit_.type_id not in self.ai.units_to_ignore)
                target = None
                if spell_target.amount > 5:
                    abilities = await self.ai.get_available_abilities(ht)
                    # medivacs = spell_target.filter(lambda x: x.type_id == unit.MEDIVAC)
                    if ability.PSISTORM_PSISTORM in abilities and \
                            self.ai.time - self.ai.psi_storm_wait > 1.4:
                        maxNeighbours = 0
                        for en in spell_target:
                            neighbours = _enemy.filter(lambda u: u.distance_to(en) <= 1.5)
                            if neighbours.amount > maxNeighbours:
                                maxNeighbours = neighbours.amount
                                target = en
                        if target is not None and self.ai.army.closer_than(1.7, target).amount < 3:
                            print("Casting Psi Storm on " + str(maxNeighbours + 1) + " units.")
                            self.ai.do(ht(ability.PSISTORM_PSISTORM, target.position))
                            self.ai.psi_storm_wait = self.ai.time

                    elif ability.FEEDBACK_FEEDBACK in abilities:
                        spell_target = spell_target.filter(lambda z: z.energy > 100).exclude_type({unit.OVERSEER})
                        if spell_target.exists:
                            spell_target = spell_target.sorted(lambda z: z.energy, reverse=True)
                            target = spell_target[0]
                            print("Casting Feedback on " + target.name + " with " + str(target.energy) + " energy.")
                            self.ai.do(ht(ability.FEEDBACK_FEEDBACK, target))
                            break

        # Disruptor
        zealots = self.ai.army(unit.ZEALOT)
        disruptors = self.ai.army(unit.DISRUPTOR)
        for dr in disruptors:
            # Cast spells   ---> look for group of enemy
            abilities = await self.ai.get_available_abilities(dr)
            if self.ai.time - self.ai.nova_wait >= 1 and ability.EFFECT_PURIFICATIONNOVA in abilities:  #
                spell_target = enemy.filter(
                    lambda unit_: not unit_.is_structure and unit_.distance_to(dr) < 12
                                  and unit_.type_id not in self.ai.units_to_ignore and unit_.type_id not in self.ai.workers_ids
                                  and not unit_.is_flying)
                target = None
                if spell_target.amount > 2:
                    tanks = spell_target.filter(lambda x: x.type_id == unit.SIEGETANKSIEGED or x.type_id == unit.THOR)
                    if tanks.amount > 1:
                        spell_target = tanks

                    maxNeighbours = 0
                    for en in spell_target:
                        neighbours = enemy.filter(lambda unit_: not unit_.is_flying and not
                        unit_.is_structure and unit_.distance_to(en) <= 1.5)
                        if neighbours.amount > maxNeighbours:
                            maxNeighbours = neighbours.amount
                            target = en
                    if target is not None and self.ai.army.closer_than(2.4, target).amount < 3:
                        dist = await self.ai._client.query_pathing(dr.position, target.position)
                        if dist is not None and dist <= 13:
                            print("Casting Purification nova on " + str(maxNeighbours + 1) + " units.")
                            self.ai.nova_wait = self.ai.time
                            self.ai.do(dr(ability.EFFECT_PURIFICATIONNOVA, target.position))
            else:
                threat = enemy.closer_than(7, dr)
                if threat.exists:
                    self.ai.do(dr.move(dr.position.towards(threat.closest_to(dr), -5)))
        # Disruptor purification nova
        if self.ai.time - self.ai.nova_wait > 0.4:
            for nova in self.ai.units(unit.DISRUPTORPHASED):
                spell_target = enemy.filter(lambda unit_: not unit_.is_structure and unit_.distance_to(nova) < 9
                                                          and unit_.type_id not in self.ai.units_to_ignore and not unit_.is_flying and unit_.type_id
                                                          not in self.ai.workers_ids)
                target = None
                if spell_target.amount > 0:
                    tanks = spell_target.filter(lambda x: x.type_id == unit.SIEGETANKSIEGED)
                    if tanks.amount > 0:
                        spell_target = tanks
                    maxNeighbours = 0
                    for en in spell_target:
                        neighbours = enemy.filter(
                            lambda unit_: not unit_.is_structure and unit_.distance_to(nova) <= 1.5
                                          and unit_.type_id not in self.ai.units_to_ignore and not unit_.is_flying and unit_.type_id
                                          not in self.ai.workers_ids)
                        if neighbours.amount > maxNeighbours:
                            maxNeighbours = neighbours.amount
                            target = en
                    if target is not None:
                        # if self.ai.army.closer_than(3,target).amount < 2:
                        print("Steering Purification nova to " + str(maxNeighbours + 1) + " units.")
                        self.ai.do(nova.move(target.position.towards(nova, -2)))

        for wp in self.ai.army(unit.WARPPRISM):
            threats = self.ai.enemy_units().filter(lambda x: x.can_attack_air and x.distance_to(wp) < 11)
            for t in threats:
                if t.target_in_range(wp):
                    self.ai.do(wp.move(wp.position.towards(t, -5)))
        for wp in self.ai.army(unit.WARPPRISMPHASING):
            threats = self.ai.enemy_units().filter(lambda x: x.can_attack_air and x.distance_to(wp) < 11)
            for t in threats:
                if t.target_in_range(wp):
                    abilities = await self.ai.get_available_abilities(wp)
                    if ability.MORPH_WARPPRISMTRANSPORTMODE in abilities:
                        self.ai.do(wp(ability.MORPH_WARPPRISMTRANSPORTMODE))
                        self.ai.do(wp.move(wp.position.towards(t, -5), queue=True))

        for dt in self.ai.army(unit.DARKTEMPLAR):
            threats = self.ai.enemy_units().filter(lambda x2: x2.distance_to(dt) < 9 and not x2.is_flying and
                                                              x2.type_id not in self.ai.units_to_ignore).sorted(
                lambda _x: _x.health + _x.shield)
            if threats.exists:
                closest = threats.closest_to(dt)
                if threats[0].health_percentage * threats[0].shield_percentage == 1 or threats[0].distance_to(dt) > \
                        closest.distance_to(dt) + 3 or not self.ai.in_pathing_grid(threats[0]):
                    target = closest
                else:
                    target = threats[0]
                self.ai.do(dt.attack(target))

        # zealot
        for zl in zealots.filter(lambda z: not z.is_attacking):
            threats = self.ai.enemy_units().filter(lambda x2: x2.distance_to(zl) < 7).sorted(
                lambda _x: _x.health + _x.shield)
            if threats.exists:
                closest = threats.closest_to(zl)
                if self.ai.enemy_race == Race.Protoss:
                    a = threats[0].shield_percentage
                else:
                    a = 1
                dist = await self.ai._client.query_pathing(zl.position, threats[0].position)
                if threats[0].health_percentage * a == 1 or dist is None or dist > closest.distance_to(zl) + 4:
                    target = closest
                else:
                    target = threats[0]
                if not zl.is_attacking:
                    if ability.EFFECT_CHARGE in await self.ai.get_available_abilities(zl):
                        self.ai.do(zl(ability.EFFECT_CHARGE, target))
                    else:
                        self.ai.do(zl.attack(target))

    async def movements(self):
        enemy_units = self.ai.enemy_units()
        enemy = enemy_units.filter(lambda x: x.type_id not in self.ai.units_to_ignore and (x.can_attack_ground
                                                                                           or x.can_attack_air))
        enemy.extend(self.ai.enemy_structures().filter(lambda b: b.type_id in self.ai.bases_ids
                                                                 or b.can_attack_ground or b.can_attack_air or b.type_id == unit.BUNKER))
        if self.ai.enemy_main_base_down or (
                self.ai.army.closer_than(20, self.ai.enemy_start_locations[0]).amount > 17 and
                not self.ai.enemy_structures().exists):
            if not self.ai.enemy_main_base_down:
                await self.ai.chat_send('enemy main base down.')
                self.ai.enemy_main_base_down = True
            self.ai.scan()
            enemy_units.extend(self.ai.enemy_structures())
            if enemy_units.exists:
                for man in self.ai.army.exclude_type(unit.OBSERVER):
                    self.ai.do(man.attack(enemy_units.closest_to(man)))

        if enemy.amount > 1:
            if enemy.closer_than(25, self.ai.start_location).amount > 1:
                destination = enemy.closest_to(self.ai.start_location).position
            else:
                destination = enemy.further_than(25, self.ai.start_location)
                if destination:
                    destination = destination.closest_to(self.ai.start_location).position
                elif self.ai.enemy_structures().exists:
                    enemy = self.ai.enemy_structures()
                    destination = enemy.closest_to(self.ai.start_location).position
                else:
                    enemy = None
                    destination = self.ai.enemy_start_locations[0].position
        elif self.ai.enemy_structures().exists:
            enemy = self.ai.enemy_structures()
            destination = enemy.closest_to(self.ai.start_location).position
        else:
            enemy = None
            if self.ai.enemy_main_base_down:
                if len(self.ai.observer_scouting_points) == 0:
                    for exp in self.ai.expansion_locations:
                        if not self.ai.structures().closer_than(7, exp).exists:
                            self.ai.observer_scouting_points.append(exp)
                    self.ai.observer_scouting_points = sorted(self.ai.observer_scouting_points,
                                                              key=lambda x: self.ai.enemy_start_locations[
                                                                  0].distance_to(x))
                if self.ai.army() and self.ai.army().closer_than(12, self.ai.observer_scouting_points[
                    self.ai.observer_scouting_index]).amount > 12 \
                        and self.ai.enemy_structures().amount < 1:
                    self.ai.observer_scouting_index += 1
                    if self.ai.observer_scouting_index == len(self.ai.observer_scouting_points):
                        self.ai.observer_scouting_index = 0
                destination = self.ai.observer_scouting_points[self.ai.observer_scouting_index]
            else:
                destination = self.ai.enemy_start_locations[0].position

        if self.ai.leader_tag is None or self.ai.army.find_by_tag(self.ai.leader_tag) is None:
            self.ai.leader_tag = self.ai.army.closest_to(destination).tag

        leader = self.ai.army.find_by_tag(self.ai.leader_tag)
        self.ai.destination = destination

        # point halfway
        dist = leader.distance_to(destination)
        step = 23
        if dist > step:
            point = leader.position.towards(destination, step)
        else:
            point = destination
        position = None
        i = 0
        while position is None:
            i += 1
            position = await self.ai.find_placement(unit.PYLON, near=point.random_on_distance(i * 2), max_distance=5,
                                                    placement_step=2, random_alternative=False)
            if i > 7:
                print("can't find position for army.")
                return
        # if everybody's here, we can go
        army = self.ai.army
        _range = 7 if army.amount < 27 else 14
        nearest = []
        i = 3
        pos = leader.position
        while not self.ai.in_pathing_grid(pos) and i < 6:
            pos = leader.position.random_on_distance(i)
            i += 1
            j = 1
            while not self.ai.in_pathing_grid(pos) and j < 3:
                # print('func j: ' + str(j))
                pos = pos.random_on_distance(j)
                j += 1
        for man in army:
            if man.distance_to(leader) <= _range:  # with army
                nearest.append(man)
                if enemy and not enemy.in_attack_range_of(man).exists:
                    # go help someone who is fighting
                    h = army.filter(lambda x: x.is_attacking)
                    if h.exists:
                        self.ai.do(man.attack(enemy.closest_to(h.closest_to(man))))
            elif man.type_id not in [unit.ZEALOT, unit.DARKTEMPLAR] or not man.is_attacking:  # away. join army
                self.ai.do(man.move(pos))
        if len(nearest) > len(self.ai.army) * 0.70:  # take next position
            if enemy and enemy.closer_than(11, leader).exists:
                return
            for man in army:
                self.ai.do(man.attack(position))

    # ======================================================= Conditions

    # ======================================================== Buffs
    def chronoboost(self):
        try:
            self.chronobooster.standard()
        except Exception as ex:
            print(ex)

    def build_assimilators(self):
        if self.ai.structures().filter(lambda x: x.type_id in [unit.GATEWAY, unit.WARPGATE]).amount == 0 or\
                (self.ai.structures(unit.NEXUS).ready.amount > 1 and self.ai.vespene > self.ai.minerals):
            return
        nexuses = self.ai.structures(unit.NEXUS)
        if nexuses.amount < 4:
            nexuses = nexuses.ready
        probes = self.ai.units(unit.PROBE)
        if probes.exists:
            for nexus in nexuses:
                vespenes = self.ai.vespene_geyser.closer_than(9,nexus)
                workers = probes.closer_than(12, nexus)
                if workers.amount > 14 or nexuses.amount > 3:
                    for vespene in vespenes:
                        if (not self.ai.already_pending(unit.ASSIMILATOR)) and (not
                        self.ai.structures(unit.ASSIMILATOR).exists or not
                        self.ai.structures(unit.ASSIMILATOR).closer_than(3, vespene).exists):
                            if not self.ai.can_afford(unit.ASSIMILATOR):
                                return
                            worker = self.ai.select_build_worker(vespene.position)
                            if worker is None:
                                break
                            self.ai.do(worker.build(unit.ASSIMILATOR,vespene))
                            self.ai.do(worker.move(worker.position.random_on_distance(1), queue=True))
