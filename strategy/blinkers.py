from army.movements import Movements
from bot.morphing import Morphing
from .strategyABS import StrategyABS
from builders.expander import Expander
from bot.chronobooster import Chronobooster
from builders.build_queues import BuildQueues
from builders.pylon_builder import PylonBuilder
from builders.assimilator_builder import AssimilatorBuilder
from army.army import Army
from bot.builder import Builder
from army.micros.micro import StalkerMicro
from bot.upgraders import ForgeUpgrader, CyberneticsUpgrader, TwilightUpgrader
from bot.trainers import WarpgateTrainer, GateTrainer, NexusTrainer, RoboticsTrainer
from bot.units_training_dicts import UnitsTrainingDicts
from army.scouting.scouting import Scouting
from economy.own_economy import OwnEconomy
from economy.enemy_economy import EnemyEconomy
from army.divisions import STALKER_x10
from bot.conditions import *


class Blinkers(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='rush', name='Blinkers')
        self.morphing_ = Morphing(ai)
        self.ai = ai
        self.army = Army(ai)

        stalker_micro = StalkerMicro(ai)
        # zealot_micro = ZealotMicro(ai)
        # self.sentry_micro = SentryMicro(ai)
        self.army.create_division('stalkers1', STALKER_x10, [stalker_micro], Movements(ai))
        self.army.create_division('stalkers2', STALKER_x10, [stalker_micro], Movements(ai))
        self.army.create_division('stalkers3', STALKER_x10, [stalker_micro], Movements(ai))
        self.army.create_division('stalkers4', STALKER_x10, [stalker_micro], Movements(ai))
        self.army.create_division('stalkers5', STALKER_x10, [stalker_micro], Movements(ai))
        self.army.create_division('stalkers6', STALKER_x10, [stalker_micro], Movements(ai))
        # self.army.create_division('zealot1', ZEALOT_x10, [zealot_micro], Movements(ai))
        # self.army.create_division('zealot2', ZEALOT_x10, [zealot_micro], Movements(ai))

        build_queue = BuildQueues.STALKER_BLINKERS
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))
        self.pylon_builder = PylonBuilder(ai)
        self.assimilator_builder = AssimilatorBuilder(ai)

        self.forge_upgrader = ForgeUpgrader(ai)
        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)

        units_training_dict = UnitsTrainingDicts.STALKER_MID
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
        self.condition_lock_spending = ConditionLockSpending(ai)

        self.chronobooster = Chronobooster(ai)


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

    def army_refresh_and_train(self):
        self.army.refresh_all_soldiers()
        self.army.train_divisions()

    async def army_do_micro(self):
        await self.army.execute_divisions_orders()
        # self.army.print_divisions_info()

    async def attack(self):
        await self.army.attack()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.blink_research_ready()

    def retreat_condition(self):
        return self.condition_retreat.army_count_less_than(5)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    def chronoboost(self):
        # try:
        self.chronobooster.standard()
        # except Exception as ex:
        #     print(ex)

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.twilight_council()

    async def morphing(self):
        await self.morphing_.morph_gates()

