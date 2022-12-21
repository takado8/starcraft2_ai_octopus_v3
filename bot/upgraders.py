from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.ids.ability_id import AbilityId as ability


class ForgeUpgrader:
    def __init__(self, ai):
        self.ai = ai

    def none(self):
        pass

    def standard(self):
        for forge in self.ai.structures(unit.FORGE).ready.idle:
            if upgrade.PROTOSSGROUNDWEAPONSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDWEAPONSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSGROUNDWEAPONSLEVEL1):
                forge.research(upgrade.PROTOSSGROUNDWEAPONSLEVEL1)
            elif upgrade.PROTOSSGROUNDWEAPONSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDWEAPONSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSGROUNDWEAPONSLEVEL2) and \
                    self.ai.structures(unit.TWILIGHTCOUNCIL).exists:
                forge.research(upgrade.PROTOSSGROUNDWEAPONSLEVEL2)
            elif self.ai.already_pending_upgrade(upgrade.PROTOSSGROUNDWEAPONSLEVEL2) or \
                    upgrade.PROTOSSGROUNDWEAPONSLEVEL2 in self.ai.state.upgrades or \
                    not self.ai.structures(unit.TWILIGHTCOUNCIL).exists:
                if upgrade.PROTOSSGROUNDWEAPONSLEVEL2 in \
                        self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDWEAPONSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSGROUNDWEAPONSLEVEL3):
                    forge.research(upgrade.PROTOSSGROUNDWEAPONSLEVEL3)
                elif upgrade.PROTOSSGROUNDARMORSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSGROUNDARMORSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSGROUNDARMORSLEVEL1):
                    forge.research(upgrade.PROTOSSGROUNDARMORSLEVEL1)
                elif upgrade.PROTOSSSHIELDSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSSHIELDSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL1):
                    forge.research(upgrade.PROTOSSSHIELDSLEVEL1)
                elif upgrade.PROTOSSGROUNDARMORSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSGROUNDARMORSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSGROUNDARMORSLEVEL2):
                    forge.research(upgrade.PROTOSSGROUNDARMORSLEVEL2)
                elif upgrade.PROTOSSGROUNDARMORSLEVEL2 in \
                        self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDARMORSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSGROUNDARMORSLEVEL3):
                    forge.research(upgrade.PROTOSSGROUNDARMORSLEVEL3)
                elif upgrade.PROTOSSSHIELDSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSSHIELDSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL2) and \
                        upgrade.PROTOSSSHIELDSLEVEL1 in self.ai.state.upgrades and self.ai.structures(
                    unit.TWILIGHTCOUNCIL).ready.exists:
                    forge.research(upgrade.PROTOSSSHIELDSLEVEL2)
                elif upgrade.PROTOSSSHIELDSLEVEL3 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSSHIELDSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL3) and \
                        upgrade.PROTOSSSHIELDSLEVEL2 in self.ai.state.upgrades:
                    forge.research(upgrade.PROTOSSSHIELDSLEVEL3)

    def shield(self):
        for forge in self.ai.structures(unit.FORGE).ready.idle:
            if upgrade.PROTOSSSHIELDSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSSHIELDSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL1):
                forge.research(upgrade.PROTOSSSHIELDSLEVEL1)
            elif upgrade.PROTOSSSHIELDSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSSHIELDSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL2) and \
                     upgrade.PROTOSSSHIELDSLEVEL1 in self.ai.state.upgrades and self.ai.structures(
                    unit.TWILIGHTCOUNCIL).ready.exists:
                forge.research(upgrade.PROTOSSSHIELDSLEVEL2)
            elif upgrade.PROTOSSSHIELDSLEVEL3 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSSHIELDSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL3) and \
                    upgrade.PROTOSSSHIELDSLEVEL2 in self.ai.state.upgrades:
                forge.research(upgrade.PROTOSSSHIELDSLEVEL3)

    def armor_first(self):
        for forge in self.ai.structures(unit.FORGE).ready.idle:
            if upgrade.PROTOSSGROUNDARMORSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDARMORSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSGROUNDARMORSLEVEL1):
                forge.research(upgrade.PROTOSSGROUNDARMORSLEVEL1)
            elif upgrade.PROTOSSSHIELDSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSSHIELDSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL1):
                forge.research(upgrade.PROTOSSSHIELDSLEVEL1)
            elif upgrade.PROTOSSGROUNDARMORSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDARMORSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSGROUNDARMORSLEVEL2) and \
                    self.ai.structures(unit.TWILIGHTCOUNCIL).exists:
                forge.research(upgrade.PROTOSSGROUNDARMORSLEVEL2)
            elif upgrade.PROTOSSSHIELDSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSSHIELDSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL2) and \
                    self.ai.structures(unit.TWILIGHTCOUNCIL).exists:
                forge.research(upgrade.PROTOSSSHIELDSLEVEL2)
            elif (self.ai.already_pending_upgrade(upgrade.PROTOSSSHIELDSLEVEL2) and upgrade.PROTOSSGROUNDARMORSLEVEL2
                  in self.ai.state.upgrades) or (self.ai.already_pending_upgrade(upgrade.PROTOSSGROUNDARMORSLEVEL2) and
                  upgrade.PROTOSSSHIELDSLEVEL2 in self.ai.state.upgrades) or \
                    (upgrade.PROTOSSGROUNDARMORSLEVEL2 in self.ai.state.upgrades and
                     upgrade.PROTOSSSHIELDSLEVEL2 in self.ai.state.upgrades) or \
                    not self.ai.structures(unit.TWILIGHTCOUNCIL).exists:
                if upgrade.PROTOSSGROUNDARMORSLEVEL2 in \
                        self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDARMORSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSGROUNDARMORSLEVEL3):
                    forge.research(upgrade.PROTOSSGROUNDARMORSLEVEL3)
                elif upgrade.PROTOSSSHIELDSLEVEL2 in \
                        self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSSHIELDSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSSHIELDSLEVEL3):
                    forge.research(upgrade.PROTOSSSHIELDSLEVEL3)
                elif upgrade.PROTOSSGROUNDWEAPONSLEVEL1 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSGROUNDWEAPONSLEVEL1) and self.ai.can_afford(upgrade.PROTOSSGROUNDWEAPONSLEVEL1):
                    forge.research(upgrade.PROTOSSGROUNDWEAPONSLEVEL1)
                elif upgrade.PROTOSSGROUNDWEAPONSLEVEL2 not in self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                        upgrade.PROTOSSGROUNDWEAPONSLEVEL2) and self.ai.can_afford(upgrade.PROTOSSGROUNDWEAPONSLEVEL2):
                    forge.research(upgrade.PROTOSSGROUNDWEAPONSLEVEL2)
                elif upgrade.PROTOSSGROUNDWEAPONSLEVEL2 in \
                        self.ai.state.upgrades and not self.ai.already_pending_upgrade(
                    upgrade.PROTOSSGROUNDWEAPONSLEVEL3) and self.ai.can_afford(upgrade.PROTOSSGROUNDWEAPONSLEVEL3):
                    forge.research(upgrade.PROTOSSGROUNDWEAPONSLEVEL3)


class CyberneticsUpgrader:
    def __init__(self, ai):
        self.ai = ai

    def warpgate(self):
        cyber = self.ai.structures(unit.CYBERNETICSCORE).ready.idle
        if cyber.exists:
            if upgrade.WARPGATERESEARCH not in self.ai.state.upgrades and \
                    not self.ai.already_pending_upgrade(upgrade.WARPGATERESEARCH) and \
                    self.ai.can_afford(upgrade.WARPGATERESEARCH):
                cyber.random.research(upgrade.WARPGATERESEARCH)

    def air_dmg(self):
        if self.ai.units().filter(lambda x: x.type_id in [unit.ORACLE, unit.VOIDRAY, unit.CARRIER,
                                                          unit.TEMPEST] and x.is_ready).exists:
            cyber = self.ai.structures(unit.CYBERNETICSCORE).ready.idle
            if cyber.exists:
                if upgrade.PROTOSSAIRWEAPONSLEVEL1 not in self.ai.state.upgrades and self.ai.can_afford(
                        upgrade.PROTOSSAIRWEAPONSLEVEL1) and \
                        not self.ai.already_pending_upgrade(upgrade.PROTOSSAIRWEAPONSLEVEL1):
                    cyber.random.research(upgrade.PROTOSSAIRWEAPONSLEVEL1)
                elif upgrade.PROTOSSAIRWEAPONSLEVEL2 not in self.ai.state.upgrades and self.ai.can_afford(
                        upgrade.PROTOSSAIRWEAPONSLEVEL2) and \
                        not self.ai.already_pending_upgrade(upgrade.PROTOSSAIRWEAPONSLEVEL2):
                    cyber.random.research(upgrade.PROTOSSAIRWEAPONSLEVEL2)
                elif upgrade.PROTOSSAIRWEAPONSLEVEL3 not in self.ai.state.upgrades and self.ai.can_afford(
                        upgrade.PROTOSSAIRWEAPONSLEVEL3) and \
                        not self.ai.already_pending_upgrade(upgrade.PROTOSSAIRWEAPONSLEVEL3):
                    cyber.random.research(upgrade.PROTOSSAIRWEAPONSLEVEL3)
                elif upgrade.PROTOSSAIRWEAPONSLEVEL3 in self.ai.state.upgrades or\
                    (self.ai.structures(unit.CYBERNETICSCORE).ready.amount > 1 and cyber.amount < 2):
                    if upgrade.PROTOSSAIRARMORSLEVEL1 not in self.ai.state.upgrades and self.ai.can_afford(
                            upgrade.PROTOSSAIRARMORSLEVEL1) and \
                            not self.ai.already_pending_upgrade(upgrade.PROTOSSAIRARMORSLEVEL1):
                        cyber.random.research(upgrade.PROTOSSAIRARMORSLEVEL1)
                    elif upgrade.PROTOSSAIRARMORSLEVEL2 not in self.ai.state.upgrades and self.ai.can_afford(
                            upgrade.PROTOSSAIRARMORSLEVEL2) and \
                            not self.ai.already_pending_upgrade(upgrade.PROTOSSAIRARMORSLEVEL2):
                        cyber.random.research(upgrade.PROTOSSAIRARMORSLEVEL2)
                    elif upgrade.PROTOSSAIRARMORSLEVEL3 not in self.ai.state.upgrades and self.ai.can_afford(
                            upgrade.PROTOSSAIRARMORSLEVEL3) and \
                            not self.ai.already_pending_upgrade(upgrade.PROTOSSAIRARMORSLEVEL3):
                        cyber.random.research(upgrade.PROTOSSAIRARMORSLEVEL3)


class TwilightUpgrader:
    def __init__(self, ai):
        self.ai = ai

    async def none(self):
        pass

    async def charge(self):
        if upgrade.CHARGE not in self.ai.state.upgrades and self.ai.structures(unit.TWILIGHTCOUNCIL).ready.exists and \
                self.ai.army(unit.ZEALOT).amount > 4:
            tc = self.ai.structures(unit.TWILIGHTCOUNCIL).ready.idle
            if tc.exists:
                tc = tc.random
                abilities = await self.ai.get_available_abilities(tc)
                if ability.RESEARCH_CHARGE in abilities:
                    tc(ability.RESEARCH_CHARGE)

    async def blink(self):
        if upgrade.BLINKTECH not in self.ai.state.upgrades and self.ai.structures(unit.TWILIGHTCOUNCIL).ready.exists:
            tc = self.ai.structures(unit.TWILIGHTCOUNCIL).ready.idle
            if tc.exists:
                tc = tc.random
                abilities = await self.ai.get_available_abilities(tc)
                if ability.RESEARCH_BLINK in abilities:
                    tc(ability.RESEARCH_BLINK)

    async def both(self):
        if self.ai.structures(unit.TWILIGHTCOUNCIL).ready.exists:
            if upgrade.CHARGE not in self.ai.state.upgrades:
                tc = self.ai.structures(unit.TWILIGHTCOUNCIL).ready.idle
                if tc.exists:
                    tc = tc.random
                    abilities = await self.ai.get_available_abilities(tc)
                    if ability.RESEARCH_CHARGE in abilities:
                        tc(ability.RESEARCH_CHARGE)
            elif upgrade.BLINKTECH not in self.ai.state.upgrades:
                tc = self.ai.structures(unit.TWILIGHTCOUNCIL).ready.idle
                if tc.exists:
                    tc = tc.random
                    abilities = await self.ai.get_available_abilities(tc)
                    if ability.RESEARCH_BLINK in abilities:
                        tc(ability.RESEARCH_BLINK)

    async def standard(self):
        if self.ai.structures(unit.TWILIGHTCOUNCIL).ready.exists:
            tc = self.ai.structures(unit.TWILIGHTCOUNCIL).ready.idle
            if tc.exists:
                tc = tc.random
                research = None
                abilities = await self.ai.get_available_abilities(tc)
                if self.ai.army(unit.STALKER).amount > 6 and upgrade.BLINKTECH not in self.ai.state.upgrades:
                    if ability.RESEARCH_BLINK in abilities:
                        research = ability.RESEARCH_BLINK
                elif upgrade.CHARGE not in self.ai.state.upgrades and self.ai.army(unit.ZEALOT).amount > 4:
                    if ability.RESEARCH_CHARGE in abilities:
                        research = ability.RESEARCH_CHARGE
                elif self.ai.army(unit.ADEPT).amount > 2 and \
                        ability.RESEARCH_ADEPTRESONATINGGLAIVES in abilities:
                    research = ability.RESEARCH_ADEPTRESONATINGGLAIVES
                if research:
                    tc(research)


class TemplarArchiveUpgrader:
    def __init__(self, ai):
        self.ai = ai

    async def none(self):
        pass

    async def storm(self):
        if upgrade.PSISTORMTECH not in self.ai.state.upgrades:
            tc = self.ai.structures(unit.TEMPLARARCHIVE).ready.idle
            if tc.exists:
                tc = tc.random
                abilities = await self.ai.get_available_abilities(tc)
                if ability.RESEARCH_PSISTORM in abilities:
                    tc(ability.RESEARCH_PSISTORM)


class FleetBeaconUpgrader:
    def __init__(self, ai):
        self.ai = ai

    async def voidrays(self):
        fleet = self.ai.structures(unit.FLEETBEACON).ready
        if fleet.exists:
            fleet = fleet.random
            if ability.FLEETBEACONRESEARCH_RESEARCHVOIDRAYSPEEDUPGRADE in await self.ai.get_available_abilities(fleet):
                fleet(ability.FLEETBEACONRESEARCH_RESEARCHVOIDRAYSPEEDUPGRADE)


class RoboticsBayUpgrader:
    def __init__(self, ai):
        self.ai = ai

    async def thermal_lances(self):
        colossi = self.ai.army(unit.COLOSSUS).ready
        if colossi.exists:
            bay = self.ai.structures(unit.ROBOTICSBAY).ready
            if bay.exists:
                bay = bay.first
                if ability.RESEARCH_EXTENDEDTHERMALLANCE in await self.ai.get_available_abilities(bay):
                    bay(ability.RESEARCH_EXTENDEDTHERMALLANCE)