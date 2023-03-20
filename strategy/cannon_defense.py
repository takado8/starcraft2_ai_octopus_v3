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
from builders.special_building_locations import UpperWall
from data_analysis.map_tools.map_positions_service import MapPositionsService
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder

from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader, RoboticsBayUpgrader
from army.divisions import WARPPRISM_x1
from sc2.unit import UnitTypeId as unit


class CannonDefense(Strategy):
    def __init__(self, ai):
        super().__init__(type='defense', name='CannonDefense', ai=ai)

        stalker_micro = StalkerMicro(ai)
        sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotMicro(ai)
        wall_guard_zealot_micro = SecondWallGuardZealotMicro(ai)
        warpprism_micro = WarpPrismMicro(ai)
        archon_micro = ArchonMicro(ai)
        disruptor_micro = DisruptorMicro(ai)
        colossus_micro = ColossusMicro(ai)
        self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 1}, [wall_guard_zealot_micro],
                                  Movements(ai, 0.33), lifetime=400)
        army_units = {unit.ZEALOT: 15, unit.STALKER: 10, unit.IMMORTAL: 4, unit.ARCHON: 10,
                      unit.SENTRY: 3, unit.OBSERVER: 1, unit.COLOSSUS: 4, unit.DISRUPTOR: 6}

        self.army.create_division('main_army', army_units, [zealot_micro, stalker_micro, sentry_micro, immortal_micro,
                                        archon_micro,disruptor_micro,colossus_micro], Movements(ai, 0.7))
        self.army.create_division('warpprism', WARPPRISM_x1, [warpprism_micro], Movements(ai, 0.2), lifetime=-360)

        map_service = MapPositionsService(ai)
        locations_dict = map_service.load_positions_dict('early_cannon')
        build_queue = BuildQueues.CANNON_DEFENSE
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
        self.workers_distribution.distribute_workers(minerals_to_gas_ratio=2)
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
        self.assimilator_builder.standard(minerals_to_gas_ratio=2)


    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        self.forge_upgrader.standard()
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
        return self.condition_retreat.army_supply_less_than(24 if self.ai.time < 480 else 80)


    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()


    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.rush_defense()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.twilight_council_glaives() or\
               await self.condition_lock_spending.twilight_council_charge()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.morph_Archons()
        await self.morphing_.set_wall_gates_resp_inside_base()
        await self.morphing_.set_second_wall_gates_resp_inside_base()
