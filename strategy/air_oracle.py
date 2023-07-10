from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.carrier import CarrierMicro
from army.micros.observer import ObserverMicro
from army.micros.oracle import OracleMicro
from army.micros.sentry import SentryMicro
from army.micros.tempest import TempestMicro
from army.micros.voidray import VoidrayMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from strategy.interfaces.secure_mineral_lines import SecureMineralLines
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

        oracle_micro = OracleMicro(ai)
        voidray_micro = VoidrayMicro(ai)
        carrier_micro = CarrierMicro(ai)
        tempest_micro = TempestMicro(ai)
        zealot_micro = ZealotMicro(ai)

        sentry_micro = SentryMicro(ai)
        self.army.create_division('adepts', {unit.ADEPT: 2}, [AdeptMicro(ai)], Movements(ai))

        self.army.create_division('oracle', ORACLE_x1, [oracle_micro], Movements(ai), lifetime=240)
        self.army.create_division('oracle2', ORACLE_x1, [OracleMicro(ai)], Movements(ai), lifetime=260)
        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('voidrays1', VOIDRAY_x3, [voidray_micro], Movements(ai), lifetime=-240)
        self.army.create_division('carriers1', CARRIER_x8, [carrier_micro], Movements(ai))
        self.army.create_division('tempests1', TEMPEST_x5, [tempest_micro], Movements(ai))
        self.army.create_division('tempests2', TEMPEST_x5, [tempest_micro], Movements(ai))
        self.army.create_division('zealot1', ZEALOT_x5, [zealot_micro], Movements(ai), lifetime=-340)
        self.army.create_division('zealot2', ZEALOT_x5, [zealot_micro], Movements(ai), lifetime=-340)
        self.army.create_division('sentry', {unit.SENTRY: 1}, [sentry_micro],Movements(ai, 0.2), lifetime=-420)


        build_queue = BuildQueues.AIR_ORACLE_CARRIERS
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)
        self.secure_lines = SecureMineralLines(ai)
        self.is_secure_lines_enabled = False

    async def execute_interfaces(self):
        await super().execute_interfaces()
        if self.is_secure_lines_enabled:
            await self.secure_lines.execute()
        else:
            if self.ai.enemy_units({unit.BANSHEE, unit.ORACLE}).exists:
                self.is_secure_lines_enabled = True

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
