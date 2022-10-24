from sc2.unit import UnitTypeId as unit


class BuildQueues:
    STALKER_RUSH = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 30, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, 48, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY,
                    unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    STALKER_MID = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY,
                     unit.NEXUS, unit.GATEWAY, unit.FORGE, unit.GATEWAY, 12,unit.TWILIGHTCOUNCIL, unit.FORGE,
                     unit.GATEWAY, unit.GATEWAY, 35, unit.NEXUS, unit.FORGE,
                     unit.GATEWAY, unit.GATEWAY,unit.GATEWAY, unit.GATEWAY, 40, unit.NEXUS,
                     unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                     unit.GATEWAY, unit.NEXUS]

    STALKER_POWER = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY,
                     unit.NEXUS, unit.GATEWAY,  unit.FORGE, unit.GATEWAY, 12, unit.TWILIGHTCOUNCIL,
                     unit.GATEWAY, unit.GATEWAY, 35, unit.NEXUS,
                     unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, 40, unit.GATEWAY, unit.NEXUS,
                     unit.GATEWAY, unit.ROBOTICSFACILITY,
                     unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                     unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]
