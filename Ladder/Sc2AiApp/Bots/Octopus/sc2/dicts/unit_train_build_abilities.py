# THIS FILE WAS AUTOMATICALLY GENERATED BY "generate_dicts_from_data_json.py" DO NOT CHANGE MANUALLY!
# ANY CHANGE WILL BE OVERWRITTEN

from ..ids.unit_typeid import UnitTypeId
from ..ids.ability_id import AbilityId
from ..ids.upgrade_id import UpgradeId

# from ..ids.buff_id import BuffId
# from ..ids.effect_id import EffectId

from typing import Dict, Set, Union

TRAIN_INFO: Dict[
    UnitTypeId, Dict[UnitTypeId, Dict[str, Union[AbilityId, bool, UnitTypeId]]]
] = {
    UnitTypeId.BARRACKS: {
        UnitTypeId.GHOST: {
            "ability": AbilityId.BARRACKSTRAIN_GHOST,
            "requires_techlab": True,
            "requires_tech_building": UnitTypeId.GHOSTACADEMY,
        },
        UnitTypeId.MARAUDER: {
            "ability": AbilityId.BARRACKSTRAIN_MARAUDER,
            "requires_techlab": True,
        },
        UnitTypeId.MARINE: {"ability": AbilityId.BARRACKSTRAIN_MARINE},
        UnitTypeId.REAPER: {"ability": AbilityId.BARRACKSTRAIN_REAPER},
    },
    UnitTypeId.COMMANDCENTER: {
        UnitTypeId.SCV: {"ability": AbilityId.COMMANDCENTERTRAIN_SCV}
    },
    UnitTypeId.CORRUPTOR: {
        UnitTypeId.BROODLORD: {
            "ability": AbilityId.MORPHTOBROODLORD_BROODLORD,
            "requires_tech_building": UnitTypeId.GREATERSPIRE,
        }
    },
    UnitTypeId.CREEPTUMOR: {
        UnitTypeId.CREEPTUMOR: {
            "ability": AbilityId.BUILD_CREEPTUMOR_TUMOR,
            "requires_placement_position": True,
        }
    },
    UnitTypeId.CREEPTUMORBURROWED: {
        UnitTypeId.CREEPTUMOR: {
            "ability": AbilityId.BUILD_CREEPTUMOR,
            "requires_placement_position": True,
        }
    },
    UnitTypeId.CREEPTUMORQUEEN: {
        UnitTypeId.CREEPTUMOR: {
            "ability": AbilityId.BUILD_CREEPTUMOR_TUMOR,
            "requires_placement_position": True,
        }
    },
    UnitTypeId.DRONE: {
        UnitTypeId.BANELINGNEST: {
            "ability": AbilityId.ZERGBUILD_BANELINGNEST,
            "requires_tech_building": UnitTypeId.SPAWNINGPOOL,
            "requires_placement_position": True,
        },
        UnitTypeId.EVOLUTIONCHAMBER: {
            "ability": AbilityId.ZERGBUILD_EVOLUTIONCHAMBER,
            "requires_tech_building": UnitTypeId.HATCHERY,
            "requires_placement_position": True,
        },
        UnitTypeId.EXTRACTOR: {"ability": AbilityId.ZERGBUILD_EXTRACTOR},
        UnitTypeId.HATCHERY: {
            "ability": AbilityId.ZERGBUILD_HATCHERY,
            "requires_placement_position": True,
        },
        UnitTypeId.HYDRALISKDEN: {
            "ability": AbilityId.ZERGBUILD_HYDRALISKDEN,
            "requires_tech_building": UnitTypeId.LAIR,
            "requires_placement_position": True,
        },
        UnitTypeId.INFESTATIONPIT: {
            "ability": AbilityId.ZERGBUILD_INFESTATIONPIT,
            "requires_tech_building": UnitTypeId.LAIR,
            "requires_placement_position": True,
        },
        UnitTypeId.LURKERDENMP: {
            "ability": AbilityId.BUILD_LURKERDEN,
            "requires_tech_building": UnitTypeId.LAIR,
            "requires_placement_position": True,
        },
        UnitTypeId.NYDUSNETWORK: {
            "ability": AbilityId.ZERGBUILD_NYDUSNETWORK,
            "requires_tech_building": UnitTypeId.LAIR,
            "requires_placement_position": True,
        },
        UnitTypeId.ROACHWARREN: {
            "ability": AbilityId.ZERGBUILD_ROACHWARREN,
            "requires_tech_building": UnitTypeId.SPAWNINGPOOL,
            "requires_placement_position": True,
        },
        UnitTypeId.SPAWNINGPOOL: {
            "ability": AbilityId.ZERGBUILD_SPAWNINGPOOL,
            "requires_tech_building": UnitTypeId.HATCHERY,
            "requires_placement_position": True,
        },
        UnitTypeId.SPINECRAWLER: {
            "ability": AbilityId.ZERGBUILD_SPINECRAWLER,
            "requires_tech_building": UnitTypeId.SPAWNINGPOOL,
            "requires_placement_position": True,
        },
        UnitTypeId.SPIRE: {
            "ability": AbilityId.ZERGBUILD_SPIRE,
            "requires_tech_building": UnitTypeId.LAIR,
            "requires_placement_position": True,
        },
        UnitTypeId.SPORECRAWLER: {
            "ability": AbilityId.ZERGBUILD_SPORECRAWLER,
            "requires_tech_building": UnitTypeId.EVOLUTIONCHAMBER,
            "requires_placement_position": True,
        },
        UnitTypeId.ULTRALISKCAVERN: {
            "ability": AbilityId.ZERGBUILD_ULTRALISKCAVERN,
            "requires_tech_building": UnitTypeId.HIVE,
            "requires_placement_position": True,
        },
    },
    UnitTypeId.FACTORY: {
        UnitTypeId.CYCLONE: {
            "ability": AbilityId.TRAIN_CYCLONE,
            "requires_techlab": True,
        },
        UnitTypeId.HELLION: {"ability": AbilityId.FACTORYTRAIN_HELLION},
        UnitTypeId.HELLIONTANK: {
            "ability": AbilityId.TRAIN_HELLBAT,
            "requires_tech_building": UnitTypeId.ARMORY,
        },
        UnitTypeId.SIEGETANK: {
            "ability": AbilityId.FACTORYTRAIN_SIEGETANK,
            "requires_techlab": True,
        },
        UnitTypeId.THOR: {
            "ability": AbilityId.FACTORYTRAIN_THOR,
            "requires_techlab": True,
            "requires_tech_building": UnitTypeId.ARMORY,
        },
        UnitTypeId.WIDOWMINE: {"ability": AbilityId.FACTORYTRAIN_WIDOWMINE},
    },
    UnitTypeId.GATEWAY: {
        UnitTypeId.ADEPT: {
            "ability": AbilityId.TRAIN_ADEPT,
            "requires_tech_building": UnitTypeId.CYBERNETICSCORE,
            "requires_power": True,
        },
        UnitTypeId.DARKTEMPLAR: {
            "ability": AbilityId.GATEWAYTRAIN_DARKTEMPLAR,
            "requires_tech_building": UnitTypeId.DARKSHRINE,
            "requires_power": True,
        },
        UnitTypeId.HIGHTEMPLAR: {
            "ability": AbilityId.GATEWAYTRAIN_HIGHTEMPLAR,
            "requires_tech_building": UnitTypeId.TEMPLARARCHIVE,
            "requires_power": True,
        },
        UnitTypeId.SENTRY: {
            "ability": AbilityId.GATEWAYTRAIN_SENTRY,
            "requires_tech_building": UnitTypeId.CYBERNETICSCORE,
            "requires_power": True,
        },
        UnitTypeId.STALKER: {
            "ability": AbilityId.GATEWAYTRAIN_STALKER,
            "requires_tech_building": UnitTypeId.CYBERNETICSCORE,
            "requires_power": True,
        },
        UnitTypeId.ZEALOT: {
            "ability": AbilityId.GATEWAYTRAIN_ZEALOT,
            "requires_power": True,
        },
    },
    UnitTypeId.HATCHERY: {
        UnitTypeId.LAIR: {
            "ability": AbilityId.UPGRADETOLAIR_LAIR,
            "requires_tech_building": UnitTypeId.SPAWNINGPOOL,
        },
        UnitTypeId.QUEEN: {
            "ability": AbilityId.TRAINQUEEN_QUEEN,
            "requires_tech_building": UnitTypeId.SPAWNINGPOOL,
        },
    },
    UnitTypeId.HIVE: {
        UnitTypeId.QUEEN: {
            "ability": AbilityId.TRAINQUEEN_QUEEN,
            "requires_tech_building": UnitTypeId.SPAWNINGPOOL,
        }
    },
    UnitTypeId.HYDRALISK: {
        UnitTypeId.LURKERMP: {
            "ability": AbilityId.MORPH_LURKER,
            "requires_tech_building": UnitTypeId.LURKERDENMP,
        }
    },
    UnitTypeId.LAIR: {
        UnitTypeId.HIVE: {
            "ability": AbilityId.UPGRADETOHIVE_HIVE,
            "requires_tech_building": UnitTypeId.INFESTATIONPIT,
        },
        UnitTypeId.QUEEN: {
            "ability": AbilityId.TRAINQUEEN_QUEEN,
            "requires_tech_building": UnitTypeId.SPAWNINGPOOL,
        },
    },
    UnitTypeId.LARVA: {
        UnitTypeId.CORRUPTOR: {
            "ability": AbilityId.LARVATRAIN_CORRUPTOR,
            "requires_tech_building": UnitTypeId.SPIRE,
        },
        UnitTypeId.DRONE: {"ability": AbilityId.LARVATRAIN_DRONE},
        UnitTypeId.HYDRALISK: {
            "ability": AbilityId.LARVATRAIN_HYDRALISK,
            "requires_tech_building": UnitTypeId.HYDRALISKDEN,
        },
        UnitTypeId.INFESTOR: {
            "ability": AbilityId.LARVATRAIN_INFESTOR,
            "requires_tech_building": UnitTypeId.INFESTATIONPIT,
        },
        UnitTypeId.MUTALISK: {
            "ability": AbilityId.LARVATRAIN_MUTALISK,
            "requires_tech_building": UnitTypeId.SPIRE,
        },
        UnitTypeId.OVERLORD: {"ability": AbilityId.LARVATRAIN_OVERLORD},
        UnitTypeId.ROACH: {
            "ability": AbilityId.LARVATRAIN_ROACH,
            "requires_tech_building": UnitTypeId.ROACHWARREN,
        },
        UnitTypeId.SWARMHOSTMP: {
            "ability": AbilityId.TRAIN_SWARMHOST,
            "requires_tech_building": UnitTypeId.INFESTATIONPIT,
        },
        UnitTypeId.ULTRALISK: {
            "ability": AbilityId.LARVATRAIN_ULTRALISK,
            "requires_tech_building": UnitTypeId.ULTRALISKCAVERN,
        },
        UnitTypeId.VIPER: {
            "ability": AbilityId.LARVATRAIN_VIPER,
            "requires_tech_building": UnitTypeId.HIVE,
        },
        UnitTypeId.ZERGLING: {
            "ability": AbilityId.LARVATRAIN_ZERGLING,
            "requires_tech_building": UnitTypeId.SPAWNINGPOOL,
        },
    },
    UnitTypeId.NEXUS: {
        UnitTypeId.MOTHERSHIP: {
            "ability": AbilityId.NEXUSTRAINMOTHERSHIP_MOTHERSHIP,
            "requires_tech_building": UnitTypeId.FLEETBEACON,
        },
        UnitTypeId.PROBE: {"ability": AbilityId.NEXUSTRAIN_PROBE},
    },
    UnitTypeId.NYDUSNETWORK: {
        UnitTypeId.NYDUSCANAL: {
            "ability": AbilityId.BUILD_NYDUSWORM,
            "requires_placement_position": True,
        }
    },
    UnitTypeId.ORACLE: {
        UnitTypeId.ORACLESTASISTRAP: {
            "ability": AbilityId.BUILD_STASISTRAP,
            "requires_placement_position": True,
        }
    },
    UnitTypeId.ORBITALCOMMAND: {
        UnitTypeId.SCV: {"ability": AbilityId.COMMANDCENTERTRAIN_SCV}
    },
    UnitTypeId.OVERLORD: {
        UnitTypeId.OVERLORDTRANSPORT: {
            "ability": AbilityId.MORPH_OVERLORDTRANSPORT,
            "requires_tech_building": UnitTypeId.LAIR,
        },
        UnitTypeId.OVERSEER: {
            "ability": AbilityId.MORPH_OVERSEER,
            "requires_tech_building": UnitTypeId.LAIR,
        },
    },
    UnitTypeId.OVERLORDTRANSPORT: {
        UnitTypeId.OVERSEER: {
            "ability": AbilityId.MORPH_OVERSEER,
            "requires_tech_building": UnitTypeId.LAIR,
        }
    },
    UnitTypeId.OVERSEER: {
        UnitTypeId.CHANGELING: {"ability": AbilityId.SPAWNCHANGELING_SPAWNCHANGELING}
    },
    UnitTypeId.OVERSEERSIEGEMODE: {
        UnitTypeId.CHANGELING: {"ability": AbilityId.SPAWNCHANGELING_SPAWNCHANGELING}
    },
    UnitTypeId.PLANETARYFORTRESS: {
        UnitTypeId.SCV: {"ability": AbilityId.COMMANDCENTERTRAIN_SCV}
    },
    UnitTypeId.PROBE: {
        UnitTypeId.ASSIMILATOR: {"ability": AbilityId.PROTOSSBUILD_ASSIMILATOR},
        UnitTypeId.CYBERNETICSCORE: {
            "ability": AbilityId.PROTOSSBUILD_CYBERNETICSCORE,
            "requires_tech_building": UnitTypeId.GATEWAY,
            "requires_placement_position": True,
        },
        UnitTypeId.DARKSHRINE: {
            "ability": AbilityId.PROTOSSBUILD_DARKSHRINE,
            "requires_tech_building": UnitTypeId.TWILIGHTCOUNCIL,
            "requires_placement_position": True,
        },
        UnitTypeId.FLEETBEACON: {
            "ability": AbilityId.PROTOSSBUILD_FLEETBEACON,
            "requires_tech_building": UnitTypeId.STARGATE,
            "requires_placement_position": True,
        },
        UnitTypeId.FORGE: {
            "ability": AbilityId.PROTOSSBUILD_FORGE,
            "requires_tech_building": UnitTypeId.PYLON,
            "requires_placement_position": True,
        },
        UnitTypeId.GATEWAY: {
            "ability": AbilityId.PROTOSSBUILD_GATEWAY,
            "requires_tech_building": UnitTypeId.PYLON,
            "requires_placement_position": True,
        },
        UnitTypeId.NEXUS: {
            "ability": AbilityId.PROTOSSBUILD_NEXUS,
            "requires_placement_position": True,
        },
        UnitTypeId.PHOTONCANNON: {
            "ability": AbilityId.PROTOSSBUILD_PHOTONCANNON,
            "requires_tech_building": UnitTypeId.FORGE,
            "requires_placement_position": True,
        },
        UnitTypeId.PYLON: {
            "ability": AbilityId.PROTOSSBUILD_PYLON,
            "requires_placement_position": True,
        },
        UnitTypeId.ROBOTICSBAY: {
            "ability": AbilityId.PROTOSSBUILD_ROBOTICSBAY,
            "requires_tech_building": UnitTypeId.ROBOTICSFACILITY,
            "requires_placement_position": True,
        },
        UnitTypeId.ROBOTICSFACILITY: {
            "ability": AbilityId.PROTOSSBUILD_ROBOTICSFACILITY,
            "requires_tech_building": UnitTypeId.CYBERNETICSCORE,
            "requires_placement_position": True,
        },
        UnitTypeId.SHIELDBATTERY: {
            "ability": AbilityId.BUILD_SHIELDBATTERY,
            "requires_tech_building": UnitTypeId.CYBERNETICSCORE,
            "requires_placement_position": True,
        },
        UnitTypeId.STARGATE: {
            "ability": AbilityId.PROTOSSBUILD_STARGATE,
            "requires_tech_building": UnitTypeId.GATEWAY,
            "requires_placement_position": True,
        },
        UnitTypeId.TEMPLARARCHIVE: {
            "ability": AbilityId.PROTOSSBUILD_TEMPLARARCHIVE,
            "requires_tech_building": UnitTypeId.TWILIGHTCOUNCIL,
            "requires_placement_position": True,
        },
        UnitTypeId.TWILIGHTCOUNCIL: {
            "ability": AbilityId.PROTOSSBUILD_TWILIGHTCOUNCIL,
            "requires_tech_building": UnitTypeId.CYBERNETICSCORE,
            "requires_placement_position": True,
        },
    },
    UnitTypeId.QUEEN: {
        UnitTypeId.CREEPTUMOR: {
            "ability": AbilityId.BUILD_CREEPTUMOR,
            "requires_placement_position": True,
        },
        UnitTypeId.CREEPTUMORQUEEN: {
            "ability": AbilityId.BUILD_CREEPTUMOR_QUEEN,
            "requires_placement_position": True,
        },
    },
    UnitTypeId.RAVEN: {
        UnitTypeId.AUTOTURRET: {"ability": AbilityId.BUILDAUTOTURRET_AUTOTURRET}
    },
    UnitTypeId.ROACH: {
        UnitTypeId.RAVAGER: {
            "ability": AbilityId.MORPHTORAVAGER_RAVAGER,
            "requires_tech_building": UnitTypeId.HATCHERY,
        }
    },
    UnitTypeId.ROBOTICSFACILITY: {
        UnitTypeId.COLOSSUS: {
            "ability": AbilityId.ROBOTICSFACILITYTRAIN_COLOSSUS,
            "requires_tech_building": UnitTypeId.ROBOTICSBAY,
            "requires_power": True,
        },
        UnitTypeId.DISRUPTOR: {
            "ability": AbilityId.TRAIN_DISRUPTOR,
            "requires_tech_building": UnitTypeId.ROBOTICSBAY,
            "requires_power": True,
        },
        UnitTypeId.IMMORTAL: {
            "ability": AbilityId.ROBOTICSFACILITYTRAIN_IMMORTAL,
            "requires_power": True,
        },
        UnitTypeId.OBSERVER: {
            "ability": AbilityId.ROBOTICSFACILITYTRAIN_OBSERVER,
            "requires_power": True,
        },
        UnitTypeId.WARPPRISM: {
            "ability": AbilityId.ROBOTICSFACILITYTRAIN_WARPPRISM,
            "requires_power": True,
        },
    },
    UnitTypeId.SCV: {
        UnitTypeId.ARMORY: {
            "ability": AbilityId.TERRANBUILD_ARMORY,
            "requires_tech_building": UnitTypeId.FACTORY,
            "requires_placement_position": True,
        },
        UnitTypeId.BARRACKS: {
            "ability": AbilityId.TERRANBUILD_BARRACKS,
            "requires_tech_building": UnitTypeId.SUPPLYDEPOT,
            "requires_placement_position": True,
        },
        UnitTypeId.BUNKER: {
            "ability": AbilityId.TERRANBUILD_BUNKER,
            "requires_tech_building": UnitTypeId.BARRACKS,
            "requires_placement_position": True,
        },
        UnitTypeId.COMMANDCENTER: {
            "ability": AbilityId.TERRANBUILD_COMMANDCENTER,
            "requires_placement_position": True,
        },
        UnitTypeId.ENGINEERINGBAY: {
            "ability": AbilityId.TERRANBUILD_ENGINEERINGBAY,
            "requires_tech_building": UnitTypeId.COMMANDCENTER,
            "requires_placement_position": True,
        },
        UnitTypeId.FACTORY: {
            "ability": AbilityId.TERRANBUILD_FACTORY,
            "requires_tech_building": UnitTypeId.BARRACKS,
            "requires_placement_position": True,
        },
        UnitTypeId.FUSIONCORE: {
            "ability": AbilityId.TERRANBUILD_FUSIONCORE,
            "requires_tech_building": UnitTypeId.STARPORT,
            "requires_placement_position": True,
        },
        UnitTypeId.GHOSTACADEMY: {
            "ability": AbilityId.TERRANBUILD_GHOSTACADEMY,
            "requires_tech_building": UnitTypeId.BARRACKS,
            "requires_placement_position": True,
        },
        UnitTypeId.MISSILETURRET: {
            "ability": AbilityId.TERRANBUILD_MISSILETURRET,
            "requires_tech_building": UnitTypeId.ENGINEERINGBAY,
            "requires_placement_position": True,
        },
        UnitTypeId.REFINERY: {"ability": AbilityId.TERRANBUILD_REFINERY},
        UnitTypeId.SENSORTOWER: {
            "ability": AbilityId.TERRANBUILD_SENSORTOWER,
            "requires_tech_building": UnitTypeId.ENGINEERINGBAY,
            "requires_placement_position": True,
        },
        UnitTypeId.STARPORT: {
            "ability": AbilityId.TERRANBUILD_STARPORT,
            "requires_tech_building": UnitTypeId.FACTORY,
            "requires_placement_position": True,
        },
        UnitTypeId.SUPPLYDEPOT: {
            "ability": AbilityId.TERRANBUILD_SUPPLYDEPOT,
            "requires_placement_position": True,
        },
    },
    UnitTypeId.SPIRE: {
        UnitTypeId.GREATERSPIRE: {
            "ability": AbilityId.UPGRADETOGREATERSPIRE_GREATERSPIRE,
            "requires_tech_building": UnitTypeId.HIVE,
        }
    },
    UnitTypeId.STARGATE: {
        UnitTypeId.CARRIER: {
            "ability": AbilityId.STARGATETRAIN_CARRIER,
            "requires_tech_building": UnitTypeId.FLEETBEACON,
            "requires_power": True,
        },
        UnitTypeId.ORACLE: {
            "ability": AbilityId.STARGATETRAIN_ORACLE,
            "requires_power": True,
        },
        UnitTypeId.PHOENIX: {
            "ability": AbilityId.STARGATETRAIN_PHOENIX,
            "requires_power": True,
        },
        UnitTypeId.TEMPEST: {
            "ability": AbilityId.STARGATETRAIN_TEMPEST,
            "requires_tech_building": UnitTypeId.FLEETBEACON,
            "requires_power": True,
        },
        UnitTypeId.VOIDRAY: {
            "ability": AbilityId.STARGATETRAIN_VOIDRAY,
            "requires_power": True,
        },
    },
    UnitTypeId.STARPORT: {
        UnitTypeId.BANSHEE: {
            "ability": AbilityId.STARPORTTRAIN_BANSHEE,
            "requires_techlab": True,
        },
        UnitTypeId.BATTLECRUISER: {
            "ability": AbilityId.STARPORTTRAIN_BATTLECRUISER,
            "requires_techlab": True,
            "requires_tech_building": UnitTypeId.FUSIONCORE,
        },
        UnitTypeId.LIBERATOR: {"ability": AbilityId.STARPORTTRAIN_LIBERATOR},
        UnitTypeId.MEDIVAC: {"ability": AbilityId.STARPORTTRAIN_MEDIVAC},
        UnitTypeId.RAVEN: {
            "ability": AbilityId.STARPORTTRAIN_RAVEN,
            "requires_techlab": True,
        },
        UnitTypeId.VIKINGFIGHTER: {"ability": AbilityId.STARPORTTRAIN_VIKINGFIGHTER},
    },
    UnitTypeId.SWARMHOSTBURROWEDMP: {
        UnitTypeId.LOCUSTMPFLYING: {"ability": AbilityId.EFFECT_SPAWNLOCUSTS}
    },
    UnitTypeId.SWARMHOSTMP: {
        UnitTypeId.LOCUSTMPFLYING: {"ability": AbilityId.EFFECT_SPAWNLOCUSTS}
    },
    UnitTypeId.WARPGATE: {
        UnitTypeId.ADEPT: {
            "ability": AbilityId.TRAINWARP_ADEPT,
            "requires_tech_building": UnitTypeId.CYBERNETICSCORE,
            "requires_placement_position": True,
            "requires_power": True,
        },
        UnitTypeId.DARKTEMPLAR: {
            "ability": AbilityId.WARPGATETRAIN_DARKTEMPLAR,
            "requires_tech_building": UnitTypeId.DARKSHRINE,
            "requires_placement_position": True,
            "requires_power": True,
        },
        UnitTypeId.HIGHTEMPLAR: {
            "ability": AbilityId.WARPGATETRAIN_HIGHTEMPLAR,
            "requires_tech_building": UnitTypeId.TEMPLARARCHIVE,
            "requires_placement_position": True,
            "requires_power": True,
        },
        UnitTypeId.SENTRY: {
            "ability": AbilityId.WARPGATETRAIN_SENTRY,
            "requires_tech_building": UnitTypeId.CYBERNETICSCORE,
            "requires_placement_position": True,
            "requires_power": True,
        },
        UnitTypeId.STALKER: {
            "ability": AbilityId.WARPGATETRAIN_STALKER,
            "requires_tech_building": UnitTypeId.CYBERNETICSCORE,
            "requires_placement_position": True,
            "requires_power": True,
        },
        UnitTypeId.ZEALOT: {
            "ability": AbilityId.WARPGATETRAIN_ZEALOT,
            "requires_placement_position": True,
            "requires_power": True,
        },
    },
    UnitTypeId.ZERGLING: {
        UnitTypeId.BANELING: {
            "ability": AbilityId.MORPHZERGLINGTOBANELING_BANELING,
            "requires_tech_building": UnitTypeId.BANELINGNEST,
        }
    },
}
