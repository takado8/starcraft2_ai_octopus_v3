from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.archon import ArchonMicro
from army.micros.colossus import ColossusMicro
from army.micros.dark_templar import DarkTemplarMicro
from army.micros.disruptor import DisruptorMicro
from army.micros.immortal import ImmortalMicro
from army.micros.sentry import SentryMicro
from army.micros.wall_guard_zealot import WallGuardZealotMicro
from army.micros.warpprism import WarpPrismMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from builders.special_building_locations import UpperWall
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from bot.upgraders import CyberneticsUpgrader, ForgeUpgrader, TwilightUpgrader, RoboticsBayUpgrader
from army.divisions import SENTRY_x3, OBSERVER_x1, WARPPRISM_x1, ADEPT_x5
from sc2.unit import UnitTypeId as unit


class DTs(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='rush', name='DTs', ai=ai)

        sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotMicro(ai)
        warpprism_micro = WarpPrismMicro(ai)
        colossus_micro = ColossusMicro(ai)
        archon_micro = ArchonMicro(ai)
        # stalker_micro = StalkerMicro(ai)
        disruptor_micro = DisruptorMicro(ai)
        dt_micro = DarkTemplarMicro(ai)
        wall_guard_zealot_micro = WallGuardZealotMicro(ai)
        adept_micro = AdeptMicro(ai)


        self.army.create_division('dts', {unit.DARKTEMPLAR: 2}, [dt_micro], Movements(ai, 0.1))
        self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 2}, [wall_guard_zealot_micro],
                                  Movements(ai, 0.33), lifetime=300)
        main_division_units = {unit.ZEALOT: 15, unit.STALKER: 5, unit.IMMORTAL: 7, unit.ARCHON: 8,
                                   unit.DISRUPTOR: 4, unit.COLOSSUS: 2}
        # self.sentry_micro = SentryMicro(ai)
        # self.army.create_division('stalkers2', STALKER_x5, [stalker_micro], Movements(ai, 0.6))
        self.army.create_division('adepts', ADEPT_x5, [adept_micro], Movements(ai, 0.6))

        self.army.create_division('main_army', main_division_units, [zealot_micro, colossus_micro,
                                                                     immortal_micro, archon_micro, disruptor_micro],
                                  Movements(ai, 0.7))

        self.army.create_division('sentry', SENTRY_x3, [sentry_micro], Movements(ai, 0.2), lifetime=-300)
        self.army.create_division('observer', OBSERVER_x1, [], Movements(ai, 0.2))
        self.army.create_division('warpprism', WARPPRISM_x1, [warpprism_micro], Movements(ai, 0.2), lifetime=-400)

        build_queue = BuildQueues.DTS
        upper_wall = UpperWall(ai)
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=upper_wall.locations_dict)
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.robotics_bay_upgrader = RoboticsBayUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)

    def handle_workers(self):
        mineral_workers = self.worker_rush_defense.worker_rush_defense()
        self.workers_distribution.distribute_workers(minerals_to_gas_ratio=1)
        if mineral_workers:
            self.speed_mining.execute(mineral_workers)
        else:
            self.speed_mining.execute(self.workers_distribution.get_mineral_workers_tags())

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()
        await self.battery_builder.build_batteries()

    async def build_pylons(self):
        await self.pylon_builder.new_standard_upper_wall()

    def build_assimilators(self):
        self.assimilator_builder.max_vespene()

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
        return self.condition_attack.total_supply_over(190)

    def retreat_condition(self):
        return self.condition_retreat.army_supply_less_than(70)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.forge() or \
         self.condition_lock_spending.thermal_lances()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.morph_Archons()
