from sc2 import AbilityId
from sc2.unit import Unit
from typing import Optional, Union
from sc2.position import Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId as unit
from bot.building_spot_validator import BuildingSpotValidator
from bot.constants import STRUCTURES_RADIUS


class Builder:
    GAP_SIZE = 0.5

    def __init__(self, ai, build_queue, expander, special_building_locations=None, random_worker=False,
                 furthest_worker=False):
        self.ai = ai
        self.expander = expander
        self.validator = BuildingSpotValidator(ai)
        self.random_worker = random_worker
        self.furthest_worker = furthest_worker
        self.build_queue = build_queue
        self.build_queue_index = 0
        self.special_building_locations = special_building_locations
        self.structures_max_radius = sorted(STRUCTURES_RADIUS, key=lambda x: STRUCTURES_RADIUS[x], reverse=True)[1]
        self.last_index_change_time = 0
        self.last_index = 0
        self.is_build_stuck = False


    async def build_from_queue(self):
        if self.last_index != self.build_queue_index:
            self.last_index_change_time = self.ai.time
            self.is_build_stuck = False
        self.last_index = self.build_queue_index
        if self.ai.time - self.last_index_change_time > 60: #build stuck
            validate = False
            if not self.is_build_stuck:
                self.is_build_stuck = True
                await self.ai.chat_send(f'Fix build stuck on idx {self.build_queue_index}')
        else:
            validate = True

        order_dict = {}
        for i in range(self.build_queue_index + 1):
            building = self.build_queue[i]
            if isinstance(building, unit):
                if building in order_dict:
                    order_dict[building][1] += 1
                else:
                    amount = self.ai.structures(building).amount
                    order_dict[building] = [amount, 1]
        if unit.GATEWAY in order_dict:
            warpgate_amount = self.ai.structures(unit.WARPGATE).amount
            order_dict[unit.GATEWAY][0] += warpgate_amount
        if unit.NEXUS in order_dict:
            order_dict[unit.NEXUS][1] += 1
        # print('order dict: {}'.format(order_dict))
        all_done = True
        for building in order_dict:
            if order_dict[building][0] < order_dict[building][1]:
                all_done = False
                # print('need to build: {}'.format(building))
                if self.ai.can_afford(building) and self.ai.already_pending(building) < \
                        (3 if building in {unit.PYLON, unit.GATEWAY, unit.PHOTONCANNON, unit.SHIELDBATTERY} else 1):
                    if building == unit.NEXUS:
                        await self.expander.expand()
                        return
                    elif self.special_building_locations and\
                            any([building in locations for locations in self.special_building_locations]):
                        all_building_types = None
                        if building == unit.GATEWAY:
                            all_building_types = {unit.GATEWAY, unit.WARPGATE}
                        locations = []
                        for location_list in self.special_building_locations:
                            if building in location_list:
                                locations.extend(location_list[building])

                        for location in locations:
                            if not self.ai.structures(all_building_types if all_building_types else building)\
                                    .closer_than(1, location).exists:
                                await self.build(building, near=location,
                                                placement_step=1, max_distance=1 if validate else 20,
                                                random_alternative=not validate, validate_location=False)
                                return

                    pylon = self.ai.get_pylon_with_least_neighbours()
                    if pylon:
                        await self.build(building, near=pylon, placement_step=4, max_distance=60,
                                        random_alternative=True, validate_location=validate)
                        # else:
                            # print("pylon is none")
        if all_done:
            # print('all done.')
            if self.build_queue_index + 1 < len(self.build_queue):
                self.build_queue_index += 1

    def get_current_building(self):
        return self.build_queue[self.build_queue_index]

    async def build(self, building: unit, near: Union[Unit, Point2, Point3], max_distance: int = 45, block=False,
                    build_worker: Optional[Unit] = None, random_alternative: bool = True,
                    placement_step: int = 3, validate_location=True, queue=False) -> bool:
        assert isinstance(near, (Unit, Point2, Point3))
        near_pylon = None
        if isinstance(near, Unit):
            if near.type_id == unit.PYLON:
                near_pylon = near
            near = near.position
        near = near.to2
        if not self.ai.can_afford(building, check_supply_cost=not block):
            # print('cant afford')
            return False
        if validate_location:
            if self.ai.townhalls.amount <= 3:
                build_only_in_main = True
            else:
                build_only_in_main = False

            place = None
            max_tries = 60
            loops = 12 if near_pylon else 1
            try:
                radius = STRUCTURES_RADIUS[building]
            except:
                radius = self.structures_max_radius

            all_pylons = self.ai.structures(unit.PYLON)
            if building == unit.PYLON and all_pylons.amount < 5:
                if all_pylons.amount < 6:
                    distance = 7
                else:
                    distance = 3
            else:
                distance = self.GAP_SIZE + radius

            for k in range(loops):
                i=0
                while place is None and i < max_tries:
                    i+=1
                    place = self.find_location(near, distance)

                    if place:
                        if build_only_in_main:
                            closest_minerals = self.ai.mineral_field.closest_to(place)
                            if closest_minerals.distance_to(place) < 10:
                                location_height = closest_minerals.position3d.z
                                main_base_height = self.ai.townhalls.closest_to(self.ai.start_location).position3d.z
                                on_main_base_lvl = abs(main_base_height - location_height) < 1
                                if not on_main_base_lvl:
                                    place = None
                                    continue
                        too_close = self.ai.structures().filter(lambda x: x.distance_to(place) < x.radius + distance)
                        close_enough = True if i > max_tries / 2 else self.ai.structures().filter(lambda x: x.distance_to(place)
                                     < x.radius + distance * 1.8).amount > 0 if building != unit.PYLON else True
                        if too_close.amount < 2 and close_enough and await self.ai.can_place_single(building, place):
                            break
                        elif i < max_tries:
                            place = None

                if near_pylon and i == max_tries and k < loops - 1:
                    print('changing pylon...')
                    place = None
                    if build_only_in_main:
                        main_base_height = self.ai.townhalls.closest_to(self.ai.start_location).position3d.z
                        pylons = self.ai.structures().filter(lambda x: x.is_ready and x.type_id == unit.PYLON
                                        and x.tag != near_pylon.tag and main_base_height - x.position3d.z < 1)
                    else:
                        pylons = self.ai.structures().filter(lambda x: x.is_ready and x.type_id == unit.PYLON
                                                                   and x.tag != near_pylon.tag)

                    pylons = sorted(pylons, key=lambda x: self.ai.structures().filter(lambda y:
                                                        y.type_id != unit.PYLON and y.distance_to(x) <= 6).amount)
                    if pylons:
                        j=0
                        if k < len(pylons):
                            j=k
                        near_pylon = pylons[j]
                        near = near_pylon.position.to2
        else:
            place = await self.ai.find_placement(building, near, max_distance, random_alternative, placement_step)

        if place is None:
            place = await self.ai.find_placement(building, near, max_distance, random_alternative, placement_step)
        if place is None:
            return False
        # validate
        if not validate_location or self.validator.is_valid_location(place.x, place.y):
            # print("valid location for " + str(building) + ": "+ str(p))
            if self.random_worker:

                builder =self.ai.workers.random
            elif self.furthest_worker:
                closest_mineral = self.ai.mineral_field.closest_to(self.ai.start_location)
                builder = self.ai.workers.furthest_to(closest_mineral)
                if self.ai.structures({unit.FORGE, unit.GATEWAY}).amount < 2 or self.ai.time > 600:
                    builder = build_worker or self.ai.select_build_worker(place)
                elif builder.distance_to(closest_mineral) < 6:
                    builder = self.ai.workers.random
            else:
                builder = build_worker or self.ai.select_build_worker(place)

            # i=0
            # while not await self.ai._client.query_pathing(builder.position, place) and i < len(self.ai.workers):
            #     builder = self.ai.workers[i]
            #     i+=1
            if builder is None:
                return False
            builder.build(building, place, queue=queue)
            return True
        else:
            return False

    def is_build_finished(self):
        return self.build_queue_index + 1 == len(self.build_queue)

    def is_build_in_progress(self):
        for building in self.build_queue:
            if isinstance(building, unit):
                if self.ai.already_pending(building):
                    return True
        return False

    def increment_build_queue_index(self):
        self.build_queue_index += 1

    def find_location(self, position, distance):
        j = 1
        while (not self.in_grid(position) or self.ai.structures().filter(lambda x:
                                    x.distance_to(position) < x.radius + distance).exists) and j < 4:
            k = 0
            while (not self.in_grid(position) or self.ai.structures().filter(lambda x:
                                    x.distance_to(position) < x.radius + distance).exists) and k < 12:
                k += 1
                position = position.random_on_distance(j * 2)
            j += 1
        return position

    def in_grid(self, pos):
        try:
            return self.ai.in_pathing_grid(pos)
        except:
            return False
    #
    #
    # def select_build_worker(self, pos: Union[Unit, Point2], force: bool = False) -> Optional[Unit]:
    #     workers = (
    #         self.ai.workers.filter(lambda w: (w.is_gathering or w.is_idle) and w.distance_to(pos) < 20) or self.ai.workers
    #     )
    #     if workers:
    #         for worker in workers:
    #             if worker.orders and len(worker.orders) == 1\
    #                 and worker.orders[0].ability.id == AbilityId.HOLDPOSITION:
    #                 return worker
    #         for worker in workers.sorted_by_distance_to(pos).prefer_idle:
    #             if (
    #                 worker not in self.ai.unit_tags_received_action
    #                 and not worker.orders
    #                 or len(worker.orders) == 1
    #                 and worker.orders[0].ability.id in {AbilityId.MOVE, AbilityId.HARVEST_GATHER, AbilityId.HOLDPOSITION}
    #
    #             ):
    #                 return worker
    #
    #         return workers.random if force else None