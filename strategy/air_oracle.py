from army.movements import Movements
from bot.morphing import Morphing
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from army.micros.micro import AirMicro, ZealotMicro, SentryMicro
from bot.upgraders import ForgeUpgrader, CyberneticsUpgrader, TwilightUpgrader
# from bot.trainers import WarpgateTrainer, GateTrainer, RoboticsTrainer, StargateTrainer
# from bot.units_training_dicts import UnitsTrainingDicts
from army.divisions import ZEALOT_x5, ORACLE_x1, CARRIER_x8, TEMPEST_x5, VOIDRAY_x5, SENTRY_x3



class AirOracle(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='air', name='AirOracle', ai=ai)
        self.morphing_ = Morphing(ai)
        # stalker_micro = StalkerMicro(ai)
        air_micro = AirMicro(ai)
        zealot_micro = ZealotMicro(ai)
        sentry_micro = SentryMicro(ai)
        self.army.create_division('oracle', ORACLE_x1, [air_micro], Movements(ai))
        # self.army.create_division('stalkers1', STALKER_x5, [stalker_micro], Movements(ai))
        # self.army.create_division('stalkers2', STALKER_x5, [stalker_micro], Movements(ai))
        self.army.create_division('voidrays1', VOIDRAY_x5, [air_micro], Movements(ai))
        # self.army.create_division('voidrays2', VOIDRAY_x5, [air_micro], Movements(ai))
        self.army.create_division('carriers1', CARRIER_x8, [air_micro], Movements(ai))
        self.army.create_division('carriers2', CARRIER_x8, [air_micro], Movements(ai))
        self.army.create_division('tempests1', TEMPEST_x5, [air_micro], Movements(ai))
        self.army.create_division('tempests2', TEMPEST_x5, [air_micro], Movements(ai))
        self.army.create_division('tempests3', TEMPEST_x5, [air_micro], Movements(ai))
        self.army.create_division('zealot1', ZEALOT_x5, [zealot_micro], Movements(ai))
        self.army.create_division('zealot2', ZEALOT_x5, [zealot_micro], Movements(ai))
        # self.army.create_division('zealot2', ZEALOT_x5, [zealot_micro], Movements(ai))
        self.army.create_division('sentry', SENTRY_x3, [sentry_micro], Movements(ai))
        # self.army.create_division('zealot1', ZEALOT_x10, [zealot_micro], Movements(ai))
        # self.army.create_division('zealot2', ZEALOT_x10, [zealot_micro], Movements(ai))

        build_queue = BuildQueues.AIR_ORACLE_CARRIERS
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))

        self.forge_upgrader = ForgeUpgrader(ai)
        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)



    def distribute_workers(self):
        self.workers_distribution.distribute_workers(resources_ratio=1.2)

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()

    async def build_pylons(self):
        await self.pylon_builder.new_standard()

    def build_assimilators(self):
        self.assimilator_builder.max_vespene()


    # =======================================================  Upgraders
    def forge_upgrade(self):
        self.forge_upgrader.none()

    def cybernetics_upgrade(self):
        self.cybernetics_upgrader.air_dmg()

    async def twilight_upgrade(self):
        await self.twilight_upgrader.charge()

    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army

    async def army_execute(self):
        await self.army.execute()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.air_dmg_lvl2_full_supply()

    def retreat_condition(self):
        return self.condition_retreat.supply_less_than(160)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    def chronoboost(self):
        # try:
        self.chronobooster.standard()
        # except Exception as ex:
        #     print(ex)

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.is_oracle_ready()

    async def morphing(self):
        await self.morphing_.morph_gates()

