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
from army.micros.tempest import TempestMicro
from army.micros.voidray import VoidrayMicro
from army.micros.wall_guard_zealot import WallGuardZealotMicro
from army.micros.warpprism import WarpPrismMicro
from army.micros.warpprism_elevator import WarpPrismElevatorMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders import PylonBuilder
from builders.battery_builder import BatteryBuilder
from builders.special_building_locations import UpperWall
from data_analysis.map_tools.positions_loader import PositionsLoader
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


class FortressToss(Strategy):
    def __init__(self, ai):
        super().__init__(type='air', name='FortressToss', ai=ai, defense=FortressDefense(ai))

        # voidray_micro = VoidrayMicro(ai)
        carrier_micro = CarrierMicro(ai)
        tempest_micro = TempestMicro(ai)
        sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotMicro(ai)
        warpprism_micro = WarpPrismMicro(ai)
        stalker_micro = StalkerMicro(ai)
        colossus_micro = ColossusMicro(ai)
        archon_micro = ArchonMicro(ai)
        disruptor_micro = DisruptorMicro(ai)
        ht_micro = HighTemplarMicro(ai)

        positions_loader = PositionsLoader(ai)
        locations_dict = positions_loader.load_positions_dict('second_wall_cannon')
        wall_guard_zealot_micro = SecondWallGuardZealotMicro(ai, locations_dict[unit.ZEALOT][0])

        self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 2}, [wall_guard_zealot_micro],
                                  Movements(ai, 0.1))

        self.army.create_division('adepts', {unit.ADEPT: 2}, [AdeptMicro(ai)], Movements(ai))
        self.army.create_division('stalkers', {unit.STALKER: 5}, [StalkerMicro(ai)], Movements(ai), lifetime=300)
        self.high_templars_amount = 3
        main_army = {unit.ZEALOT: 3, unit.STALKER: 15, unit.SENTRY: 2, unit.IMMORTAL: 3,
                     unit.HIGHTEMPLAR: self.high_templars_amount,
                     unit.ARCHON: 6, unit.COLOSSUS: 3, unit.DISRUPTOR: 2, unit.CARRIER: 10, unit.TEMPEST: 10}
        self.army.create_division('main_army', main_army, [zealot_micro, carrier_micro, tempest_micro, sentry_micro,
            stalker_micro, immortal_micro, colossus_micro, archon_micro, ht_micro, disruptor_micro], Movements(ai),
                                                                                             lifetime=-300)

        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai), lifetime=-380)
        self.army.create_division('observer2', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai), lifetime=-460)
        self.army.create_division('oracle', ORACLE_x1, [OracleDefenseMicro(ai)], Movements(ai), lifetime=-360)
        self.army.create_division('warpprism', WARPPRISM_x1, [warpprism_micro],Movements(ai, 0.2), lifetime=-360)


        build_queue = BuildQueues.FORTRESS_TOSS
        # upper_wall = UpperWall(ai)

        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[locations_dict])
        self.battery_builder = BatteryBuilder(ai)
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

    async def execute_interfaces(self):
        await super().execute_interfaces()
        await self.shield_battery_interface.execute()
        await self.wall_builder.execute()


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
        await self.battery_builder.build_batteries(when_minerals_more_than=150, amount=6)

    async def build_pylons(self):
        await self.pylon_builder.new_standard_upper_wall()

    def build_assimilators(self):
        if self.ai.time < 240:
            self.assimilator_builder.one_vespene()
        else:
            self.assimilator_builder.standard(minerals_to_gas_ratio=1)

    # =======================================================  Upgraders
    async def do_upgrades(self):
        await self.templar_archive_upgrader.storm()
        self.cybernetics_upgrader.warpgate()
        if self.ai.structures(unit.STARGATE).exists:
            self.cybernetics_upgrader.air_dmg()
        self.forge_upgrader.standard()
        await self.robotics_bay_upgrader.thermal_lances()
        await self.twilight_upgrader.blink()
        if self.ai.time > 600:
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
        return self.condition_retreat.army_supply_less_than(40 if self.ai.time < 500 else 70)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return self.condition_lock_spending.thermal_lances() or self.condition_lock_spending.psi_storm()\
    or (await self.condition_lock_spending.forge() if self.ai.time > 600 else False)

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_second_wall_gates_resp_inside_base()
        await self.morphing_.morph_Archons(self.high_templars_amount)
