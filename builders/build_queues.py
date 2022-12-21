from sc2.unit import UnitTypeId as unit


class BuildQueues:
    STALKER_RUSH = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 30, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, 48, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY,
                    unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    ADEPT_DEFENSE = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, 8, unit.GATEWAY, unit.GATEWAY, 30,
                     unit.NEXUS, unit.TWILIGHTCOUNCIL, 35,
                    unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSBAY, 48, unit.NEXUS, unit.TEMPLARARCHIVE,
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
                           unit.NEXUS, unit.FORGE, unit.STARGATE, unit.NEXUS,
                           unit.STARGATE, unit.STARGATE, unit.TWILIGHTCOUNCIL, unit.NEXUS,
                           unit.STARGATE, unit.NEXUS, unit.NEXUS, unit.NEXUS]

    ONE_BASE_ROBO = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.ROBOTICSFACILITY, unit.NEXUS, 16,
                unit.ROBOTICSBAY, unit.GATEWAY, unit.GATEWAY, 24, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                unit.TWILIGHTCOUNCIL, 50, unit.NEXUS, unit.ROBOTICSFACILITY, 80,  unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY,  110,  unit.NEXUS, unit.ROBOTICSFACILITY, unit.GATEWAY, 110, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY,unit.ROBOTICSFACILITY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    COLOSSUS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.NEXUS, unit.ROBOTICSFACILITY, 4,
                unit.ROBOTICSBAY, unit.GATEWAY, unit.GATEWAY, 24, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                unit.TWILIGHTCOUNCIL, 50, unit.NEXUS, unit.ROBOTICSFACILITY, 80, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, 110, unit.NEXUS, unit.ROBOTICSFACILITY, unit.GATEWAY, 110, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                unit.GATEWAY, unit.NEXUS]

    ARCHONS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.TWILIGHTCOUNCIL, unit.NEXUS, 4,
                unit.TEMPLARARCHIVE, unit.GATEWAY, unit.GATEWAY, 14, unit.GATEWAY, unit.NEXUS, unit.GATEWAY,
                 50, unit.NEXUS, unit.ROBOTICSFACILITY, 80, unit.GATEWAY, unit.FORGE,
                unit.GATEWAY, unit.GATEWAY, 120, unit.NEXUS, unit.ROBOTICSFACILITY, unit.GATEWAY, 140, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                unit.GATEWAY, unit.NEXUS]

