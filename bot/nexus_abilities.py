from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.buff_id import BuffId as buff
from sc2.units import Units
import random


class Chronobooster:
    def __init__(self,ai):
        self.ai = ai
        self.standard_chrono_queue = [unit.NEXUS,
                                      unit.STARGATE, unit.ROBOTICSFACILITY,
                                      unit.CYBERNETICSCORE, unit.FORGE, unit.TWILIGHTCOUNCIL]
        self.stalker_proxy_chrono_queue = [unit.NEXUS, unit.CYBERNETICSCORE]

    async def air(self):
        pass

    def standard(self):
        if self.ai.structures(unit.NEXUS).exists and self.ai.structures(unit.PYLON).ready.exists:
            nexuses = self.ai.structures().filter(lambda x: x.type_id == unit.NEXUS and x.is_ready and x.energy >= 50)
            # starting_nexus = self.ai.structures(unit.NEXUS).closest_to(self.ai.start_location.position)
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
                            if abil_id == ability.STARGATETRAIN_CARRIER:
                                time = 64
                            elif abil_id == ability.STARGATETRAIN_TEMPEST:
                                time = 43
                            elif abil_id == ability.RESEARCH_WARPGATE:
                                time = 150
                            elif abil_id == ability.RESEARCH_BLINK:
                                time = 121
                            elif abil_id == ability.RESEARCH_CHARGE:
                                time = 100
                            elif abil_id == ability.RESEARCH_PROTOSSGROUNDWEAPONS:
                                            #
                                            # ability.RESEARCH_PROTOSSSHIELDS:
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
                    if target.type_id in [unit.NEXUS, unit.GATEWAY]:
                        self.standard_chrono_queue.remove(target.type_id)
                    self.ai.do(nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST,target))
                    return
                # else:
                # #     warpgates = self.ai.structures(unit.WARPGATE).ready
                # #     targets = []
                # #     for warpgate in warpgates:
                # #         abilities = await self.ai.get_available_abilities(warpgate)
                # #         if ability.WARPGATETRAIN_STALKER in abilities:
                # #             targets.append(warpgate)
                #     if targets:
                #         target = random.choice(targets)
                #         self.ai.do(nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST,target))
                #         return

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
                            if abil_id == ability.STARGATETRAIN_CARRIER:
                                time = 64
                            elif abil_id == ability.STARGATETRAIN_TEMPEST:
                                time = 43
                            elif abil_id == ability.RESEARCH_WARPGATE:
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
                    if target.type_id in [unit.NEXUS, unit.GATEWAY]:
                        self.stalker_proxy_chrono_queue.remove(target.type_id)
                    self.ai.do(nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST,target))
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
                        self.ai.do(nexus(ability.EFFECT_CHRONOBOOSTENERGYCOST,target))
                        return


class ShieldOvercharge:
    def __init__(self, ai):
        self.ai = ai

    async def shield_overcharge(self):
        en = self.ai.enemy_units()
        if en.exists and en.closer_than(40, self.ai.defend_position).amount > 5:
            nexus = self.ai.structures(unit.NEXUS).ready.closest_to(self.ai.defend_position)
            battery = self.ai.structures(unit.SHIELDBATTERY).ready.closer_than(10, nexus) \
                .sorted(lambda x: x.health, reverse=True)
            if battery and nexus:
                battery = battery[0]
                if nexus.energy >= 50:
                    abilities = await self.ai.get_available_abilities(nexus)
                    # print('nexus abilities: {}'.format(abilities))
                    if ability.BATTERYOVERCHARGE_BATTERYOVERCHARGE in abilities:
                        nexus(ability.BATTERYOVERCHARGE_BATTERYOVERCHARGE, battery)