from army.defense.worker_rush_defense import WorkerRushDefense
from army.divisions import WARPPRISM_x1, TEMPEST_x5
from army.micros.carrier import CarrierMicro
from army.micros.tempest import TempestMicro
from army.micros.voidray_cannon_defense import VoidrayCannonDefenseMicro
from army.micros.warpprism_elevator import WarpPrismElevatorMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from data_analysis.map_tools.positions_loader import PositionsLoader
from strategy.interfaces.gas_builder import GasBuilder
from strategy.interfaces.set_nexus_resp import SetNexusResp
from strategy.interfaces.shield_battery_heal_buildings import ShieldBatteryHealBuildings
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder

from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader, RoboticsBayUpgrader
from sc2.unit import UnitTypeId as unit


class WorkerRushDefenseStrategy(Strategy):
    def __init__(self, ai):
        carrier_micro = CarrierMicro(ai)
        tempest_micro = TempestMicro(ai)
        super().__init__(type='defense', name='WorkerRushDefenseStrategy', ai=ai)
        # self.army.create_division('stalker', {unit.ADEPT: 5}, [StalkerMicro(ai)], Movements(ai, 0.1))
        self.army.create_division('voidray', {unit.VOIDRAY: 40}, [VoidrayCannonDefenseMicro(ai)], Movements(ai, 0.6),
                                  lifetime=2000)
        # self.army.create_division('carriers1', {unit.CARRIER: 20}, [CarrierMicro(ai)], Movements(ai))
        self.army.create_division('warpprism', WARPPRISM_x1, [WarpPrismElevatorMicro(ai)],
                                  Movements(ai, 0.2), lifetime=-1000)
        self.army.create_division('carriers1', {unit.CARRIER: 10}, [carrier_micro], Movements(ai), lifetime=-1000)
        self.army.create_division('tempests1', TEMPEST_x5, [tempest_micro], Movements(ai), lifetime=-1000)
        self.army.create_division('tempests2', TEMPEST_x5, [tempest_micro], Movements(ai), lifetime=-1000)

        positions_loader = PositionsLoader(ai)
        locations_dict = positions_loader.load_positions_dict('worker_rush_defense')
        locations_dict2 = positions_loader.load_positions_dict('cannon_rush_defense')
        build_queue = BuildQueues.WORKER_RUSH_DEFENSE
        special_locations = [locations_dict, locations_dict2]
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=special_locations, furthest_worker=True)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.robotics_bay_upgrader = RoboticsBayUpgrader(ai)

        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)
        self.worker_rush_defense = WorkerRushDefense(ai)
        self.shield_battery_interface = ShieldBatteryHealBuildings(ai)
        self.set_nexus_resp_interface = SetNexusResp(ai)
        self.gas_builder = GasBuilder(ai)

    async def execute_interfaces(self):
        await super().execute_interfaces()
        await self.shield_battery_interface.execute()
        await self.set_nexus_resp_interface.execute()
        await self.gas_builder.execute()

    async def handle_workers(self):
        mineral_workers = await self.worker_rush_defense.worker_rush_defense() if \
            self.ai.structures({unit.PYLON, unit.GATEWAY, unit.FORGE}).amount < 4 else None
        self.workers_distribution.distribute_workers(minerals_to_gas_ratio=1)
        if not self.ai.structures({unit.GATEWAY, unit.FORGE}).exists:
            if mineral_workers:
                self.speed_mining.execute(mineral_workers)
            else:
                self.speed_mining.execute(self.workers_distribution.get_mineral_workers_tags())
        if self.ai.structures(unit.ASSIMILATOR).amount >= 2 and self.builder.random_worker is False:
            self.builder.random_worker = True


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
        if self.ai.units(unit.VOIDRAY).exists and self.ai.structures(unit.STARGATE).ready.idle.amount <= 1:
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
        if self.ai.time < 1000:
            army_supply = 100
        else:
            army_supply = 80
        return self.condition_attack.army_supply_over(army_supply)


    def retreat_condition(self):
        if self.ai.time < 480:
            army_supply = 21
        elif self.ai.time < 1000:
            army_supply = 36
        else:
            army_supply = 60
        return self.condition_retreat.army_supply_less_than(army_supply)


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
