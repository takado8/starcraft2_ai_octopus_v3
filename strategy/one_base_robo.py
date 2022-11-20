from army.movements import Movements
from bot.morphing import Morphing
from .strategyABS import StrategyABS
from builders.expander import Expander
from bot.chronobooster import Chronobooster
from builders.build_queues import BuildQueues
from builders.pylon_builder import PylonBuilder
from builders.assimilator_builder import AssimilatorBuilder
from army.army import Army
from builders.builder import Builder
from army.micros.micro import StalkerMicro, ZealotMicro, SentryMicro, ImmortalMicro
from bot.upgraders import ForgeUpgrader, CyberneticsUpgrader, TwilightUpgrader
from bot.trainers import WarpgateTrainer, GateTrainer, NexusTrainer, RoboticsTrainer
from bot.units_training_dicts import UnitsTrainingDicts
from army.scouting.scouting import Scouting
from economy.info.own_economy import OwnEconomy
from economy.info.enemy_economy import EnemyEconomy
from army.divisions import STALKER_x10, ZEALOT_x10, SENTRY_x3, IMMORTAL_x5
from bot.conditions import *
from economy.workers.distribute_workers import DistributeWorkers


class OneBaseRobo(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='defend', name='OneBaseRobo')
        self.morphing_ = Morphing(ai)
        self.ai = ai
        self.army = Army(ai)

        stalker_micro = StalkerMicro(ai)
        zealot_micro = ZealotMicro(ai)
        sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        self.sentry_micro = SentryMicro(ai)
        self.army.create_division('stalkers1', STALKER_x10, [stalker_micro], Movements(ai, 0.5))
        self.army.create_division('stalkers2', STALKER_x10, [stalker_micro], Movements(ai, 0.5))
        self.army.create_division('stalkers3', STALKER_x10, [stalker_micro], Movements(ai, 0.5))
        self.army.create_division('immortals1', IMMORTAL_x5, [immortal_micro], Movements(ai, 0.3))
        self.army.create_division('immortals2', IMMORTAL_x5, [immortal_micro], Movements(ai, 0.3))
        self.army.create_division('sentry1', SENTRY_x3, [sentry_micro], Movements(ai, 0.2))
        # self.army.create_division('stalkers5', STALKER_x10, [stalker_micro], Movements(ai, 0.2))
        self.army.create_division('zealot1', ZEALOT_x10, [zealot_micro], Movements(ai))
        self.army.create_division('zealot2', ZEALOT_x10, [zealot_micro], Movements(ai))
        # self.army.create_division('zealot2', ZEALOT_x10, [zealot_micro], Movements(ai))
        self.workers_distribution = DistributeWorkers(ai)

        build_queue = BuildQueues.ONE_BASE_ROBO
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))
        self.pylon_builder = PylonBuilder(ai)
        self.assimilator_builder = AssimilatorBuilder(ai)

        self.forge_upgrader = ForgeUpgrader(ai)
        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)

        units_training_dict = UnitsTrainingDicts.ONE_BASE_ROBO
        self.nexus_trainer = NexusTrainer(ai)
        self.gate_trainer = GateTrainer(ai, units_training_dict)
        self.warpgate_trainer = WarpgateTrainer(ai, units_training_dict)
        self.robotics_trainer = RoboticsTrainer(ai, units_training_dict)

        self.own_economy = OwnEconomy(ai)
        self.enemy_economy = EnemyEconomy(ai)
        self.scouting = Scouting(ai, self.enemy_economy)

        self.condition_attack = ConditionAttack(ai)
        self.condition_counter_attack = ConditionCounterAttack(ai)
        self.condition_retreat = ConditionRetreat(ai)

        self.chronobooster = Chronobooster(ai)

    def distribute_workers(self):
        self.workers_distribution.distribute_workers()

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()

    async def build_pylons(self):
        await self.pylon_builder.new_standard()
        await self.pylon_builder.proxy()

    def build_assimilators(self):
        self.assimilator_builder.standard()


    # =======================================================  Upgraders
    def forge_upgrade(self):
        self.forge_upgrader.standard()

    def cybernetics_upgrade(self):
        self.cybernetics_upgrader.warpgate()

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

    def army_refresh_and_train(self):
        self.army.refresh_all_soldiers()
        self.army.create_training_order()

    async def army_do_micro(self):
        await self.army.execute_micro()
        # self.army.print_divisions_info()

    async def attack(self):
        await self.army.attack()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.supply_over(190)

    def retreat_condition(self):
        return self.condition_retreat.supply_less_than(60)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    def chronoboost(self):
        # try:
        self.chronobooster.warpgate()
        # except Exception as ex:
        #     print(ex)

    async def lock_spending_condition(self):
        pass

    async def morphing(self):
        await self.morphing_.morph_gates()

