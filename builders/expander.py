from sc2.ids.unit_typeid import UnitTypeId as unit


class Expander:
    def __init__(self, ai):
        self.ai = ai

    async def expand(self):
        await self._expand_now()

    async def _expand_now(self):
        building = unit.NEXUS
        location = await self.get_next_expansion()
        if location is not None:
            await self.ai.build(building,near=location,max_distance=5,random_alternative=False,placement_step=1)

    async def get_next_expansion(self):
        """Find next expansion location."""
        closest = None
        distance = 999999
        for el in self.ai.expansion_locations_list:

            def is_near_to_expansion(t):
                return t.distance_to(el) < 15

            if any(map(is_near_to_expansion, self.ai.townhalls)):
                # already taken
                continue

            rich_gas = self.ai.vespene_geyser(unit.RICHVESPENEGEYSER)
            if rich_gas.exists and rich_gas.closer_than(15, el).exists:
                # skip rich gas 'cause it's buggy.
                continue

            startp = self.ai._game_info.player_start_location
            d = await self.ai._client.query_pathing(startp, el)
            if d is None:
                d = startp.distance_to(el)

            if d < distance:
                distance = d
                closest = el

        return closest


    async def _get_next_expansion_by_distance(self):
        closest = None
        distance = 99999

        def is_near_to_expansion(t):
            return t.position.distance_to(el) < 5

        for el in self.ai.expansion_locations:
            if any(map(is_near_to_expansion,self.ai.townhalls)):
                # already taken
                continue
            startp = self.ai.structures(unit.NEXUS).closest_to(self.ai.start_location)
            d = startp.distance_to(el)
            if d < distance:
                distance = d
                closest = el
        return closest
