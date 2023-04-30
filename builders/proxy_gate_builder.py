from sc2.unit import UnitTypeId as unit


class ProxyGateBuilder:
    def __init__(self, ai):
        self.ai = ai

    async def build_proxy_gate(self):
        proxy_pylon = self.ai.structures().filter(lambda x: x.type_id == unit.PYLON and x.is_ready
                                    and x.distance_to(self.ai.main_base_ramp.top_center) > 35)
        if proxy_pylon:
            proxy_pylon = proxy_pylon.furthest_to(self.ai.start_location)
            gates = self.ai.structures({unit.GATEWAY, unit.WARPGATE})
            if not gates or not gates.closer_than(7, proxy_pylon).exists:
                await self.ai.build(unit.GATEWAY, near=proxy_pylon, validate_location=False)
