from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from army.micros.micro import StalkerMicro, ImmortalMicro, SentryMicro, ZealotMicro, WarpPrismMicro, \
    ColossusMicro, AirMicro, ArchonMicro, DisruptorMicro
from bot.upgraders import CyberneticsUpgrader, ForgeUpgrader, TwilightUpgrader, RoboticsBayUpgrader
from army.divisions import IMMORTAL_x2, IMMORTAL_x5, SENTRY_x3, OBSERVER_x1, \
    STALKER_x5, ZEALOT_x10, WARPPRISM_x1, COLOSSUS_x2, VOIDRAY_x3, CARRIER_x8, TEMPEST_x5
from sc2.unit import UnitTypeId as unit


class OneBaseRobo(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='defend', name='OneBaseRobo', ai=ai)

        sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotMicro(ai)
        warpprism_micro = WarpPrismMicro(ai)
        colossus_micro = ColossusMicro(ai)
        archon_micro = ArchonMicro(ai)
        stalker_micro = StalkerMicro(ai)
        disruptor_micro = DisruptorMicro(ai)
        self.army.create_division('stalkers1', STALKER_x5, [stalker_micro], Movements(ai, 0.6))

        main_division_units = {unit.ZEALOT: 3, unit.STALKER: 7, unit.IMMORTAL: 7, unit.COLOSSUS: 3, unit.ARCHON: 8,
                               unit.DISRUPTOR: 4}
        # self.sentry_micro = SentryMicro(ai)
        self.army.create_division('stalkers2', STALKER_x5, [stalker_micro], Movements(ai, 0.6))
        self.army.create_division('stalkers3', STALKER_x5, [stalker_micro], Movements(ai, 0.6))

        self.army.create_division('main_army', main_division_units, [zealot_micro, colossus_micro,
                                                                     immortal_micro, archon_micro, disruptor_micro],
                                  Movements(ai, 0.7))

        self.army.create_division('sentry', SENTRY_x3, [sentry_micro], Movements(ai, 0.2), lifetime=-300)
        self.army.create_division('observer', OBSERVER_x1, [], Movements(ai, 0.2))
        self.army.create_division('warpprism', WARPPRISM_x1, [warpprism_micro], Movements(ai, 0.2), lifetime=-400)

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
        self.assimilator_builder.standard()

    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        self.forge_upgrader.armor_first()
        await self.twilight_upgrader.standard()
        await self.robotics_bay_upgrader.thermal_lances()

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
        await self.morphing_.morph_Archons()
