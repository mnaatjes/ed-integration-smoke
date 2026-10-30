"""Extracts Inara event specifications and synthesizes formal Draft 2020-12 JSON Schemas."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

from ed_schema import create_schema_engine

ROOT_DIR = Path(__file__).resolve().parent.parent
INARA_SCHEMAS_DIR = ROOT_DIR / "schemas" / "inara"

# Definitive structural event definitions derived from inara_upstream.py & Inara API Docs
INARA_EVENTS_CATALOG: dict[str, dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # 1. Profile, Friends & Social
    # -------------------------------------------------------------------------
    "getCommanderProfile": {
        "description": "Returns basic information about commander from Inara like ranks, squadron, etc.",
        "properties": {
            "searchName": {"type": "string", "description": "Commander's name for exact match search."}
        },
        "required": ["searchName"],
    },
    "addCommanderFriend": {
        "description": "Adds a friend request to the target commander on Inara.",
        "properties": {
            "commanderName": {"type": "string", "description": "In-game name of the target commander."},
            "gamePlatform": {
                "type": "string",
                "enum": ["pc", "xbox", "ps4"],
                "description": "Target commander's game platform.",
            },
        },
        "required": ["commanderName", "gamePlatform"],
    },
    "delCommanderFriend": {
        "description": "Removes a target commander from the friends list on Inara.",
        "properties": {
            "commanderName": {"type": "string", "description": "In-game name of the target commander."},
            "gamePlatform": {
                "type": "string",
                "enum": ["pc", "xbox", "ps4"],
                "description": "Target commander's game platform.",
            },
        },
        "required": ["commanderName", "gamePlatform"],
    },
    "setCommanderCredits": {
        "description": "Updates commander's credit balance, assets, and loan debt.",
        "properties": {
            "commanderCredits": {"type": "integer", "description": "Current available credits."},
            "commanderLoan": {"type": "integer", "description": "Current loan debt if any."},
            "commanderAssets": {"type": "integer", "description": "Total assets value."},
        },
        "required": ["commanderCredits"],
    },
    "setCommanderGameStatistics": {
        "description": "Synchronizes complete career game statistics from statistics event.",
        "properties": {
            "bankAccount": {"type": "object", "additionalProperties": True},
            "combat": {"type": "object", "additionalProperties": True},
            "crime": {"type": "object", "additionalProperties": True},
            "smuggling": {"type": "object", "additionalProperties": True},
            "trading": {"type": "object", "additionalProperties": True},
            "mining": {"type": "object", "additionalProperties": True},
            "exploration": {"type": "object", "additionalProperties": True},
            "passengers": {"type": "object", "additionalProperties": True},
            "searchAndRescue": {"type": "object", "additionalProperties": True},
            "crafting": {"type": "object", "additionalProperties": True},
            "crew": {"type": "object", "additionalProperties": True},
            "multicrew": {"type": "object", "additionalProperties": True},
            "materialTraderStats": {"type": "object", "additionalProperties": True},
            "cqc": {"type": "object", "additionalProperties": True},
            "exobiology": {"type": "object", "additionalProperties": True},
            "thargoid": {"type": "object", "additionalProperties": True},
        },
        "required": [],
    },
    # -------------------------------------------------------------------------
    # 2. Ranks & Reputations
    # -------------------------------------------------------------------------
    "setCommanderRankPilot": {
        "description": "Updates commander pilot ranks and progression percentages.",
        "properties": {
            "rankName": {
                "type": "string",
                "enum": [
                    "combat",
                    "trade",
                    "exploration",
                    "cqc",
                    "soldier",
                    "exobiologist",
                    "federation",
                    "empire",
                ],
            },
            "rankValue": {"type": "integer", "minimum": 0},
            "rankProgress": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        },
        "required": ["rankName", "rankValue"],
    },
    "setCommanderRankEngineer": {
        "description": "Updates unlocked engineer rank stage/grade.",
        "properties": {
            "engineerName": {"type": "string"},
            "rankValue": {"type": "integer", "minimum": 0, "maximum": 5},
            "rankStage": {"type": "integer"},
        },
        "required": ["engineerName"],
    },
    "setCommanderRankPower": {
        "description": "Updates Powerplay affiliation, rank, and weekly merits.",
        "properties": {
            "powerName": {"type": "string"},
            "rankValue": {"type": "integer", "minimum": 0},
            "timePledged": {"type": "integer", "description": "Seconds pledged."},
            "merits": {"type": "integer"},
        },
        "required": ["powerName"],
    },
    "setCommanderReputationMajorFaction": {
        "description": "Updates major faction reputation percentages (Federation, Empire, Alliance).",
        "properties": {
            "majorfactionName": {
                "type": "string",
                "enum": ["Federation", "Empire", "Alliance", "Independent"],
            },
            "reputationValue": {"type": "number", "minimum": -1.0, "maximum": 1.0},
        },
        "required": ["majorfactionName", "reputationValue"],
    },
    "setCommanderReputationMinorFaction": {
        "description": "Updates minor faction reputation value.",
        "properties": {
            "minorfactionName": {"type": "string"},
            "reputationValue": {"type": "number", "minimum": -1.0, "maximum": 1.0},
        },
        "required": ["minorfactionName", "reputationValue"],
    },
    # -------------------------------------------------------------------------
    # 3. Fleet, Ships & Outfitting
    # -------------------------------------------------------------------------
    "addCommanderShip": {
        "description": "Registers a newly purchased ship in the commander's fleet.",
        "properties": {
            "shipType": {"type": "string"},
            "shipGameID": {"type": "integer"},
            "shipName": {"type": "string"},
            "shipIdent": {"type": "string"},
            "shipHullValue": {"type": "integer"},
            "shipModulesValue": {"type": "integer"},
            "isCurrentShip": {"type": "boolean"},
            "isHot": {"type": "boolean"},
        },
        "required": ["shipType", "shipGameID"],
    },
    "setCommanderShip": {
        "description": "Updates basic metadata of an existing ship in fleet.",
        "properties": {
            "shipType": {"type": "string"},
            "shipGameID": {"type": "integer"},
            "shipName": {"type": "string"},
            "shipIdent": {"type": "string"},
            "shipHullValue": {"type": "integer"},
            "shipModulesValue": {"type": "integer"},
            "isCurrentShip": {"type": "boolean"},
            "isHot": {"type": "boolean"},
            "starsystemName": {"type": "string"},
            "stationName": {"type": "string"},
            "marketID": {"type": "integer"},
        },
        "required": ["shipType", "shipGameID"],
    },
    "delCommanderShip": {
        "description": "Deletes/sells a ship from the fleet.",
        "properties": {
            "shipType": {"type": "string"},
            "shipGameID": {"type": "integer"},
        },
        "required": ["shipType", "shipGameID"],
    },
    "setCommanderShipLoadout": {
        "description": "Sets the complete outfitting loadout and engineering mods for a ship.",
        "properties": {
            "shipType": {"type": "string"},
            "shipGameID": {"type": "integer"},
            "shipLoadout": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "slotName": {"type": "string"},
                        "itemName": {"type": "string"},
                        "itemValue": {"type": "integer"},
                        "itemHealth": {"type": "number"},
                        "isOn": {"type": "boolean"},
                        "itemPriority": {"type": "integer"},
                        "itemAmmoClip": {"type": "integer"},
                        "itemAmmoHopper": {"type": "integer"},
                        "engineering": {
                            "type": "object",
                            "properties": {
                                "blueprintName": {"type": "string"},
                                "blueprintLevel": {"type": "integer"},
                                "blueprintQuality": {"type": "number"},
                                "experimentalEffect": {"type": "string"},
                                "modifiers": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "value": {"type": "number"},
                                            "originalValue": {"type": "number"},
                                            "lessIsGood": {"type": "boolean"},
                                        },
                                        "required": ["name", "value"],
                                    },
                                },
                            },
                            "required": ["blueprintName", "blueprintLevel"],
                        },
                    },
                    "required": ["slotName", "itemName"],
                },
            },
        },
        "required": ["shipType", "shipGameID", "shipLoadout"],
    },
    "setCommanderShipTransfer": {
        "description": "Sets ship in-transit transfer status.",
        "properties": {
            "shipType": {"type": "string"},
            "shipGameID": {"type": "integer"},
            "starsystemName": {"type": "string"},
            "stationName": {"type": "string"},
            "marketID": {"type": "integer"},
            "transferTime": {"type": "integer"},
        },
        "required": ["shipType", "shipGameID", "starsystemName"],
    },
    "setCommanderStorageModules": {
        "description": "Updates inventory of stored outfitting modules.",
        "properties": {
            "modules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "itemName": {"type": "string"},
                        "itemValue": {"type": "integer"},
                        "itemHot": {"type": "boolean"},
                        "starsystemName": {"type": "string"},
                        "stationName": {"type": "string"},
                        "marketID": {"type": "integer"},
                        "storageSlot": {"type": "integer"},
                        "inTransit": {"type": "boolean"},
                    },
                    "required": ["itemName"],
                },
            }
        },
        "required": ["modules"],
    },
    # -------------------------------------------------------------------------
    # 4. Inventory, Materials & Suits
    # -------------------------------------------------------------------------
    "resetCommanderInventory": {
        "description": "Resets inventory collections prior to clean synchronization.",
        "properties": {
            "inventoryTypes": {
                "type": "array",
                "items": {"type": "string", "enum": ["materials", "cargo", "data", "components"]},
            }
        },
        "required": [],
    },
    "setCommanderInventory": {
        "description": "Sets general item inventory counts.",
        "properties": {
            "itemName": {"type": "string"},
            "itemCount": {"type": "integer", "minimum": 0},
        },
        "required": ["itemName", "itemCount"],
    },
    "setCommanderInventoryCargo": {
        "description": "Sets commodity cargo manifest.",
        "properties": {
            "cargo": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "itemName": {"type": "string"},
                        "itemCount": {"type": "integer", "minimum": 1},
                        "isStolen": {"type": "boolean"},
                        "isMission": {"type": "boolean"},
                    },
                    "required": ["itemName", "itemCount"],
                },
            }
        },
        "required": ["cargo"],
    },
    "setCommanderInventoryMaterials": {
        "description": "Synchronizes complete manufactured, raw, and encoded material stocks.",
        "properties": {
            "materials": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "itemName": {"type": "string"},
                        "itemCount": {"type": "integer", "minimum": 0},
                    },
                    "required": ["itemName", "itemCount"],
                },
            }
        },
        "required": ["materials"],
    },
    "setCommanderSuitLoadout": {
        "description": "Registers an Odyssey on-foot suit loadout.",
        "properties": {
            "suitID": {"type": "integer"},
            "suitName": {"type": "string"},
            "suitLoadoutName": {"type": "string"},
            "suitModules": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["suitID", "suitName"],
    },
    "updateCommanderSuitLoadout": {
        "description": "Updates an existing Odyssey suit loadout.",
        "properties": {
            "suitID": {"type": "integer"},
            "suitName": {"type": "string"},
            "suitLoadoutName": {"type": "string"},
            "suitModules": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["suitID"],
    },
    "delCommanderSuitLoadout": {
        "description": "Deletes a suit loadout.",
        "properties": {
            "suitID": {"type": "integer"},
        },
        "required": ["suitID"],
    },
    # -------------------------------------------------------------------------
    # 5. Travel & Location
    # -------------------------------------------------------------------------
    "setCommanderTravelLocation": {
        "description": "Updates commander's current star system and station.",
        "properties": {
            "starsystemName": {"type": "string"},
            "stationName": {"type": "string"},
            "marketID": {"type": "integer"},
            "bodyName": {"type": "string"},
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
            "shipType": {"type": "string"},
            "shipGameID": {"type": "integer"},
            "isTaxiDropShip": {"type": "boolean"},
        },
        "required": ["starsystemName"],
    },
    "addCommanderTravelFSDJump": {
        "description": "Logs an FSD hyperspace jump event.",
        "properties": {
            "starsystemName": {"type": "string"},
            "jumpDistance": {"type": "number"},
            "fuelUsed": {"type": "number"},
            "fuelLevel": {"type": "number"},
            "boostUsed": {"type": "boolean"},
            "shipType": {"type": "string"},
            "shipGameID": {"type": "integer"},
        },
        "required": ["starsystemName"],
    },
    "addCommanderTravelCarrierJump": {
        "description": "Logs a Fleet Carrier hyperspace jump.",
        "properties": {
            "starsystemName": {"type": "string"},
            "stationName": {"type": "string"},
            "marketID": {"type": "integer"},
            "bodyName": {"type": "string"},
        },
        "required": ["starsystemName"],
    },
    "addCommanderTravelDock": {
        "description": "Logs a docking event at a station, outpost, or carrier.",
        "properties": {
            "starsystemName": {"type": "string"},
            "stationName": {"type": "string"},
            "marketID": {"type": "integer"},
            "shipType": {"type": "string"},
            "shipGameID": {"type": "integer"},
        },
        "required": ["starsystemName", "stationName"],
    },
    "addCommanderTravelLand": {
        "description": "Logs a planetary touchdown.",
        "properties": {
            "starsystemName": {"type": "string"},
            "bodyName": {"type": "string"},
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
            "shipType": {"type": "string"},
            "shipGameID": {"type": "integer"},
        },
        "required": ["starsystemName", "bodyName"],
    },
    # -------------------------------------------------------------------------
    # 6. Combat Events
    # -------------------------------------------------------------------------
    "addCommanderCombatKill": {
        "description": "Logs an NPC or PvP combat kill.",
        "properties": {
            "starsystemName": {"type": "string"},
            "targetName": {"type": "string"},
            "targetShip": {"type": "string"},
            "targetRank": {"type": "string"},
            "reward": {"type": "integer"},
        },
        "required": ["starsystemName", "targetName"],
    },
    "addCommanderCombatDeath": {
        "description": "Logs player ship destruction.",
        "properties": {
            "starsystemName": {"type": "string"},
            "opponentName": {"type": "string"},
            "wingOpponentNames": {"type": "array", "items": {"type": "string"}},
            "isPvP": {"type": "boolean"},
        },
        "required": ["starsystemName"],
    },
    "addCommanderCombatInterdiction": {
        "description": "Logs player attempting an FSD interdiction on another ship.",
        "properties": {
            "starsystemName": {"type": "string"},
            "targetName": {"type": "string"},
            "isSuccess": {"type": "boolean"},
            "isPlayer": {"type": "boolean"},
        },
        "required": ["starsystemName", "targetName", "isSuccess"],
    },
    "addCommanderCombatInterdicted": {
        "description": "Logs player being interdicted by another ship.",
        "properties": {
            "starsystemName": {"type": "string"},
            "interdictorName": {"type": "string"},
            "isSubmitted": {"type": "boolean"},
            "isPlayer": {"type": "boolean"},
        },
        "required": ["starsystemName", "interdictorName"],
    },
    "addCommanderCombatInterdictionEscape": {
        "description": "Logs escaping an interdiction vector tether.",
        "properties": {
            "starsystemName": {"type": "string"},
            "interdictorName": {"type": "string"},
        },
        "required": ["starsystemName", "interdictorName"],
    },
    # -------------------------------------------------------------------------
    # 7. Missions, Permits & Community Goals
    # -------------------------------------------------------------------------
    "addCommanderMission": {
        "description": "Registers an accepted mission.",
        "properties": {
            "missionName": {"type": "string"},
            "missionGameID": {"type": "integer"},
            "missionExpiry": {"type": "string", "format": "date-time"},
            "influence": {"type": "string"},
            "reputation": {"type": "string"},
            "reward": {"type": "integer"},
            "wing": {"type": "boolean"},
            "minorfactionName": {"type": "string"},
            "starsystemName": {"type": "string"},
            "stationName": {"type": "string"},
        },
        "required": ["missionName", "missionGameID"],
    },
    "setCommanderMissionCompleted": {
        "description": "Marks a mission successfully completed.",
        "properties": {
            "missionName": {"type": "string"},
            "missionGameID": {"type": "integer"},
            "reward": {"type": "integer"},
            "donation": {"type": "integer"},
            "permits": {"type": "array", "items": {"type": "string"}},
            "commodities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "count": {"type": "integer"},
                    },
                    "required": ["name", "count"],
                },
            },
            "materials": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "count": {"type": "integer"},
                    },
                    "required": ["name", "count"],
                },
            },
        },
        "required": ["missionName", "missionGameID"],
    },
    "setCommanderMissionFailed": {
        "description": "Marks a mission failed.",
        "properties": {
            "missionName": {"type": "string"},
            "missionGameID": {"type": "integer"},
            "fine": {"type": "integer"},
        },
        "required": ["missionName", "missionGameID"],
    },
    "setCommanderMissionAbandoned": {
        "description": "Marks a mission abandoned.",
        "properties": {
            "missionName": {"type": "string"},
            "missionGameID": {"type": "integer"},
            "fine": {"type": "integer"},
        },
        "required": ["missionName", "missionGameID"],
    },
    "addCommanderPermit": {
        "description": "Records star system entry permit acquisition.",
        "properties": {
            "starsystemName": {"type": "string"},
        },
        "required": ["starsystemName"],
    },
    "setCommunityGoal": {
        "description": "Synchronizes community goal state.",
        "properties": {
            "communitygoalGameID": {"type": "integer"},
            "communitygoalName": {"type": "string"},
            "starsystemName": {"type": "string"},
            "stationName": {"type": "string"},
            "goalExpiry": {"type": "string", "format": "date-time"},
            "tierReached": {"type": "integer"},
            "tierMax": {"type": "integer"},
            "contributorsNum": {"type": "integer"},
            "contributionsTotal": {"type": "integer"},
            "isCompleted": {"type": "boolean"},
        },
        "required": ["communitygoalGameID", "communitygoalName"],
    },
    "setCommanderCommunityGoalProgress": {
        "description": "Synchronizes commander contribution to a community goal.",
        "properties": {
            "communitygoalGameID": {"type": "integer"},
            "contribution": {"type": "integer"},
            "percentileBand": {"type": "number"},
            "tierPercentile": {"type": "number"},
        },
        "required": ["communitygoalGameID", "contribution"],
    },
}


def build_envelope_schema() -> dict[str, Any]:
    """Builds root batch envelope schema for Inara API v1."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://inara.cz/schemas/inapi/v1/envelope#",
        "title": "InaraBatchEnvelope",
        "description": "Standard root batch request envelope for the Inara API v1.",
        "type": "object",
        "additionalProperties": False,
        "required": ["header", "events"],
        "properties": {
            "header": {
                "type": "object",
                "additionalProperties": False,
                "required": ["appName", "appVersion", "APIkey"],
                "properties": {
                    "appName": {"type": "string", "minLength": 1},
                    "appVersion": {"type": "string", "minLength": 1},
                    "isBeingDeveloped": {"type": "boolean"},
                    "APIkey": {"type": "string", "minLength": 1},
                    "commanderName": {"type": "string"},
                    "commanderFrontierID": {"type": "string"},
                },
            },
            "events": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["eventName", "eventTimestamp", "eventData"],
                    "properties": {
                        "eventName": {"type": "string", "minLength": 1},
                        "eventTimestamp": {"type": "string", "format": "date-time"},
                        "eventCustomID": {"type": "integer"},
                        "eventData": {"type": "object"},
                    },
                },
            },
        },
    }


def generate_all_inara_schemas() -> None:
    INARA_SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_schema_engine()

    print("=" * 70)
    print("INARA DRAFT 2020-12 JSON SCHEMA GENERATOR")
    print("=" * 70)

    # 1. Generate root envelope schema
    envelope_schema = build_envelope_schema()
    envelope_file = INARA_SCHEMAS_DIR / "inara_batch_envelope.json"
    envelope_file.write_text(json.dumps(envelope_schema, indent=2) + "\n", encoding="utf-8")
    print(f"[1/41] Generated Envelope Schema: {envelope_file.name}")

    # 2. Generate individual event schemas
    generated_count = 1
    for event_name, spec in sorted(INARA_EVENTS_CATALOG.items()):
        event_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://inara.cz/schemas/events/{event_name}#",
            "title": f"Inara{event_name[:1].upper() + event_name[1:]}",
            "description": spec["description"],
            "type": "object",
            "additionalProperties": False,
            "required": ["eventName", "eventTimestamp", "eventData"],
            "properties": {
                "eventName": {"type": "string", "const": event_name},
                "eventTimestamp": {"type": "string", "format": "date-time"},
                "eventCustomID": {"type": "integer"},
                "eventData": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": spec["properties"],
                    "required": spec.get("required", []),
                },
            },
        }

        schema_file = INARA_SCHEMAS_DIR / f"{event_name}.json"
        schema_file.write_text(json.dumps(event_schema, indent=2) + "\n", encoding="utf-8")
        generated_count += 1
        print(f"[{generated_count}/41] Generated Event Schema: {schema_file.name} ({event_name})")

    print("\n" + "=" * 70)
    print(f"SUCCESS: Generated {generated_count} Draft 2020-12 schemas in schemas/inara/")
    print("=" * 70)


if __name__ == "__main__":
    generate_all_inara_schemas()
