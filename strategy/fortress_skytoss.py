from army.defense.fortress_defense import FortressDefense
from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.archon import ArchonMicro
from army.micros.carrier import CarrierMicro
# from army.micros.carrier_updated import CarrierMicroUpdated
from army.micros.carrier_mothership import CarrierMothershipMicro
from army.micros.colossus import ColossusMicro
from army.micros.disruptor import DisruptorMicro
from army.micros.high_templar import HighTemplarMicro
from army.micros.immortal import ImmortalMicro
from army.micros.observer import ObserverMicro
from army.micros.oracle_defense import OracleDefenseMicro
from army.micros.second_wall_guard_zealot import SecondWallGuardZealotMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker import StalkerMicro
from army.micros.tempest import TempestMicro
from army.micros.tempest_mothership import TempestMothershipMicro
from army.micros.voidray import VoidrayMicro
from army.micros.voidray_cannon_defense import VoidrayCannonDefenseMicro
from army.micros.wall_guard_zealot import WallGuardZealotMicro
from army.micros.warpprism import WarpPrismMicro
from army.micros.warpprism_elevator import WarpPrismElevatorMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders import PylonBuilder, CannonBuilder
from builders.battery_builder import BatteryBuilder
from builders.special_building_locations import UpperWall
from data_analysis.map_tools.positions_loader import PositionsLoader
from strategy.interfaces.mothership import Mothership
from strategy.interfaces.second_wall_builder import SecondWallBuilder
from strategy.interfaces.shield_battery_heal_buildings import ShieldBatteryHealBuildings
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader, RoboticsBayUpgrader, \
    TemplarArchiveUpgrader
from army.divisions import TEMPEST_x5, VOIDRAY_x3, OBSERVER_x1, ORACLE_x1, WARPPRISM_x1
import time


class FortressSkyToss(Strategy):
    def __init__(self, ai):
        super().__init__(type='air', name='FortressSkyToss', ai=ai, defense=FortressDefense(ai))

        # voidray_micro =
        carrier_micro = CarrierMothershipMicro(ai)
        tempest_micro = TempestMothershipMicro(ai)

        positions_loader = PositionsLoader(ai)
        locations_dict = positions_loader.load_positions_dict('second_wall_cannon')
        wall_guard_zealot_micro = SecondWallGuardZealotMicro(ai, locations_dict[unit.ZEALOT][0])

        self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 2}, [wall_guard_zealot_micro],
                                  Movements(ai, 0.1))
        self.army.create_division('adepts', {unit.ADEPT: 2}, [AdeptMicro(ai)], Movements(ai))
        self.army.create_division('stalkers', {unit.STALKER: 2}, [StalkerMicro(ai)], Movements(ai))
        self.army.create_division('immortals', {unit.IMMORTAL: 2}, [ImmortalMicro(ai)], Movements(ai))
        # self.army.create_division('voidrays1', {unit.VOIDRAY: 3}, [VoidrayMicro(ai)], Movements(ai))
        # self.army.create_division('voidrays2', {unit.VOIDRAY: 5}, [VoidrayMicro(ai)], Movements(ai))
        self.army.create_division('voidrays3',
                                  {unit.VOIDRAY: 12, unit.MOTHERSHIP: 1, unit.CARRIER: 4, unit.TEMPEST: 8, unit.OBSERVER: 1},
                                  [VoidrayCannonDefenseMicro(ai), tempest_micro, ObserverMicro(ai),
                                   carrier_micro], Movements(ai))

        # self.army.create_division('observer2', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai), lifetime=-460)
        self.army.create_division('oracle', ORACLE_x1, [OracleDefenseMicro(ai)], Movements(ai), lifetime=-360)

        build_queue = BuildQueues.FORTRESS_SKYTOSS

        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[locations_dict])
        self.battery_builder = BatteryBuilder(ai)
        self.cannon_builder = CannonBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)
        self.pylon_builder.special_locations = locations_dict[unit.PYLON]
        self.shield_battery_interface = ShieldBatteryHealBuildings(ai)
        self.wall_builder = SecondWallBuilder(ai)
        self.mother_ship_interface = Mothership(ai)

    async def execute_interfaces(self):
        await super().execute_interfaces()
        await self.shield_battery_interface.execute()
        await self.wall_builder.execute()
        await self.mother_ship_interface.execute()
        await self.battery_builder.build_batteries(when_minerals_more_than=400, amount=6)
        await self.cannon_builder.build_cannons(when_minerals_more_than=350, amount=4)


    async def handle_workers(self):
        mineral_workers = await self.worker_rush_defense.worker_rush_defense()
        self.workers_distribution.distribute_workers(1)
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
        if self.ai.time < 180:
            self.assimilator_builder.one_vespene()
        else:
            self.assimilator_builder.standard()

    # =======================================================  Upgraders
    async def do_upgrades(self):
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
        return self.condition_retreat.army_supply_less_than(80)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.is_mothership_ready()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_second_wall_gates_resp_inside_base()
