from sc2.unit import UnitTypeId as unit


class BuildQueues:
    STALKER_RUSH = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 30, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.ROBOTICSFACILITY, 48, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY,
                    unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    STALKER_MID = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY,
                     unit.NEXUS, unit.FORGE, unit.GATEWAY,  unit.GATEWAY, 7, unit.TWILIGHTCOUNCIL, unit.FORGE,
                     unit.GATEWAY, unit.GATEWAY, 20, unit.NEXUS, unit.FORGE,
                     unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 30, unit.NEXUS, 45,
                     unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                     unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.NEXUS]

    STALKER_BLINKERS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.TWILIGHTCOUNCIL,
                        unit.GATEWAY, unit.GATEWAY, 20, unit.NEXUS,
                   unit.GATEWAY, unit.GATEWAY, 20, unit.NEXUS,
                   unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, 30, unit.NEXUS, 45,
                   unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                   unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.NEXUS, unit.NEXUS]

    AIR_ORACLE_CARRIERS = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.STARGATE, 4, unit.NEXUS,
                            20, unit.FLEETBEACON, unit.NEXUS, unit.STARGATE, 40,
                           unit.STARGATE, unit.NEXUS, unit.STARGATE, unit.NEXUS, unit.STARGATE, unit.NEXUS,
                           unit.STARGATE, unit.NEXUS, unit.STARGATE, unit.NEXUS, unit.STARGATE, unit.NEXUS]