from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.buff_id import BuffId as buff
from sc2.units import Units
from bot.constants import ABILITIES_TIME
import random


class Chronobooster:
    def __init__(self,ai):
        self.ai = ai
        self.standard_chrono_queue = [unit.NEXUS, unit.GATEWAY, unit.ROBOTICSBAY,
                                      unit.STARGATE, unit.ROBOTICSFACILITY,
                                      unit.CYBERNETICSCORE, unit.FORGE, unit.TWILIGHTCOUNCIL]
        self.stalker_proxy_chrono_queue = [unit.NEXUS, unit.CYBERNETICSCORE]
        self.rush_defense_chrono_queue = [unit.NEXUS, unit.GATEWAY, unit.ROBOTICSBAY, unit.STARGATE,
                                          unit.CYBERNETICSCORE,
                                       unit.ROBOTICSFACILITY, unit.TWILIGHTCOUNCIL]

    async def air(self):
        pass

    def standard(self):
        if self.ai.structures(unit.NEXUS).exists and self.ai.structures(unit.PYLON).ready.exists:
            nexuses = self.ai.structures().filter(
                lambda x: x.type_id == unit.NEXUS and x.is_ready and x.energy >= 50).sorted(key=lambda x:
                                                                                            x.energy)
            if not nexuses:
                return
            if nexuses.amount > 1:
                nexuses.pop(0)
            elif self.ai.structures(unit.SHIELDBATTERY).amount > 0 and nexuses.first.energy < 100:
                return
            i = 0
            for nexus in nexuses:
                # if nexus != starting_nexus and nexus.energy < 100:
                #     continue
                # targets = None
                targets_filtered = Units([],self.ai)
                while targets_filtered.amount < 1 and i < len(self.standard_chrono_queue):
                    targets = self.ai.structures().filter(lambda x: x.type_id == self.standard_chrono_queue[i] and x.is_ready and
                                                not x.is_idle and not x.has_buff(buff.CHRONOBOOSTENERGYCOST))
                    for tg in targets:
                        if tg.orders:
                            progress = tg.orders[0].progress
                            abil_id = tg.orders[0].ability.id
                            # print('ability id: {}'.format(abil_id))
                            if abil_id in ABILITIES_TIME:
                                time = ABILITIES_TIME[abil_id]
                            elif abil_id == ability.RESEARCH_PROTOSSGROUNDWEAPONS:
                                if upgrade.PROTOSSGROUNDWEAPONSLEVEL1 not in self.ai.state.upgrades:
                                    time = 129
                                elif upgrade.PROTOSSGROUNDWEAPONSLEVEL2 not in self.ai.state.upgrades:
                                    time = 154
                                else:
                                    time = 179
                            elif abil_id == ability.RESEARCH_PROTOSSGROUNDARMOR:
                                if upgrade.PROTOSSGROUNDARMORSLEVEL1 not in self.ai.state.upgrades:
                                    time = 129
                                elif upgrade.PROTOSSGROUNDARMORSLEVEL2 not in self.ai.state.upgrades:
                                    time = 154
                                else:
                                    time = 179
                            elif abil_id == ability.RESEARCH_PROTOSSSHIELDS:
                                if upgrade.PROTOSSSHIELDSLEVEL1 not in self.ai.state.upgrades:
                                    time = 129
                                elif upgrade.PROTOSSSHIELDSLEVEL2 not in self.ai.state.upgrades:
                                    time = 154
                                else:
                                    time = 179
                            else:
                                time = 31

                            time_left = time * (1 - progress)
                            # print('time left: ' + str(round(time_left,1)) + '  for unit ' + str(abil_id)[10:])
                            if time_left < 30:
                                # print('skipping')
                                targets.remove(tg)
                            else:
                                # print('allowing cast on ' + str(tg.type_id) + ' for unit ' + str(abil_id)[10:] +
                                #       ' with time left: ' + str(time_left))
                                targets_filtered.append(tg)
                        else:
                            targets.remove(tg)
                    if targets_filtered.amount < 1:
                        i += 1
                if targets_filtered:
                    target = targets_filtered.random
                    if target.type_id in [unit.GATEWAY]:
                        self.standard_chrono_queue.remove(target.type_id)
                    nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST,target)
                    return


    def rush_defense(self):
        if self.ai.structures(unit.NEXUS).exists:
            nexuses = self.ai.structures().filter(
                lambda x: x.type_id == unit.NEXUS and x.is_ready and x.energy >= 50).sorted(key=lambda x:
                                                                                            x.energy)
            if not nexuses:
                return
            if nexuses.amount > 1:
                nexuses.pop(0)
            elif self.ai.structures(unit.SHIELDBATTERY).amount > 0 and nexuses.first.energy < 100:
                return
            i = 0
            for nexus in nexuses:
                targets_filtered = Units([],self.ai)
                while targets_filtered.amount < 1 and i < len(self.rush_defense_chrono_queue):
                    targets = self.ai.structures().filter(lambda x: x.type_id == self.rush_defense_chrono_queue[i] and x.is_ready and
                                                not x.is_idle and not x.has_buff(buff.CHRONOBOOSTENERGYCOST))
                    for tg in targets:
                        if tg.orders:
                            progress = tg.orders[0].progress
                            abil_id = tg.orders[0].ability.id
                            # print('ability id: {}'.format(abil_id))
                            if abil_id in ABILITIES_TIME:
                                time = ABILITIES_TIME[abil_id]
                            elif abil_id in {ability.GATEWAYTRAIN_ZEALOT, ability.GATEWAYTRAIN_STALKER,
                                             ability.TRAIN_ADEPT, ability.GATEWAYTRAIN_SENTRY}:
                                time = 800
                            elif abil_id in {ability.MORPH_GATEWAY, ability.MORPH_WARPGATE}:
                                continue
                            elif abil_id == ability.RESEARCH_PROTOSSGROUNDWEAPONS:
                                if upgrade.PROTOSSGROUNDWEAPONSLEVEL1 not in self.ai.state.upgrades:
                                    time = 129
                                elif upgrade.PROTOSSGROUNDWEAPONSLEVEL2 not in self.ai.state.upgrades:
                                    time = 154
                                else:
                                    time = 179
                            elif abil_id == ability.RESEARCH_PROTOSSGROUNDARMOR:
                                if upgrade.PROTOSSGROUNDARMORSLEVEL1 not in self.ai.state.upgrades:
                                    time = 129
                                elif upgrade.PROTOSSGROUNDARMORSLEVEL2 not in self.ai.state.upgrades:
                                    time = 154
                                else:
                                    time = 179
                            elif abil_id == ability.RESEARCH_PROTOSSSHIELDS:
                                if upgrade.PROTOSSSHIELDSLEVEL1 not in self.ai.state.upgrades:
                                    time = 129
                                elif upgrade.PROTOSSSHIELDSLEVEL2 not in self.ai.state.upgrades:
                                    time = 154
                                else:
                                    time = 179
                            else:
                                time = 31

                            time_left = time * (1 - progress)
                            # print('time left: ' + str(round(time_left,1)) + '  for unit ' + str(abil_id)[10:])
                            if time_left < 30:
                                # print('skipping')
                                targets.remove(tg)
                            else:
                                # print('allowing cast on ' + str(tg.type_id) + ' for unit ' + str(abil_id)[10:] +
                                #       ' with time left: ' + str(time_left))
                                targets_filtered.append(tg)
                        else:
                            targets.remove(tg)
                    if targets_filtered.amount < 1:
                        i += 1
                if targets_filtered:
                    target = targets_filtered.random
                    if target.type_id == unit.NEXUS:
                        self.rush_defense_chrono_queue.remove(target.type_id)
                    nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST,target)
                    return

    def rapid_expansion(self):
        if self.ai.structures(unit.NEXUS).exists and self.ai.structures(unit.PYLON).ready.exists:
            nexuses = self.ai.structures().filter(
                lambda x: x.type_id == unit.NEXUS and x.is_ready and x.energy >= 50).sorted(key=lambda x:
                                                                                            x.energy)
            if not nexuses:
                return
            if nexuses.amount > 1:
                nexuses.pop(0)
            elif self.ai.structures(unit.SHIELDBATTERY).amount > 0 and nexuses.first.energy < 100:
                return
            if self.ai.time < 300:
                chrono_queue = [unit.NEXUS]
            else:
                chrono_queue = self.standard_chrono_queue
            i = 0
            for nexus in nexuses:
                targets_filtered = Units([],self.ai)
                while targets_filtered.amount < 1 and i < len(chrono_queue):
                    targets = self.ai.structures().filter(lambda x: x.type_id == chrono_queue[i] and x.is_ready and
                                                not x.is_idle and not x.has_buff(buff.CHRONOBOOSTENERGYCOST))
                    for tg in targets:
                        if tg.orders:
                            progress = tg.orders[0].progress
                            abil_id = tg.orders[0].ability.id
                            # print('ability id: {}'.format(abil_id))
                            if abil_id in ABILITIES_TIME:
                                time = ABILITIES_TIME[abil_id]
                            elif abil_id in {ability.GATEWAYTRAIN_ZEALOT, ability.GATEWAYTRAIN_STALKER,
                                             ability.TRAIN_ADEPT, ability.GATEWAYTRAIN_SENTRY}:
                                time = 800
                            elif abil_id in {ability.MORPH_GATEWAY, ability.MORPH_WARPGATE}:
                                continue
                            elif abil_id == ability.RESEARCH_PROTOSSGROUNDWEAPONS:
                                if upgrade.PROTOSSGROUNDWEAPONSLEVEL1 not in self.ai.state.upgrades:
                                    time = 129
                                elif upgrade.PROTOSSGROUNDWEAPONSLEVEL2 not in self.ai.state.upgrades:
                                    time = 154
                                else:
                                    time = 179
                            elif abil_id == ability.RESEARCH_PROTOSSGROUNDARMOR:
                                if upgrade.PROTOSSGROUNDARMORSLEVEL1 not in self.ai.state.upgrades:
                                    time = 129
                                elif upgrade.PROTOSSGROUNDARMORSLEVEL2 not in self.ai.state.upgrades:
                                    time = 154
                                else:
                                    time = 179
                            elif abil_id == ability.RESEARCH_PROTOSSSHIELDS:
                                if upgrade.PROTOSSSHIELDSLEVEL1 not in self.ai.state.upgrades:
                                    time = 129
                                elif upgrade.PROTOSSSHIELDSLEVEL2 not in self.ai.state.upgrades:
                                    time = 154
                                else:
                                    time = 179
                            else:
                                time = 31

                            time_left = time * (1 - progress)
                            # print('time left: ' + str(round(time_left,1)) + '  for unit ' + str(abil_id)[10:])
                            if time_left < 30:
                                # print('skipping')
                                targets.remove(tg)
                            else:
                                # print('allowing cast on ' + str(tg.type_id) + ' for unit ' + str(abil_id)[10:] +
                                #       ' with time left: ' + str(time_left))
                                targets_filtered.append(tg)
                        else:
                            targets.remove(tg)
                    if targets_filtered.amount < 1:
                        i += 1
                if targets_filtered:
                    target = targets_filtered.random
                    nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST,target)
                    return

    async def stalker_proxy(self):
        if self.ai.structures(unit.NEXUS).exists and self.ai.structures(unit.PYLON).ready.exists:
            nexuses = self.ai.structures().filter(lambda x: x.type_id == unit.NEXUS and x.is_ready and x.energy >= 50)
            i = 0
            for nexus in nexuses:
                # targets = None
                targets_filtered = Units([],self.ai)
                while targets_filtered.amount < 1 and i < len(self.stalker_proxy_chrono_queue):
                    targets = self.ai.structures().filter(lambda x: x.type_id == self.stalker_proxy_chrono_queue[i] and x.is_ready and
                                                not x.is_idle and not x.has_buff(buff.CHRONOBOOSTENERGYCOST))
                    for tg in targets:
                        if tg.orders:
                            progress = tg.orders[0].progress
                            abil_id = tg.orders[0].ability.id

                            if abil_id == ability.RESEARCH_WARPGATE:
                                time = 110
                            else:
                                time = 31

                            time_left = time * (1 - progress)
                            # print('time left: ' + str(round(time_left,1)) + '  for unit ' + str(abil_id)[10:])
                            if time_left < 30:
                                # print('skipping')
                                targets.remove(tg)
                            else:
                                # print('allowing cast on ' + str(tg.type_id) + ' for unit ' + str(abil_id)[10:] +
                                #       ' with time left: ' + str(time_left))
                                targets_filtered.append(tg)
                        else:
                            targets.remove(tg)
                    if targets_filtered.amount < 1:
                        i += 1
                if targets_filtered:
                    target = targets_filtered.random
                    if target.type_id in [unit.GATEWAY]:
                        self.stalker_proxy_chrono_queue.remove(target.type_id)
                    nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST,target)
                    return
                else:
                    warpgates = self.ai.structures(unit.WARPGATE).ready
                    targets = []
                    for warpgate in warpgates:
                        abilities = await self.ai.get_available_abilities(warpgate)
                        if ability.WARPGATETRAIN_STALKER in abilities:
                            targets.append(warpgate)
                    if targets:
                        target = random.choice(targets)
                        nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST,target)
                        return


class ShieldOvercharge:
    def __init__(self, ai):
        self.ai = ai

    async def shield_overcharge(self):
        en = self.ai.enemy_units()
        if en.exists and en.closer_than(15, self.ai.defend_position).amount > (5 if self.ai.time > 460 else 2):
            # print("enemy close to defend position")
            nexuses = self.ai.structures().filter(lambda x: x.type_id == unit.NEXUS and x.is_ready and x.energy >= 50)
            if nexuses:
                nexus = nexuses.first
            else:
                # print('no nexus with energy to cast overcharge')
                return

            batteries = self.ai.structures(unit.SHIELDBATTERY).ready.closer_than(15, nexuses.closest_to(self.ai.defend_position)) \
                .sorted(lambda x: x.health, reverse=True)
            # if not batteries:
            #     print("no batteries in range")
            if batteries and nexus and self.ai.army().filter(lambda x: x.distance_to(batteries[0]) <= 6
                                                                     and x.shield_percentage < 0.6).exists:
                # print('want to cast overcharge...')
                batteries = batteries[0]
                abilities = await self.ai.get_available_abilities(nexus)
                # print('nexus abilities: {}'.format(abilities))
                if ability.BATTERYOVERCHARGE_BATTERYOVERCHARGE in abilities:
                    nexus(ability.BATTERYOVERCHARGE_BATTERYOVERCHARGE, batteries)
                    # print('overcharge casted.')
                # else:
                #     print('no overcharge in abilities.')
            # else:
            #     print('no units to cast overcharge for.')