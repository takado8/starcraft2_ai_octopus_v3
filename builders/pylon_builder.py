from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2
import math


class PylonBuilder:
    def __init__(self, ai):
        self.ai = ai
        self.is_proxy_pylon_built = False

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
            pylons = self.ai.structures(unit.PYLON)
            if self.ai.supply_cap < 100:
                pos = self.ai.start_location.position.towards(self.ai.main_base_ramp.top_center,5)
                max_d = 23
                pending = 2 if self.ai.time > 180 else 1
                left = 5
                step = 7
            else:
                pos = self.ai.structures(unit.NEXUS).ready.random.position
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
                        pos = self.ai.game_info.map_center.towards_with_random_angle(self.ai.enemy_start_locations[0],
                            self.ai.start_location.distance_to(self.ai.game_info.map_center) / 2,
                                                                              max_difference=math.pi/4)
                    else:
                        pos = Point2(self.ai.coords['proxy'])
                    c = 0
                    placement = None
                    while placement is None and c < 10:
                        c += 1
                        placement = await self.ai.find_placement(unit.PYLON, near=pos, max_distance=20, placement_step=2,
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
            if self.ai.supply_cap < 130:
                pos = self.ai.start_location.position.towards(self.ai.main_base_ramp.top_center, 4).random_on_distance(5)
                max_d = 25
                pending = 2 if self.ai.time > 180 else 1
                left = 5
                step = 7
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
                step = 5
            if self.ai.supply_left < left:  # or (pylons.amount < 1 and self.ai.structures(unit.GATEWAY).exists):
                if self.ai.already_pending(unit.PYLON) < pending:
                    # pos = pos.random_on_distance(7)
                    result = await self.ai.build(unit.PYLON, max_distance=max_d, placement_step=step, near=pos)
                    i = 0
                    while not result and i < 12:
                        i += 1
                        pos = pos.random_on_distance(7)
                        result = await self.ai.build(unit.PYLON, max_distance=max_d, placement_step=step, near=pos)