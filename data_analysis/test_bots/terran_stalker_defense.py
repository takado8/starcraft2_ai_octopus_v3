import random

import sc2

from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability
from sc2 import run_game, maps, Race
from sc2.player import Bot
from data_analysis.test_bots.worker_rush import WorkerRushZergBot


class TerranStalkerDefense(sc2.BotAI):
    def __init__(self):
        super().__init__()
        self.depots_pos = None
        self.second_depot_place = None

    async def on_start(self):
        self.depots_pos = [x for x in self.main_base_ramp.corner_depots]

    async def on_step(self, iteration):
        self.train_workers()
        await self.distribute_workers()
        await self.build_depots()
        await self.build_barracks()
        # await self.build_factory()
        await self.build_bunker()
        await self.build_refinery()
        self.train_marines()
        # self.train_tank()
        # self.siege_up_tanks()
        self.load_up_bunkers()
        self.build_barracks_reactor()
        await self.build_factory_techlab()
        # await self.expand()
        self.lower_depots()
        self.marine_micro()
        self.repair_damaged_units()

    async def expand(self):
        if self.structures(unit.BUNKER).ready.exists and self.townhalls.amount < 2:
            if self.can_afford(unit.COMMANDCENTER) and not self.already_pending(unit.COMMANDCENTER):
                await self.expand_now()

    def lower_depots(self):
        if not self.enemy_units.filter(lambda x: x.can_attack_ground or x.can_attack_air).exists:
            for depot in self.structures(unit.SUPPLYDEPOT).ready:
                depot(ability.MORPH_SUPPLYDEPOT_LOWER)
        else:
            for depot in self.structures(unit.SUPPLYDEPOTLOWERED).ready:
                depot(ability.MORPH_SUPPLYDEPOT_RAISE)

    async def build_refinery(self):
        if self.can_afford(unit.REFINERY) and self.structures(unit.REFINERY).amount < 2 and not self.already_pending(
                unit.REFINERY):
            await self.build(unit.REFINERY,
                             near=self.vespene_geyser.closer_than(10, self.start_location.position).random)

    def train_marines(self):
        barracks = self.structures().filter(lambda x: x.type_id == unit.BARRACKS and x.is_ready and
                                                      len(x.orders) < 2 and x.has_reactor)

        if self.can_afford(unit.MARINE) and barracks.exists:
            self.train(unit.MARINE)

    def train_tank(self):
        if self.can_afford(unit.SIEGETANK) and self.structures(unit.FACTORY).ready.idle.exists and \
                self.units({unit.SIEGETANK, unit.SIEGETANKSIEGED}).amount < 4:
            self.train(unit.SIEGETANK)

    async def build_bunker(self):
        if self.can_afford(unit.BUNKER) and self.structures(unit.BARRACKS).ready.exists and \
                self.structures(unit.BUNKER).amount < 1 and not self.already_pending(unit.BUNKER):
            natural_location = \
                min([(self.main_base_ramp.bottom_center.distance_to(x), x) for x in self.expansion_locations_list],
                    key=lambda x: x[0])[1]
            # bunker_location = self.mineral_field.closest_to(natural_location).position.towards(natural_location, 10)
            bunker_location = natural_location.position.towards(self.game_info.map_center, 10)
            await self.build(unit.BUNKER, bunker_location)

    async def build_factory(self):
        if self.can_afford(unit.FACTORY) and not self.already_pending(unit.FACTORY) \
                and self.structures(unit.FACTORY).amount < 1 and self.structures(unit.BARRACKS).ready.exists:
            await self.build(unit.FACTORY, self.start_location.position.random_on_distance(12))

    async def build_barracks(self):
        barracks = self.structures(unit.BARRACKS)
        if self.can_afford(unit.BARRACKS) and not self.already_pending(unit.BARRACKS):
            if not barracks:
                await self.build(unit.BARRACKS, self.main_base_ramp.barracks_correct_placement)
            elif 2 > barracks.amount > 0 :#and self.structures(unit.FACTORY).exists:
                await self.build(unit.BARRACKS, self.start_location.position.random_on_distance(12))

    def train_workers(self):
        if self.can_afford(unit.SCV) and self.workers.amount < self.townhalls.amount * 16 + self.structures(
                unit.REFINERY).amount * 3 \
                and self.townhalls.ready.idle.exists:
            self.train(unit.SCV)

    async def build_depots(self):
        depots = self.structures({unit.SUPPLYDEPOT, unit.SUPPLYDEPOTLOWERED})
        if self.can_afford(unit.SUPPLYDEPOT) and not self.already_pending(unit.SUPPLYDEPOT) and \
                (depots.amount < 2 or self.supply_left < 5):

            if not depots or not depots.closer_than(0.2, self.depots_pos[0]).exists:
                place = self.depots_pos[0]
            elif not depots or not depots.closer_than(0.2, self.depots_pos[1]).exists:
                place = self.depots_pos[1]
            else:
                place = self.start_location.position.random_on_distance(7)
            await self.build(unit.SUPPLYDEPOT, place)

    def build_barracks_reactor(self):
        if self.can_afford(unit.BARRACKSREACTOR):
            barracks = self.structures().filter(lambda x: x.type_id == unit.BARRACKS and x.is_ready and
                                               not x.has_reactor)

            for barrack in barracks:
                barrack(ability.BUILD_REACTOR_BARRACKS, barrack.position)

    async def build_factory_techlab(self):
        if self.can_afford(unit.TECHLAB):
            factories = self.structures().filter(lambda x: x.type_id == unit.FACTORY and x.is_ready)
            factories_no_lab = factories.filter(lambda x: not x.has_techlab)
            if factories_no_lab and factories_no_lab.amount == factories.amount:
                can_place_add_on = False
                for factory in factories:
                    if await self.can_place_single(unit.FACTORYTECHLAB,factory.add_on_position):
                        factory(ability.BUILD_TECHLAB_FACTORY, factory.position)
                        can_place_add_on = True
                        break
                if not can_place_add_on:
                    factory = factories_no_lab.random
                    factory(ability.BUILD_TECHLAB_FACTORY,
                            await self.find_placement(unit.FACTORY, near=factory.position))

    def siege_up_tanks(self):
        tanks = self.units(unit.SIEGETANK).ready.idle
        bunkers = self.structures(unit.BUNKER)
        if bunkers.exists:
            siege_location = bunkers.random.position.towards(self.game_info.map_center, -5)\
                .random_on_distance(3)
        else:
            siege_location = self.main_base_ramp.top_center.towards(self.main_base_ramp.bottom_center, -5) \
                .random_on_distance(2)

        for tank in tanks:
            if tank.distance_to(siege_location) > 3:
                tank.move(siege_location)
            else:
                tank(ability.SIEGEMODE_SIEGEMODE)

    def load_up_bunkers(self):
        bunkers = self.structures(unit.BUNKER)
        marines = self.units(unit.MARINE).ready
        if marines:
            for bunker in bunkers:
                if bunker.cargo_left > 0:
                    marines.closest_to(bunker)(ability.SMART, bunker)

    def marine_micro(self):
        enemy = self.enemy_units()
        marines = self.units(unit.MARINE).ready

        if enemy and enemy.closer_than(20, self.main_base_ramp.top_center).exists:
            for marine in marines.idle:
                marine.attack(enemy.closest_to(marine.position))
        else:
            bunkers = self.structures(unit.BUNKER)

            for marine in marines:
                if bunkers.exists:
                    bunker = bunkers.closest_to(marine)
                    if marine.distance_to(bunker) > 10:
                        marine.move(bunker.position.random_on_distance(5))

    async def make_mules(self):
        for base in self.townhalls.ready:
            abilities = await self.get_available_abilities(base)
            print(abilities)
            if base.energy >= 50:
                base(ability.CALLDOWNMULE_CALLDOWNMULE, self.mineral_field.closest_to(base))

    def repair_damaged_units(self):
        tanks = self.units().filter(lambda x: x.type_id in {unit.SIEGETANKSIEGED, unit.SIEGETANK} and
                                    x.health_percentage < 1)
        bunkers = self.structures().filter(lambda x: x.type_id == unit.BUNKER and x.health_percentage < 1)
        wall_buildings = self.structures().filter(lambda x: x.type_id in {unit.SUPPLYDEPOT,
                             unit.BARRACKS, unit.BARRACKSREACTOR,unit.BARRACKSTECHLAB} and x.health_percentage< 1 and
                                                     x.distance_to(self.main_base_ramp.top_center) < 5)

        workers = self.workers.filter(lambda x: x.is_idle or x.is_gathering or x.is_moving)

        for damaged in tanks + bunkers + wall_buildings:
            if workers:
                worker = workers.closest_to(damaged)
                worker.repair(damaged)
                workers.remove(worker)
            else:
                break



def run(real_time=0):
    if real_time:
        real_time = True
    else:
        real_time = False

    maps_list = ["BerlingradAIE", "HardwireAIE", "InsideAndOutAIE", "MoondanceAIE", "StargazersAIE",
                 "WaterfallAIE"]

    # a_map = maps_list[5]
    a_map = random.choice(maps_list)
    run_game(map_settings=maps.get(a_map), players=[
        Bot(race=Race.Terran, ai=TerranStalkerDefense(), name='PositionsSetup'),
        Bot(race=Race.Zerg, ai=WorkerRushZergBot(), name='ZergRush')

    ], realtime=real_time)


if __name__ == '__main__':
    run(real_time=0)
