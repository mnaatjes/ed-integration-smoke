---
title: "Live Telemetry & Event Ingestion Coverage Report"
tags: ["telemetry", "verification", "coverage", "ed-models", "audit"]
created_at: "2026-11-03"
last_updated_at: "2026-11-03"
---

# Live Telemetry & Event Ingestion Coverage Report

Summary of all Frontier journal events, status bitflags, and companion snapshots ingested and validated by `ed-integration-smoke` against `ed-models`.

## Operational Metrics

* **Total Cataloged Targets:** 305
* **Achieved Targets:** 111 (36.39%)
* **Total Recorded Hits:** 93,713
* **Validation Engine:** `ed-models` v0.2.1

## Achieved Target Ledger

| # | Target Identifier | Type | Chapter | Hit Count | First Seen | Last Seen |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| 1 | `CarrierBankTransfer` | `event` | carrier | 1 | 2026-11-03T01:26:23Z | 2026-11-03T01:26:23Z |
| 2 | `CarrierCrewServices` | `event` | carrier | 2 | 2026-11-03T02:11:21Z | 2026-11-03T02:11:32Z |
| 3 | `CarrierDepositFuel` | `event` | carrier | 1 | 2026-11-03T01:34:37Z | 2026-11-03T01:34:37Z |
| 4 | `CarrierFinance` | `event` | carrier | 5 | 2026-11-03T01:45:19Z | 2026-11-03T01:45:35Z |
| 5 | `CarrierJumpRequest` | `event` | carrier | 1 | 2026-11-02T04:33:06Z | 2026-11-02T04:33:06Z |
| 6 | `CarrierLocation` | `event` | carrier | 5 | 2026-10-25T23:55:10Z | 2026-11-02T04:49:10Z |
| 7 | `CarrierStats` | `event` | carrier | 5 | 2026-11-02T02:58:22Z | 2026-11-02T04:33:09Z |
| 8 | `Bounty` | `event` | combat | 1 | 2026-11-03T01:21:59Z | 2026-11-03T01:21:59Z |
| 9 | `HeatWarning` | `event` | combat | 3 | 2026-11-03T01:50:57Z | 2026-11-03T01:53:13Z |
| 10 | `ShieldState` | `event` | combat | 2 | 2026-11-03T02:14:42Z | 2026-11-03T02:16:06Z |
| 11 | `ShipTargeted` | `event` | combat | 17 | 2026-11-02T03:03:33Z | 2026-11-03T01:18:41Z |
| 12 | `UnderAttack` | `event` | combat | 2 | 2026-11-03T01:18:56Z | 2026-11-03T01:20:55Z |
| 13 | `DiscoveryScan` | `event` | exploration | 1 | 2026-11-02T04:07:26Z | 2026-11-02T04:07:26Z |
| 14 | `FSSAllBodiesFound` | `event` | exploration | 4 | 2026-11-02T03:31:58Z | 2026-11-02T04:30:08Z |
| 15 | `FSSBodySignals` | `event` | exploration | 1 | 2026-11-02T03:15:06Z | 2026-11-02T03:15:06Z |
| 16 | `FSSDiscoveryScan` | `event` | exploration | 3 | 2026-11-02T03:08:10Z | 2026-11-02T03:27:14Z |
| 17 | `FSSSignalDiscovered` | `event` | exploration | 6 | 2026-10-25T23:55:58Z | 2026-11-02T05:05:03Z |
| 18 | `NavBeaconScan` | `event` | exploration | 1 | 2026-11-02T03:01:18Z | 2026-11-02T03:01:18Z |
| 19 | `SAAScanComplete` | `event` | exploration | 4 | 2026-11-02T03:07:12Z | 2026-11-02T04:22:44Z |
| 20 | `SAASignalsFound` | `event` | exploration | 2 | 2026-11-02T04:07:24Z | 2026-11-02T04:22:44Z |
| 21 | `Scan` | `event` | exploration | 32 | 2026-11-02T03:01:18Z | 2026-11-02T04:39:00Z |
| 22 | `ScanBaryCentre` | `event` | exploration | 4 | 2026-11-02T03:01:18Z | 2026-11-02T04:04:35Z |
| 23 | `Backpack` | `event` | odyssey | 2 | 2026-08-14T02:01:12Z | 2026-11-02T04:26:56Z |
| 24 | `DeleteSuitLoadout` | `event` | odyssey | 1 | 2026-11-02T04:26:46Z | 2026-11-02T04:26:46Z |
| 25 | `Disembark` | `event` | odyssey | 1 | 2026-11-02T04:26:51Z | 2026-11-02T04:26:51Z |
| 26 | `Embark` | `event` | odyssey | 1 | 2026-11-02T04:27:18Z | 2026-11-02T04:27:18Z |
| 27 | `ShipLocker` | `event` | odyssey | 52 | 2026-10-25T18:33:48Z | 2026-11-02T05:05:03Z |
| 28 | `SuitLoadout` | `event` | odyssey | 1 | 2026-11-02T04:26:56Z | 2026-11-02T04:26:56Z |
| 29 | `SwitchSuitLoadout` | `event` | odyssey | 1 | 2026-11-02T04:26:40Z | 2026-11-02T04:26:40Z |
| 30 | `ApproachSettlement` | `event` | other | 1 | 2026-11-02T04:45:28Z | 2026-11-02T04:45:28Z |
| 31 | `CargoTransfer` | `event` | other | 2 | 2026-11-03T01:34:15Z | 2026-11-03T01:34:55Z |
| 32 | `Friends` | `event` | other | 2 | 2026-10-25T23:54:14Z | 2026-10-25T23:56:15Z |
| 33 | `FuelScoop` | `event` | other | 21 | 2026-11-02T03:23:35Z | 2026-11-02T05:02:59Z |
| 34 | `ModuleInfo` | `event` | other | 4 | 2026-08-20T22:37:15Z | 2026-11-02T04:52:00Z |
| 35 | `Music` | `event` | other | 49 | 2026-10-25T23:55:58Z | 2026-11-02T04:38:54Z |
| 36 | `ReceiveText` | `event` | other | 42 | 2026-10-25T23:55:58Z | 2026-11-02T05:07:00Z |
| 37 | `ReservoirReplenished` | `event` | other | 8 | 2026-11-02T03:15:30Z | 2026-11-02T04:43:52Z |
| 38 | `Scanned` | `event` | other | 1 | 2026-11-02T03:04:15Z | 2026-11-02T03:04:15Z |
| 39 | `Shutdown` | `event` | other | 4 | 2026-11-02T05:08:17Z | 2026-11-03T02:28:20Z |
| 40 | `Status` | `event` | other | 20,643 | 2026-11-02T02:50:31.163050Z | 2026-11-03T02:33:30.886140Z |
| 41 | `SupercruiseDestinationDrop` | `event` | other | 3 | 2026-11-02T03:00:23Z | 2026-11-02T05:04:58Z |
| 42 | `USSDrop` | `event` | other | 1 | 2026-11-03T01:49:44Z | 2026-11-03T01:49:44Z |
| 43 | `SquadronStartup` | `event` | squadrons | 2 | 2026-10-25T23:55:23Z | 2026-11-02T02:46:38Z |
| 44 | `Cargo` | `event` | startup | 5 | 2026-10-25T18:28:28Z | 2026-11-02T02:53:32Z |
| 45 | `Commander` | `event` | startup | 2 | 2026-10-25T23:55:07Z | 2026-11-02T02:46:19Z |
| 46 | `Fileheader` | `event` | startup | 2 | 2026-10-25T23:53:40Z | 2026-11-02T02:44:37Z |
| 47 | `LoadGame` | `event` | startup | 2 | 2026-10-25T23:55:07Z | 2026-11-02T02:46:19Z |
| 48 | `Loadout` | `event` | startup | 8 | 2026-10-25T23:55:58Z | 2026-11-03T01:35:37Z |
| 49 | `Materials` | `event` | startup | 2 | 2026-10-25T23:55:07Z | 2026-11-02T02:46:19Z |
| 50 | `Missions` | `event` | startup | 2 | 2026-10-25T23:55:58Z | 2026-11-02T02:47:09Z |
| 51 | `Progress` | `event` | startup | 2 | 2026-10-25T23:55:09Z | 2026-11-02T02:46:20Z |
| 52 | `Rank` | `event` | startup | 2 | 2026-10-25T23:55:09Z | 2026-11-02T02:46:20Z |
| 53 | `Reputation` | `event` | startup | 2 | 2026-10-25T23:55:09Z | 2026-11-02T02:46:20Z |
| 54 | `Statistics` | `event` | startup | 2 | 2026-10-25T23:55:54Z | 2026-11-02T02:47:05Z |
| 55 | `BuyAmmo` | `event` | station | 1 | 2026-11-03T01:27:02Z | 2026-11-03T01:27:02Z |
| 56 | `BuyDrones` | `event` | station | 1 | 2026-11-02T02:53:26Z | 2026-11-02T02:53:26Z |
| 57 | `EngineerProgress` | `event` | station | 2 | 2026-10-25T23:55:09Z | 2026-11-02T02:46:20Z |
| 58 | `Market` | `event` | station | 3 | 2026-10-25T18:29:19Z | 2026-11-02T05:01:06Z |
| 59 | `ModuleBuy` | `event` | station | 1 | 2026-11-02T05:00:02Z | 2026-11-02T05:00:02Z |
| 60 | `ModuleRetrieve` | `event` | station | 1 | 2026-11-02T02:57:38Z | 2026-11-02T02:57:38Z |
| 61 | `ModuleSell` | `event` | station | 1 | 2026-11-02T05:00:25Z | 2026-11-02T05:00:25Z |
| 62 | `ModuleStore` | `event` | station | 1 | 2026-11-02T02:57:55Z | 2026-11-02T02:57:55Z |
| 63 | `Outfitting` | `event` | station | 5 | 2026-11-02T02:52:16Z | 2026-11-02T05:00:21Z |
| 64 | `RefuelAll` | `event` | station | 3 | 2026-11-02T04:48:24Z | 2026-11-02T05:07:34Z |
| 65 | `Repair` | `event` | station | 6 | 2026-11-02T02:53:11Z | 2026-11-02T04:57:53Z |
| 66 | `RepairAll` | `event` | station | 1 | 2026-11-03T01:58:18Z | 2026-11-03T01:58:18Z |
| 67 | `SellDrones` | `event` | station | 1 | 2026-11-02T02:53:29Z | 2026-11-02T02:53:29Z |
| 68 | `SetUserShipName` | `event` | station | 3 | 2026-11-03T02:12:42Z | 2026-11-03T02:13:38Z |
| 69 | `Shipyard` | `event` | station | 2 | 2026-10-25T18:33:39Z | 2026-11-03T01:10:20Z |
| 70 | `ShipyardSwap` | `event` | station | 3 | 2026-11-03T01:10:40Z | 2026-11-03T02:14:23Z |
| 71 | `StoredModules` | `event` | station | 7 | 2026-11-02T02:52:16Z | 2026-11-02T05:00:21Z |
| 72 | `StoredShips` | `event` | station | 2 | 2026-11-03T01:10:20Z | 2026-11-03T01:11:04Z |
| 73 | `CARGO_SCOOP_DEPLOYED` | `status_flag` | status | 8 | 2026-11-03T02:15:08.800943Z | 2026-11-03T02:15:12.954112Z |
| 74 | `DOCKED` | `status_flag` | status | 4,555 | 2026-11-02T02:50:31.161318Z | 2026-11-03T02:28:20.325245Z |
| 75 | `FLIGHT_ASSIST_OFF` | `status_flag` | status | 4 | 2026-11-03T01:27:36.126619Z | 2026-11-03T01:53:47.411053Z |
| 76 | `FSD_CHARGING` | `status_flag` | status | 1,283 | 2026-11-02T02:59:25.167970Z | 2026-11-03T01:57:27.972567Z |
| 77 | `FSD_COOLDOWN` | `status_flag` | status | 521 | 2026-11-02T03:00:30.241472Z | 2026-11-03T01:57:58.789570Z |
| 78 | `FSD_MASS_LOCKED` | `status_flag` | status | 5,502 | 2026-11-02T02:50:31.162403Z | 2026-11-03T02:28:20.326172Z |
| 79 | `HARDPOINTS_DEPLOYED` | `status_flag` | status | 887 | 2026-11-02T03:00:54.670187Z | 2026-11-03T01:57:06.661021Z |
| 80 | `HAS_LAT_LONG` | `status_flag` | status | 2,129 | 2026-11-02T04:22:58.466851Z | 2026-11-03T01:48:18.918353Z |
| 81 | `IN_MAIN_SHIP` | `status_flag` | status | 19,409 | 2026-11-02T02:50:31.162715Z | 2026-11-03T02:28:20.326408Z |
| 82 | `IS_IN_DANGER` | `status_flag` | status | 547 | 2026-11-02T03:04:06.149888Z | 2026-11-03T01:58:04.094235Z |
| 83 | `LANDED` | `status_flag` | status | 142 | 2026-11-02T04:26:13.567084Z | 2026-11-03T01:43:05.936466Z |
| 84 | `LANDING_GEAR_DOWN` | `status_flag` | status | 5,232 | 2026-11-02T02:50:31.161750Z | 2026-11-03T02:28:20.325671Z |
| 85 | `LIGHTS_ON` | `status_flag` | status | 11 | 2026-11-03T01:27:17.883106Z | 2026-11-03T01:55:38.237722Z |
| 86 | `NIGHT_VISION` | `status_flag` | status | 8 | 2026-11-03T01:48:01.894414Z | 2026-11-03T01:55:38.232498Z |
| 87 | `SCOOPING_FUEL` | `status_flag` | status | 1,379 | 2026-11-02T03:23:34.328300Z | 2026-11-03T01:50:21.465771Z |
| 88 | `SHIELDS_UP` | `status_flag` | status | 19,310 | 2026-11-02T02:50:31.162095Z | 2026-11-03T02:28:20.325925Z |
| 89 | `SILENT_RUNNING` | `status_flag` | status | 16 | 2026-11-03T02:14:43.018054Z | 2026-11-03T02:15:27.176935Z |
| 90 | `SUPERCRUISE` | `status_flag` | status | 11,227 | 2026-11-02T02:59:36.355466Z | 2026-11-03T01:57:53.403988Z |
| 91 | `COLD` | `status_flag2` | status2 | 69 | 2026-11-02T04:26:58.739754Z | 2026-11-03T01:43:05.923464Z |
| 92 | `GLIDE_MODE` | `status_flag2` | status2 | 130 | 2026-11-02T04:23:58.227921Z | 2026-11-03T01:47:11.877345Z |
| 93 | `ON_FOOT` | `status_flag2` | status2 | 69 | 2026-11-02T04:26:58.739307Z | 2026-11-03T01:43:05.923032Z |
| 94 | `ON_FOOT_EXTERIOR` | `status_flag2` | status2 | 69 | 2026-11-02T04:26:58.739969Z | 2026-11-03T01:43:05.923692Z |
| 95 | `ON_FOOT_ON_PLANET` | `status_flag2` | status2 | 69 | 2026-11-02T04:26:58.739538Z | 2026-11-03T01:43:05.923249Z |
| 96 | `ApproachBody` | `event` | travel | 2 | 2026-11-02T04:23:02Z | 2026-11-02T04:45:04Z |
| 97 | `Docked` | `event` | travel | 3 | 2026-11-02T04:47:06Z | 2026-11-02T05:07:31Z |
| 98 | `DockingGranted` | `event` | travel | 3 | 2026-11-02T04:46:23Z | 2026-11-02T05:07:00Z |
| 99 | `DockingRequested` | `event` | travel | 3 | 2026-11-02T04:46:23Z | 2026-11-02T05:07:00Z |
| 100 | `FSDJump` | `event` | travel | 21 | 2026-11-02T03:23:00Z | 2026-11-02T05:02:53Z |
| 101 | `FSDTarget` | `event` | travel | 27 | 2026-11-02T03:22:12Z | 2026-11-02T05:01:37Z |
| 102 | `LeaveBody` | `event` | travel | 2 | 2026-11-02T04:29:27Z | 2026-11-02T04:53:04Z |
| 103 | `Liftoff` | `event` | travel | 1 | 2026-11-02T04:27:25Z | 2026-11-02T04:27:25Z |
| 104 | `Location` | `event` | travel | 3 | 2026-10-25T23:55:58Z | 2026-11-03T01:09:18Z |
| 105 | `NavRoute` | `event` | travel | 7 | 2026-11-02T03:22:12Z | 2026-11-02T05:01:37Z |
| 106 | `NavRouteClear` | `event` | travel | 7 | 2026-08-14T04:23:02Z | 2026-11-02T05:02:44Z |
| 107 | `StartJump` | `event` | travel | 25 | 2026-11-02T02:59:29Z | 2026-11-02T05:02:34Z |
| 108 | `SupercruiseEntry` | `event` | travel | 4 | 2026-11-02T02:59:34Z | 2026-11-02T04:52:59Z |
| 109 | `SupercruiseExit` | `event` | travel | 5 | 2026-11-02T03:00:25Z | 2026-11-02T05:05:03Z |
| 110 | `Touchdown` | `event` | travel | 1 | 2026-11-02T04:26:12Z | 2026-11-02T04:26:12Z |
| 111 | `Undocked` | `event` | travel | 3 | 2026-11-02T02:58:43Z | 2026-11-02T05:01:37Z |
