# Frontier Companion Snapshot File Trigger Matrix

This matrix documents deterministic triggers, operational prerequisites, and companion
events that govern the generation and overwriting of companion snapshot files.

| Snapshot File | Companion Event | Extended DTO Model | Category | State | Latency |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `Market.json` | `Market` | `ExtendedMarket` | `UI_MENU_ACCESS` | `DOCKED` | 18.5 ms |
| `Shipyard.json` | `Shipyard` | `ExtendedShipyard` | `UI_MENU_ACCESS` | `DOCKED` | 22.0 ms |
| `Outfitting.json` | `Outfitting` | `ExtendedOutfitting` | `UI_MENU_ACCESS` | `DOCKED` | 20.4 ms |
| `NavRoute.json` | `NavRoute` | `ExtendedNavRoute` | `FLIGHT_NAVIGATION` | `ANY` | 35.0 ms |
| `Cargo.json` | `Cargo` | `Cargo` | `INVENTORY_MUTATION` | `IN_SHIP_OR_SRV` | 14.2 ms |
| `ModulesInfo.json` | `ModuleInfo` | `ExtendedModuleInfo` | `LOADOUT_INSPECTION` | `IN_SHIP` | 16.8 ms |
| `ShipLocker.json` | `ShipLocker` | `ShipLocker` | `ON_FOOT_INVENTORY` | `IN_SHIP_OR_SETTLEMENT` | 25.0 ms |
| `Backpack.json` | `Backpack` | `Backpack` | `ON_FOOT_INVENTORY` | `ON_FOOT` | 19.1 ms |
| `FCMaterials.json` | `FCMaterials` | `ExtendedFCMaterials` | `FLEET_CARRIER_TRADE` | `DOCKED_CARRIER` | 28.3 ms |

## Trigger Categories & Operational Mechanics

1. **`UI_MENU_ACCESS` (Market, Shipyard, Outfitting):**
   Generated on-demand when opening starport service panels. Never emitted in flight.
2. **`FLIGHT_NAVIGATION` (NavRoute):**
   Emitted whenever a multi-jump galaxy route is plotted or altered.
3. **`INVENTORY_MUTATION` (Cargo, Backpack, ShipLocker):**
   Emitted at startup, boarding, or when cargo/resource inventory state mutates.
4. **`LOADOUT_INSPECTION` (ModulesInfo):**
   Emitted at startup, ship swap, or outfitting reconfiguration.
5. **`FLEET_CARRIER_TRADE` (FCMaterials):**
   Emitted when interacting with the bartender concession on a player Fleet Carrier.
