from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.ids.ability_id import AbilityId


class ConditionAttack:
    def __init__(self, ai):
        self.ai = ai

    def none(self):
        pass

    def adepts_more_than(self, amount):
        return self.ai.army(unit.ADEPT).ready.amount > amount and not self.ai.after_first_attack

    def stalkers_more_than(self, amount):
        return self.ai.army(unit.STALKER).ready.amount > amount and not self.ai.after_first_attack

    def warpgate_research_ready(self):
        return (not self.ai.first_attack) and upgrade.WARPGATERESEARCH in self.ai.state.upgrades

    def ground_weapons_and_armor_lvl2(self):
        return upgrade.PROTOSSGROUNDWEAPONSLEVEL2 in self.ai.state.upgrades and \
               upgrade.PROTOSSGROUNDARMORSLEVEL1 in self.ai.state.upgrades

    def blink_research_ready(self):
        return (not self.ai.first_attack) and upgrade.BLINKTECH in self.ai.state.upgrades

    def air_dmg_lvl2_full_supply(self):
        return upgrade.PROTOSSAIRWEAPONSLEVEL2 in self.ai.state.upgrades and \
               self.ai.supply_used > 193

    def army_supply_over(self, supply):
        return self.ai.supply_army > supply

    def total_supply_over(self, supply):
        return self.ai.supply_used > supply


class ConditionCounterAttack:
    def __init__(self, ai):
        self.ai = ai

    def counter_attack(self):
        en = self.ai.enemy_units()
        return en.exists and en.closer_than(25, self.ai.defend_position).amount > 5

    def counter_attack_wide_range(self):
        en = self.ai.enemy_units()
        return en.exists and en.closer_than(35, self.ai.defend_position).amount > 3


class ConditionRetreat:
    def __init__(self, ai):
        self.ai = ai

    def none(self):
        pass

    def stalker_proxy(self):
        return self.ai.attack and self.ai.army.amount < (2 if self.ai.time < 300 else 5)

    def army_count_less_than(self, army_count):
        return self.ai.attack and self.ai.army.amount < army_count

    def army_supply_less_than(self, supply):
        return self.ai.supply_army < supply


class ConditionTransform:
    def __init__(self, ai):
        self.ai = ai

    async def none(self):
        pass

    async def adept_defend(self):
        if ((not self.ai.first_attack) and self.ai.time > 340) or (self.ai.first_attack and self.ai.army_supply > 12):
            if upgrade.WARPGATERESEARCH in self.ai.state.upgrades:
                enemy = self.ai.enemy_units()
                if enemy.exists:
                    enemy_in_base = enemy.closer_than(30, self.ai.defend_position)
                    if enemy_in_base.amount > 1:
                        return
                self.ai.after_first_attack = False
                self.ai.first_attack = False
                await self.ai.set_strategy('stalker_proxy')

    async def stalker_defend(self):
        if ((not self.ai.first_attack) and self.ai.time > 300) or (
                self.ai.after_first_attack and self.ai.army.amount > 4):
            self.ai.after_first_attack = False
            self.ai.first_attack = False
            await self.ai.set_strategy('stalker_proxy')

    async def stalker_proxy(self):
        if self.ai.after_first_attack and self.ai.army.amount > 7:
            # self.ai.after_first_attack = False
            # self.ai.first_attack = False
            await self.ai.set_strategy('2b_colossus')

    async def adept_proxy(self):
        if self.ai.after_first_attack and self.ai.army.amount > 7:
            # self.ai.after_first_attack = False
            # self.ai.first_attack = False
            await self.ai.set_strategy('2b_archons')

    async def two_base_colossus(self):
        if self.ai.after_first_attack and self.ai.army.amount > 13:
            self.ai.after_first_attack = False
            self.ai.first_attack = False
            await self.ai.set_strategy('macro')

    async def two_base_archons(self):
        if self.ai.after_first_attack and self.ai.army.amount > 13:
            self.ai.after_first_attack = False
            self.ai.first_attack = False
            await self.ai.set_strategy('bio')

    async def macro(self):
        if self.ai.after_first_attack and self.ai.army.amount > 27 and self.ai.time > 1000 and self.ai.minerals > 1000 \
                and self.ai.vespene > 500:
            self.ai.after_first_attack = False
            self.ai.first_attack = False
            await self.ai.set_strategy('bio')


class ConditionLockSpending:
    def __init__(self, ai):
        self.ai = ai

    async def none(self):
        pass

    async def is_mothership_ready(self):
        return self.ai.army({unit.CARRIER, unit.TEMPEST}).amount >= 2 and not self.ai.units(unit.MOTHERSHIP).exists and \
               ('is_mothership_created' not in self.ai.global_variables or
                not self.ai.global_variables['is_mothership_created'])

    async def is_oracle_ready(self):
        return self.ai.time < 300 and self.ai.structures(unit.STARGATE).exists \
                and not self.ai.structures(unit.STARGATE).ready.exists and (self.ai.minerals < 550 or
                                                                            self.ai.vespene < 50)

    async def is_voidray_ready(self):
        return self.ai.time < 300 and self.ai.structures(unit.STARGATE).exists \
            and not self.ai.structures(unit.STARGATE).ready.exists

    async def twilight_council_blink(self):
        if upgrade.BLINKTECH not in self.ai.state.upgrades:
            twilight_council = self.ai.structures(unit.TWILIGHTCOUNCIL).ready
            if twilight_council.exists and twilight_council.idle.exists:
                twilight_council = twilight_council.first
                abilities = await self.ai.get_available_abilities(twilight_council, ignore_resource_requirements=True)
                for ab in abilities:
                    if ab == AbilityId.RESEARCH_BLINK:
                        if not self.ai.can_afford(ab):
                            return True
            return False

    async def twilight_council_charge(self):
        if upgrade.CHARGE not in self.ai.state.upgrades:
            twilight_council = self.ai.structures(unit.TWILIGHTCOUNCIL).ready
            if twilight_council.exists and twilight_council.idle.exists:
                twilight_council = twilight_council.first
                abilities = await self.ai.get_available_abilities(twilight_council, ignore_resource_requirements=True)
                for ab in abilities:
                    if ab == AbilityId.RESEARCH_CHARGE:
                        if not self.ai.can_afford(ab):
                            return True
            return False

    async def twilight_council_glaives(self):
            twilight_council = self.ai.structures(unit.TWILIGHTCOUNCIL).ready
            if twilight_council.exists and twilight_council.idle.exists:
                twilight_council = twilight_council.first
                abilities = await self.ai.get_available_abilities(twilight_council, ignore_resource_requirements=True)
                for ab in abilities:
                    if ab == AbilityId.RESEARCH_ADEPTRESONATINGGLAIVES:
                        if not self.ai.can_afford(ab):
                            return True
            return False

    def thermal_lances(self):
        return upgrade.EXTENDEDTHERMALLANCE not in self.ai.state.upgrades and \
               self.ai.structures(unit.ROBOTICSBAY).ready.idle.exists and self.ai.units(unit.COLOSSUS).exists

    def psi_storm(self):
        return upgrade.PSISTORMTECH not in self.ai.state.upgrades and\
               self.ai.structures(unit.TEMPLARARCHIVE).ready.idle.exists

    async def forge(self):
        upgrades_abilities_ids = [AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1,
                                  AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL1,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2,
                                  AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL2,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3,
                                  AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL3]

        if self.ai.structures(unit.TWILIGHTCOUNCIL).ready.exists:
            upgds = [upgrade.PROTOSSGROUNDWEAPONSLEVEL1, upgrade.PROTOSSGROUNDARMORSLEVEL1,
                     upgrade.PROTOSSSHIELDSLEVEL1,
                     upgrade.PROTOSSGROUNDWEAPONSLEVEL2, upgrade.PROTOSSGROUNDARMORSLEVEL2,
                     upgrade.PROTOSSSHIELDSLEVEL2,
                     upgrade.PROTOSSGROUNDWEAPONSLEVEL3, upgrade.PROTOSSGROUNDARMORSLEVEL3,
                     upgrade.PROTOSSSHIELDSLEVEL3]
        else:
            upgds = [upgrade.PROTOSSGROUNDWEAPONSLEVEL1, upgrade.PROTOSSGROUNDARMORSLEVEL1,
                     upgrade.PROTOSSSHIELDSLEVEL1]
        done = True
        for u in upgds:
            if u not in self.ai.state.upgrades:
                done = False
                break
        if not done:
            forges = self.ai.structures(unit.FORGE).ready
            if forges.exists:
                for forge in forges.idle:
                    abilities = await self.ai.get_available_abilities(forge, ignore_resource_requirements=True)
                    for ab in abilities:
                        if ab in upgrades_abilities_ids:
                            if not self.ai.can_afford(ab):
                                return True
        return False
