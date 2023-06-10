from sc2 import Race

from army.defense.fortress_defense import FortressDefense
from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.archon import ArchonMicro
from army.micros.carrier import CarrierMicro
# from army.micros.carrier_updated import CarrierMicroUpdated
from army.micros.colossus import ColossusMicro
from army.micros.disruptor import DisruptorMicro
from army.micros.high_templar import HighTemplarMicro
from army.micros.immortal import ImmortalMicro
from army.micros.observer import ObserverMicro
from army.micros.oracle_defense import OracleDefenseMicro
from army.micros.second_wall_guard_zealot import SecondWallGuardZealotMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker import StalkerMicro
from army.micros.stalker_blink import StalkerBlinkMicro
from army.micros.tempest import TempestMicro
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
from strategy.interfaces.secure_mineral_lines import SecureMineralLines
from strategy.interfaces.shield_battery_heal_buildings import ShieldBatteryHealBuildings
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader, RoboticsBayUpgrader, \
    TemplarArchiveUpgrader
from army.divisions import TEMPEST_x5, VOIDRAY_x3, OBSERVER_x1, ORACLE_x1, WARPPRISM_x1
from sc2.ids.upgrade_id import UpgradeId as upgrade


class Blinkers(Strategy):
    def __init__(self, ai):
        super().__init__(type='mid', name='Blinkers', ai=ai, defense=FortressDefense(ai))

        # voidray_micro = VoidrayMicro(ai)
        # carrier_micro = CarrierMicro(ai)
        # tempest_micro = TempestMicro(ai)
        sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotMicro(ai)
        warpprism_micro = WarpPrismMicro(ai)
        stalker_micro = StalkerBlinkMicro(ai)
        colossus_micro = ColossusMicro(ai)
        # archon_micro = ArchonMicro(ai)
        # disruptor_micro = DisruptorMicro(ai)
        # ht_micro = HighTemplarMicro(ai)

        positions_loader = PositionsLoader(ai)
        locations_dict = positions_loader.load_positions_dict('second_wall_cannon')
        locations_dict[unit.GATEWAY].append(locations_dict[unit.FORGE][0])
        del locations_dict[unit.FORGE]
        wall_guard_zealot_micro = SecondWallGuardZealotMicro(ai, locations_dict[unit.ZEALOT][0])

        self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 2 if self.ai.enemy_race == Race.Zerg else 1}, [wall_guard_zealot_micro],
                                  Movements(ai, 0.1))
        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))

        self.army.create_division('adepts', {unit.ADEPT: 1}, [AdeptMicro(ai)], Movements(ai), lifetime=300)
        self.army.create_division('main', {unit.STALKER: 30, unit.IMMORTAL: 2,
                                           unit.SENTRY: 1, unit.COLOSSUS: 3, unit.DISRUPTOR: 4},
                                  [stalker_micro, immortal_micro, sentry_micro, colossus_micro],
                                  Movements(ai))

        self.army.create_division('observer2', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('warpprism', WARPPRISM_x1, [warpprism_micro],Movements(ai, 0.2), lifetime=-360)
        self.army.create_division('sentry', {unit.SENTRY: 2}, [sentry_micro],Movements(ai, 0.2), lifetime=-480)
        self.army.create_division('chargelots', {unit.ZEALOT: 20}, [zealot_micro], Movements(ai, 0.1), lifetime=False)


        build_queue = BuildQueues.BLINKERS
        # upper_wall = UpperWall(ai)

        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[locations_dict])
        self.battery_builder = BatteryBuilder(ai)
        self.cannon_builder = CannonBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.robotics_bay_upgrader = RoboticsBayUpgrader(ai)
        self.templar_archive_upgrader = TemplarArchiveUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)
        self.pylon_builder.special_locations = locations_dict[unit.PYLON]
        self.shield_battery_interface = ShieldBatteryHealBuildings(ai)
        self.wall_builder = SecondWallBuilder(ai)
        self.mother_ship_interface = Mothership(ai)
        self.secure_lines = SecureMineralLines(ai)

    async def execute_interfaces(self):
        await super().execute_interfaces()
        if self.ai.enemy_race == Race.Terran:
            await self.secure_lines.execute()
        await self.shield_battery_interface.execute()
        await self.wall_builder.execute()

        # await self.mother_ship_interface.execute()
        # if self.ai.iteration % 10 == 0:
        #     # await self.battery_builder.build_batteries(when_minerals_more_than=170, amount=2)
        #     await self.battery_builder.build_batteries(when_minerals_more_than=250, amount=5)
        #     # await self.cannon_builder.build_cannons(when_minerals_more_than=150, amount=2)
        #     await self.cannon_builder.build_cannons(when_minerals_more_than=270, amount=2)

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
        # if self.ai.time < 90:
        #     self.assimilator_builder.one_vespene()
        # else:
        self.assimilator_builder.standard(minerals_to_gas_ratio=2)

    # =======================================================  Upgraders
    async def do_upgrades(self):
        if self.ai.army(unit.ADEPT).exists or self.ai.already_pending(unit.ADEPT):
            self.cybernetics_upgrader.warpgate()
        self.forge_upgrader.standard()
        await self.twilight_upgrader.blink()
        if upgrade.BLINKTECH in self.ai.state.upgrades:
            await self.twilight_upgrader.charge()

    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army

    async def army_execute(self):
        await self.army.execute()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.blink_research_ready() or self.condition_attack.army_value_n_times_the_enemy(1.6)

    def retreat_condition(self):
        return self.condition_retreat.army_value_n_times_the_enemy(0.5)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.forge() or \
               await self.condition_lock_spending.twilight_council_blink()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_second_wall_gates_resp_inside_base()
