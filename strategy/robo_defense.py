from sc2 import Race

from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.carrier import CarrierMicro
from army.micros.colossus import ColossusMicro
from army.micros.disruptor import DisruptorMicro
from army.micros.immortal import ImmortalMicro
from army.micros.observer import ObserverMicro
from army.micros.phoenix import PhoenixMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker import StalkerMicro
from army.micros.voidray import VoidrayMicro
from army.micros.wall_guard_zealot import WallGuardZealotMicro
from army.micros.warpprism import WarpPrismMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from builders.special_building_locations import UpperWall
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from bot.upgraders import CyberneticsUpgrader, ForgeUpgrader, TwilightUpgrader, RoboticsBayUpgrader
from army.divisions import OBSERVER_x1
from sc2.unit import UnitTypeId as unit


class RoboDefense(Strategy):
    def __init__(self, ai):
        super().__init__(type='defense', name='RoboDefense', ai=ai)

        immortal_micro = ImmortalMicro(ai, use_division_backout_position=False)
        disruptor_micro = DisruptorMicro(ai)
        # voidray_micro = VoidrayMicro(ai)
        stalker_micro = StalkerMicro(ai, use_division_backout_position=False)
        # carrier_micro = CarrierMicro(ai, use_division_backout_position=False)
        colossus_micro = ColossusMicro(ai, use_division_backout_position=False)
        zealot_micro = WallGuardZealotMicro(ai) if self.ai.enemy_race == Race.Zerg else ZealotMicro(ai)
        self.army.create_division('zealot', {unit.ZEALOT: 1}, micros=[zealot_micro],
                                                                   movements=Movements(ai), lifetime=90)
        # self.army.create_division('zealots', {unit.ZEALOT: 7}, [ZealotMicro(ai)], Movements(ai, 0.1), lifetime=-420)
        self.army.create_division('main_army', {unit.STALKER: 20, unit.ADEPT: 10, unit.IMMORTAL: 8, unit.COLOSSUS: 4,
                                                unit.WARPPRISM: 1, unit.OBSERVER: 1, unit.DISRUPTOR: 6, unit.SENTRY: 3},
                                  [immortal_micro, disruptor_micro, colossus_micro, ObserverMicro(ai),
                                   WarpPrismMicro(ai), SentryMicro(ai), stalker_micro, AdeptMicro(ai)],
                                  Movements(ai, movements_step=25, units_ratio_before_next_step=0.65))
        # self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai, 0.1))

        build_queue = BuildQueues.ROBO_DEFENSE
        upper_wall = UpperWall(ai)
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[upper_wall.locations_dict])
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
        await self.pylon_builder.new_standard_upper_wall()

    def build_assimilators(self):
        self.assimilator_builder.standard()

    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        # self.cybernetics_upgrader.air_dmg()
        self.forge_upgrader.standard()
        await self.robotics_bay_upgrader.thermal_lances()
        await self.twilight_upgrader.standard()

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
        return self.condition_retreat.army_supply_less_than(40 if self.ai.time < 400 else 70)

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
        # await self.morphing_.morph_Archons()
        await self.morphing_.set_wall_gates_resp_inside_base()
