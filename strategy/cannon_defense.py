from sc2 import Race

from army.defense.target_selector_defense import TargetSelectorDefense
from army.defense.worker_rush_defense import WorkerRushDefense
from army.micros.adept import AdeptMicro
from army.micros.archon import ArchonMicro
from army.micros.immortal import ImmortalMicro
from army.micros.observer import ObserverMicro
from army.micros.sentry import SentryMicro
from army.micros.stalker_blink import StalkerBlinkMicro
from army.micros.warpprism import WarpPrismMicro
from army.micros.zealot import ZealotMicro
from army.movements import Movements
from bot.nexus_abilities import ShieldOvercharge
from builders import CannonBuilder
from builders.battery_builder import BatteryBuilder
from data_analysis.map_tools.positions_loader import PositionsLoader
from strategy.interfaces.secure_mineral_lines import SecureMineralLines
from strategy.interfaces.shield_battery_heal_buildings import ShieldBatteryHealBuildings
from .interfaces.siege_infrastructure import SiegeInfrastructure
from .strategyABS import Strategy
from builders.expander import Expander
from builders.build_queues import BuildQueues
from builders.builder import Builder
from sc2.ids.upgrade_id import UpgradeId as upgrade
from bot.upgraders import CyberneticsUpgrader, TwilightUpgrader, ForgeUpgrader, RoboticsBayUpgrader
from sc2.unit import UnitTypeId as unit


class CannonDefense(Strategy):
    def __init__(self, ai):
        super().__init__(type='defense', name='CannonDefense', ai=ai)
        stalker_micro = StalkerBlinkMicro(ai)
        observer_micro = ObserverMicro(ai)

        self.army.create_division('adept', {unit.ADEPT: 1}, [AdeptMicro(ai)], Movements(ai),
                                  target_selector=TargetSelectorDefense(ai))
        self.army.create_division('stalker', {unit.STALKER: 1}, [stalker_micro], Movements(ai),
                                  target_selector=TargetSelectorDefense(ai))
        self.army.create_division('observer', {unit.OBSERVER: 1}, [observer_micro], Movements(ai),
                                  target_selector=TargetSelectorDefense(ai))
        main_army = {unit.ZEALOT: 12, unit.STALKER: 20,  unit.IMMORTAL: 3,
                     unit.ARCHON: 10, unit.SENTRY: 3, unit.OBSERVER: 1, unit.WARPPRISM: 1}
        self.army.create_division('main_army', main_army, [SentryMicro(ai), ZealotMicro(ai), ArchonMicro(ai),
                                    stalker_micro, observer_micro, ImmortalMicro(ai), WarpPrismMicro(ai)],
                                  Movements(ai, 0.85,9), lifetime=-180)

        positions_loader = PositionsLoader(ai)
        locations_dict = positions_loader.load_positions_dict('cannon_defense')
        build_queue = BuildQueues.CANNON_DEFENSE

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
        self.shield_battery_interface = ShieldBatteryHealBuildings(ai)
        self.secure_lines = SecureMineralLines(ai)
        self.cannon_builder = CannonBuilder(ai)
        self.siege_infrastructure = SiegeInfrastructure(ai)

    async def execute_interfaces(self):
        await super().execute_interfaces()
        await self.shield_battery_interface.execute()
        if self.ai.enemy_race == Race.Zerg and self.ai.time > 360:
            await self.secure_lines.execute()
        elif self.ai.enemy_race == Race.Terran and self.ai.time > 240:
            await self.secure_lines.execute()
        elif self.ai.enemy_race == Race.Protoss and self.ai.time > 300:
            await self.secure_lines.execute()
        await self.cannon_builder.build_cannons(when_minerals_more_than=410, amount=2)
        await self.battery_builder.build_batteries(when_minerals_more_than=420, amount=4)
        await self.siege_infrastructure.execute()


    async def handle_workers(self):
        mineral_workers = await self.worker_rush_defense.worker_rush_defense() if \
            self.ai.structures(unit.PHOTONCANNON).amount < 1 else None
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

    def build_assimilators(self):
        if self.ai.structures(unit.PHOTONCANNON).exists:
            self.assimilator_builder.standard(minerals_to_gas_ratio=1)

    # =======================================================  Upgraders
    async def do_upgrades(self):
        self.cybernetics_upgrader.warpgate()
        self.forge_upgrader.standard()
        await self.twilight_upgrader.charge()
        if upgrade.CHARGE in self.ai.state.upgrades:
            await self.twilight_upgrader.blink()

    # =======================================================  Trainers

    def train_probes(self):
        self.nexus_trainer.probes_standard()

    # =======================================================  Army
    async def army_execute(self):
        await self.army.execute()

    # ======================================================= Conditions
    def attack_condition(self):
        return (self.condition_attack.ground_weapons_and_armor_lvl2() and not self.ai.after_first_attack) or\
               self.condition_attack.total_supply_over(195)


    def retreat_condition(self):
        return self.condition_retreat.army_value_n_times_the_enemy(1) and self.condition_retreat.army_supply_less_than(90)


    def counter_attack_condition(self):
        return self.condition_counter_attack.counter_attack() and self.condition_attack.army_value_n_times_the_enemy(2)


    # ======================================================== Buffs
    async def nexus_abilities(self):
        self.chronobooster.rush_defense()
        await self.shield_overcharge.shield_overcharge()

    async def lock_spending_condition(self):
        return await self.condition_lock_spending.twilight_council_charge() or\
             await self.condition_lock_spending.twilight_council_blink() or\
               (await self.condition_lock_spending.forge() if self.ai.time > 600 else False)

    async def morphing(self):
        await self.morphing_.morph_gates()
        await self.morphing_.morph_Archons()
