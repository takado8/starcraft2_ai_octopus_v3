from sc2.unit import UnitTypeId as unit


class BuildQueues:
    STALKER_RUSH = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 30, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, 48, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY,
                    unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    STALKER_BLINKERS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.TWILIGHTCOUNCIL,
                        unit.GATEWAY, unit.GATEWAY, 20, unit.NEXUS,
                        unit.GATEWAY, unit.GATEWAY, 20, unit.NEXUS,
                        unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 30, unit.NEXUS, 45,
                        unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                        unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.NEXUS, unit.NEXUS]

    AIR_ORACLE_CARRIERS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.NEXUS, unit.STARGATE,
                           10, unit.FLEETBEACON, unit.STARGATE, unit.NEXUS, 40, unit.STARGATE, unit.ROBOTICSFACILITY,
                           unit.NEXUS, unit.STARGATE, unit.NEXUS, 120, unit.STARGATE, unit.STARGATE, unit.NEXUS,
                           unit.STARGATE, unit.NEXUS, unit.NEXUS, unit.NEXUS]

    ONE_BASE_ROBO = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.ROBOTICSFACILITY, 16, unit.NEXUS,
                     unit.FORGE,
                     unit.GATEWAY, unit.GATEWAY, 30, unit.NEXUS, unit.GATEWAY, unit.TWILIGHTCOUNCIL, 50, unit.NEXUS,
                     unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, 120, unit.NEXUS, unit.GATEWAY, 140,
                     unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY, unit.GATEWAY,
                     unit.NEXUS]

    COLOSSUS = [unit.GATEWAY, unit.CYBERNETICSCORE,  unit.NEXUS, unit.ROBOTICSFACILITY, 4,
                unit.ROBOTICSBAY, unit.GATEWAY, unit.GATEWAY, 24, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                unit.TWILIGHTCOUNCIL, 50, unit.NEXUS, unit.ROBOTICSFACILITY, 80,
                unit.GATEWAY, unit.GATEWAY,  120,  unit.NEXUS, unit.GATEWAY, 140,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]
