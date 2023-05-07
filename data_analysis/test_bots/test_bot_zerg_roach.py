import sc2
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade
from sc2.ids.ability_id import AbilityId as ability


class RoachBurrowBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        drones = self.units(unit.DRONE)
        overlords = self.units(unit.OVERLORD)
        roaches = self.units(unit.ROACH)
        # burrowed_roaches = roaches.filter(lambda r: r.is_burrowed)
        larvae = self.units(unit.LARVA)
        # Train drones and overlords as necessary.
        if drones.amount < 19:
            if self.can_afford(unit.DRONE) and larvae.exists:
                larvae.random.train(unit.DRONE)
        if overlords.amount < 5:
            if self.can_afford(unit.OVERLORD) and larvae.exists:
                larvae.random.train(unit.OVERLORD)

            # Get the current number of extractors
        num_extractors = self.units(sc2.UnitTypeId.EXTRACTOR).amount

        # Build an extractor if we have less than 1 and can afford it
        if num_extractors < 1 and self.can_afford(sc2.UnitTypeId.EXTRACTOR):
            drone = self.workers.random
            target = self.vespene_geyser.closest_to(drone.position)
            drone.build_gas(target)

        # Build a spawning pool if we don't have one yet.
        if not self.structures(unit.SPAWNINGPOOL) and not self.already_pending(unit.SPAWNINGPOOL):
            if self.can_afford(unit.SPAWNINGPOOL):
                await self.build(unit.SPAWNINGPOOL, near=self.start_location.towards(self.game_info.map_center, 5))

        # hatchery = self.townhalls.ready  # Get the first ready Hatchery
        # if hatchery:
        #     hatchery = hatchery.first
        #     if self.can_afford(unit.LAIR):
        #         hatchery(ability.UPGRADETOLAIR_LAIR)  # Morph the Hatchery into a Lair

        # Build a roach warren if we don't have one yet.
        if not self.structures(unit.ROACHWARREN) and not self.already_pending(unit.ROACHWARREN):
            if self.can_afford(unit.ROACHWARREN):
                await self.build(unit.ROACHWARREN, near=self.start_location.towards(self.game_info.map_center, 8))

        if self.can_afford(ability.RESEARCH_BURROW):
            hatchery = self.townhalls.ready
            if hatchery:
                hatchery = hatchery.first
                hatchery(ability.RESEARCH_BURROW)
            else:
                lair = self.structures(unit.LAIR).ready
                if lair:
                    lair = lair.first
                    lair(ability.RESEARCH_BURROW)


        # Build roaches when we have the resources and larva.
        if self.structures(unit.ROACHWARREN).ready.exists and self.can_afford(unit.ROACH) \
                and larvae.exists:
            larvae.random.train(unit.ROACH)

        # Attack with roaches.
        if upgrade.BURROW in self.state.upgrades:
            for roach in roaches:
                if roach.health_percentage < 0.65:
                    roach(ability.BURROWDOWN_ROACH)
                else:
                    roach.attack(self.enemy_start_locations[0])

            for roach_burrowed in self.units(unit.ROACHBURROWED):
                if roach_burrowed.health_percentage > 0.95 and self.enemy_units:
                    roach_burrowed(ability.BURROWUP_ROACH)
