from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.carrier import CarrierMicro
from army.micros.carrier_mothership import CarrierMothershipMicro
from army.micros.observer import ObserverMicro
from army.micros.oracle_defense import OracleDefenseMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker import StalkerMicro
from army.micros.tempest import TempestMicro
from army.micros.voidray import VoidrayMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders import CannonBuilder
from builders.battery_builder import BatteryBuilder
from builders.special_building_locations import UpperWall
from strategy.interfaces.mothership import Mothership
from strategy.interfaces.secure_mineral_lines import SecureMineralLines
from strategy.interfaces.shield_battery_heal_buildings import ShieldBatteryHealBuildings
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader
from army.divisions import VOIDRAY_x3, OBSERVER_x1, ORACLE_x1
import time


class SkytossCarriers(Strategy):
    def __init__(self, ai):
        super().__init__(type='air', name='SkytossCarriers', ai=ai)

        voidray_micro = VoidrayMicro(ai)
        carrier_micro = CarrierMothershipMicro(ai)
        # tempest_micro = TempestMicro(ai)
        # zealot_micro = ZealotMicro(ai)
        sentry_micro = SentryMicro(ai)


        self.army.create_division('adepts', {unit.ADEPT: 1}, [AdeptMicro(ai)], Movements(ai))
        self.army.create_division('stalker', {unit.STALKER: 1}, [StalkerMicro(ai)], Movements(ai))
        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('observer2', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('voidrays1', {unit.VOIDRAY:1}, [voidray_micro], Movements(ai))
        self.army.create_division('oracle', ORACLE_x1, [OracleDefenseMicro(ai)], Movements(ai))

        self.army.create_division('carriers1', {unit.CARRIER: 20, unit.MOTHERSHIP: 1}, [carrier_micro],
                                  Movements(ai))
        # self.army.create_division('tempests1', TEMPEST_x5, [tempest_micro], Movements(ai))
        # self.army.create_division('tempests2', TEMPEST_x5, [tempest_micro], Movements(ai))
        # self.army.create_division('zealot1', ZEALOT_x5, [zealot_micro], Movements(ai), lifetime=-640)
        # self.army.create_division('zealot2', ZEALOT_x5, [zealot_micro], Movements(ai), lifetime=-40)
        self.army.create_division('sentry', {unit.SENTRY: 2}, [sentry_micro], Movements(ai, 0.2), lifetime=-600)

        build_queue = BuildQueues.SKYTOSS
        upper_wall = UpperWall(ai)
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[upper_wall.locations_dict])
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

    async def execute_interfaces(self):
        await super().execute_interfaces()
        await self.secure_lines.execute()
        if self.ai.time > 500:
            await self.mother_ship_interface.execute()
        await self.shield_battery_interface.execute()
        if self.interface_time_consumed > 220 and self.ai.iteration % 30 != 0:
            return

        start = time.time()
        await self.cannon_builder.build_cannons(when_minerals_more_than=410, amount=2)
        await self.battery_builder.build_batteries(when_minerals_more_than=420,
                                                   amount=3 if self.interface_time_consumed > 500 else 5)
        end = time.time()
        self.interface_time_consumed += end - start

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
        return self.condition_retreat.army_value_n_times_the_enemy(1)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        if self.ai.time > 1200:
            return await self.condition_lock_spending.is_mothership_ready()
        else:
            return False

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_wall_gates_resp_inside_base()
