from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.ids.ability_id import AbilityId as ability


class EvolutionStrategy:
    def __init__(self, ai):
        self.ai = ai
        self.type = 'macro'
        self.name = 'evo'

    # =======================================================  Builders
    def build_gateway(self, max_count):
        gates_count = self.ai.structures(unit.GATEWAY).amount
        gates_count += self.ai.structures(unit.WARPGATE).amount

        pylon = self.ai.get_pylon_with_least_neighbours()
        if gates_count < max_count and self.ai.can_afford(unit.GATEWAY) and pylon and \
                self.ai.already_pending(unit.GATEWAY) < 1:
            await self.ai.build(unit.GATEWAY, near=pylon, placement_step=3, max_distance=12,
                                random_alternative=True)

    def build_cybernetics(self, max_count):
        if self.ai.structures(unit.CYBERNETICSCORE).amount < max_count and not self.ai.already_pending(
                unit.CYBERNETICSCORE) and \
                self.ai.structures(unit.GATEWAY).ready.exists:
            cybernetics_position = self.ai.get_pylon_with_least_neighbours()
            if cybernetics_position:
                await self.ai.build(unit.CYBERNETICSCORE, near=cybernetics_position, placement_step=3,
                                    random_alternative=True, max_distance=20)

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

    def twilight_upgrades(self):
        if upgrade.CHARGE not in self.ai.state.upgrades and self.ai.structures(unit.TWILIGHTCOUNCIL).ready.exists and \
                self.ai.army(unit.ZEALOT).amount > 4:
            tc = self.ai.structures(unit.TWILIGHTCOUNCIL).ready.idle
            if tc.exists:
                tc = tc.random
                abilities = await self.ai.get_available_abilities(tc)
                if ability.RESEARCH_CHARGE in abilities:
                    self.ai.do(tc(ability.RESEARCH_CHARGE))

    # =======================================================  Trainers
    def warp_units(self, max_archons, max_sentry, max_stalkers, max_adepts, max_zealots):
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
                elif self.ai.can_afford(unit.ADEPT) and self.ai.structures(unit.CYBERNETICSCORE).ready.exists\
                        and self.ai.units(unit.ADEPT).amount < max_adepts:
                    self.ai.do(warpgate.warp_in(unit.ADEPT, placement))
                elif self.ai.minerals > 350 and \
                        self.ai.supply_left > 1 and self.ai.units(unit.ZEALOT).amount < max_zealots:
                    self.ai.do(warpgate.warp_in(unit.ZEALOT, placement))

    def gate_train(self, max_stalkers, max_zealots, max_adepts):
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

    # =======================================================  Army

    async def micro(self):
        await self._micro.new()

    async def movements(self):
        await self._movements.attack_formation_brand_new_newest_thee_most_new_shit_in_whole_wide_world()

    # ======================================================= Conditions

    # ======================================================== Buffs
