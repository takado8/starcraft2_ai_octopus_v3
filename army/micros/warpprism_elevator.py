from army.micros.microABS import MicroABS
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit


class WarpPrismElevatorMicro(MicroABS):
    def __init__(self, ai):
        super().__init__("WarpPrismMicro", ai)
        self.lifted_tags = set()


    async def do_micro(self, division):
        prisms = division.get_units(self.ai.iteration, unit.WARPPRISM)
        workers_tags = self.ai.strategy.workers_distribution.get_distant_mining_workers_tags()
        workers = self.ai.workers.filter(lambda x: x.tag in workers_tags and x.tag not in self.lifted_tags)

        for prism in prisms:
            self.ai.army.remove(prism)
            abilities = await self.ai.get_available_abilities(prism)
            for worker in workers:
                abilities = await self.ai.get_available_abilities(prism)
                if ability.LOAD_WARPPRISM in abilities and workers:
                    prism(ability.LOAD_WARPPRISM, worker, queue=True)
                    self.lifted_tags.add(worker.tag)
                else:
                    self.unload(prism)

            if not workers or all({worker.tag in self.lifted_tags for worker in workers}) or\
                    ability.LOAD_WARPPRISM not in abilities:
                self.unload(prism)

        return 1

    def unload(self, prism):
        spot = self.ai.main_base_ramp.bottom_center.towards(
            self.ai.main_base_ramp.top_center, -5)
        if not self.ai.enemy_units.exists or not self.ai.enemy_units.closer_than(20, spot):
            prism(ability.UNLOADALLAT_WARPPRISM, spot)