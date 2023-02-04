from sc2.unit import UnitTypeId as unit


class BuildQueues:
    STALKER_RUSH = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 32, unit.NEXUS,
                    unit.ROBOTICSFACILITY, unit.TWILIGHTCOUNCIL, unit.TEMPLARARCHIVE, 30, unit.NEXUS, unit.FORGE,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                    unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.ROBOTICSFACILITY,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    ADEPT_RUSH = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 32,
                  unit.NEXUS,
                  unit.ROBOTICSFACILITY, unit.TWILIGHTCOUNCIL, unit.TEMPLARARCHIVE, 30, unit.NEXUS, unit.FORGE,
                  unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                  unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.ROBOTICSFACILITY,
                  unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    ADEPT_DEFENSE = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.SHIELDBATTERY, 6,
                     unit.GATEWAY, unit.GATEWAY, 12,  unit.GATEWAY, unit.NEXUS, unit.TWILIGHTCOUNCIL,
                     unit.TEMPLARARCHIVE, unit.GATEWAY, unit.NEXUS, 26, unit.FORGE, unit.GATEWAY,
                     unit.GATEWAY,unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY,  30, unit.FORGE,
                     unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.ROBOTICSFACILITY, unit.GATEWAY,
                     unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.ROBOTICSBAY,
                     unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    ZEALOT_RUSH_DEFENSE = [unit.PYLON, unit.GATEWAY, unit.GATEWAY, unit.CYBERNETICSCORE, 4, unit.SHIELDBATTERY, 6,
                           unit.GATEWAY, unit.GATEWAY, 8, unit.NEXUS, unit.TWILIGHTCOUNCIL,
                           unit.TEMPLARARCHIVE, unit.GATEWAY, unit.NEXUS, 20, unit.FORGE, unit.GATEWAY,
                           unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, 30, unit.FORGE,
                           unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.ROBOTICSFACILITY, unit.GATEWAY,
                           unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.ROBOTICSBAY,
                           unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    AIR_ORACLE_CARRIERS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.NEXUS, unit.STARGATE,
                           10, unit.FLEETBEACON, unit.STARGATE, unit.NEXUS, 40, unit.STARGATE, unit.ROBOTICSFACILITY,
                           unit.NEXUS, unit.FORGE, unit.STARGATE, unit.NEXUS,
                           unit.STARGATE, unit.STARGATE, unit.TWILIGHTCOUNCIL, unit.NEXUS,
                           unit.STARGATE, unit.NEXUS, unit.NEXUS, unit.NEXUS]

    SKYTOSS = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.NEXUS, unit.STARGATE, unit.SHIELDBATTERY,
                           10, unit.FLEETBEACON, unit.STARGATE, unit.NEXUS, 40, unit.STARGATE, unit.ROBOTICSFACILITY,
                           unit.NEXUS, unit.FORGE, unit.STARGATE, unit.NEXUS,
                           unit.STARGATE, unit.STARGATE, unit.NEXUS,
                           unit.STARGATE, unit.NEXUS, unit.NEXUS, unit.NEXUS]


    ONE_BASE_ROBO = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.ROBOTICSFACILITY,
                     unit.SHIELDBATTERY, 16, unit.NEXUS,
                     unit.ROBOTICSBAY, unit.GATEWAY, unit.GATEWAY, 32, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                     unit.TWILIGHTCOUNCIL, unit.NEXUS, 50, unit.TEMPLARARCHIVE, unit.ROBOTICSFACILITY, 60, unit.GATEWAY,
                     unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.FORGE, unit.ROBOTICSFACILITY, unit.GATEWAY,
                     unit.GATEWAY,
                     unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                     unit.GATEWAY, unit.NEXUS]

    COLOSSUS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.NEXUS, unit.ROBOTICSFACILITY, 6,
                unit.ROBOTICSBAY, 12, unit.GATEWAY, 20, unit.NEXUS, unit.TWILIGHTCOUNCIL, unit.GATEWAY,
                unit.TEMPLARARCHIVE, unit.FORGE, unit.NEXUS, 40, unit.GATEWAY, 60,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.FORGE, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                unit.GATEWAY, unit.NEXUS]

    RAPID_EXPANSION = [unit.NEXUS, unit.GATEWAY, unit.CYBERNETICSCORE, unit.NEXUS, unit.ROBOTICSFACILITY, unit.NEXUS,
                unit.ROBOTICSBAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.TWILIGHTCOUNCIL,unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                unit.TEMPLARARCHIVE, unit.FORGE, unit.NEXUS, unit.GATEWAY, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.FORGE, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY,
                unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                unit.GATEWAY, unit.NEXUS]

    DTS = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.SHIELDBATTERY, unit.TWILIGHTCOUNCIL,
           unit.DARKSHRINE, 4,
           unit.NEXUS, 16, unit.ROBOTICSFACILITY, unit.TEMPLARARCHIVE, unit.GATEWAY, unit.NEXUS, unit.GATEWAY,
           unit.FORGE,
           unit.GATEWAY, unit.NEXUS, 50, unit.GATEWAY, unit.ROBOTICSFACILITY, 60, unit.GATEWAY,
           unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.FORGE, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY,
           unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
           unit.GATEWAY, unit.NEXUS]
