from army.defense.target_selector_defense import TargetSelectorDefense
from army.micros.observer import ObserverMicro
from army.micros.oracle_defense import OracleDefenseMicro
from army.micros.stalker_blink import StalkerBlinkMicro
from army.movements import Movements
from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.unit_typeid import UnitTypeId as unit

INVISIBLE_UNITS_IDS = {unit.DARKTEMPLAR, unit.BANSHEE, unit.LURKER, unit.LURKERBURROWED,
                       unit.WIDOWMINE, unit.WIDOWMINEBURROWED, unit.ROACHBURROWED}


class EmergencyDetection(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai
        self.is_reported = False
        self.invisible_units_detected = False

    async def execute(self):
        if not self.invisible_units_detected:
            invisible_units = self.ai.enemy_units(INVISIBLE_UNITS_IDS)
            dark_shrine = self.ai.enemy_structures(unit.DARKSHRINE)
            if invisible_units.exists or dark_shrine.exists:
                self.invisible_units_detected = True
                await self.ai.chat_send('Tag:2_Invisible units detected.')

        if self.invisible_units_detected:
            if 'emergency_observer1' not in self.ai.strategy.army.divisions:
                target_selector_defense = TargetSelectorDefense(self.ai)

                self.ai.strategy.army.create_division('emergency_observer1', {unit.OBSERVER: 1},
                                                      [ObserverMicro(self.ai)], Movements(self.ai),
                                                      target_selector=target_selector_defense)
                self.ai.strategy.army.create_division('emergency_observer2', {unit.OBSERVER: 1},
                                                      [ObserverMicro(self.ai)], Movements(self.ai))
            if not self.ai.structures(unit.ROBOTICSFACILITY).exists:
                if self.ai.structures(unit.STARGATE).exists and \
                        'emergency_oracle1' not in self.ai.strategy.army.divisions:
                    target_selector_defense = TargetSelectorDefense(self.ai)

                    self.ai.strategy.army.create_division('emergency_oracle1', {unit.ORACLE: 1},
                                                          [OracleDefenseMicro(self.ai)], Movements(self.ai),
                                                          target_selector=target_selector_defense)

                if self.ai.can_afford(unit.ROBOTICSFACILITY) and not self.ai.already_pending(unit.ROBOTICSFACILITY):
                    await self.ai.build(unit.ROBOTICSFACILITY, near=self.ai.start_location, max_distance=40,
                                        random_alternative=True)
