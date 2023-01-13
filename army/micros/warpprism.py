from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit


class WarpPrismMicro(MicroABS):
    def __init__(self, ai):
        super().__init__("WarpPrismMicro", ai)

    async def do_micro(self, division):
        if self.ai.attack:
            dist = self.ai.enemy_start_locations[0].distance_to(self.ai.game_info.map_center) * 0.8
            for warp in division.get_units(unit.WARPPRISM):
                if warp.distance_to(self.ai.enemy_start_locations[0]) <= dist:
                    abilities = await self.ai.get_available_abilities(warp)
                    if ability.MORPH_WARPPRISMPHASINGMODE in abilities:
                        warp(ability.MORPH_WARPPRISMPHASINGMODE)
        else:
            for warp in self.ai.units(unit.WARPPRISMPHASING):
                abilities = await self.ai.get_available_abilities(warp)
                if ability.MORPH_WARPPRISMTRANSPORTMODE in abilities:
                    warp(ability.MORPH_WARPPRISMTRANSPORTMODE)
            for warp in division.get_units(unit.WARPPRISM):
                if warp.distance_to(self.ai.start_location) > 5:
                    warp.move(self.ai.start_location, queue=True)
        return 1

