import sc2
from sc2.constants import UnitTypeId


class WorkerRushZergBot(sc2.BotAI):

    async def on_step(self, iteration):
        larva_id = UnitTypeId.LARVA
        drone = UnitTypeId.DRONE


        if self.units(UnitTypeId.OVERLORD).amount < 1 and not self.already_pending(UnitTypeId.OVERLORD):
            self.train(UnitTypeId.OVERLORD)

        if self.units(larva_id).amount > 0:
            self.train(UnitTypeId.DRONE)

        if self.time > 33:
            for unit in self.units:
                if unit.type_id == drone:
                    unit.attack(self.enemy_start_locations[0])
