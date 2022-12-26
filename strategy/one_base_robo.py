from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from army.micros.micro import StalkerMicro, ImmortalMicro, SentryMicro, ZealotMicro, WarpPrismMicro, \
    ColossusMicro, AirMicro
from bot.upgraders import CyberneticsUpgrader, ForgeUpgrader, TwilightUpgrader, RoboticsBayUpgrader
from army.divisions import IMMORTAL_x2, IMMORTAL_x5, SENTRY_x3, OBSERVER_x1, \
    STALKER_x5, ZEALOT_x10, WARPPRISM_x1, COLOSSUS_x2, VOIDRAY_x3, CARRIER_x8, TEMPEST_x5


class OneBaseRobo(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='defend', name='OneBaseRobo', ai=ai)

        stalker_micro = StalkerMicro(ai)
        # sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotMicro(ai)
        air_micro = AirMicro(ai)
        #
        # warpprism_micro = WarpPrismMicro(ai)
        # colossus_micro = ColossusMicro(ai)
        # self.sentry_micro = SentryMicro(ai)
        self.army.create_division('stalkers1', STALKER_x5, [stalker_micro], Movements(ai, 0.6), lifetime=600)
        self.army.create_division('stalkers2', STALKER_x5, [stalker_micro], Movements(ai, 0.6), lifetime=600)
        self.army.create_division('immortals1', IMMORTAL_x2, [immortal_micro], Movements(ai, 0.2), lifetime=500)
        self.army.create_division('immortals2', IMMORTAL_x2, [immortal_micro], Movements(ai, 0.2), lifetime=500)
        self.army.create_division('voidrays1', VOIDRAY_x3, [air_micro], Movements(ai))
        self.army.create_division('carriers1', CARRIER_x8, [air_micro], Movements(ai))
        self.army.create_division('tempests1', TEMPEST_x5, [air_micro], Movements(ai))
        self.army.create_division('tempests2', TEMPEST_x5, [air_micro], Movements(ai))
        self.army.create_division('zealots', ZEALOT_x10, [zealot_micro], Movements(ai, 0.33))
        # self.army.create_division('sentry', SENTRY_x3, [sentry_micro], Movements(ai, 0.2), lifetime=-300)
        self.army.create_division('observer', OBSERVER_x1, [], Movements(ai, 0.2))
        # self.army.create_division('warpprism', WARPPRISM_x1, [warpprism_micro], Movements(ai, 0.2), lifetime=-400)

        build_queue = BuildQueues.ONE_BASE_ROBO
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai))
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.robotics_bay_upgrader = RoboticsBayUpgrader(ai)

    def handle_workers(self):
        self.workers_distribution.distribute_workers()
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
        self.cybernetics_upgrader.warpgate()
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
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.forge() and \
               self.condition_lock_spending.thermal_lances()

    async def morphing(self):
        await self.morphing_.morph_gates()
