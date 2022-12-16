from army.movements import Movements
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from army.micros.micro import StalkerMicro
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader
from army.divisions import STALKER_x10



class Blinkers(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='rush', name='StalkerProxy', ai=ai)

        stalker_micro = StalkerMicro(ai)
        # self.sentry_micro = SentryMicro(ai)
        self.army.create_division('stalkers1', STALKER_x10, [stalker_micro], Movements(ai, 0.6))
        self.army.create_division('stalkers2', STALKER_x10, [stalker_micro], Movements(ai, 0.5))
        self.army.create_division('stalkers3', STALKER_x10, [stalker_micro], Movements(ai, 0.5))
        self.army.create_division('stalkers4', STALKER_x10, [stalker_micro], Movements(ai, 0.2))
        self.army.create_division('stalkers5', STALKER_x10, [stalker_micro], Movements(ai, 0.2))

        build_queue = BuildQueues.STALKER_BLINKERS
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)

    def handle_workers(self):
        self.workers_distribution.handle_workers()

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()

    async def build_pylons(self):
        await self.pylon_builder.new_standard()
        # await self.pylon_builder.proxy()

    def build_assimilators(self):
        self.assimilator_builder.standard(minerals_to_gas_ratio=1)

    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        await self.twilight_upgrader.blink()

    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army

    async def army_execute(self):
        await self.army.execute()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.blink_research_ready()

    def retreat_condition(self):
        return self.condition_retreat.army_count_less_than(5)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    def nexus_abilities(self):
        # try:
        self.chronobooster.standard()
        # except Exception as ex:
        #     print(ex)

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.twilight_council_blink()

    async def morphing(self):
        await self.morphing_.morph_gates()
