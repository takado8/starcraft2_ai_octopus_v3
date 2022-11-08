from sc2.unit import UnitTypeId as unit


class UnitsTrainingDicts:
    STALKER_RUSH = {unit.ZEALOT: 0, unit.ADEPT: 0, unit.STALKER: 80, unit.IMMORTAL: 10,
                     unit.ARCHON: 0, unit.SENTRY: 0}

    STALKER_MID = {unit.ZEALOT: 0, unit.ADEPT: 0, unit.STALKER: 70, unit.IMMORTAL: 0,
                    unit.ARCHON: 0, unit.SENTRY: 0}

    STALKER_POWER = {unit.ZEALOT: 12, unit.ADEPT: 0, unit.STALKER: 40, unit.IMMORTAL: 10,
                   unit.ARCHON: 0, unit.SENTRY: 3}

    AIR_ORACLE_CARRIERS = {unit.ZEALOT: 10, unit.STALKER: 0, unit.ORACLE: 1, unit.CARRIER: 8,
                           unit.TEMPEST: 8, unit.VOIDRAY: 3, unit.ADEPT: 0, unit.ARCHON: 0, unit.SENTRY: 1,
                           unit.IMMORTAL: 0}