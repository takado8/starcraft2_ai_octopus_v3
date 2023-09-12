from sc2 import Race

from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.carrier import CarrierMicro
from army.micros.carrier_mothership import CarrierMothershipMicro
from army.micros.observer import ObserverMicro
from army.micros.oracle_defense import OracleDefenseMicro
from army.micros.phoenix import PhoenixMicro
from army.micros.second_wall_guard_zealot import SecondWallGuardZealotMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker import StalkerMicro
from army.micros.stalker_blink import StalkerBlinkMicro
from army.micros.tempest import TempestMicro
from army.micros.tempest_mothership import TempestMothershipMicro
from army.micros.voidray import VoidrayMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders import CannonBuilder
from builders.battery_builder import BatteryBuilder
from builders.special_building_locations import UpperWall
from data_analysis.map_tools.positions_loader import PositionsLoader
from strategy.interfaces.mothership import Mothership
from strategy.interfaces.second_wall_builder import SecondWallBuilder
from strategy.interfaces.secure_mineral_lines import SecureMineralLines
from strategy.interfaces.shield_battery_heal_buildings import ShieldBatteryHealBuildings
from strategy.interfaces.siege_infrastructure import SiegeInfrastructure
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader
from army.divisions import VOIDRAY_x3, OBSERVER_x1, ORACLE_x1
import time


class PhoenixStalker(Strategy):
    def __init__(self, ai):
        super().__init__(type='air', name='PhoenixStalker', ai=ai)
        positions_loader = PositionsLoader(ai)

        locations_dict = positions_loader.load_positions_dict('second_wall_cannon')
        locations_dict[unit.GATEWAY].append(locations_dict[unit.FORGE][0])
        del locations_dict[unit.FORGE]
        sentry_micro = SentryMicro(ai, locations_dict[unit.ZEALOT][0])
        wall_guard_zealot_micro = SecondWallGuardZealotMicro(ai, locations_dict[unit.ZEALOT][0])
        self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 2}, [wall_guard_zealot_micro],
                                  Movements(ai, 0.1))
        self.pylon_builder.special_locations = locations_dict[unit.PYLON]
        blink_locations_dict = positions_loader.load_positions_dict('blink_to_main')
        blink_locations = blink_locations_dict[unit.PYLON]
        phoenix_micro = PhoenixMicro(ai)
        carrier_micro = CarrierMothershipMicro(ai)
        tempest_micro = TempestMothershipMicro(ai)
        stalker_micro = StalkerBlinkMicro(ai)
        zealot_micro = ZealotMicro(ai)

        self.army.create_division('adepts', {unit.ADEPT: 1}, [AdeptMicro(ai)], Movements(ai), lifetime=300)
        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('observer2', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('phoienix1', {unit.PHOENIX: 10}, [phoenix_micro], Movements(ai))
        self.army.create_division('phoienix2', {unit.PHOENIX: 10}, [phoenix_micro], Movements(ai))
        self.army.create_division('stalkers1', {unit.STALKER: 10, unit.ZEALOT: 7}, [stalker_micro, zealot_micro], Movements(ai))
        self.army.create_division('stalkers2', {unit.STALKER: 10, unit.ZEALOT: 7}, [stalker_micro, zealot_micro], Movements(ai))
        self.army.create_division('main', {unit.CARRIER: 20, unit.TEMPEST: 5},
                                  [stalker_micro, carrier_micro, tempest_micro,phoenix_micro], Movements(ai))
        self.army.create_division('oracle', ORACLE_x1, [OracleDefenseMicro(ai)], Movements(ai))

        self.army.create_division('sentry', {unit.SENTRY: 1}, [sentry_micro], Movements(ai, 0.2), lifetime=-650)

        build_queue = BuildQueues.PHOENIX_STALKER

        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[locations_dict])
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)
        self.secure_lines = SecureMineralLines(ai)
        self.shield_battery_interface = ShieldBatteryHealBuildings(ai)
        self.cannon_builder = CannonBuilder(ai)
        self.interface_time_consumed = 0
        self.wall_builder = SecondWallBuilder(ai)
        self.siege_infrastructure = SiegeInfrastructure(ai)

    async def execute_interfaces(self):
        await super().execute_interfaces()
        # await self.siege_infrastructure.execute()
        await self.wall_builder.execute()
        if self.ai.time > 360:
            await self.secure_lines.execute()
        await self.shield_battery_interface.execute()
        await self.cannon_builder.build_cannons(when_minerals_more_than=410, amount=2)
        await self.battery_builder.build_batteries(when_minerals_more_than=420, amount=4)

    async def handle_workers(self):
        mineral_workers = await self.worker_rush_defense.worker_rush_defense()
        self.workers_distribution.distribute_workers()
        if mineral_workers:
            self.speed_mining.execute(mineral_workers)
        else:
            self.speed_mining.execute(self.workers_distribution.get_mineral_workers_tags())

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()

    async def build_pylons(self):
        await self.pylon_builder.new_standard_upper_wall()

    def build_assimilators(self):
        self.assimilator_builder.max_vespene()

    # =======================================================  Upgraders
    async def do_upgrades(self):
        await self.twilight_upgrader.blink()

        self.cybernetics_upgrader.warpgate()
        self.cybernetics_upgrader.air_dmg()
        self.forge_upgrader.shield()

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
        return self.condition_retreat.army_value_n_times_the_enemy(1) and self.condition_retreat.army_supply_less_than(90)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        await self.condition_lock_spending.twilight_council_blink()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_wall_gates_resp_inside_base()
