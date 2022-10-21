from strategy.manager import Strategy


class TwoBaseColossus(Strategy):
    def __init__(self, ai):
        super().__init__(ai)
        self.type = 'macro'
        self.name = '2b_colossus'

    # =======================================================  Builders
    async def gate_build(self):
        await self._gate_builder.three_standard()

    def assimilator_build(self):
        self._assimilator_builder.more_vespene()

    async def stargate_build(self):
        await self._stargate_builder.none()

    async def forge_build(self):
        await self._forge_builder.none()

    async def twilight_build(self):
        await self._twilight_builder.none()

    async def templar_archives_build(self):
        await self._templar_archives_builder.none()

    async def pylon_first_build(self):
        await self._pylon_builder.first_and_next_standard()

    async def pylon_next_build(self):
        await self._pylon_builder.none()

    async def proxy(self):
        await self._pylon_builder.none()

    async def cybernetics_build(self):
        await self._cybernetics_builder.standard_old()

    async def robotics_build(self):
        await self._robotics_builder.double()

    async def robotics_bay_build(self):
        await self._robotics_bay_builder.standard_old()

    async def cannons_build(self):
        await self._cannon_builder.double_per_nex()

    async def expand(self):
        await self._expander.two_bases()

    # =======================================================  Upgraders

    def cybernetics_upgrades(self):
        self._cybernetics_upgrader.standard_old()

    def forge_upgrades(self):
        self._forge_upgrader.standard_old()

    async def twilight_upgrades(self):
        await self._twilight_upgrader.none()

    async def templar_archives_upgrades(self):
        pass

    async def fleet_beacon_upgrades(self):
        pass


    # =======================================================  Trainers

    def nexus_train(self):
        self._nexus_trainer.probes_standard()

    def gate_train(self):
        self._gate_trainer.zealots()

    def stargate_train(self):
        self._stargate_trainer.none()

    def robotics_train(self):
        self._robotics_trainer.colossus()

    async def warpgate_train(self):
        await self._warpgate_trainer.two_base_colossus()

    # =======================================================  Army

    async def micro(self):
        await self._micro.new()

    async def movements(self):
        await self._movements.attack_formation_brand_new_newest_thee_most_new_shit_in_whole_wide_world()


    # ======================================================= Conditions

    def attack_condition(self):
        return self._condition_attack.colossus()

    def counter_attack_condition(self):
        return self._condition_attack.counter_attack()

    def retreat_condition(self):
        return self._condition_retreat.two_base()

    async def transformation(self):
        await self._condition_transform.two_base_colossus()
