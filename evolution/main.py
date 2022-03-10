import random
import sc2
from sc2 import run_game, maps, Race, Difficulty, AIBuild, AbilityId
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2, Point3
from bot.building_spot_validator import BuildingSpotValidator
from bot.chronobooster import Chronobooster
from typing import Optional, Union
from strategy.stalker_proxy import StalkerProxy
from strategy.macro import Macro
from strategy.manager import Strategy
from bot.builder import Builder


class OctopusEvo(sc2.BotAI):
    army_ids = [unit.ADEPT, unit.STALKER, unit.ZEALOT, unit.SENTRY, unit.OBSERVER, unit.IMMORTAL, unit.ARCHON,
                unit.HIGHTEMPLAR, unit.DARKTEMPLAR, unit.WARPPRISM, unit.VOIDRAY, unit.CARRIER, unit.COLOSSUS,
                unit.TEMPEST]
    bases_ids = [unit.NEXUS, unit.COMMANDCENTER, unit.COMMANDCENTERFLYING, unit.ORBITALCOMMAND,
                 unit.ORBITALCOMMANDFLYING,
                 unit.PLANETARYFORTRESS, unit.HIVE, unit.HATCHERY, unit.LAIR]
    units_to_ignore = [unit.LARVA, unit.EGG, unit.INTERCEPTOR]
    enemy_main_base_down = False
    leader_tag = None
    destination = None
    psi_storm_wait = 0
    nova_wait = 0

    def __init__(self, genome):
        super().__init__()
        self.builder = Builder(self)
        self.spot_validator = BuildingSpotValidator(self)
        self.chronobooster = Chronobooster(self)
        self.attack = False
        self.first_attack = False
        self.retreat = False
        self.after_first_attack = False
        self.defend_position = None
        self.army = None
        self.observer_scouting_index = 0
        self.observer_scouting_points = []
        self.strategy: Strategy = None
        self.genome = genome
        self.chromosome_index = 0

    async def on_start(self):
        self.strategy = Macro(self)

    async def on_step(self, iteration: int):
        # get genome row (chromosome) for this time
        time_frame = int(self.time / 30)
        if time_frame > self.chromosome_index:
            self.chromosome_index = time_frame
            print('time: {}'.format(self.time))
            print('chromosome index: {}'.format(self.chromosome_index))

        self.assign_defend_position()
        self.army = self.units().filter(lambda x: x.type_id in self.army_ids and x.is_ready)

        await self.distribute_workers()
        await self.build_pylons()
        await self.build_gateway()
        await self.build_cybernetics()
        await self.warp_units()
        await self.morph_gates()
        await self.chronoboost()
        self.train_probes()
        self.train_units()
        self.upgrade_warpgate()
        self.build_assimilators()
        await self.strategy.forge_build()
        await self.strategy.robotics_build()
        await self.strategy.robotics_bay_build()
        await self.strategy.templar_archives_build()
        await self.strategy.pylon_first_build()
        await self.strategy.twilight_build()
        await self.strategy.dark_shrine_build()
        self.strategy.robotics_train()
        await self.strategy.templar_archives_upgrades()
        self.strategy.forge_upgrades()
        await self.strategy.expand()
        await self.strategy.transformation()
        await self.morph_Archons()
        await self.strategy.twilight_upgrades()

        # attack
        if (not self.attack) and (not self.strategy.retreat_condition()) and (
                self.strategy.counter_attack_condition() or self.attack_condition()):
            # await self.chat_send('Attack!  army len: ' + str(len(self.army)))
            self.first_attack = True
            self.attack = True
            self.retreat = False
        # retreat
        if self.strategy.retreat_condition():
            # await self.chat_send('Retreat! army len: ' + str(len(self.army)))
            self.retreat = True
            self.attack = False
            self.after_first_attack = True

        try:
            if self.attack:
                await self.strategy.movements()
            else:
                await self.defend()

        except Exception as ex:
            print(ex)
            await self.chat_send('on_step error 10')
        try:
            await self.strategy.micro()
        except Exception as ex:
            print(ex)
            await self.chat_send('on_step error 9 -> micro_units')
            raise ex

    async def build_gateway(self):
        await self.strategy.gate_build()

    async def build_pylons(self):
        await self.strategy.pylon_next_build()

    async def build_cybernetics(self):
        await self.strategy.cybernetics_build()

    async def build(self, building: unit, near: Union[Unit, Point2, Point3], max_distance: int = 20, block=False,
                    build_worker: Optional[Unit] = None, random_alternative: bool = True,
                    placement_step: int = 3, ) -> bool:
        return await self.builder.build(building=building, near=near, max_distance=max_distance, block=block,
                                               build_worker=build_worker, random_alternative=random_alternative)

    def train_probes(self):
        self.strategy.nexus_train()
        # workers = self.workers.amount
        # nex = self.structures(unit.NEXUS).amount
        # if not self.structures(unit.PYLON).exists and workers == 14:
        #     return
        # if workers < 20 * nex and workers < 55:
        #     for nexus in self.structures(unit.NEXUS).ready:
        #         if nexus.is_idle and self.can_afford(unit.PROBE):
        #             self.do(nexus.train(unit.PROBE))
        # elif 54 < workers < 74:
        #     if self.can_afford(unit.PROBE) and not self.already_pending(unit.PROBE):
        #         if self.structures(unit.NEXUS).idle.amount < nex:
        #             return
        #         nexus = self.structures(unit.NEXUS).ready.idle.random
        #         self.do(nexus.train(unit.PROBE))

    def train_units(self):
        self.strategy.gate_train()
        # if self.structures(unit.CYBERNETICSCORE).ready.exists:
        #     gateways = self.structures(unit.GATEWAY).ready.idle
        #     for gateway in gateways:
        #         if self.can_afford(unit.STALKER):
        #             self.do(gateway.train(unit.STALKER))

    async def warp_units(self):
        await self.strategy.warpgate_train()
        # warpgates = self.structures(unit.WARPGATE).ready.idle
        # if warpgates.exists:
        #     if self.attack:
        #         prisms = self.units(unit.WARPPRISMPHASING)
        #         if prisms.exists:
        #             pos = prisms.furthest_to(self.start_location).position
        #         else:
        #             furthest_pylon = self.structures(unit.PYLON).ready.furthest_to(self.start_location.position)
        #             pos = furthest_pylon.position
        #     else:
        #         pos = self.structures(unit.PYLON).ready.closer_than(35, self.start_location).furthest_to(
        #             self.start_location).position
        #     placement = None
        #     i = 0
        #     while placement is None:
        #         i += 1
        #         placement = await self.find_placement(AbilityId.TRAINWARP_ADEPT, near=pos.random_on_distance(5),
        #                                               max_distance=5, placement_step=2, random_alternative=False)
        #         if i > 5:
        #             print("can't find position for warpin.")
        #             return
        #     for warpgate in warpgates:
        #         abilities = await self.get_available_abilities(warpgate)
        #         if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
        #             if self.can_afford(unit.STALKER):
        #                 self.do(warpgate.warp_in(unit.STALKER, placement))

    async def morph_gates(self):
        for gateway in self.structures(unit.GATEWAY).ready:
            abilities = await self.get_available_abilities(gateway)
            if AbilityId.MORPH_WARPGATE in abilities and self.can_afford(AbilityId.MORPH_WARPGATE):
                self.do(gateway(AbilityId.MORPH_WARPGATE))

    def upgrade_warpgate(self):
        cyber = self.structures(unit.CYBERNETICSCORE).ready.idle
        if cyber.exists:
            if upgrade.WARPGATERESEARCH not in self.state.upgrades and \
                    not self.already_pending_upgrade(upgrade.WARPGATERESEARCH) and \
                    self.can_afford(upgrade.WARPGATERESEARCH):
                self.do(cyber.random.research(upgrade.WARPGATERESEARCH))

    def build_assimilators(self):
        if self.structures().filter(lambda x: x.type_id in [unit.GATEWAY, unit.WARPGATE]).amount == 0 or \
                (self.structures(unit.NEXUS).ready.amount > 1 and self.vespene > self.minerals):
            return
        if not self.can_afford(unit.ASSIMILATOR):
            return
        nexuses = self.structures(unit.NEXUS)
        if nexuses.amount < 4:
            nexuses = nexuses.ready
        probes = self.units(unit.PROBE)
        if probes.exists:
            for nexus in nexuses:
                vespenes = self.vespene_geyser.closer_than(9, nexus)
                workers = probes.closer_than(12, nexus)
                if workers.amount > 14 or nexuses.amount > 3:
                    for vespene in vespenes:
                        if (not self.already_pending(unit.ASSIMILATOR)) and\
                                (not self.structures(unit.ASSIMILATOR).exists or not
                                         self.structures(unit.ASSIMILATOR).closer_than(3, vespene).exists):
                            worker = self.select_build_worker(vespene.position)
                            if worker is None:
                                break
                            self.do(worker.build(unit.ASSIMILATOR, vespene))
                            self.do(worker.move(worker.position.random_on_distance(1), queue=True))

    async def chronoboost(self):
        await self.strategy.chronoboost()

    async def defend(self):
        enemy = self.enemy_units()
        if 3 > enemy.amount > 0:
            hunters = []
            hunters_ids = [unit.STALKER, unit.OBSERVER, unit.ADEPT, unit.VOIDRAY]
            regular = []
            for man in self.army:
                if man.type_id in hunters_ids:
                    hunters.append(man)
                else:
                    regular.append(man)
            for hunter in hunters:
                if hunter.distance_to(self.start_location) < 50:
                    self.do(hunter.attack(enemy.closest_to(hunter)))
                else:
                    self.do(hunter.move(self.defend_position))
            dist = 7
            for man in regular:
                position = Point2(self.defend_position).towards(self.game_info.map_center, 3) if \
                    man.type_id == unit.ZEALOT else Point2(self.defend_position)
                if man.distance_to(self.defend_position) > dist:
                    self.do(man.move(position.random_on_distance(random.randint(1, 2))))
        elif enemy.amount > 2:
            dist = 12
            for man in self.army:
                position = Point2(self.defend_position).towards(self.game_info.map_center, 3) if \
                    man.type_id == unit.ZEALOT else Point2(self.defend_position)
                distance = man.distance_to(self.defend_position)
                if distance > dist:
                    if self.retreat and distance > 2 * dist:
                        self.do(man.move(position.random_on_distance(random.randint(1, 2))))
                    else:
                        self.do(man.attack(position.random_on_distance(random.randint(1, 2))))
        else:
            dist = 7
            for man in self.army:
                position = Point2(self.defend_position).towards(self.game_info.map_center, 3) if \
                    man.type_id == unit.ZEALOT else Point2(self.defend_position)
                if man.distance_to(self.defend_position) > dist:
                    self.do(man.attack(position.random_on_distance(random.randint(1, 2))))

    def assign_defend_position(self):
        nex = self.structures(unit.NEXUS)
        enemy = self.enemy_units()

        if enemy.exists and enemy.closer_than(50, self.start_location).amount > 1:
            self.defend_position = enemy.closest_to(self.enemy_start_locations[0]).position
        elif nex.amount < 2:
            self.defend_position = self.main_base_ramp.top_center.towards(self.main_base_ramp.bottom_center, -6)
        else:
            self.defend_position = nex.closest_to(self.enemy_start_locations[0]).position.towards(
                self.game_info.map_center, 5)

    def scan(self):
        scouts = self.units(unit.PHOENIX).filter(lambda z: z.is_hallucination)
        if scouts.amount < 3:
            snts = self.army(unit.SENTRY)
            if snts.exists and self.time < 1800:
                snts = self.army(unit.SENTRY).filter(lambda z: z.energy >= 75)
                if snts:
                    for se in snts:
                        self.do(se(AbilityId.HALLUCINATION_PHOENIX))
                    scouts = self.units(unit.PHOENIX).filter(lambda z: z.is_hallucination)
            else:
                scouts = self.units({unit.WARPPRISM, unit.OBSERVER})
                if not scouts.exists:
                    scouts = self.army.filter(lambda z: z.is_flying)
                    if not scouts.exists:
                        scouts = self.units(unit.PROBE).closest_n_units(self.enemy_start_locations[0], 3)
                        if not scouts.exists:
                            scouts = self.units().closest_n_units(self.enemy_start_locations[0], 3)
        if scouts.exists:
            if len(self.observer_scouting_points) == 0:
                for exp in self.expansion_locations_list:
                    if not self.structures().closer_than(7, exp).exists:
                        self.observer_scouting_points.append(exp)
                self.observer_scouting_points = sorted(self.observer_scouting_points,
                                                       key=lambda x: self.enemy_start_locations[0].distance_to(x))
            for px in scouts.idle:
                self.do(px.move(self.observer_scouting_points[self.observer_scouting_index]))
                self.observer_scouting_index += 1
                if self.observer_scouting_index == len(self.observer_scouting_points):
                    self.observer_scouting_index = 0

    def attack_condition(self):
        return self.strategy.attack_condition()

    def get_pylon_with_least_neighbours(self):
        return self.spot_validator.get_pylon_with_least_neighbours()

    def forge_upg_priority(self):
        if self.structures(unit.TWILIGHTCOUNCIL).ready.exists:
            upgds = [upgrade.PROTOSSGROUNDWEAPONSLEVEL1, upgrade.PROTOSSGROUNDARMORSLEVEL2,
                     upgrade.PROTOSSSHIELDSLEVEL1]
        else:
            upgds = [upgrade.PROTOSSGROUNDWEAPONSLEVEL1, upgrade.PROTOSSGROUNDARMORSLEVEL1,
                     upgrade.PROTOSSSHIELDSLEVEL1]
        done = True
        for u in upgds:
            if u not in self.state.upgrades:
                done = False
                break
        if not done:
            if self.structures(unit.FORGE).ready.idle.exists:
                return True
        return False

    def get_super_pylon(self):
        pylons = self.structures(unit.PYLON).ready
        if pylons.exists:
            pylons = pylons.closer_than(45, self.start_location)
            if pylons.exists:
                pylons = pylons.sorted_by_distance_to(self.enemy_start_locations[0])
                warps = self.structures().filter(lambda x: x.type_id in [unit.WARPGATE, unit.NEXUS] and x.is_ready)
                if warps.exists:
                    for pylon in pylons:
                        if warps.closer_than(6.5, pylon).exists:
                            return pylon
                return pylons[-1]

    async def blink(self, stalker, target):
        if stalker.type_id == unit.STALKER:
            abilities = await self.get_available_abilities(stalker)
            if AbilityId.EFFECT_BLINK_STALKER in abilities:
                self.do(stalker(AbilityId.EFFECT_BLINK_STALKER, target))
                return True
            else:
                return False
        else:
            return False

    async def morph_Archons(self):
        if upgrade.PSISTORMTECH is self.state.upgrades or self.already_pending_upgrade(upgrade.PSISTORMTECH):
            archons = self.army(unit.ARCHON)
            ht_amount = int(archons.amount / 2)
            ht_thresh = ht_amount + 1
        else:
            ht_thresh = 1
        if self.units(unit.HIGHTEMPLAR).amount > ht_thresh:
            hts = self.units(unit.HIGHTEMPLAR).sorted(lambda u: u.energy)
            ht2 = hts[0]
            ht1 = hts[1]
            if ht2 and ht1:
                for ht in self.army(unit.HIGHTEMPLAR):
                    if ht.tag == ht1.tag or ht.tag == ht2.tag:
                        self.army.remove(ht)
                if ht1.distance_to(ht2) > 4:
                    if ht1.distance_to(self.main_base_ramp.bottom_center) > 30:
                        self.do(ht1.move(ht2))
                        self.do(ht2.move(ht1))
                    else:
                        self.do(ht1.move(self.main_base_ramp.bottom_center))
                        self.do(ht2.move(self.main_base_ramp.bottom_center))
                else:
                    # print('morphing!')
                    from s2clientprotocol import raw_pb2 as raw_pb
                    from s2clientprotocol import sc2api_pb2 as sc_pb
                    command = raw_pb.ActionRawUnitCommand(
                        ability_id=AbilityId.MORPH_ARCHON.value,
                        unit_tags=[ht1.tag, ht2.tag],
                        queue_command=False
                    )
                    action = raw_pb.ActionRaw(unit_command=command)
                    await self._client._execute(action=sc_pb.RequestAction(
                        actions=[sc_pb.Action(action_raw=action)]
                    ))



def test(real_time=0, n=1):
    if real_time == 1:
        real_time = True
    else:
        real_time = False
    for i in range(n):
        print('==================================================================================--> ' + str(i))
        # try:
        botVsComputer(real_time)
        # except Exception as ex:
        #     print('Error.')
        #     print(ex)


def botVsComputer(real_time):
    maps_set = ["TritonLE", "Ephemeron",
                # 'DiscoBloodbathLE',      #'Eternal Empire LE','Nightshade LE','Simulacrum LE',
                'World of Sleepers LE', 'AcropolisLE', 'ThunderbirdLE', 'WintersGateLE']
    races = [Race.Protoss, Race.Zerg, Race.Terran]

    # computer_builds = [AIBuild.Rush]
    # computer_builds = [AIBuild.Timing]
    # computer_builds = [AIBuild.Air]
    # computer_builds = [AIBuild.Power]
    computer_builds = [AIBuild.Macro]
    build = random.choice(computer_builds)
    # map_index = random.randint(0, 6)
    race_index = random.randint(0, 2)
    res = run_game(map_settings=maps.get(random.choice(maps_set)), players=[
        Bot(race=Race.Protoss, ai=OctopusEvo(None), name='Octopus'),
        Computer(race=races[2], difficulty=Difficulty.VeryHard, ai_build=build)
    ], realtime=real_time)
    return res, build, races[race_index]


# CheatMoney   VeryHard


if __name__ == '__main__':
    import time
    start = time.time()
    test(real_time=1, n=1)
    stop = time.time()
    print('\n\ntime elapsed: {} s\n\n'.format(int(stop - start)))
