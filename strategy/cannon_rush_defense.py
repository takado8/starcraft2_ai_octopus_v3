from army.defense.worker_rush_defense import WorkerRushDefense
from army.divisions import WARPPRISM_x1
from army.micros.carrier import CarrierMicro
from army.micros.voidray_cannon_defense import VoidrayCannonDefenseMicro
from army.micros.warpprism_elevator import WarpPrismElevatorMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from data_analysis.map_tools.positions_loader import PositionsLoader
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder

from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader, RoboticsBayUpgrader
from sc2.unit import UnitTypeId as unit


class CannonRushDefense(Strategy):
    def __init__(self, ai):
        super().__init__(type='defense', name='CannonRushDefense', ai=ai)
        # self.army.create_division('stalker', {unit.ADEPT: 5}, [StalkerMicro(ai)], Movements(ai, 0.1))
        self.army.create_division('voidray', {unit.VOIDRAY: 10}, [VoidrayCannonDefenseMicro(ai)], Movements(ai, 0.6), lifetime=480)
        self.army.create_division('carriers1', {unit.CARRIER: 20}, [CarrierMicro(ai)], Movements(ai))
        self.army.create_division('warpprism', WARPPRISM_x1, [WarpPrismElevatorMicro(ai)], Movements(ai, 0.2), lifetime=-260)

        positions_loader = PositionsLoader(ai)
        locations_dict = positions_loader.load_positions_dict('cannon_rush_defense')
        build_queue = BuildQueues.CANNON_RUSH_DEFENSE
        special_locations = [locations_dict]
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=special_locations, random_worker=True)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.robotics_bay_upgrader = RoboticsBayUpgrader(ai)

        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)
        self.worker_rush_defense = WorkerRushDefense(ai)

    async def handle_workers(self):
        mineral_workers = await self.worker_rush_defense.worker_rush_defense() if \
            self.ai.structures(unit.PHOTONCANNON).amount < 3 else None
        self.workers_distribution.distribute_workers(minerals_to_gas_ratio=1)
        if mineral_workers:
            self.speed_mining.execute(mineral_workers)
        else:
            self.speed_mining.execute(self.workers_distribution.get_mineral_workers_tags())

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()

    async def build_pylons(self):
        await self.pylon_builder.new_standard_upper_wall()
        await self.battery_builder.build_batteries(when_minerals_more_than=600, amount=4)

    def build_assimilators(self):
        self.assimilator_builder.standard(minerals_to_gas_ratio=1)


    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.air_dmg()
        self.forge_upgrader.shield()


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
        return self.condition_retreat.army_count_less_than(6 if self.ai.time < 360 else 15)


    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()


    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.rush_defense()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.none()
               # await self.condition_lock_spending.forge()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_wall_gates_resp_inside_base()
