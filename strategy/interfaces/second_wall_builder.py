from strategy.interfaces.interfaceABS import InterfaceABS



class SecondWallBuilder(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai
        self.builder_tag = None

    async def execute(self):
        if 120 > self.ai.time > 5:
            if not self.builder_tag or not self.ai.workers.find_by_tag(self.builder_tag):
                mineral_workers = self.ai.workers.filter(lambda x: x.tag in self.ai.strategy.workers_distribution.get_mineral_workers_tags())
                builder = mineral_workers.closest_to(self.ai.main_base_ramp.bottom_center)
                self.builder_tag = builder.tag
            else:
                builder = self.ai.workers.find_by_tag(self.builder_tag)
                if builder:
                    natural_location = min(self.ai.expansion_locations_list, key=lambda x: x.distance_to(
                        self.ai.main_base_ramp.bottom_center)).position
                    if builder.distance_to(natural_location) > 10:
                        builder.move(natural_location)
                    #     builder.hold_position(queue=True)
                    # elif isinstance(builder.order_target, int):
                    #     builder.hold_position()
