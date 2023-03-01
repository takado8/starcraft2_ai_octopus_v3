from sc2.unit import UnitTypeId as unit


class SpecialBuildingsLocationsABS:
    def __init__(self, ai):
        self.ai = ai

    @property
    def locations_dict(self):
        raise NotImplementedError


class UpperWall(SpecialBuildingsLocationsABS):
    def __init__(self, ai):
        super().__init__(ai)

    @property
    def locations_dict(self):
        return {unit.PYLON: [self.ai.main_base_ramp.protoss_wall_pylon],
                unit.GATEWAY: [self.ai.main_base_ramp.protoss_wall_buildings[0]],
                unit.CYBERNETICSCORE: [self.ai.main_base_ramp.protoss_wall_buildings[1]],
                unit.SHIELDBATTERY: [self.ai.main_base_ramp.protoss_wall_buildings[1].towards(
                    self.ai.main_base_ramp.protoss_wall_buildings[0], -2.5)]
                }


class UpperWallGates(SpecialBuildingsLocationsABS):
    def __init__(self, ai):
        super().__init__(ai)

    @property
    def locations_dict(self):
        return {unit.PYLON: [self.ai.main_base_ramp.protoss_wall_pylon],
                unit.GATEWAY: [self.ai.main_base_ramp.protoss_wall_buildings[0],
                               self.ai.main_base_ramp.protoss_wall_buildings[1]],
                unit.SHIELDBATTERY: [self.ai.main_base_ramp.protoss_wall_buildings[1].towards(
                    self.ai.main_base_ramp.protoss_wall_buildings[0], -2.5)]
                }


class UpperWallLockdown(SpecialBuildingsLocationsABS):
    def __init__(self, ai):
        super().__init__(ai)

    @property
    def locations_dict(self):
        return {unit.PYLON: [self.ai.main_base_ramp.protoss_wall_warpin],
                unit.GATEWAY: [self.ai.main_base_ramp.protoss_wall_buildings[0],
                               self.ai.main_base_ramp.protoss_wall_buildings[1]],
                unit.SHIELDBATTERY: [self.ai.main_base_ramp.protoss_wall_buildings[1].towards(
                    self.ai.main_base_ramp.protoss_wall_buildings[0], -2.5)]
                }