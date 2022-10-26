from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade


class ConditionAttack:
    def __init__(self, ai):
        self.ai = ai

    def none(self):
        pass

    def rush(self):
        return (not self.ai.first_attack) and upgrade.WARPGATERESEARCH in self.ai.state.upgrades

    def blink_complete(self):
        return (not self.ai.first_attack) and upgrade.BLINKTECH in self.ai.state.upgrades

    def ground_weapons_and_armor_lvl2(self):
        return upgrade.PROTOSSGROUNDWEAPONSLEVEL2 in self.ai.state.upgrades and \
               upgrade.PROTOSSGROUNDARMORSLEVEL2 in self.ai.state.upgrades and \
               self.ai.supply_used > 160

    def air(self):
        return upgrade.PROTOSSAIRWEAPONSLEVEL2 in self.ai.state.upgrades and \
               self.ai.supply_used > 193


class ConditionCounterAttack:
    def __init__(self, ai):
        self.ai = ai

    def counter_attack(self):
        en = self.ai.enemy_units()
        return en.exists and en.closer_than(40, self.ai.defend_position).amount > 5


class ConditionRetreat:
    def __init__(self, ai):
        self.ai = ai

    def none(self):
        pass

    def stalker_proxy(self):
        return self.ai.attack and self.ai.army.amount < (2 if self.ai.time < 300 else 5)

    def army_count_less_than(self, army_count):
        return self.ai.attack and self.ai.army.amount < army_count


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
