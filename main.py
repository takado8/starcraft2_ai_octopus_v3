import random
import sc2
from sc2 import run_game, maps, Race, Difficulty, AIBuild, AbilityId, Result
from sc2.ids.effect_id import EffectId as effect
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2, Point3
from bot.building_spot_validator import BuildingSpotValidator
from bot.chronobooster import Chronobooster
from typing import Optional, Union
from bot.coords import coords
from bot.constants import ARMY_IDS, BASES_IDS, WORKERS_IDS, UNITS_TO_IGNORE

from evolution.evo import Evolution
from strategy.stalker_mid import StalkerMid
from strategy.stalker_proxy import StalkerProxy


class OctopusEvo(sc2.BotAI):
    army_ids = ARMY_IDS
    bases_ids = BASES_IDS
    units_to_ignore = UNITS_TO_IGNORE
    workers_ids = WORKERS_IDS

    enemy_main_base_down = False
    leader_tag = None
    destination = None
    lost_cost = 0
    killed_cost = 0
    scoutings_last_attack = 0

    def __init__(self, genome=None):
        super().__init__()
        self.structures_amount = 0
        self.spot_validator = BuildingSpotValidator(self)
        self.chronobooster = Chronobooster(self)
        self.attack = False
        self.first_attack = False
        self.retreat = False
        self.after_first_attack = False
        self.defend_position = None
        self.army = None
        self.strategy: StalkerMid = None
        self.coords = None

    # async def on_unit_created(self, unit: Unit):
    #     if unit.is_mine and unit.type_id in self.army_ids:
    #         self.strategy.army.add_unassigned_soldier(unit)

    async def on_unit_destroyed(self, unit_tag: int):
        self.strategy.enemy_economy.on_unit_destroyed(unit_tag)

    async def on_start(self):
        self.strategy = StalkerMid(self)
        map_name = str(self.game_info.map_name)
        print('map_name: ' + map_name)
        print('start location: ' + str(self.start_location.position))
        if map_name in coords and self.start_location.position in coords[map_name]:
            self.coords = coords[map_name][self.start_location.position]
            print('getting coords successful.')
        else:
            print('getting coords failed')
            await self.chat_send('getting coords failed')

    async def on_step(self, iteration: int):
        # self.save_stats()
        self.set_game_step()
        self.army = self.units().filter(lambda x: x.type_id in self.army_ids and x.is_ready)
        self.strategy.army_refresh_and_train()
        self.assign_defend_position()
        await self.distribute_workers()
        await self.morph_gates()
        self.strategy.chronoboost()
        await self.warp_prism()
        await self.morph_Archons()
        await self.strategy.build_pylons()
        self.strategy.train_probes()
        self.strategy.build_assimilators()
        await self.strategy.twilight_upgrade()
        self.strategy.cybernetics_upgrade()
        self.strategy.forge_upgrade()
        # await self.build_batteries()
        # await self.shield_overcharge()
        #
        ## scan
        # self.strategy.scouting.scan_middle_game()
        self.strategy.scouting.gather_enemy_info()
        self.strategy.own_economy.calculate_units_report()
        self.strategy.enemy_economy.calculate_enemy_units_report()

        # if iteration % 30 == 0:
        #     self.strategy.enemy_economy.print_enemy_info()
        #     self.strategy.own_economy.print_own_economy_info()
        #
        ## attack
        army_priority = False
        if (not self.attack) and (not self.retreat_condition()) and (
                self.counter_attack_condition() or self.attack_condition()):
            # await self.chat_send('Attack!  army len: ' + str(len(self.army)))
            self.first_attack = True
            self.attack = True
            self.retreat = False
            army_priority = True
        # retreat
        if self.retreat_condition():
            # await self.chat_send('Retreat! army len: ' + str(len(self.army)))
            self.retreat = True
            self.attack = False
            self.after_first_attack = True
        try:
            if self.attack:
                await self.strategy.army.attack()
            else:
                await self.defend()
        except Exception as ex:
            print(ex)
            await self.chat_send('on_step error 10')
            raise ex
        try:
            await self.strategy.army_do_micro()
        except Exception as ex:
            print(ex)
            await self.chat_send('on_step error 9')
            raise ex
        self.avoid_aoe()
        #
        ## build
        current_building = self.strategy.builder.get_current_building()

        build_in_progress = self.strategy.builder.is_build_in_progress()
        build_finished = self.strategy.builder.is_build_finished()

        if not isinstance(current_building, unit):
            min_army_supply = current_building
            if self.state.score.food_used_army > min_army_supply:
                self.strategy.builder.increment_build_queue_index()
            else:
                army_priority = True
        forge_priority = await self.is_forge_upg_priority()
        if (build_in_progress or build_finished or army_priority or
            (self.minerals > 500 and self.vespene > 300)) and not forge_priority:
            await self.strategy.train_units()

        if not army_priority and not build_finished and not forge_priority:
            await self.strategy.build_from_queue()

    async def build(self, building: unit, near: Union[Unit, Point2, Point3], max_distance: int = 20, block=False,
                    build_worker: Optional[Unit] = None, random_alternative: bool = True,
                    placement_step: int = 3, ) -> bool:
        return await self.strategy.builder.build(building=building, near=near, max_distance=max_distance, block=block,
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
                position = Point2(self.defend_position).towards(self.game_info.map_center, 5) if \
                    man.type_id == unit.ZEALOT else Point2(self.defend_position)
                if man.distance_to(self.defend_position) > dist:
                    self.do(man.attack(position.random_on_distance(random.randint(1, 2))))

    def assign_defend_position(self):
        nex = self.structures(unit.NEXUS).ready
        enemy = self.enemy_units()

        if enemy.exists and enemy.closer_than(50, self.start_location).amount > 1:
            self.defend_position = enemy.closest_to(self.enemy_start_locations[0]).position
        elif nex.amount < 2:
            self.defend_position = self.main_base_ramp.top_center.towards(self.main_base_ramp.bottom_center, -6)
        else:
            self.defend_position = nex.closest_to(self.enemy_start_locations[0]).position.towards(
                self.game_info.map_center, 5)

    def get_pylon_with_least_neighbours(self):
        return self.spot_validator.get_pylon_with_least_neighbours()

    async def is_forge_upg_priority(self):
        upgrades_abilities_ids = [AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1,
                                  AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL1,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2,
                                  AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL2,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3,
                                  AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3,
                                  AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL3]

        if self.structures(unit.TWILIGHTCOUNCIL).ready.exists:
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
            if u not in self.state.upgrades:
                done = False
                break
        if not done:
            forges = self.structures(unit.FORGE).ready
            if forges.exists:
                for forge in forges.idle:
                    abilities = await self.get_available_abilities(forge, ignore_resource_requirements=True)
                    for ab in abilities:
                        if ab in upgrades_abilities_ids:
                            if not self.can_afford(ab):
                                return True
        return False

    def set_game_step(self):
        if self.enemy_units().exists:
            self._client.game_step = 4
        else:
            self._client.game_step = 8

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
        self.structures_amount = self.structures().amount

    def attack_condition(self):
        return self.strategy.attack_condition()

    def retreat_condition(self):
        return self.strategy.retreat_condition()

    def counter_attack_condition(self):
        return self.strategy.counter_attack_condition()

    def avoid_aoe(self):
        aoes_ids = [effect.RAVAGERCORROSIVEBILECP, effect.PSISTORMPERSISTENT, effect.NUKEPERSISTENT,
                    effect.LIBERATORTARGETMORPHDELAYPERSISTENT]
        purification_novas = self.enemy_units(unit.DISRUPTORPHASED)
        purification_novas.extend(self.units(unit.DISRUPTORPHASED))
        for man in self.army:
            if purification_novas.exists and purification_novas.closer_than(3, man).exists:
                self.do(man.move(man.position.towards(purification_novas.closest_to(man), -4)))
                continue
            for eff in self.state.effects:
                if eff.id in aoes_ids:
                    positions = eff.positions
                    for position in positions:
                        if man.distance_to(position) < eff.radius + 2:
                            self.do(man.move(man.position.towards(position, -3)))

    async def build_batteries(self):
        nexuses = self.structures(unit.NEXUS).ready
        if nexuses.amount > 1:
            start_nexus = nexuses.closest_to(self.start_location.position)
            nexuses.remove(start_nexus)
            for nexus in nexuses:
                pylon = self.structures(unit.PYLON).ready.closer_than(11, nexus)
                if pylon.exists:
                    pylon = pylon.furthest_to(nexus)
                    if self.structures(unit.SHIELDBATTERY).closer_than(5, pylon.position).amount < 2 \
                            and self.already_pending(unit.SHIELDBATTERY) < 2:
                        await self.build(unit.SHIELDBATTERY, pylon.position, max_distance=5,
                                         random_alternative=False, placement_step=2)
                elif self.already_pending(unit.PYLON) < 1:
                    minerals = self.mineral_field.closest_to(nexus.position)
                    if minerals.distance_to(nexus.position) < 12:
                        pylon_spot = nexus.position.towards(minerals, -7)
                        await self.build(unit.PYLON, pylon_spot)

    async def shield_overcharge(self):
        en = self.enemy_units()
        if en.exists and en.closer_than(40, self.defend_position).amount > 5:
            nexus = self.structures(unit.NEXUS).ready.closest_to(self.defend_position)
            battery = self.structures(unit.SHIELDBATTERY).ready.closer_than(10, nexus) \
                .sorted(lambda x: x.health, reverse=True)
            if battery and nexus:
                battery = battery[0]
                if nexus.energy >= 50:
                    abilities = await self.get_available_abilities(nexus)
                    # print('nexus abilities: {}'.format(abilities))
                    if AbilityId.BATTERYOVERCHARGE_BATTERYOVERCHARGE in abilities:
                        self.do(nexus(AbilityId.BATTERYOVERCHARGE_BATTERYOVERCHARGE, battery))


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
    # computer_builds = [AIBuild.Timing, AIBuild.Rush, AIBuild.Power, AIBuild.Macro]
    # computer_builds = [AIBuild.Timing]
    # computer_builds = [AIBuild.Air]
    computer_builds = [AIBuild.Power]
    # computer_builds = [AIBuild.Macro]
    build = random.choice(computer_builds)

    # map_index = random.randint(0, 6)
    # race_index = random.randint(0, 2)
    result = run_game(map_settings=maps.get(random.choice(maps_set)), players=[
        Bot(race=Race.Protoss, ai=ai, name='Octopus'),
        Computer(race=races[2], difficulty=Difficulty.VeryHard, ai_build=build)
    ], realtime=real_time)
    return result, ai  # , build, races[race_index]


def test(genome, real_time=1):
    ai = OctopusEvo(genome)
    result, ai = botVsComputer(ai, real_time)
    print('Result: {}'.format(result))
    print('lost: {}'.format(ai.lost_cost))
    print('killed: {}'.format(ai.killed_cost))

    if result == Result.Victory:
        win = 1
    elif result == Result.Defeat:
        win = 0
    elif ai.structures_amount > 5:
        win = 1
    else:
        win = 0
    return win, ai.killed_cost, ai.lost_cost


# CheatMoney   VeryHard


if __name__ == '__main__':
    import time
    import uuid

    evo = Evolution(population_count=15, reproduction_rate=0.70, load_population_directory='genomes/initial')
    generations_nb = 15
    generation_directory_name = 'genomes/{}_generation_'.format(str(uuid.uuid4()))
    for i in range(generations_nb):
        k = 0
        for subject in evo.population:
            k += 1
            print('sub nr: {}'.format(k))
            print(subject.genome)
            start = time.time()
            # subject.genome.build_order = OctopusEvo.strategy.build_order
            # subject.genome.units_ratio = OctopusEvo.UNITS_RATIO
            win, killed, lost = test(real_time=0, genome=subject.genome)
            stop = time.time()
            print('result: {} time elapsed: {} s'.format('win' if win else 'lost', int(stop - start)))
            fitness = 10000 * win + killed - lost
            subject.fitness = fitness
        print('i: {} avg fit: {} best fit: {}'.format(i, round(
            sum([s.fitness for s in evo.population]) / len(evo.population), 4),
                                                      round(max([s.fitness for s in evo.population]), 4)))
        evo.evolve()

        for s in evo.population:
            s.genome.save_genome(directory=generation_directory_name + str(i + 1))

    for s in evo.population:
        print(s.genome)
        print('fit: {}'.format(s.fitness))
        s.genome.save_genome(directory=generation_directory_name + 'final')
