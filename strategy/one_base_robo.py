from army.movements import Movements
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from army.micros.micro import StalkerMicro, ImmortalMicro, SentryMicro, ZealotMicro, WarpPrismMicro
from bot.upgraders import CyberneticsUpgrader, ForgeUpgrader, TwilightUpgrader
from army.divisions import STALKER_x10, IMMORTAL_x2, IMMORTAL_x5, SENTRY_x3, OBSERVER_x1,\
    STALKER_x5, ZEALOT_x10, WARPPRISM_x1




class OneBaseRobo(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='rush', name='OneBaseRobo', ai=ai)

        stalker_micro = StalkerMicro(ai)
        sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotMicro(ai)
        warpprism_micro = WarpPrismMicro(ai)
        # self.sentry_micro = SentryMicro(ai)
        self.army.create_division('stalkers1', STALKER_x5, [stalker_micro], Movements(ai, 0.6))
        self.army.create_division('immortals1', IMMORTAL_x2, [immortal_micro], Movements(ai, 0.2))
        self.army.create_division('immortals2', IMMORTAL_x2, [immortal_micro], Movements(ai, 0.2))
        self.army.create_division('stalkers2', STALKER_x5, [stalker_micro], Movements(ai, 0.5))
        self.army.create_division('stalkers3', STALKER_x5, [stalker_micro], Movements(ai, 0.5))
        self.army.create_division('stalkers4', STALKER_x5, [stalker_micro], Movements(ai, 0.5))
        self.army.create_division('immortals3', IMMORTAL_x5, [immortal_micro], Movements(ai, 0.2))
        self.army.create_division('zealots', ZEALOT_x10, [zealot_micro], Movements(ai, 0.33))
        self.army.create_division('zealots2', ZEALOT_x10, [zealot_micro], Movements(ai, 0.33))
        self.army.create_division('sentry', SENTRY_x3, [sentry_micro], Movements(ai, 0.2), lifetime=-300)
        self.army.create_division('observer', OBSERVER_x1, [], Movements(ai, 0.2))
        self.army.create_division('warpprism', WARPPRISM_x1, [warpprism_micro], Movements(ai, 0.2), lifetime=-400)

        build_queue = BuildQueues.ONE_BASE_ROBO
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)

    def distribute_workers(self):
        self.workers_distribution.distribute_workers()

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()

    async def build_pylons(self):
        await self.pylon_builder.new_standard()

    def build_assimilators(self):
        self.assimilator_builder.standard(minerals_to_gas_ratio=1.5)

    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        self.forge_upgrader.standard()
        await self.twilight_upgrader.standard()

    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army

    async def army_execute(self):
        await self.army.execute()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.supply_over(190)

    def retreat_condition(self):
        return self.condition_retreat.supply_less_than(15 if self.ai.time < 400 else 50)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    def chronoboost(self):
        # try:
        self.chronobooster.standard()
        # except Exception as ex:
        #     print(ex)

    async def lock_spending_condition(self):
        await self.condition_lock_spending.forge()

    async def morphing(self):
        await self.morphing_.morph_gates()
