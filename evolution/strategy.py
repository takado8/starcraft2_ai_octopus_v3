from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from builders.expander import Expander
from bot.chronobooster import Chronobooster
from builders.build_queues import BuildQueues
from builders.pylon_builder import PylonBuilder
from builders.assimilator_builder import AssimilatorBuilder
from army.army import Army
from bot.builder import Builder
from army.micro import StalkerMicro, SentryMicro, ZealotMicro
from bot.upgraders import ForgeUpgrader, CyberneticsUpgrader, TwilightUpgrader
from bot.trainers import WarpgateTrainer, GateTrainer, NexusTrainer, RoboticsTrainer
from bot.units_training_dicts import UnitsTrainingDicts
from army.scouting.scouting import Scouting
from economy.own_economy import OwnEconomy
from economy.enemy_economy import EnemyEconomy


class EvolutionStrategy:
    def __init__(self, ai):
        self.ai = ai
        self.type = 'macro'
        self.name = 'evo'
        self.chronobooster = Chronobooster(ai)
        self.stalker_micro = StalkerMicro(ai)
        self.zealot_micro = ZealotMicro(ai)
        self.sentry_micro = SentryMicro(ai)

        self.army = Army(ai)
        build_queue = BuildQueues.STALKER_RUSH
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))
        self.pylon_builder = PylonBuilder(ai)
        self.assimilator_builder = AssimilatorBuilder(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        units_training_dict = UnitsTrainingDicts.STALKER_RUSH
        self.nexus_trainer = NexusTrainer(ai)
        self.gate_trainer = GateTrainer(ai, units_training_dict)
        self.warpgate_trainer = WarpgateTrainer(ai, units_training_dict)
        self.robotics_trainer = RoboticsTrainer(ai, units_training_dict)
        self.own_economy = OwnEconomy(ai)
        self.enemy_economy = EnemyEconomy(ai)
        self.scouting = Scouting(ai, self.enemy_economy)


    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()

    async def build_pylons(self):
        await self.pylon_builder.new_standard()
        await self.pylon_builder.proxy()

    # =======================================================  Upgraders
    def forge_upgrade(self):
        self.forge_upgrader.standard()

    def cybernetics_upgrade(self):
        self.cybernetics_upgrader.standard()

    async def twilight_upgrade(self):
        await self.twilight_upgrader.standard()

    # =======================================================  Trainers
    async def train_units(self):
        self.gate_trainer.standard()
        await self.warpgate_trainer.standard()
        self.robotics_trainer.standard_new()

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army

    async def micro(self):
        # self.army_obj.do_stuff()
        await self.stalker_micro.personal_new()
        await self.zealot_micro.standard()
        await self.sentry_micro.standard()

    async def movements(self):
        enemy_units = self.ai.enemy_units()
        enemy = enemy_units.filter(lambda x: x.type_id not in self.ai.units_to_ignore and (x.can_attack_ground
                                                                                           or x.can_attack_air))
        enemy.extend(self.ai.enemy_structures().filter(lambda b: b.type_id in self.ai.bases_ids
                                                                 or b.can_attack_ground or b.can_attack_air or b.type_id == unit.BUNKER))
        if self.ai.enemy_main_base_down or (
                self.ai.army.closer_than(20, self.ai.enemy_start_locations[0]).amount > 17 and
                not self.ai.enemy_structures().exists):
            if not self.ai.enemy_main_base_down:
                await self.ai.chat_send('enemy main base down.')
                self.ai.enemy_main_base_down = True
            self.ai.scan()
            enemy_units.extend(self.ai.enemy_structures())
            if enemy_units.exists:
                for man in self.ai.army.exclude_type(unit.OBSERVER):
                    self.ai.do(man.attack(enemy_units.closest_to(man)))


        if enemy.amount > 1:
            if enemy.closer_than(35, self.ai.start_location).amount > 1:
                destination = enemy.closest_to(self.ai.start_location).position
            else:
                destination = enemy.further_than(25, self.ai.start_location)
                if destination:
                    destination = destination.closest_to(self.ai.start_location).position
                elif self.ai.enemy_structures().exists:
                    enemy = self.ai.enemy_structures()
                    destination = enemy.closest_to(self.ai.start_location).position
                else:
                    enemy = None
                    destination = self.ai.enemy_start_locations[0].position
        elif self.ai.enemy_structures().exists:
            enemy = self.ai.enemy_structures()
            destination = enemy.closest_to(self.ai.start_location).position
        else:
            enemy = None
            if self.ai.enemy_main_base_down:
                if len(self.ai.observer_scouting_points) == 0:
                    for exp in self.ai.expansion_locations:
                        if not self.ai.structures().closer_than(7, exp).exists:
                            self.ai.observer_scouting_points.append(exp)
                    self.ai.observer_scouting_points = sorted(self.ai.observer_scouting_points,
                                                              key=lambda x: self.ai.enemy_start_locations[
                                                                  0].distance_to(x))
                if self.ai.army() and self.ai.army().closer_than(12, self.ai.observer_scouting_points[
                    self.ai.observer_scouting_index]).amount > 12 \
                        and self.ai.enemy_structures().amount < 1:
                    self.ai.observer_scouting_index += 1
                    if self.ai.observer_scouting_index == len(self.ai.observer_scouting_points):
                        self.ai.observer_scouting_index = 0
                destination = self.ai.observer_scouting_points[self.ai.observer_scouting_index]
            else:
                destination = self.ai.enemy_start_locations[0].position

        if self.ai.leader_tag is None or self.ai.army.find_by_tag(self.ai.leader_tag) is None:
            self.ai.leader_tag = self.ai.army.closest_to(destination).tag

        leader = self.ai.army.find_by_tag(self.ai.leader_tag)
        self.ai.destination = destination

        # point halfway
        dist = leader.distance_to(destination)
        step = 23
        if dist > step:
            point = leader.position.towards(destination, step)
        else:
            point = destination
        position = None
        i = 0
        while position is None:
            i += 1
            position = await self.ai.find_placement(unit.PYLON, near=point.random_on_distance(i * 2), max_distance=5,
                                                    placement_step=2, random_alternative=False)
            if i > 7:
                print("can't find position for army.")
                return
        # if everybody's here, we can go
        army = self.ai.army
        _range = 7 if army.amount < 27 else 14
        nearest = []
        i = 3
        pos = leader.position
        while not self.ai.in_pathing_grid(pos) and i < 6:
            pos = leader.position.random_on_distance(i)
            i += 1
            j = 1
            while not self.ai.in_pathing_grid(pos) and j < 3:
                # print('func j: ' + str(j))
                pos = pos.random_on_distance(j)
                j += 1
        for man in army:
            if man.distance_to(leader) <= _range:  # with army
                nearest.append(man)
                if enemy and not enemy.in_attack_range_of(man).exists:
                    # go help someone who is fighting
                    h = army.filter(lambda x: x.is_attacking)
                    if h.exists:
                        self.ai.do(man.attack(enemy.closest_to(h.closest_to(man))))
            elif man.type_id not in [unit.ZEALOT, unit.DARKTEMPLAR] or not man.is_attacking:  # away. join army
                self.ai.do(man.move(pos))
        if len(nearest) > len(self.ai.army) * 0.70:  # take next position
            if enemy and enemy.closer_than(11, leader).exists:
                return
            for man in army:
                self.ai.do(man.attack(position))

    # ======================================================= Conditions

    # ======================================================== Buffs
    def chronoboost(self):
        try:
            self.chronobooster.standard()
        except Exception as ex:
            print(ex)

    def build_assimilators(self):
        self.assimilator_builder.standard()
