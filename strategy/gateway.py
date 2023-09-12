from sc2 import Race

from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.archon import ArchonMicro
from army.micros.immortal import ImmortalMicro
from army.micros.observer import ObserverMicro
from army.micros.second_wall_guard_zealot import SecondWallGuardZealotMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker_blink import StalkerBlinkMicro
from army.micros.warpprism import WarpPrismMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders import CannonBuilder
from builders.battery_builder import BatteryBuilder
from builders.proxy_gate_builder import ProxyGateBuilder
from data_analysis.map_tools.positions_loader import PositionsLoader
from strategy.interfaces.second_wall_builder import SecondWallBuilder
from strategy.interfaces.secure_mineral_lines import SecureMineralLines
from strategy.interfaces.shield_battery_heal_buildings import ShieldBatteryHealBuildings
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from army.micros.stalker import StalkerMicro
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader
from army.divisions import STALKER_x10, ZEALOT_x10
from sc2.unit import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade



class Gateway(Strategy):
    def __init__(self, ai):
        super().__init__(type='rush', name='Gateway', ai=ai)

        positions_loader = PositionsLoader(ai)
        if self.ai.enemy_race == Race.Zerg:
            locations_dict = positions_loader.load_positions_dict('second_wall_cannon')
            locations_dict[unit.GATEWAY].append(locations_dict[unit.FORGE][0])
            del locations_dict[unit.FORGE]
            sentry_micro = SentryMicro(ai, locations_dict[unit.ZEALOT][0])
            wall_guard_zealot_micro = SecondWallGuardZealotMicro(ai, locations_dict[unit.ZEALOT][0])
            self.army.create_division('wall_guard_zealots', {unit.ZEALOT: 2}, [wall_guard_zealot_micro],
                                      Movements(ai, 0.1))
            self.pylon_builder.special_locations = locations_dict[unit.PYLON]
        else:
            locations_dict = None
            sentry_micro = SentryMicro(ai)
        if self.ai.enemy_race == Race.Terran:
            blink_locations_dict = positions_loader.load_positions_dict('blink_to_main')
            blink_locations = blink_locations_dict[unit.PYLON]
        else:
            blink_locations = None
        stalker_micro = StalkerBlinkMicro(ai, blink_locations=blink_locations)
        # self.army.create_division('stalkers1', STALKER_x10, [stalker_micro], Movements(ai, 0.7))
        # self.army.create_division('stalkers2', STALKER_x10, [stalker_micro], Movements(ai, 0.7))

        main_army = {unit.ZEALOT: 15, unit.IMMORTAL: 2, unit.STALKER: 20
            , unit.ARCHON: 10, unit.SENTRY: 3, unit.OBSERVER: 1, unit.WARPPRISM: 1}
        self.army.create_division('main_army', main_army, [sentry_micro, ZealotMicro(ai), ArchonMicro(ai),
                                        ObserverMicro(ai), ImmortalMicro(ai), WarpPrismMicro(ai), stalker_micro],
                                  Movements(ai, 0.7))

        build_queue = BuildQueues.GATEWAY
        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[locations_dict] if locations_dict else None)
        self.battery_builder = BatteryBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)
        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.worker_rush_defense = WorkerRushDefense(ai)
        self.proxy_gate_builder = ProxyGateBuilder(ai)
        self.shield_battery_interface = ShieldBatteryHealBuildings(ai)
        self.cannon_builder = CannonBuilder(ai)
        self.secure_lines = SecureMineralLines(ai)
        self.wall_builder = SecondWallBuilder(ai)

        self.emergency_expansion.mineral_threshold1 = 1000
        self.emergency_expansion.mineral_threshold2 = 800
        self.emergency_expansion.excess_expansion_threshold = 1000


    async def execute_interfaces(self):
        await super().execute_interfaces()
        await self.wall_builder.execute()
        await self.shield_battery_interface.execute()
        if self.ai.time > 420:
            await self.battery_builder.build_batteries(when_minerals_more_than=400, amount=4)
            await self.cannon_builder.build_cannons(when_minerals_more_than=350, amount=2)
        if self.ai.enemy_race == Race.Zerg and self.ai.time > 360:
            await self.secure_lines.execute()
        elif self.ai.enemy_race == Race.Terran and self.ai.time > 240:
            await self.secure_lines.execute()
        elif self.ai.enemy_race == Race.Protoss and self.ai.time > 300:
            await self.secure_lines.execute()


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
        if self.ai.enemy_race == Race.Zerg:
            await self.pylon_builder.new_standard_upper_wall()
        else:
            await self.pylon_builder.new_standard()


    def build_assimilators(self):
        self.assimilator_builder.standard(minerals_to_gas_ratio=2)

    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        self.forge_upgrader.standard()
        await self.twilight_upgrader.blink()
        if upgrade.BLINKTECH in self.ai.state.upgrades:
            await self.twilight_upgrader.charge()

    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army

    async def army_execute(self):
        await self.army.execute()

    # ======================================================= Conditions
    def attack_condition(self):
        return self.condition_attack.blink_research_ready() or (self.condition_attack.blink_research_ready_raw()
                and self.condition_attack.army_value_n_times_the_enemy(2)) or self.condition_attack.total_supply_over(195)

    def retreat_condition(self):
        return self.condition_retreat.army_value_n_times_the_enemy(1)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack()

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.twilight_council_charge() or \
               await self.condition_lock_spending.twilight_council_blink() or \
               await self.condition_lock_spending.forge()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.morph_Archons()
