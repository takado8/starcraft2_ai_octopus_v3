from sc2 import Race

from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.carrier import CarrierMicro
from army.micros.carrier_mothership import CarrierMothershipMicro
from army.micros.immortal import ImmortalMicro
from army.micros.observer import ObserverMicro
from army.micros.oracle_defense import OracleDefenseMicro
from army.micros.second_wall_guard_zealot import SecondWallGuardZealotMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker import StalkerMicro
from army.micros.stalker_blink import StalkerBlinkMicro
from army.micros.tempest import TempestMicro
from army.micros.tempest_mothership import TempestMothershipMicro
from army.micros.voidray import VoidrayMicro
from army.micros.warpprism import WarpPrismMicro
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
from army.divisions import VOIDRAY_x3, OBSERVER_x1, ORACLE_x1, WARPPRISM_x1
import time


class SkytossTempest(Strategy):
    def __init__(self, ai):
        super().__init__(type='air', name='SkytossTempest', ai=ai)
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

        # voidray_micro = VoidrayMicro(ai)
        # carrier_micro = CarrierMothershipMicro(ai)
        tempest_micro = TempestMothershipMicro(ai)
        blink_locations_dict = positions_loader.load_positions_dict('blink_to_main')
        blink_locations = blink_locations_dict[unit.PYLON]
        stalker_micro = StalkerBlinkMicro(ai, blink_locations=blink_locations)

        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('observer2', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('stalkers', {unit.STALKER: 25, unit.SENTRY: 2}, [sentry_micro, stalker_micro],
                                  Movements(ai, units_ratio_before_next_step=0.6, movements_step=15))

        self.army.create_division('main_army', {unit.TEMPEST: 25},
                                  [tempest_micro], Movements(ai))
        self.army.create_division('warpprism', WARPPRISM_x1, [WarpPrismMicro(ai)], Movements(ai, 0.2))

        self.army.create_division('sentry', {unit.SENTRY: 1}, [sentry_micro], Movements(ai, 0.2), lifetime=-650)
        self.army.create_division('chargelots', {unit.ZEALOT: 10}, [ZealotMicro(ai)], Movements(ai, 0.1), lifetime=-600)
        self.army.create_division('chargelots_summon', {unit.ZEALOT: 20}, [ZealotMicro(ai)], Movements(ai, 0.1),
                                  lifetime=False)
        self.army.create_division('immortals', {unit.IMMORTAL:  4},
                                  [ImmortalMicro(ai)], Movements(ai))
        build_queue = BuildQueues.TWO_BASE_SKYTOSS

        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[locations_dict] if locations_dict else None)
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)
        self.mother_ship_interface = Mothership(ai)
        self.secure_lines = SecureMineralLines(ai)
        self.shield_battery_interface = ShieldBatteryHealBuildings(ai)
        self.cannon_builder = CannonBuilder(ai)
        self.interface_time_consumed = 0
        self.wall_builder = SecondWallBuilder(ai)
        self.mother_ship_interface = Mothership(ai)
        self.siege_infrastructure = SiegeInfrastructure(ai)

    async def execute_interfaces(self):
        await super().execute_interfaces()
        await self.wall_builder.execute()
        if self.ai.time > 300:
            await self.secure_lines.execute()
        await self.shield_battery_interface.execute()
        await self.cannon_builder.build_cannons(when_minerals_more_than=410, amount=2)
        await self.battery_builder.build_batteries(when_minerals_more_than=420, amount=4)
        await self.siege_infrastructure.execute()
        # if self.ai.time > 420:
        #     await self.mother_ship_interface.execute()

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
        # await self.twilight_upgrader.charge()

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
        return self.condition_retreat.army_value_n_times_the_enemy(1) and self.condition_retreat.army_supply_less_than(90)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        await self.condition_lock_spending.none()


    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_wall_gates_resp_inside_base()
