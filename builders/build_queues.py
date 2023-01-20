from sc2.unit import UnitTypeId as unit


class BuildQueues:
    STALKER_RUSH = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 30, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, 48, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY,
                    unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    ADEPT_DEFENSE = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.SHIELDBATTERY, 4,
                     unit.GATEWAY, unit.GATEWAY, unit.TWILIGHTCOUNCIL, 16, unit.NEXUS, unit.TEMPLARARCHIVE,
                    unit.GATEWAY, unit.GATEWAY, unit.NEXUS, 30, unit.DARKSHRINE, unit.FORGE,
                     unit.GATEWAY, unit.NEXUS, unit.GATEWAY, 40, unit.FORGE,
                    unit.GATEWAY, unit.GATEWAY, unit.NEXUS,unit.ROBOTICSFACILITY, unit.GATEWAY,
                     unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
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

    ONE_BASE_ROBO = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.ROBOTICSFACILITY,
                     unit.SHIELDBATTERY, 16, unit.NEXUS,
                     unit.ROBOTICSBAY, unit.GATEWAY, unit.GATEWAY, 32, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                unit.TWILIGHTCOUNCIL, unit.NEXUS, 50, unit.TEMPLARARCHIVE, unit.ROBOTICSFACILITY, 60, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.FORGE, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                unit.GATEWAY, unit.NEXUS]

    COLOSSUS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.NEXUS, unit.ROBOTICSFACILITY, 6,
                unit.ROBOTICSBAY, 12, unit.GATEWAY, 24, unit.NEXUS, unit.TWILIGHTCOUNCIL, unit.GATEWAY,
                unit.TEMPLARARCHIVE, unit.NEXUS, 40, unit.FORGE, unit.GATEWAY, 60,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.FORGE, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                unit.GATEWAY, unit.NEXUS]

    ARCHONS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.TWILIGHTCOUNCIL, unit.NEXUS, 4,
                unit.TEMPLARARCHIVE, unit.GATEWAY, unit.GATEWAY, 14, unit.GATEWAY, unit.NEXUS, unit.GATEWAY,
                 50, unit.NEXUS, unit.ROBOTICSFACILITY, 80, unit.GATEWAY, unit.FORGE,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                unit.GATEWAY, unit.NEXUS]

    DTS = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.SHIELDBATTERY, unit.TWILIGHTCOUNCIL, unit.DARKSHRINE, 4,
           unit.NEXUS, 16,unit.ROBOTICSFACILITY, unit.TEMPLARARCHIVE, unit.GATEWAY,  unit.NEXUS, unit.GATEWAY,
                    unit.FORGE,
                unit.GATEWAY, unit.NEXUS, 50, unit.GATEWAY, unit.ROBOTICSFACILITY, 60, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.FORGE, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                unit.GATEWAY, unit.NEXUS]