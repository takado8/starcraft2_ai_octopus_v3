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
                           unit.STARGATE, unit.NEXUS,unit.NEXUS, unit.NEXUS]

    ONE_BASE_ROBO = [unit.GATEWAY, unit.CYBERNETICSCORE, unit.GATEWAY, unit.ROBOTICSFACILITY, 20,  unit.NEXUS, unit.FORGE,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS, unit.GATEWAY, unit.TWILIGHTCOUNCIL,
                    unit.GATEWAY, unit.NEXUS, unit.ROBOTICSFACILITY, unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS,
                    unit.GATEWAY, unit.GATEWAY, unit.GATEWAY, unit.NEXUS]

    ORACLE_PROXY = [unit.GATEWAY, unit.CYBERNETICSCORE]