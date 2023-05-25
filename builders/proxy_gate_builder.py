from sc2.unit import UnitTypeId as unit


class ProxyGateBuilder:
    def __init__(self, ai):
        self.ai = ai
        self.proxy_added = False

    async def build_proxy_gate(self):
        if not self.proxy_added:
            proxy_pylon = self.ai.structures().filter(lambda x: x.type_id == unit.PYLON
                                        and x.distance_to(self.ai.main_base_ramp.top_center) > 35)
            if proxy_pylon:
                proxy_pylon = proxy_pylon.furthest_to(self.ai.start_location)
                place = await self.ai.find_placement(unit.GATEWAY, near=proxy_pylon.position, max_distance=6,
                                                     random_alternative=False)
                if place:
                    self.ai.strategy.builder.special_building_locations = [{unit.GATEWAY: [place]}]
                    self.proxy_added = True
