from sc2.unit import UnitTypeId as unit
from sc2.ids.effect_id import EffectId as effect


ARMY_IDS = {unit.ADEPT, unit.STALKER, unit.ZEALOT, unit.SENTRY, unit.OBSERVER, unit.IMMORTAL, unit.ARCHON,
            unit.HIGHTEMPLAR, unit.DARKTEMPLAR, unit.WARPPRISM, unit.VOIDRAY, unit.CARRIER, unit.COLOSSUS,
            unit.TEMPEST}

SPECIAL_UNITS_IDS = {unit.ORACLE}

BASES_IDS = {unit.NEXUS, unit.COMMANDCENTER, unit.COMMANDCENTERFLYING, unit.ORBITALCOMMAND,
             unit.ORBITALCOMMANDFLYING,
             unit.PLANETARYFORTRESS, unit.HIVE, unit.HATCHERY, unit.LAIR}

UNITS_TO_IGNORE = {unit.LARVA, unit.EGG, unit.INTERCEPTOR}

WORKERS_IDS = {unit.SCV, unit.PROBE, unit.DRONE, unit.MULE}

ANTI_AIR_IDS = {unit.MISSILETURRET, unit.PHOTONCANNON, unit.WIDOWMINE, unit.SPORECRAWLER}

AIR_PRIORITY_UNITS = {unit.VOIDRAY,unit.WIDOWMINE, unit.BUNKER, unit.VIKING, unit.PHOENIX, unit.THOR,
                      unit.QUEEN, unit.BATTLECRUISER}

AOE_IDS = {effect.RAVAGERCORROSIVEBILECP, effect.PSISTORMPERSISTENT, effect.NUKEPERSISTENT,
                    effect.LIBERATORTARGETMORPHDELAYPERSISTENT}

BUILDING_OF_ORIGIN_DICT = {unit.ZEALOT: unit.GATEWAY, unit.STALKER: unit.GATEWAY, unit.ADEPT: unit.GATEWAY,
                           unit.SENTRY: unit.GATEWAY, unit.DARKTEMPLAR: unit.GATEWAY, unit.HIGHTEMPLAR: unit.GATEWAY,
                           unit.OBSERVER: unit.ROBOTICSFACILITY, unit.IMMORTAL: unit.ROBOTICSFACILITY,
                           unit.COLOSSUS: unit.ROBOTICSFACILITY, unit.DISRUPTOR: unit.ROBOTICSFACILITY,
                           unit.ORACLE: unit.STARGATE, unit.VOIDRAY: unit.STARGATE, unit.PHOENIX: unit.STARGATE,
                           unit.TEMPEST: unit.STARGATE, unit.CARRIER: unit.STARGATE}