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


class UpperWallForge(SpecialBuildingsLocationsABS):
    def __init__(self, ai):
        super().__init__(ai)

    @property
    def locations_dict(self):
        # lower_corner = max(self.ai.main_base_ramp.lower, key=lambda x: self.ai.start_location.distance_to(x))
        natural_position = sorted(self.ai.expansion_locations_list,
                         key=lambda x: self.ai.main_base_ramp.bottom_center.distance_to(x))[0]
        pylon_position = natural_position.towards(self.ai.game_info.map_center, 5)
        photon_cannons = pylon_position.towards(natural_position, 3).random_on_distance(3)

        return {unit.PYLON: [self.ai.main_base_ramp.protoss_wall_pylon,
                             pylon_position],
                unit.FORGE: [self.ai.main_base_ramp.protoss_wall_buildings[1]],
                unit.GATEWAY: [self.ai.main_base_ramp.protoss_wall_buildings[0]],
                unit.PHOTONCANNON: [photon_cannons, photon_cannons
                                    ,photon_cannons],
                unit.SHIELDBATTERY: [self.ai.main_base_ramp.protoss_wall_buildings[1].towards(
                    self.ai.main_base_ramp.protoss_wall_buildings[0], -2.5)]
                }