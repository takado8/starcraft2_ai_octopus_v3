from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2


class PylonBuilder:
    def __init__(self, ai, special_locations=None):
        self.ai = ai
        self.is_proxy_pylon_built = False
        self.special_locations = special_locations
        self.enemy_expansions = sorted(self.ai.expansion_locations_list,
                                       key=lambda x: self.ai.enemy_start_locations[0].distance_to(x))

    async def none(self):
        pass

    async def next_standard(self):
        pylons = self.ai.structures(unit.PYLON)
        if pylons.exists:
            await self.first_and_next_standard()

    async def first_in_lower_wall(self):
        if self.ai.structures(unit.PYLON).amount < 1 and self.ai.can_afford(unit.PYLON) and not self.ai.already_pending(unit.PYLON):
            placement = Point2(self.ai.coords['pylon'])
            await self.ai.build(unit.PYLON, near=placement, placement_step=0, max_distance=0,random_alternative=False)

    async def first_in_upper_wall(self):
        if self.ai.structures(unit.PYLON).amount < 1 and self.ai.can_afford(unit.PYLON) and not self.ai.already_pending(unit.PYLON):
            placement = self.ai.main_base_ramp.protoss_wall_pylon

            await self.ai.build(unit.PYLON, near=placement, placement_step=0, max_distance=0,random_alternative=False)

    async def first_and_next_standard(self):
        if self.ai.supply_cap < 200:
            # pylons = self.ai.structures(unit.PYLON)
            if self.ai.supply_cap < 100:
                pos = self.ai.start_location.position.towards(self.ai.main_base_ramp.top_center,5)
                max_d = 35
                pending = 2 if self.ai.time > 180 else 1
                left = 5
                step = 7
            else:
                pos = self.ai.townhalls().ready.random.position
                max_d = 27
                pending = 3
                left = 9
                step = 5
            if self.ai.supply_left < left:  # or (pylons.amount < 1 and self.ai.structures(unit.GATEWAY).exists):
                if self.ai.already_pending(unit.PYLON) < pending:
                    result = await self.ai.build(unit.PYLON,max_distance=max_d, placement_step=step, near=pos)
                    i = 0
                    while not result and i < 12:
                        i+=1
                        pos = pos.random_on_distance(2)
                        result = await self.ai.build(unit.PYLON,max_distance=max_d,placement_step=step,near=pos)

    async def proxy(self):
        pylons = self.ai.structures(unit.PYLON)
        if not self.is_proxy_pylon_built and pylons.exists and self.ai.structures(unit.CYBERNETICSCORE).exists and\
                self.ai.can_afford(unit.PYLON):
            if pylons.further_than(40, self.ai.start_location.position).amount == 0:
                if not self.ai.already_pending(unit.PYLON):
                    if self.ai.coords is None:

                        position = self.enemy_expansions[5]
                        position = self.ai.mineral_field.closer_than(9, position).center.towards(position, -3)
                    else:
                        position = Point2(self.ai.coords['proxy'])
                    c = 0
                    placement = None
                    while placement is None and c < 10:
                        c += 1
                        placement = await self.ai.find_placement(unit.PYLON, near=position, max_distance=12, placement_step=2,
                                                         random_alternative=False)
                    if placement is not None:
                        worker = self.ai.units(unit.PROBE).closest_to(placement)
                        done = await self.ai.build(unit.PYLON, near=placement, build_worker=worker)
                        # if done:
                        #     self.ai.do(worker.hold_position(queue=True))
            else:
                self.is_proxy_pylon_built = True

    async def new_standard(self):
        if self.ai.supply_cap < 200:
            # if self.ai.structures(unit.PYLON).amount < 1:
            #     if not self.ai.already_pending(unit.PYLON):
            #         placement = self.ai.main_base_ramp.protoss_wall_pylon
            #
            #         await self.ai.build(unit.PYLON, near=placement, placement_step=0, max_distance=0,
            #                             random_alternative=False)
            # else:
            if self.ai.supply_cap < 60:
                pos = self.ai.start_location.position
                max_d = 25
                pending = 2 if self.ai.time > 180 else 1
                left = 7
                step = 10
            elif self.ai.supply_cap < 120:
                pos = self.ai.start_location.position
                max_d = 40
                pending = 2
                left = 10
                step = 8
            else:
                pos = self.ai.structures(unit.NEXUS).ready
                if pos.exists:
                    pos = pos.random.position
                else:
                    return
                minerals = self.ai.mineral_field.closest_to(pos)
                if minerals.distance_to(pos) < 12:
                    pos = pos.towards(minerals, -7).random_on_distance(2)
                max_d = 45
                pending = 3
                left = 9
                step = 6
            if self.ai.supply_left < left:  # or (pylons.amount < 1 and self.ai.structures(unit.GATEWAY).exists):
                if self.ai.already_pending(unit.PYLON) < pending:
                    # pos = pos.random_on_distance(7)
                    result = None
                    i = 0
                    while not result and i < 7:
                        i += 1
                        pos = pos.random_on_distance(7)
                        result = await self.ai.build(unit.PYLON, max_distance=max_d, placement_step=step, near=pos)

    async def new_standard_upper_wall(self):
        if self.ai.supply_cap < 200 and self.ai.structures(unit.PYLON).exists and self.ai.can_afford(unit.PYLON):

            if self.ai.supply_cap < 80:
                pos = self.ai.start_location.position
                max_d = 20
                pending = 2 if self.ai.time > 180 else 1
                left = 7
                step = 8
            elif self.ai.supply_cap < 120:
                pos = self.ai.start_location.position
                max_d = 30
                pending = 2
                left = 10
                step = 6
            else:
                pos = self.ai.structures(unit.NEXUS).ready
                if pos.exists:
                    pos = pos.random.position
                else:
                    return
                minerals = self.ai.mineral_field.closest_to(pos)
                if minerals.distance_to(pos) < 12:
                    pos = pos.towards(minerals, -7).random_on_distance(2)
                max_d = 45
                pending = 3
                left = 12
                step = 6
            if self.ai.supply_left < left:  # or (pylons.amount < 1 and self.ai.structures(unit.GATEWAY).exists):
                if self.ai.already_pending(unit.PYLON) < pending:
                    # pos = pos.random_on_distance(7)
                    result = None
                    if self.special_locations:
                        for location in self.special_locations:
                            if not self.ai.structures().filter(lambda x: x.type_id == unit.PYLON and
                                                        x.distance_to(location) < 1).exists:
                                await self.ai.build(unit.PYLON, max_distance=1, placement_step=1, near=location,
                                                    validate_location=False)
                                return

                    i = 0
                    while not result and i < 7:
                        i += 1
                        pos = pos.random_on_distance(5)
                        result = await self.ai.build(unit.PYLON, max_distance=max_d, placement_step=step, near=pos)

    async def cannon_rush_defense(self):
        if self.ai.supply_cap < 200 and 3 >= self.ai.structures(unit.PYLON).amount >= 1 and self.ai.can_afford(unit.PYLON):

            if self.ai.supply_cap < 80:
                pos = self.ai.start_location.position
                max_d = 20
                pending = 2 if self.ai.time > 180 else 1
                left = 7
                step = 8
            elif self.ai.supply_cap < 120:
                pos = self.ai.start_location.position
                max_d = 30
                pending = 2
                left = 10
                step = 6
            else:
                pos = self.ai.structures(unit.NEXUS).ready
                if pos.exists:
                    pos = pos.random.position
                else:
                    return
                minerals = self.ai.mineral_field.closest_to(pos)
                if minerals.distance_to(pos) < 12:
                    pos = pos.towards(minerals, -7).random_on_distance(2)
                max_d = 45
                pending = 3
                left = 12
                step = 6
            if self.ai.supply_left < left:  # or (pylons.amount < 1 and self.ai.structures(unit.GATEWAY).exists):
                if self.ai.already_pending(unit.PYLON) < pending:
                    # pos = pos.random_on_distance(7)
                    result = None
                    i = 0
                    while not result and i < 7:
                        i += 1
                        pos = pos.random_on_distance(5)
                        result = await self.ai.build(unit.PYLON, max_distance=max_d, placement_step=step, near=pos)
