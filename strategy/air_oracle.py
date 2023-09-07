from sc2 import Race

from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.carrier import CarrierMicro
from army.micros.carrier_mothership import CarrierMothershipMicro
from army.micros.observer import ObserverMicro
from army.micros.oracle import OracleMicro
from army.micros.oracle_defense import OracleDefenseMicro
from army.micros.second_wall_guard_zealot import SecondWallGuardZealotMicro
from army.micros.sentry import SentryMicro
from army.micros.tempest import TempestMicro
from army.micros.tempest_mothership import TempestMothershipMicro
from army.micros.voidray import VoidrayMicro
from army.micros.voidray_cannon_defense import VoidrayCannonDefenseMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from data_analysis.map_tools.positions_loader import PositionsLoader
from strategy.interfaces.detct_bunker_contain import DetectBunkerContain
from strategy.interfaces.mothership import Mothership
from strategy.interfaces.secure_mineral_lines import SecureMineralLines
from strategy.interfaces.siege_infrastructure import SiegeInfrastructure
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader
from army.divisions import ZEALOT_x5, ORACLE_x1, CARRIER_x8, TEMPEST_x5, VOIDRAY_x3, OBSERVER_x1


class AirOracle(Strategy):
    def __init__(self, ai):
        super().__init__(type='air', name='AirOracle', ai=ai)
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

        oracle_micro = OracleMicro(ai)

        self.army.create_division('adepts', {unit.ADEPT: 1}, [AdeptMicro(ai)], Movements(ai))
        self.army.create_division('stalkers', {unit.STALKER: 2}, [AdeptMicro(ai)], Movements(ai))

        self.army.create_division('oracle', ORACLE_x1, [oracle_micro], Movements(ai), lifetime=280)
        self.army.create_division('oracle2', ORACLE_x1, [OracleDefenseMicro(ai)], Movements(ai))
        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        # self.army.create_division('voidrays1', VOIDRAY_x3, [voidray_micro], Movements(ai), lifetime=-240)

        self.army.create_division('main',
                                      {unit.CARRIER: 6, unit.TEMPEST: 15, unit.OBSERVER: 1},
                                      [TempestMothershipMicro(ai), ObserverMicro(ai),
                                       CarrierMothershipMicro(ai)], Movements(ai))

        self.army.create_division('sentry', {unit.SENTRY: 1}, [sentry_micro],Movements(ai, 0.2), lifetime=-420)


        build_queue = BuildQueues.AIR_ORACLE_CARRIERS
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[locations_dict] if locations_dict else None)

        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)
        self.secure_lines = SecureMineralLines(ai)
        self.is_secure_lines_enabled = False
        self.mother_ship_interface = Mothership(ai)
        self.detect_bunker_contain = DetectBunkerContain(ai)
        self.siege_infrastructure = SiegeInfrastructure(ai)

    async def execute_interfaces(self):
        await super().execute_interfaces()
        if self.is_secure_lines_enabled:
            await self.secure_lines.execute()
        else:
            if self.ai.enemy_units({unit.BANSHEE, unit.ORACLE}).exists:
                self.is_secure_lines_enabled = True
        if self.ai.enemy_race == Race.Terran:
            await self.detect_bunker_contain.execute()
        await self.siege_infrastructure.execute()

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
        await self.battery_builder.build_batteries()

    async def build_pylons(self):
        if self.ai.enemy_race == Race.Zerg:
            await self.pylon_builder.new_standard_upper_wall()
        else:
            await self.pylon_builder.new_standard()

    def build_assimilators(self):
        self.assimilator_builder.max_vespene()

    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.air_dmg()
        self.forge_upgrader.shield()
        await self.twilight_upgrader.charge()

    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army

    async def army_execute(self):
        await self.army.execute()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.air_dmg_lvl2_full_supply() or \
               self.condition_attack.army_value_n_times_the_enemy(2)

    def retreat_condition(self):
        return self.condition_retreat.army_value_n_times_the_enemy(1)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
            return await self.condition_lock_spending.is_oracle_ready()

    async def morphing(self):
        await self.morphing_.morph_gates()
