from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.archon import ArchonMicro
from army.micros.immortal import ImmortalMicro
from army.micros.observer import ObserverMicro
from army.micros.sentry import SentryMicro
from army.micros.warpprism import WarpPrismMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from army.micros.stalker import StalkerMicro
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader
from sc2.unit import UnitTypeId as unit
from army.divisions import STALKER_x10, ADEPT_x5


class AdeptProxy(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='rush', name='AdeptProxy', ai=ai)

        adept_micro = AdeptMicro(ai)
        stalker_micro = StalkerMicro(ai)
        self.army.create_division('adepts1', ADEPT_x5, [adept_micro], Movements(ai, 0.1))
        self.army.create_division('adepts2', ADEPT_x5, [adept_micro], Movements(ai, 0.1))
        self.army.create_division('adepts3', ADEPT_x5, [adept_micro], Movements(ai, 0.1), lifetime=300)
        # self.army.create_division('adepts4', ADEPT_x5, [adept_micro], Movements(ai, 0.1))
        # self.army.create_division('adepts5', ADEPT_x5, [adept_micro], Movements(ai, 0.1))
        self.army.create_division('stalkers6', STALKER_x10, [stalker_micro], Movements(ai, 0.1), lifetime=-300)
        # self.army.create_division('stalkers7', STALKER_x10, [stalker_micro], Movements(ai, 0.1), lifetime=-360)
        main_army = {unit.IMMORTAL: 4, unit.ARCHON: 6, unit.SENTRY: 3, unit.OBSERVER: 1, unit.WARPPRISM: 1}
        self.army.create_division('main_army', main_army, [stalker_micro, ArchonMicro(ai), SentryMicro(ai),
                ImmortalMicro(ai), ObserverMicro(ai), WarpPrismMicro(ai)], Movements(ai, 0.7), lifetime=-380)

        build_queue = BuildQueues.ADEPT_RUSH
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)
        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)

    async def handle_workers(self):
        mineral_workers = await self.worker_rush_defense.worker_rush_defense()
        self.workers_distribution.distribute_workers(minerals_to_gas_ratio=3)
        if mineral_workers:
            self.speed_mining.execute(mineral_workers)
        else:
            self.speed_mining.execute(self.workers_distribution.get_mineral_workers_tags())

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()
        await self.battery_builder.build_batteries()

    async def build_pylons(self):
        await self.pylon_builder.new_standard()
        await self.pylon_builder.proxy()

    def build_assimilators(self):
        self.assimilator_builder.standard(minerals_to_gas_ratio=3)

    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        self.forge_upgrader.standard()
        await self.twilight_upgrader.glaives()
        await self.twilight_upgrader.blink()

    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army

    async def army_execute(self):
        await self.army.execute()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.adepts_more_than(4) or self.condition_attack.total_supply_over(195)

    def retreat_condition(self):
        return self.condition_retreat.army_count_less_than(4)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        await self.chronobooster.stalker_proxy()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.twilight_council_glaives() or\
        await self.condition_lock_spending.twilight_council_blink() or \
        await self.condition_lock_spending.forge()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.morph_Archons()
