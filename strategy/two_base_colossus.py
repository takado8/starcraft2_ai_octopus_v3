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
from strategy.interfaces.emergency_expansion import EmergencyExpansion
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
from army.divisions import TEMPEST_x5, VOIDRAY_x3, OBSERVER_x1, ORACLE_x1, WARPPRISM_x1, CARRIER_x8
from sc2.ids.upgrade_id import UpgradeId as upgrade


class TwoBaseColossusUpdated(Strategy):
    def __init__(self, ai):
        super().__init__(type='mid', name='TwoBaseColossusUpdated', ai=ai)
        self.scouting.scouting_active_after_s = 300

        positions_loader = PositionsLoader(ai)
        if self.ai.enemy_race == Race.Zerg:
            locations_dict = positions_loader.load_positions_dict('second_wall_cannon')
            locations_dict[unit.GATEWAY].append(locations_dict[unit.FORGE][0])
            del locations_dict[unit.FORGE]
            sentry_micro = SentryMicro(ai, locations_dict[unit.ZEALOT][0])
            wall_guard_zealot_micro = SecondWallGuardZealotMicro(ai, locations_dict[unit.ZEALOT][0])
            self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 2}, [wall_guard_zealot_micro],
                                      Movements(ai, 0.1))
            self.pylon_builder.special_locations = locations_dict[unit.PYLON]
        else:
            locations_dict = None
            sentry_micro = SentryMicro(ai)

        # blink_locations_dict = positions_loader.load_positions_dict('blink_to_main')
        # blink_locations = blink_locations_dict[unit.PYLON]
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotMicro(ai)
        warpprism_micro = WarpPrismMicro(ai)
        stalker_micro = StalkerBlinkMicro(ai)
        colossus_micro = ColossusMicro(ai)
        # carrier_micro = CarrierMicro(ai)
        # tempest_micro = TempestMicro(ai)
        # archon_micro = ArchonMicro(ai)
        disruptor_micro = DisruptorMicro(ai)
        # ht_micro = HighTemplarMicro(ai)

        self.army.create_division('adepts', {unit.ADEPT: 2 if self.ai.enemy_race == Race.Protoss else 1},
                                  [AdeptMicro(ai)], Movements(ai), lifetime=300)

        #
        # self.army.create_division('stalkers', {unit.STALKER: 20, unit.SENTRY: 1}, [stalker_micro, sentry_micro],
        #                           Movements(ai, units_ratio_before_next_step=0.6, movements_step=10))

        self.army.create_division('main', {unit.STALKER: 30,  unit.COLOSSUS: 3, unit.IMMORTAL: 2, unit.DISRUPTOR: 5,
                                           unit.SENTRY: 2},
                                  [stalker_micro, immortal_micro, sentry_micro, colossus_micro, disruptor_micro],
                                  Movements(ai, 0.8))
        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('warpprism', WARPPRISM_x1, [warpprism_micro], Movements(ai, 0.2))
        #
        # self.army.create_division('carriers1', CARRIER_x8, [carrier_micro], Movements(ai))
        # self.army.create_division('tempests1', TEMPEST_x5, [tempest_micro], Movements(ai))

        # self.army.create_division('observer2', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('sentry', {unit.SENTRY: 2}, [sentry_micro],Movements(ai, 0.2), lifetime=-600)
        # self.army.create_division('chargelots', {unit.ZEALOT: 10}, [zealot_micro], Movements(ai, 0.1), lifetime=-600)
        self.army.create_division('chargelots_summon', {unit.ZEALOT: 20}, [zealot_micro], Movements(ai, 0.1), lifetime=False)

        build_queue = BuildQueues.TWO_BASE_COLOSSUS

        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[locations_dict] if locations_dict else None)
        self.battery_builder = BatteryBuilder(ai)
        self.cannon_builder = CannonBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.robotics_bay_upgrader = RoboticsBayUpgrader(ai)
        self.templar_archive_upgrader = TemplarArchiveUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)
        self.shield_battery_interface = ShieldBatteryHealBuildings(ai)
        self.wall_builder = SecondWallBuilder(ai)
        self.mother_ship_interface = Mothership(ai)
        self.secure_lines = SecureMineralLines(ai)

    async def execute_interfaces(self):
        await super().execute_interfaces()
        if self.ai.enemy_race == Race.Terran and self.ai.time > 380:
            await self.secure_lines.execute()
        elif self.ai.enemy_race == Race.Zerg:
            await self.wall_builder.execute()
        await self.shield_battery_interface.execute()

        if self.ai.iteration % 10 == 0:
            await self.battery_builder.build_batteries(when_minerals_more_than=450, amount=4)
            await self.cannon_builder.build_cannons(when_minerals_more_than=460, amount=2)

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
        if self.ai.enemy_race == Race.Zerg:
            await self.pylon_builder.new_standard_upper_wall()
        else:
            await self.pylon_builder.new_standard()

    def build_assimilators(self):
        # if self.ai.time < 90:
        #     self.assimilator_builder.one_vespene()
        # else:
        self.assimilator_builder.standard(minerals_to_gas_ratio=2)

    # =======================================================  Upgraders
    async def do_upgrades(self):
        if self.ai.army(unit.COLOSSUS).exists or self.ai.already_pending(unit.COLOSSUS):
            await self.robotics_bay_upgrader.thermal_lances()
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
        return (self.condition_attack.army_supply_over(90) and not self.ai.after_first_attack) or\
               (self.condition_attack.army_value_n_times_the_enemy(2.5) and self.ai.after_first_attack) or\
               self.condition_attack.total_supply_over(195)

    def retreat_condition(self):
        return self.condition_retreat.army_value_n_times_the_enemy(1.5)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack() and self.condition_attack.army_value_n_times_the_enemy(3)

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.forge() or \
               await self.condition_lock_spending.twilight_council_blink() or\
                self.condition_lock_spending.thermal_lances()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_second_wall_gates_resp_inside_base()
