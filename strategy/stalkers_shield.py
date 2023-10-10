from sc2 import Race

from army.defense.fortress_defense import FortressDefense
from army.defense.target_selector_defense import TargetSelectorDefense
from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.adept_shield import AdeptShieldMicro
from army.micros.archon import ArchonMicro
from army.micros.colossus import ColossusMicro
from army.micros.disruptor import DisruptorMicro
from army.micros.immortal import ImmortalMicro
from army.micros.observer import ObserverMicro
from army.micros.second_wall_guard_zealot import SecondWallGuardZealotMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker_blink import StalkerBlinkMicro
from army.micros.stalker_shield import StalkerShieldMicro
from army.micros.warpprism import WarpPrismMicro
from army.micros.zealot import ZealotMicro
from army.micros.zealot_shield import ZealotShieldMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders import CannonBuilder
from builders.battery_builder import BatteryBuilder
from builders.special_building_locations import UpperWall
from data_analysis.map_tools.positions_loader import PositionsLoader
from strategy.interfaces.mothership import Mothership
from strategy.interfaces.second_wall_builder import SecondWallBuilder
from strategy.interfaces.secure_mineral_lines import SecureMineralLines
from strategy.interfaces.shield_battery_heal_buildings import ShieldBatteryHealBuildings
from .interfaces.siege_infrastructure import SiegeInfrastructure
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader, RoboticsBayUpgrader, \
    TemplarArchiveUpgrader
from army.divisions import OBSERVER_x1
from sc2.ids.upgrade_id import UpgradeId as upgrade


class StalkersShield(Strategy):
    def __init__(self, ai):
        super().__init__(type='macro', name='StalkersShield', ai=ai, defense=FortressDefense(ai))
        # tempest_micro = TempestMicro(ai)
        adept_micro = AdeptMicro(ai)
        sentry_micro = SentryMicro(ai)
        immortal_micro = ImmortalMicro(ai)
        zealot_micro = ZealotShieldMicro(ai)
        warpprism_micro = WarpPrismMicro(ai)
        stalker_micro = StalkerShieldMicro(ai)
        colossus_micro = ColossusMicro(ai)
        archon_micro = ArchonMicro(ai)
        disruptor_micro = DisruptorMicro(ai)
        target_selector_defense = TargetSelectorDefense(ai)



        self.army.create_division('adepts', {unit.ADEPT: 1}, [AdeptShieldMicro(ai)], Movements(ai), lifetime=300,
                                  target_selector=target_selector_defense)
        self.army.create_division('stalkers_home', {unit.STALKER: 3}, [stalker_micro], Movements(ai),
                                  target_selector=target_selector_defense)
        self.army.create_division('observer_home', OBSERVER_x1, [ObserverMicro(ai)], Movements(ai),
                                  target_selector=target_selector_defense)

        main_army = {unit.STALKER: 25, unit.ADEPT: 15, unit.SENTRY: 2, unit.COLOSSUS: 3, unit.IMMORTAL: 3,
                     unit.OBSERVER: 1, unit.ARCHON: 4,
                     unit.DISRUPTOR: 3, unit.WARPPRISM: 1}

        self.army.create_division('main_army', main_army, [zealot_micro, sentry_micro, warpprism_micro,AdeptShieldMicro(ai),
                                                           stalker_micro, immortal_micro, colossus_micro, archon_micro,
                                                           disruptor_micro], Movements(ai, movements_step=20,
                                                                                 units_ratio_before_next_step=0.75))
        self.army.create_division('chargelots', {unit.ZEALOT: 20}, [zealot_micro],
                                  Movements(ai, 0.1),
                                  lifetime=False)
        build_queue = BuildQueues.STALKER_SHIELD
        upper_wall = UpperWall(ai)
        # positions_loader = PositionsLoader(ai)
        # locations_dict = positions_loader.load_positions_dict('second_wall_cannon')
        # locations_dict[unit.GATEWAY].append(locations_dict[unit.FORGE][0])
        # del locations_dict[unit.FORGE]

        self.builder = Builder(ai, build_queue=build_queue, expander=Expander(ai),
                               special_building_locations=[upper_wall.locations_dict])
        self.battery_builder = BatteryBuilder(ai)
        self.cannon_builder = CannonBuilder(ai)
        self.shield_overcharge = ShieldOvercharge(ai)

        self.cybernetics_upgrader = CyberneticsUpgrader(ai)
        self.twilight_upgrader = TwilightUpgrader(ai)
        self.forge_upgrader = ForgeUpgrader(ai)
        self.robotics_bay_upgrader = RoboticsBayUpgrader(ai)
        self.templar_archive_upgrader = TemplarArchiveUpgrader(ai)

        self.worker_rush_defense = WorkerRushDefense(ai)
        # self.pylon_builder.special_locations = locations_dict[unit.PYLON]
        self.shield_battery_interface = ShieldBatteryHealBuildings(ai)
        self.wall_builder = SecondWallBuilder(ai)
        self.mother_ship_interface = Mothership(ai)
        self.secure_lines = SecureMineralLines(ai)
        self.siege_infrastructure = SiegeInfrastructure(ai, min_minerals=170, min_army_supply=60)

    async def execute_interfaces(self):
        await super().execute_interfaces()
        await self.siege_infrastructure.execute()
        if self.ai.time > 300:
            await self.secure_lines.execute()
        await self.shield_battery_interface.execute()

        if self.ai.iteration % 10 == 0:
            await self.battery_builder.build_batteries(when_minerals_more_than=200, amount=6)
            await self.cannon_builder.build_cannons(when_minerals_more_than=250, amount=3)

    async def handle_workers(self):
        mineral_workers = await self.worker_rush_defense.worker_rush_defense()
        self.workers_distribution.distribute_workers(1)
        if mineral_workers:
            self.speed_mining.execute(mineral_workers)
        else:
            self.speed_mining.execute(self.workers_distribution.get_mineral_workers_tags())

    # =======================================================  Builders
    async def build_from_queue(self):
        await self.builder.build_from_queue()

    async def build_pylons(self):
        await self.pylon_builder.new_standard_upper_wall()

    def build_assimilators(self):
        if self.ai.time < 160:
            self.assimilator_builder.one_vespene()
        else:
            self.assimilator_builder.standard(minerals_to_gas_ratio=2)

    # =======================================================  Upgraders
    async def do_upgrades(self):
        if self.ai.army(unit.ADEPT).exists or self.ai.already_pending(unit.ADEPT):
            self.cybernetics_upgrader.warpgate()
        if self.ai.time > 300:
            self.forge_upgrader.standard()
        await self.robotics_bay_upgrader.thermal_lances()
        await self.twilight_upgrader.blink()
        if upgrade.BLINKTECH in self.ai.state.upgrades:
            await self.twilight_upgrader.glaives()
        if upgrade.BLINKTECH in self.ai.state.upgrades and self.ai.minerals > 150 and self.ai.vespene > 150:
            await self.twilight_upgrader.charge()

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
        return self.condition_retreat.army_value_n_times_the_enemy(1) and self.condition_retreat.army_supply_less_than(90)

    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack() and self.condition_attack.army_value_n_times_the_enemy(2)

    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.standard()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return self.condition_lock_spending.thermal_lances() \
            or (await self.condition_lock_spending.forge() if self.ai.time > 360 else False) or \
            await self.condition_lock_spending.twilight_council_blink()

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.set_second_wall_gates_resp_inside_base()
        await self.morphing_.morph_Archons()
