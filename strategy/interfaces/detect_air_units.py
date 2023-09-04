from army.micros.stalker_blink import StalkerBlinkMicro
from army.movements import Movements
from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.unit_typeid import UnitTypeId as unit


class DetectAirUnits(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai

    async def execute(self):
        AIR_UNITS_IDS = {unit.BATTLECRUISER}
        air_units = self.ai.enemy_units(AIR_UNITS_IDS)
        fusion_core = self.ai.enemy_structures(unit.FUSIONCORE)

        if air_units.exists or fusion_core.exists:
            await self.ai.chat_send('Tag:Air units detected.')
            self.ai.strategy = self.ai.strategy_manager.follow_up_strategies['SkytossTempest'](self.ai)
            self.ai.strategy.army.create_division('stalkers', {unit.STALKER: 30},
                                                  [StalkerBlinkMicro(self.ai)],
                Movements(self.ai, units_ratio_before_next_step=0.6, movements_step=15), lifetime=False)
