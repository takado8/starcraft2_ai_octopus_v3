from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.carrier import CarrierMicro
# from army.micros.carrier_updated import CarrierMicroUpdated
from army.micros.observer import ObserverMicro
from army.micros.oracle_defense import OracleDefenseMicro
from army.micros.tempest import TempestMicro
from army.micros.voidray import VoidrayMicro
from army.micros.wall_guard_zealot import WallGuardZealotMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders.battery_builder import BatteryBuilder
from builders.special_building_locations import UpperWall
from .strategyABS import StrategyABS
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader
from army.divisions import TEMPEST_x5, VOIDRAY_x3, OBSERVER_x1, ORACLE_x1


class SkyToss(StrategyABS):
    def __init__(self, ai):
        super().__init__(type='air', name='SkyToss', ai=ai)

        voidray_micro = VoidrayMicro(ai)
        carrier_micro = CarrierMicro(ai)
        tempest_micro = TempestMicro(ai)
        zealot_micro = ZealotMicro(ai)

        self.army.create_division('adepts', {unit.ADEPT: 2}, [AdeptMicro(ai)], Movements(ai))
        self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 1}, [WallGuardZealotMicro(ai)], Movements(ai))
        self.army.create_division('zealots', {unit.ZEALOT: 5}, [zealot_micro], Movements(ai), lifetime=-380)
        self.army.create_division('observer', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        # self.army.create_division('observer2', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai))
        self.army.create_division('voidrays1', VOIDRAY_x3, [voidray_micro], Movements(ai))
        self.army.create_division('oracle', ORACLE_x1, [OracleDefenseMicro(ai)], Movements(ai), lifetime=-300)
        self.army.create_division('carriers1', {unit.CARRIER: 10}, [carrier_micro], Movements(ai))
        self.army.create_division('tempests1', TEMPEST_x5, [tempest_micro], Movements(ai))
        self.army.create_division('tempests2', TEMPEST_x5, [tempest_micro], Movements(ai))
        # self.army.create_division('zealot1', ZEALOT_x5, [zealot_micro], Movements(ai), lifetime=-640)
        # self.army.create_division('zealot2', ZEALOT_x5, [zealot_micro], Movements(ai), lifetime=-40)

        build_queue = BuildQueues.SKYTOSS
        upper_wall = UpperWall(ai)
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=upper_wall.locations_dict)
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)

    def handle_workers(self):
        mineral_workers = self.worker_rush_defense.worker_rush_defense()
        self.workers_distribution.distribute_workers()
        if mineral_workers:
            self.speed_mining.execute(mineral_workers)
        else:
            self.speed_mining.execute(self.workers_distribution.get_mineral_workers_tags())

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()
        await self.battery_builder.build_batteries(when_minerals_more_than=700)

    async def build_pylons(self):
        await self.pylon_builder.new_standard_upper_wall()

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
        return self.condition_retreat.army_supply_less_than(95)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.none()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_wall_gates_resp_inside_base()
