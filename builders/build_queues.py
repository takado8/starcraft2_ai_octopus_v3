from sc2.unit import UnitTypeId as unit


class BuildQueues:
    STALKER_RUSH = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 32, unit.NEXUS,
                    unit.ROBOTICSFACILITY, unit.TWILIGHTCOUNCIL, unit.TEMPLARARCHIVE, 30, unit.NEXUS, unit.FORGE,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                    unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.ROBOTICSFACILITY,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    STALKER_DEFENSE = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.ROBOTICSFACILITY, unit.GATEWAY,
                    unit.GATEWAY, 32, unit.NEXUS,
                    unit.ROBOTICSBAY, unit.FORGE,unit.TWILIGHTCOUNCIL, 40, unit.NEXUS, unit.ROBOTICSFACILITY,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY,50, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                    unit.GATEWAY,50, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.ROBOTICSFACILITY,
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
                           10, unit.FLEETBEACON, unit.STARGATE, unit.NEXUS, 30, unit.STARGATE,
                           unit.NEXUS,unit.ROBOTICSFACILITY, unit.FORGE, unit.STARGATE, unit.TWILIGHTCOUNCIL, unit.NEXUS,
                           unit.STARGATE, unit.STARGATE, unit.NEXUS,
                           unit.STARGATE, unit.NEXUS, unit.NEXUS, unit.NEXUS]

    SKYTOSS_DEFENSE = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.SHIELDBATTERY, 8, unit.STARGATE,
                       unit.FLEETBEACON, unit.GATEWAY,
                        20, unit.NEXUS,  unit.ROBOTICSFACILITY, unit.GATEWAY,unit.FORGE, unit.GATEWAY,
               40, unit.NEXUS, unit.TWILIGHTCOUNCIL, unit.STARGATE, unit.ROBOTICSFACILITY, unit.ROBOTICSBAY, 60,
               unit.NEXUS, unit.STARGATE, unit.NEXUS, 80,
               unit.STARGATE, unit.STARGATE, unit.NEXUS, unit.GATEWAY,  unit.GATEWAY,
               unit.STARGATE,unit.ROBOTICSFACILITY, unit.NEXUS, unit.NEXUS, unit.NEXUS]

    ORACLE_DEFENSE = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.NEXUS, unit.STARGATE, unit.SHIELDBATTERY,
                      10, unit.FLEETBEACON, unit.STARGATE, unit.NEXUS, 30, unit.STARGATE,
                      unit.NEXUS, unit.ROBOTICSFACILITY, unit.FORGE, unit.STARGATE, unit.TWILIGHTCOUNCIL, unit.NEXUS,
                      unit.STARGATE, unit.STARGATE, unit.NEXUS,
                      unit.STARGATE, unit.NEXUS, unit.NEXUS, unit.NEXUS]

    COLOSSUS = [unit.NEXUS, unit.GATEWAY, unit.CYBERNETICSCORE, unit.ROBOTICSFACILITY, unit.ROBOTICSBAY, 12,
                            unit.NEXUS,unit.ROBOTICSFACILITY, unit.GATEWAY, unit.FORGE, unit.NEXUS,unit.GATEWAY,
                            unit.GATEWAY, 60, unit.STARGATE, unit.FLEETBEACON,
                            unit.ROBOTICSFACILITY, unit.GATEWAY, 80,
                           unit.NEXUS,  unit.STARGATE, unit.TWILIGHTCOUNCIL, unit.NEXUS, 80,
                           unit.STARGATE, unit.STARGATE, unit.NEXUS,unit.ROBOTICSFACILITY,
                           unit.STARGATE, unit.NEXUS, unit.NEXUS, unit.NEXUS]

    ROBO_DEFENSE = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.SHIELDBATTERY, unit.ROBOTICSFACILITY,
                    unit.GATEWAY, 20,  unit.NEXUS, unit.ROBOTICSBAY, unit.GATEWAY, unit.NEXUS,
                    unit.FORGE, unit.TWILIGHTCOUNCIL,
                    unit.GATEWAY,  42, unit.NEXUS, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY, 56,unit.NEXUS,
                    unit.GATEWAY, 60, unit.ROBOTICSFACILITY, unit.NEXUS, unit.NEXUS, 70,
                    unit.NEXUS, unit.ROBOTICSFACILITY, unit.NEXUS, unit.NEXUS, unit.NEXUS]

    DTS = [unit.PYLON, unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.SHIELDBATTERY, unit.TWILIGHTCOUNCIL,
           unit.DARKSHRINE, 4,
           unit.NEXUS, 16, unit.ROBOTICSFACILITY, unit.TEMPLARARCHIVE, unit.GATEWAY, unit.NEXUS, unit.GATEWAY,
           unit.FORGE,
           unit.GATEWAY, unit.NEXUS, 50, unit.GATEWAY, unit.ROBOTICSBAY, 60, unit.GATEWAY,
           unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.FORGE, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY,
           unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
           unit.GATEWAY, unit.NEXUS]

    CANNON_DEFENSE = [unit.PYLON, unit.PYLON, unit.FORGE, unit.GATEWAY, unit.PHOTONCANNON,
                      unit.PHOTONCANNON, unit.CYBERNETICSCORE, 6, unit.NEXUS, unit.SHIELDBATTERY, unit.ROBOTICSFACILITY,
                      15, unit.GATEWAY,
                      unit.GATEWAY, 20,  unit.SHIELDBATTERY,unit.TWILIGHTCOUNCIL,
                      32,unit.NEXUS, unit.ROBOTICSBAY, unit.STARGATE,  unit.FLEETBEACON,
                     unit.NEXUS, unit.STARGATE, unit.STARGATE, unit.NEXUS,
                      unit.GATEWAY, unit.GATEWAY, unit.STARGATE, unit.NEXUS,
                      unit.STARGATE, unit.NEXUS, unit.NEXUS, unit.NEXUS, unit.GATEWAY,
                      unit.GATEWAY, unit.ROBOTICSFACILITY,unit.NEXUS,
                           unit.GATEWAY,
                           unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                           unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    CANNON_RUSH_DEFENSE = [unit.PYLON, unit.FORGE, unit.GATEWAY, unit.PYLON, unit.PHOTONCANNON,
                      unit.PHOTONCANNON, unit.PHOTONCANNON, unit.PHOTONCANNON, unit.CYBERNETICSCORE, 6,
                      unit.GATEWAY, unit.NEXUS,unit.GATEWAY, unit.NEXUS, unit.ROBOTICSFACILITY, unit.TWILIGHTCOUNCIL,
                      unit.TEMPLARARCHIVE, unit.GATEWAY, unit.NEXUS, 20, unit.FORGE, unit.GATEWAY,
                      unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, 30, unit.FORGE,
                      unit.GATEWAY, unit.GATEWAY, unit.NEXUS,  unit.GATEWAY,
                      unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.ROBOTICSBAY,
                      unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    PROXY_MIX = [unit.PYLON, unit.GATEWAY, unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.GATEWAY, 16, unit.NEXUS,
                    unit.ROBOTICSFACILITY, unit.TWILIGHTCOUNCIL, unit.TEMPLARARCHIVE, 30, unit.NEXUS, unit.FORGE,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.FORGE,
                    unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.ROBOTICSFACILITY,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]