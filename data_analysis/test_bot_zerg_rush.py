import sc2
from sc2.constants import UnitTypeId


class SimpleZergBot(sc2.BotAI):
    pool_exists = False

    async def on_step(self, iteration):
        spawning_pool = UnitTypeId.SPAWNINGPOOL
        larva_id = UnitTypeId.LARVA
        drone = UnitTypeId.DRONE
        zergling = UnitTypeId.ZERGLING

        if not self.pool_exists and not self.units(spawning_pool).exists and not self.already_pending(spawning_pool):
            if self.can_afford(spawning_pool):
                await self.build(spawning_pool, near=self.townhalls.first)
                self.pool_exists = True
        if self.units(UnitTypeId.OVERLORD).amount < 2 and not self.already_pending(UnitTypeId.OVERLORD):
            self.train(UnitTypeId.OVERLORD)

        if not self.pool_exists or self.units(larva_id).amount > 2:
            self.train(UnitTypeId.DRONE)
        for larva in self.units(larva_id):
            if self.can_afford(zergling) and larva.noqueue:
                larva.train(zergling)

        if self.units(zergling).amount > 3:
            for unit in self.units:
                if unit.type_id == larva_id or unit.type_id == drone:
                    unit.attack(self.enemy_start_locations[0])
                elif unit.type_id == zergling:
                    unit.attack(self.enemy_start_locations[0])
