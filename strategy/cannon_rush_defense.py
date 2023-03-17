from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.archon import ArchonMicro
from army.micros.colossus import ColossusMicro
from army.micros.disruptor import DisruptorMicro
from army.micros.immortal import ImmortalMicro
from army.micros.probe import ProbeMicro
from army.micros.second_wall_guard_zealot import SecondWallGuardZealotMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker import StalkerMicro
from army.micros.warpprism import WarpPrismMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from data_analysis.map_tools.map_positions_service import MapPositionsService
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder

from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader, RoboticsBayUpgrader
from army.divisions import ADEPT_x5, WARPPRISM_x1, STALKER_x5, ARCHONS_x5, SENTRY_x1, IMMORTAL_x2, OBSERVER_x1
from sc2.unit import UnitTypeId as unit


class CannonRushDefense(Strategy):
    def __init__(self, ai):
        super().__init__(type='defense', name='CannonRushDefense', ai=ai)
        stalker_micro = StalkerMicro(ai)
        sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotMicro(ai)
        wall_guard_zealot_micro = WallGuardZealotMicro(ai)
        warpprism_micro = WarpPrismMicro(ai)
        archon_micro = ArchonMicro(ai)
        disruptor_micro = DisruptorMicro(ai)
        colossus_micro = ColossusMicro(ai)
        # dt_micro = DarkTemplarMicro(ai)
        self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 1}, [wall_guard_zealot_micro],
                                  Movements(ai, 0.33), lifetime=400)
        self.army.create_division('zealots', {unit.ZEALOT: 10}, [zealot_micro], Movements(ai, 0.1))
        self.army.create_division('zealots2', {unit.ZEALOT: 5}, [zealot_micro], Movements(ai, 0.1))

        self.army.create_division('stalkers', STALKER_x5, [stalker_micro], Movements(ai, 0.2))
        self.army.create_division('immortals1', IMMORTAL_x2, [immortal_micro], Movements(ai, 0.2))
        self.army.create_division('immortals2', IMMORTAL_x2, [immortal_micro], Movements(ai, 0.2))

        self.army.create_division('archons1', ARCHONS_x5, [archon_micro], Movements(ai, 0.2))
        self.army.create_division('archons2', ARCHONS_x5, [archon_micro], Movements(ai, 0.2))

        self.army.create_division('stalkers1', STALKER_x5, [stalker_micro], Movements(ai, 0.5))

        self.army.create_division('sentry1', SENTRY_x1, [sentry_micro], Movements(ai, 0.2), lifetime=-220)
        self.army.create_division('sentry2', SENTRY_x1, [sentry_micro], Movements(ai, 0.2), lifetime=-360)
        self.army.create_division('sentry3', SENTRY_x1, [sentry_micro], Movements(ai, 0.2), lifetime=-260)
        self.army.create_division('observer', OBSERVER_x1, [], Movements(ai, 0.2))
        self.army.create_division('warpprism', WARPPRISM_x1, [warpprism_micro], Movements(ai, 0.2), lifetime=-360)

        map_service = MapPositionsService(ai)
        locations_dict = map_service.load_positions_dict('cannon_rush_defense')
        build_queue = BuildQueues.CANNON_RUSH_DEFENSE
        # upper_wall = UpperWall(ai)
        special_locations = [locations_dict]
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=special_locations)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.robotics_bay_upgrader = RoboticsBayUpgrader(ai)

        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)
        self.worker_rush_defense = WorkerRushDefense(ai)
        self.probes_micro = ProbeMicro(ai)

    async def handle_workers(self):
        # self.probes_micro.do_micro()
        mineral_workers = await self.worker_rush_defense.worker_rush_defense()
        self.workers_distribution.distribute_workers(minerals_to_gas_ratio=4)
        if mineral_workers:
            self.speed_mining.execute(mineral_workers)
        else:
            self.speed_mining.execute(self.workers_distribution.get_mineral_workers_tags())

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()

    async def build_pylons(self):
        await self.pylon_builder.new_standard_upper_wall()
        await self.battery_builder.build_batteries()

    def build_assimilators(self):
        self.assimilator_builder.standard(minerals_to_gas_ratio=5)


    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        self.forge_upgrader.armor_first()
        await self.twilight_upgrader.standard()


    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()


    # =======================================================  Army

    async def army_execute(self):
        await self.army.execute()


    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.total_supply_over(195)


    def retreat_condition(self):
        return self.condition_retreat.army_supply_less_than(24 if self.ai.time < 480 else 40)


    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()


    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.rush_defense()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.twilight_council_glaives()
               # await self.condition_lock_spending.forge()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.morph_Archons()
        await self.morphing_.set_wall_gates_resp_inside_base()
