from sc2.unit import UnitTypeId as unit
from sc2.ids.effect_id import EffectId as effect
from sc2.ids.ability_id import AbilityId as ability

ARMY_IDS = {unit.ADEPT, unit.STALKER, unit.ZEALOT, unit.SENTRY, unit.OBSERVER, unit.IMMORTAL, unit.ARCHON,
            unit.HIGHTEMPLAR, unit.DARKTEMPLAR, unit.WARPPRISM, unit.VOIDRAY, unit.CARRIER, unit.COLOSSUS,
            unit.TEMPEST, unit.DISRUPTOR, unit.PHOENIX, unit.MOTHERSHIP}

SPECIAL_UNITS_IDS = {unit.ORACLE}

BASES_IDS = {unit.NEXUS, unit.COMMANDCENTER, unit.COMMANDCENTERFLYING, unit.ORBITALCOMMAND,
             unit.ORBITALCOMMANDFLYING,
             unit.PLANETARYFORTRESS, unit.HIVE, unit.HATCHERY, unit.LAIR}

UNITS_TO_IGNORE = {unit.LARVA, unit.EGG, unit.AUTOTURRET}

WORKERS_IDS = {unit.SCV, unit.PROBE, unit.DRONE, unit.MULE}

ANTI_AIR_IDS = {unit.MISSILETURRET, unit.PHOTONCANNON, unit.WIDOWMINE, unit.SPORECRAWLER}

AIR_PRIORITY_UNITS = {unit.VOIDRAY, unit.WIDOWMINE, unit.BUNKER, unit.VIKING, unit.PHOENIX, unit.THOR, unit.INFESTOR,
                      unit.QUEEN, unit.BATTLECRUISER, unit.CARRIER, unit.TEMPEST, unit.CORRUPTOR, unit.MUTALISK, unit.MEDIVAC,
                      unit.RAVEN, unit.LIBERATOR}

GROUND_AOE_IDS = {effect.RAVAGERCORROSIVEBILECP, effect.PSISTORMPERSISTENT, effect.NUKEPERSISTENT,
                  effect.LIBERATORTARGETMORPHDELAYPERSISTENT}

AIR_AOE_IDS = {effect.RAVAGERCORROSIVEBILECP, effect.PSISTORMPERSISTENT, effect.NUKEPERSISTENT}

BUILDING_OF_ORIGIN_DICT = {unit.ZEALOT: unit.GATEWAY, unit.STALKER: unit.GATEWAY, unit.ADEPT: unit.GATEWAY,
                           unit.SENTRY: unit.GATEWAY, unit.DARKTEMPLAR: unit.GATEWAY, unit.HIGHTEMPLAR: unit.GATEWAY,
                           unit.OBSERVER: unit.ROBOTICSFACILITY, unit.IMMORTAL: unit.ROBOTICSFACILITY,
                           unit.WARPPRISM: unit.ROBOTICSFACILITY, unit.COLOSSUS: unit.ROBOTICSFACILITY,
                           unit.DISRUPTOR: unit.ROBOTICSFACILITY,
                           unit.ORACLE: unit.STARGATE, unit.VOIDRAY: unit.STARGATE, unit.PHOENIX: unit.STARGATE,
                           unit.TEMPEST: unit.STARGATE, unit.CARRIER: unit.STARGATE}

ABILITIES_TIME = {ability.STARGATETRAIN_CARRIER: 64, ability.STARGATETRAIN_TEMPEST: 43,
                  ability.STARGATETRAIN_ORACLE: 37, ability.RESEARCH_WARPGATE: 150, ability.RESEARCH_BLINK: 121,
                  ability.RESEARCH_CHARGE: 100, ability.ROBOTICSFACILITYTRAIN_OBSERVER: 1,
                  ability.ROBOTICSFACILITYTRAIN_IMMORTAL: 39, ability.RESEARCH_ADEPTRESONATINGGLAIVES: 100,
                  ability.RESEARCH_EXTENDEDTHERMALLANCE: 100, ability.NEXUSTRAIN_PROBE: 1500
                  }

BURROWING_UNITS_IDS = {unit.ROACH, unit.ROACHBURROWED, unit.LURKER, unit.LURKERBURROWED,
                       unit.WIDOWMINE, unit.WIDOWMINEBURROWED}

STRUCTURES_RADIUS = {
    unit.PYLON: 1.125,
    unit.GATEWAY: 1.8125,
    unit.WARPGATE: 1.8125,
    unit.ASSIMILATOR: 1.6875,
    unit.FORGE: 1.8125,
    unit.CYBERNETICSCORE: 1.8125,
    unit.NEXUS: 2.75,
    unit.PHOTONCANNON: 1.125,
    unit.ROBOTICSFACILITY: 1.8125,
    unit.STARGATE: 1.8125,
    unit.TWILIGHTCOUNCIL: 1.8125,
    unit.ROBOTICSBAY: 1.8125,
    unit.FLEETBEACON: 1.8125,
    unit.TEMPLARARCHIVE: 1.8125,
    unit.DARKSHRINE: 1.5,
    unit.SHIELDBATTERY: 1.125,
}


GAS_VALUE = 1