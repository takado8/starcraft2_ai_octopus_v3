import random
import sc2
from sc2 import run_game, maps, Race, Difficulty, AIBuild, AbilityId, Result
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2, Point3
from bot.building_spot_validator import BuildingSpotValidator
from bot.chronobooster import Chronobooster
from typing import Optional, Union
from evolution.strategy import EvolutionStrategy
from bot.builder import Builder


class OctopusEvo(sc2.BotAI):
    army_ids = [unit.ADEPT, unit.STALKER, unit.ZEALOT, unit.SENTRY, unit.OBSERVER, unit.IMMORTAL, unit.ARCHON,
                unit.HIGHTEMPLAR, unit.DARKTEMPLAR, unit.WARPPRISM, unit.VOIDRAY, unit.CARRIER, unit.COLOSSUS,
                unit.TEMPEST]
    bases_ids = [unit.NEXUS, unit.COMMANDCENTER, unit.COMMANDCENTERFLYING, unit.ORBITALCOMMAND,
                 unit.ORBITALCOMMANDFLYING,
                 unit.PLANETARYFORTRESS, unit.HIVE, unit.HATCHERY, unit.LAIR]
    units_to_ignore = [unit.LARVA, unit.EGG, unit.INTERCEPTOR]
    workers_ids = [unit.SCV, unit.PROBE, unit.DRONE, unit.MULE]
    enemy_main_base_down = False
    leader_tag = None
    destination = None
    psi_storm_wait = 0
    nova_wait = 0
    lost_cost = 0
    killed_cost = 0


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
        self.strategy: EvolutionStrategy = None
        self.genome = genome
        self.build_order = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                            unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.TWILIGHTCOUNCIL,
                            unit.TEMPLARARCHIVE, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY,
                            unit.ROBOTICSFACILITY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS]
        self.build_order_index = 0
        self.eco_to_army_ratio = 0.25 #genome.eco_to_army_ratio
        # self.units_ratio = genome.units_ratio

    async def on_start(self):
        self.strategy = EvolutionStrategy(self)

    async def on_step(self, iteration: int):
        self.save_stats()

        self.army = self.units().filter(lambda x: x.type_id in self.army_ids and x.is_ready)
        self.assign_defend_position()
        await self.distribute_workers()
        await self.morph_gates()
        self.strategy.chronoboost()
        await self.warp_prism()
        await self.morph_Archons()
        await self.strategy.build_pylons()
        self.strategy.train_probes()
        self.strategy.build_assimilators()
        await self.strategy.twilight_upgrades()
        self.strategy.cybernetics_upgrade()
        self.strategy.forge_upgrades()

        supply_army = self.state.score.total_used_minerals_army + 1.2 * self.state.score.total_used_vespene_army\
                      - self.state.score.lost_minerals_army - 1.2 * self.state.score.lost_vespene_army
        supply_eco = self.state.score.total_used_minerals_economy + 1.2 * self.state.score.total_used_vespene_economy\
                     - 1000 - self.state.score.lost_minerals_economy - 1.2 * self.state.score.lost_vespene_economy
        print('supply used army: {}\nsupply used eco: {}'.format(supply_army, supply_eco))
        build_in_progress = False
        for building in self.build_order:
            if self.already_pending(building):
                build_in_progress = True
        build_finished = False
        if self.build_order_index + 1 == len(self.build_order):
            build_finished = True

        if build_in_progress or build_finished or (self.minerals > 500 and self.vespene > 300):
            await self.strategy.train_units()

        await self.strategy.build_from_queue()

        # attack
        if (not self.attack) and (not self.retreat_condition(army_count_retreat=15)) and (
                self.counter_attack_condition() or self.attack_condition(max_supply=195)):
            # await self.chat_send('Attack!  army len: ' + str(len(self.army)))
            self.first_attack = True
            self.attack = True
            self.retreat = False
        # retreat
        if self.retreat_condition(5):
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

    async def build(self, building: unit, near: Union[Unit, Point2, Point3], max_distance: int = 20, block=False,
                    build_worker: Optional[Unit] = None, random_alternative: bool = True,
                    placement_step: int = 3, ) -> bool:
        return await self.builder.build(building=building, near=near, max_distance=max_distance, block=block,
                                        build_worker=build_worker, random_alternative=random_alternative)

    async def morph_gates(self):
        for gateway in self.structures(unit.GATEWAY).ready:
            abilities = await self.get_available_abilities(gateway)
            if AbilityId.MORPH_WARPGATE in abilities and self.can_afford(AbilityId.MORPH_WARPGATE):
                self.do(gateway(AbilityId.MORPH_WARPGATE))

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

    async def warp_prism(self):
        if self.attack:
            dist = self.enemy_start_locations[0].distance_to(self.game_info.map_center) * 0.8
            for warp in self.units(unit.WARPPRISM):
                if warp.distance_to(self.enemy_start_locations[0]) <= dist:
                    abilities = await self.get_available_abilities(warp)
                    if AbilityId.MORPH_WARPPRISMPHASINGMODE in abilities:
                        self.do(warp(AbilityId.MORPH_WARPPRISMPHASINGMODE))
        else:
            for warp in self.units(unit.WARPPRISMPHASING):
                abilities = await self.get_available_abilities(warp)
                if AbilityId.MORPH_WARPPRISMTRANSPORTMODE in abilities:
                    self.do(warp(AbilityId.MORPH_WARPPRISMTRANSPORTMODE))

    def save_stats(self):
        self.lost_cost = self.state.score.lost_minerals_army + 1.2 * self.state.score.lost_vespene_army
        self.killed_cost = self.state.score.killed_minerals_army + 1.2 * self.state.score.killed_vespene_army
        # print('lost_cost: ' + str(self.lost_cost))
        # print('killed_cost: ' + str(self.killed_cost))

    def attack_condition(self, max_supply):
        return self.supply_used > max_supply

    def retreat_condition(self, army_count_retreat):
        return self.attack and self.army.amount < army_count_retreat

    def counter_attack_condition(self):
        en = self.enemy_units()
        return en.exists and en.closer_than(40, self.defend_position).amount > 5


def botVsComputer(ai, real_time=0):
    if real_time:
        real_time = True
    else:
        real_time = False
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
    # race_index = random.randint(0, 2)
    result = run_game(map_settings=maps.get(random.choice(maps_set)), players=[
        Bot(race=Race.Protoss, ai=ai, name='Octopus'),
        Computer(race=races[0], difficulty=Difficulty.VeryHard, ai_build=build)
    ], realtime=real_time)
    return result, ai  # , build, races[race_index]


def test(genome, real_time=0):
    ai = OctopusEvo(genome)
    result, ai = botVsComputer(ai, real_time)
    print('Result: {}'.format(result))
    print('lost: {}'.format(ai.lost_cost))
    print('killed: {}'.format(ai.killed_cost))
    if result == Result.Victory:
        win = 1
    else:
        win = 0
    return win, ai.killed_cost, ai.lost_cost


# CheatMoney   VeryHard


if __name__ == '__main__':
    import time

    start = time.time()
    test(real_time=1, genome=None)
    stop = time.time()
    print('\n\ntime elapsed: {} s\n\n'.format(int(stop - start)))
