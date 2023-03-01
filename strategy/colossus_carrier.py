from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.carrier import CarrierMicro
from army.micros.colossus import ColossusMicro
from army.micros.disruptor import DisruptorMicro
from army.micros.immortal import ImmortalMicro
from army.micros.observer import ObserverMicro
from army.micros.phoenix import PhoenixMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker import StalkerMicro
from army.micros.voidray import VoidrayMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from bot.upgraders import CyberneticsUpgrader, ForgeUpgrader, TwilightUpgrader, RoboticsBayUpgrader
from army.divisions import OBSERVER_x1
from sc2.unit import UnitTypeId as unit


class ColossusCarrier(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='mid', name='ColossusCarrier', ai=ai)

        immortal_micro = ImmortalMicro(ai)
        disruptor_micro = DisruptorMicro(ai)
        voidray_micro = VoidrayMicro(ai)

        self.army.create_division('zealot', {unit.ZEALOT: 1}, [ZealotMicro(ai)], Movements(ai), lifetime=90)
        self.army.create_division('zealots', {unit.ZEALOT: 5}, [ZealotMicro(ai)], Movements(ai, 0.1), lifetime=-420)
        self.army.create_division('main_army', {unit.STALKER: 5, unit.ADEPT: 2, unit.IMMORTAL: 4, unit.COLOSSUS: 4,
                                               unit.DISRUPTOR: 3, unit.VOIDRAY: 3, unit.CARRIER: 15, unit.SENTRY: 2},
                                  [immortal_micro, disruptor_micro, voidray_micro, ColossusMicro(ai), PhoenixMicro(ai),
                                  SentryMicro(ai), StalkerMicro(ai), CarrierMicro(ai)], Movements(ai, movements_step=10,
                                                    units_ratio_before_next_step=0.85))
        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai, 0.1))

        build_queue = BuildQueues.COLOSSUS
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.robotics_bay_upgrader = RoboticsBayUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)

    def handle_workers(self):
        mineral_workers = self.worker_rush_defense.worker_rush_defense()
        self.workers_distribution.distribute_workers(minerals_to_gas_ratio=1)
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

    def build_assimilators(self):
        self.assimilator_builder.max_vespene()

    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        self.cybernetics_upgrader.air_dmg()
        self.forge_upgrader.shield()
        await self.robotics_bay_upgrader.thermal_lances()

    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army

    async def army_execute(self):
        await self.army.execute()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.total_supply_over(193)

    def retreat_condition(self):
        return self.condition_retreat.army_supply_less_than(70 if self.ai.time < 400 else 90)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return self.condition_lock_spending.thermal_lances()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.morph_Archons()
        await self.morphing_.set_wall_gates_resp_inside_base()
