---
title: "RES-0001: Fleet Carrier vs. Starport Shipyard Snapshot Duality"
tags: ["frontier-journal", "shipyard", "fleet-carrier", "snapshot", "telemetry"]
created_at: "2026-11-08"
last_updated_at: "2026-11-08"
---

# RES-0001: Fleet Carrier vs. Starport Shipyard Snapshot Duality

## 1. Diagnostic Summary

Frontier Developments' official Player Journal specification defines `Shipyard.json` as a companion snapshot file recording available ships for retail purchase at the current port. However, empirical telemetry analysis reveals that when docked at a player-owned **Fleet Carrier**, the game client reuses the exact same `Shipyard.json` schema to dump the commander's **stored fleet inventory and total outfitted ship valuations**, rather than dealership inventory.

## 2. Theoretical Mechanism

Frontier Developments maintains two separate logging mechanisms for shipyards:

1. **Companion Snapshot File (`Shipyard.json`):** Generated in the journal directory whenever the player opens the Shipyard user interface.
2. **Temporal Journal Event (`StoredShips`):** Appended to `Journal.<timestamp>.<part>.log` containing `ShipsHere` and `ShipsRemote` arrays with unique player ship instances.

When interacting with a standard starport or outpost with shipyard services enabled:
* `Shipyard.json` emits a `PriceList` array containing stock hulls for sale.
* `ShipPrice` values correspond strictly to unengineered base hull retail costs.

When interacting with a **Fleet Carrier**:
* Even when retail ship sales are inactive on the carrier (the Carrier Shipyard sales module is uninstalled or unprovisioned), opening the carrier's Shipyard menu to transfer or switch ships triggers an overwrite of `Shipyard.json`.
* The client engine re-purposes the `PriceList` array to output the player's personal fleet stationed aboard that carrier.
* The `ShipPrice` field no longer reflects stock base purchase prices; instead, it outputs the **aggregate insurance valuation** (base hull + all fitted core/optional modules and weapons).

## 3. Empirical Evidence & Comparison

### 3.1 Observed Fleet Carrier Payload (`V4X-N6J`)

Querying `GET /api/v1/snapshots/Shipyard` while docked at Fleet Carrier `V4X-N6J` (Wolf 397) yields:

```json
{
  "timestamp": "2026-11-08T06:02:26Z",
  "event": "Shipyard",
  "MarketID": 3715110400,
  "StationName": "V4X-N6J",
  "StarSystem": "Wolf 397",
  "Horizons": true,
  "AllowCobraMkIV": false,
  "PriceList": [
    { "id": 0, "ShipType": "panthermkii", "ShipType_Localised": "Panther Clipper Mk II", "ShipPrice": 413078737 },
    { "id": 0, "ShipType": "explorer_nx", "ShipType_Localised": "Caspian Explorer", "ShipPrice": 278352150 },
    { "id": 0, "ShipType": "python_nx", "ShipType_Localised": "Python Mk II", "ShipPrice": 250010253 },
    { "id": 0, "ShipType": "python", "ShipPrice": 152096048 },
    { "id": 0, "ShipType": "lakonminer", "ShipType_Localised": "Type-11 Prospector", "ShipPrice": 83945450 },
    { "id": 0, "ShipType": "typex", "ShipType_Localised": "Alliance Chieftain", "ShipPrice": 79710820 },
    { "id": 0, "ShipType": "smallcombat01_nx", "ShipType_Localised": "Kestrel Mk II", "ShipPrice": 61695630 },
    { "id": 0, "ShipType": "mandalay", "ShipPrice": 55599553 },
    { "id": 0, "ShipType": "mediumtransport01", "ShipType_Localised": "Lynx Highliner", "ShipPrice": 34170577 },
    { "id": 0, "ShipType": "vulture", "ShipPrice": 23731470 },
    { "id": 0, "ShipType": "dolphin", "ShipPrice": 17820422 },
    { "id": 0, "ShipType": "diamondbackxl", "ShipType_Localised": "Diamondback Explorer", "ShipPrice": 15180844 },
    { "id": 0, "ShipType": "cobramkv", "ShipType_Localised": "Cobra Mk V", "ShipPrice": 14634527 },
    { "id": 0, "ShipType": "dolphin", "ShipPrice": 12258948 },
    { "id": 0, "ShipType": "empire_courier", "ShipType_Localised": "Imperial Courier", "ShipPrice": 5887416 },
    { "id": 0, "ShipType": "empire_eagle", "ShipType_Localised": "Imperial Eagle", "ShipPrice": 2047825 }
  ]
}
```

### 3.2 Key Indicators of Personal Fleet Semantics

1. **Outfitting Valuation vs. Retail Price:**
   * **Python:** Retail hull cost is ~56,978,180 CR. The carrier snapshot records `152,096,048 CR`, matching an A-rated, military-outfitted build.
   * **Vulture:** Retail hull cost is ~4,925,615 CR. The carrier snapshot records `23,731,470 CR`.
   * **Imperial Courier:** Retail hull cost is ~2,542,931 CR. The carrier snapshot records `5,887,416 CR`.
   * **Imperial Eagle:** Retail hull cost is ~110,830 CR. The carrier snapshot records `2,047,825 CR`.
2. **Duplicate Hull Types with Divergent Valuations:**
   * Two separate `dolphin` entries exist in the array:
     * Instance 1: `17,820,422 CR`
     * Instance 2: `12,258,948 CR`
   * Standard station retail dealerships never list duplicate hulls for the same ship model. This confirms two distinct owned Dolphin hulls stationed on the carrier with different module loadouts.
3. **Absence of Retail Service:**
   * The carrier `V4X-N6J` does not run the Shipyard dealership service, yet the file is generated upon interacting with carrier ship storage.

## 4. Telemetry & CLI Design Remediation

1. **Table Title & Column Header Adaptation:**
   * Renderers must not naively label `Shipyard.json` as `"Ships for Sale"`.
   * When inspecting station names matching Fleet Carrier registration patterns (e.g., `XXX-XXX`) or when detecting Fleet Carrier station context, title tables as `Shipyard: Stored Ships & Valuations`.
   * Use column header `Valuation / Price (CR)` to remain semantically accurate across both contexts.
2. **Hydration Mapping:**
   * `ed_hydrator` and downstream consumer apps should preserve the dual interpretation, allowing UI surfaces to display stored carrier fleets when docked at carrier hubs.
