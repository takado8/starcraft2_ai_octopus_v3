from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from army.micros.micro import AirMicro, ZealotMicro
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader
from army.divisions import ZEALOT_x5, ORACLE_x1, CARRIER_x8, TEMPEST_x5, VOIDRAY_x3, OBSERVER_x1


class AirOracle(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='air', name='AirOracle', ai=ai)

        air_micro = AirMicro(ai)
        zealot_micro = ZealotMicro(ai)
        # sentry_micro = SentryMicro(ai)
        self.army.create_division('oracle', ORACLE_x1, [air_micro], Movements(ai), lifetime=240)
        self.army.create_division('observer', OBSERVER_x1, [air_micro], Movements(ai))
        self.army.create_division('voidrays1', VOIDRAY_x3, [air_micro], Movements(ai))
        self.army.create_division('carriers1', CARRIER_x8, [air_micro], Movements(ai))
        self.army.create_division('tempests1', TEMPEST_x5, [air_micro], Movements(ai))
        self.army.create_division('tempests2', TEMPEST_x5, [air_micro], Movements(ai))
        self.army.create_division('zealot1', ZEALOT_x5, [zealot_micro], Movements(ai))
        self.army.create_division('zealot2', ZEALOT_x5, [zealot_micro], Movements(ai))

        build_queue = BuildQueues.AIR_ORACLE_CARRIERS
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)

    def handle_workers(self):
        self.workers_distribution.distribute_workers(minerals_to_gas_ratio=2)
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
        return self.condition_attack.air_dmg_lvl2_full_supply()

    def retreat_condition(self):
        return self.condition_retreat.supply_less_than(80)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        # try:
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()
        # except Exception as ex:
        #     print(ex)

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.is_oracle_ready()

    async def morphing(self):
        await self.morphing_.morph_gates()
