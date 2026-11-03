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
* **Total Recorded Hits:** 504,981
* **Validation Engine:** `ed-models` v0.2.1

## Achieved Target Ledger

| # | Target Identifier | Type | Chapter | Hit Count | First Seen | Last Seen |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| 1 | `CarrierBankTransfer` | `event` | carrier | 226 | 2026-11-03T01:26:23.605569Z | 2026-11-03T02:28:24.465274Z |
| 2 | `CarrierCrewServices` | `event` | carrier | 92 | 2026-11-03T02:11:21.866746Z | 2026-11-03T02:28:29.649053Z |
| 3 | `CarrierDepositFuel` | `event` | carrier | 127 | 2026-11-03T01:34:38.074870Z | 2026-11-03T02:28:26.509918Z |
| 4 | `CarrierFinance` | `event` | carrier | 597 | 2026-11-03T01:54:57.838707Z | 2026-11-03T02:28:28.606785Z |
| 5 | `CarrierJumpRequest` | `event` | carrier | 183 | 2026-11-02T04:33:07.897829Z | 2026-11-03T01:51:22.478745Z |
| 6 | `CarrierLocation` | `event` | carrier | 4,805 | 2026-11-02T03:20:29.630263Z | 2026-11-03T02:28:21.359122Z |
| 7 | `CarrierStats` | `event` | carrier | 2,454 | 2026-11-02T03:20:45.057010Z | 2026-11-03T02:28:28.631709Z |
| 8 | `Bounty` | `event` | combat | 441 | 2026-11-03T01:22:00.969423Z | 2026-11-03T02:28:27.559729Z |
| 9 | `HeatWarning` | `event` | combat | 266 | 2026-11-03T01:56:18.637435Z | 2026-11-03T02:28:27.559232Z |
| 10 | `ShieldState` | `event` | combat | 53 | 2026-11-03T02:14:57.535171Z | 2026-11-03T02:28:30.681427Z |
| 11 | `ShipTargeted` | `event` | combat | 25,607 | 2026-11-02T03:20:51.722399Z | 2026-11-03T02:28:28.598948Z |
| 12 | `UnderAttack` | `event` | combat | 751 | 2026-11-03T01:18:56.678553Z | 2026-11-03T02:28:27.558718Z |
| 13 | `DiscoveryScan` | `event` | exploration | 327 | 2026-11-02T04:07:37.655535Z | 2026-11-03T01:51:21.406811Z |
| 14 | `FSSAllBodiesFound` | `event` | exploration | 1,641 | 2026-11-02T03:32:11.206621Z | 2026-11-03T01:51:21.437395Z |
| 15 | `FSSBodySignals` | `event` | exploration | 858 | 2026-11-02T03:21:13.961270Z | 2026-11-03T01:51:19.233097Z |
| 16 | `FSSDiscoveryScan` | `event` | exploration | 2,520 | 2026-11-02T03:21:10.657725Z | 2026-11-03T02:28:23.420366Z |
| 17 | `FSSSignalDiscovered` | `event` | exploration | 73,881 | 2026-11-02T03:20:30.686297Z | 2026-11-03T02:28:22.394030Z |
| 18 | `NavBeaconScan` | `event` | exploration | 1,099 | 2026-11-02T03:20:50.599785Z | 2026-11-03T01:51:18.179920Z |
| 19 | `SAAScanComplete` | `event` | exploration | 1,846 | 2026-11-02T03:21:07.309300Z | 2026-11-03T01:51:21.410852Z |
| 20 | `SAASignalsFound` | `event` | exploration | 634 | 2026-11-02T04:07:25.169116Z | 2026-11-03T01:51:21.411116Z |
| 21 | `Scan` | `event` | exploration | 51,756 | 2026-11-02T04:22:41.597314Z | 2026-11-03T01:51:22.498124Z |
| 22 | `ScanBaryCentre` | `event` | exploration | 2,498 | 2026-11-02T03:20:50.610190Z | 2026-11-03T01:51:21.376400Z |
| 23 | `Backpack` | `event` | odyssey | 476 | 2026-11-02T03:20:29.596915Z | 2026-11-03T01:51:28.879657Z |
| 24 | `DeleteSuitLoadout` | `event` | odyssey | 278 | 2026-11-02T04:27:19.873037Z | 2026-11-03T01:51:21.415728Z |
| 25 | `Disembark` | `event` | odyssey | 278 | 2026-11-02T04:27:19.873514Z | 2026-11-03T01:51:21.415971Z |
| 26 | `Embark` | `event` | odyssey | 278 | 2026-11-02T04:27:19.889786Z | 2026-11-03T01:51:21.418084Z |
| 27 | `ShipLocker` | `event` | odyssey | 24,172 | 2026-11-02T03:20:29.599063Z | 2026-11-03T02:28:30.675853Z |
| 28 | `SuitLoadout` | `event` | odyssey | 278 | 2026-11-02T04:27:19.874045Z | 2026-11-03T01:51:21.416211Z |
| 29 | `SwitchSuitLoadout` | `event` | odyssey | 282 | 2026-11-02T04:27:12.177707Z | 2026-11-03T01:51:21.415476Z |
| 30 | `ApproachSettlement` | `event` | other | 77 | 2026-11-02T04:45:29.294418Z | 2026-11-03T01:51:24.613994Z |
| 31 | `CargoTransfer` | `event` | other | 254 | 2026-11-03T01:34:16.549175Z | 2026-11-03T02:28:26.510413Z |
| 32 | `Friends` | `event` | other | 504 | 2026-11-02T03:20:29.608447Z | 2026-11-03T01:38:15.266924Z |
| 33 | `FuelScoop` | `event` | other | 6,951 | 2026-11-02T03:23:36.370150Z | 2026-11-03T01:51:27.829303Z |
| 34 | `ModuleInfo` | `event` | other | 1,650 | 2026-11-02T03:20:29.596240Z | 2026-11-03T02:28:30.677040Z |
| 35 | `Music` | `event` | other | 58,734 | 2026-11-02T03:20:30.690872Z | 2026-11-03T02:28:30.681183Z |
| 36 | `ReceiveText` | `event` | other | 25,338 | 2026-11-02T03:20:30.685822Z | 2026-11-03T02:28:30.688821Z |
| 37 | `ReservoirReplenished` | `event` | other | 3,770 | 2026-11-02T03:21:16.133415Z | 2026-11-03T02:28:24.459073Z |
| 38 | `Scanned` | `event` | other | 1,286 | 2026-11-02T03:20:56.128015Z | 2026-11-03T02:28:28.595168Z |
| 39 | `Shutdown` | `event` | other | 15 | 2026-11-02T05:08:17.817997Z | 2026-11-03T02:28:31.700324Z |
| 40 | `Status` | `event` | other | 20,595 | 2026-11-02T02:50:31.163050Z | 2026-11-03T02:32:42.322282Z |
| 41 | `SupercruiseDestinationDrop` | `event` | other | 1,915 | 2026-11-02T03:20:48.440549Z | 2026-11-03T02:28:28.607073Z |
| 42 | `USSDrop` | `event` | other | 93 | 2026-11-03T01:55:41.414177Z | 2026-11-03T02:28:27.546438Z |
| 43 | `SquadronStartup` | `event` | squadrons | 2,378 | 2026-11-02T03:20:29.637746Z | 2026-11-03T02:28:21.358878Z |
| 44 | `Cargo` | `event` | startup | 5,980 | 2026-11-02T03:20:29.595138Z | 2026-11-03T02:28:26.510713Z |
| 45 | `Commander` | `event` | startup | 2,418 | 2026-11-02T03:20:29.605611Z | 2026-11-03T02:28:21.356391Z |
| 46 | `Fileheader` | `event` | startup | 2,428 | 2026-11-02T03:20:29.607802Z | 2026-11-03T02:28:21.356142Z |
| 47 | `LoadGame` | `event` | startup | 2,408 | 2026-11-02T03:20:29.611861Z | 2026-11-03T02:28:21.357896Z |
| 48 | `Loadout` | `event` | startup | 6,106 | 2026-11-02T03:20:30.692569Z | 2026-11-03T02:28:30.676550Z |
| 49 | `Materials` | `event` | startup | 2,418 | 2026-11-02T03:20:29.606396Z | 2026-11-03T02:28:21.356648Z |
| 50 | `Missions` | `event` | startup | 2,349 | 2026-11-02T03:20:30.691918Z | 2026-11-03T02:28:22.395720Z |
| 51 | `Progress` | `event` | startup | 2,402 | 2026-11-02T03:20:29.622194Z | 2026-11-03T02:28:21.357143Z |
| 52 | `Rank` | `event` | startup | 2,402 | 2026-11-02T03:20:29.621665Z | 2026-11-03T02:28:21.356896Z |
| 53 | `Reputation` | `event` | startup | 2,402 | 2026-11-02T03:20:29.622709Z | 2026-11-03T02:28:21.357387Z |
| 54 | `Statistics` | `event` | startup | 2,364 | 2026-11-02T03:20:30.676462Z | 2026-11-03T02:28:21.358630Z |
| 55 | `BuyAmmo` | `event` | station | 291 | 2026-11-03T01:27:06.552703Z | 2026-11-03T02:28:28.615734Z |
| 56 | `BuyDrones` | `event` | station | 1,540 | 2026-11-02T03:20:38.319442Z | 2026-11-03T01:51:18.164897Z |
| 57 | `EngineerProgress` | `event` | station | 2,402 | 2026-11-02T03:20:29.623219Z | 2026-11-03T02:28:21.357642Z |
| 58 | `Market` | `event` | station | 2,139 | 2026-11-02T03:20:29.595661Z | 2026-11-03T01:51:28.880146Z |
| 59 | `ModuleBuy` | `event` | station | 26 | 2026-11-02T05:05:11.318389Z | 2026-11-03T01:51:26.736202Z |
| 60 | `ModuleRetrieve` | `event` | station | 1,441 | 2026-11-02T03:20:40.545222Z | 2026-11-03T01:51:18.166320Z |
| 61 | `ModuleSell` | `event` | station | 26 | 2026-11-02T05:05:11.321383Z | 2026-11-03T01:51:26.739959Z |
| 62 | `ModuleStore` | `event` | station | 1,241 | 2026-11-02T03:20:41.706262Z | 2026-11-03T01:51:18.170503Z |
| 63 | `Outfitting` | `event` | station | 5,064 | 2026-11-02T03:20:36.194391Z | 2026-11-03T02:28:29.650125Z |
| 64 | `RefuelAll` | `event` | station | 410 | 2026-11-02T04:48:26.201285Z | 2026-11-03T02:28:30.681919Z |
| 65 | `Repair` | `event` | station | 3,281 | 2026-11-02T03:20:37.251664Z | 2026-11-03T02:28:30.672571Z |
| 66 | `RepairAll` | `event` | station | 71 | 2026-11-03T01:58:29.299472Z | 2026-11-03T02:28:28.615976Z |
| 67 | `SellDrones` | `event` | station | 1,524 | 2026-11-02T03:20:38.366782Z | 2026-11-03T01:51:18.165369Z |
| 68 | `SetUserShipName` | `event` | station | 96 | 2026-11-03T02:12:54.734513Z | 2026-11-03T02:28:30.674361Z |
| 69 | `Shipyard` | `event` | station | 1,214 | 2026-11-02T03:20:29.597589Z | 2026-11-03T02:28:30.674874Z |
| 70 | `ShipyardSwap` | `event` | station | 1,002 | 2026-11-03T01:10:40.989135Z | 2026-11-03T02:28:30.675607Z |
| 71 | `StoredModules` | `event` | station | 6,934 | 2026-11-02T03:20:37.234292Z | 2026-11-03T02:28:29.650401Z |
| 72 | `StoredShips` | `event` | station | 1,011 | 2026-11-03T01:10:20.690584Z | 2026-11-03T02:28:30.675119Z |
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
| 96 | `ApproachBody` | `event` | travel | 379 | 2026-11-02T04:26:55.521391Z | 2026-11-03T01:51:24.613473Z |
| 97 | `Docked` | `event` | travel | 430 | 2026-11-02T04:47:07.345306Z | 2026-11-03T02:28:30.680941Z |
| 98 | `DockingGranted` | `event` | travel | 444 | 2026-11-02T04:46:48.067870Z | 2026-11-03T02:28:30.679509Z |
| 99 | `DockingRequested` | `event` | travel | 448 | 2026-11-02T04:46:48.066401Z | 2026-11-03T02:28:30.678776Z |
| 100 | `FSDJump` | `event` | travel | 7,214 | 2026-11-02T03:23:01.604123Z | 2026-11-03T01:51:27.826236Z |
| 101 | `FSDTarget` | `event` | travel | 10,883 | 2026-11-02T03:22:23.694859Z | 2026-11-03T01:51:26.744005Z |
| 102 | `LeaveBody` | `event` | travel | 256 | 2026-11-02T04:29:29.565444Z | 2026-11-03T01:51:26.722158Z |
| 103 | `Liftoff` | `event` | travel | 231 | 2026-11-02T04:27:38.670222Z | 2026-11-03T01:51:21.421657Z |
| 104 | `Location` | `event` | travel | 2,349 | 2026-11-02T03:20:30.690308Z | 2026-11-03T02:28:22.394961Z |
| 105 | `NavRoute` | `event` | travel | 3,680 | 2026-11-02T03:22:13.344769Z | 2026-11-03T01:51:26.743743Z |
| 106 | `NavRouteClear` | `event` | travel | 2,643 | 2026-11-02T03:20:29.598375Z | 2026-11-03T01:51:28.879408Z |
| 107 | `StartJump` | `event` | travel | 10,508 | 2026-11-02T03:20:47.287957Z | 2026-11-03T02:28:28.599230Z |
| 108 | `SupercruiseEntry` | `event` | travel | 3,052 | 2026-11-02T03:20:48.391217Z | 2026-11-03T02:28:28.599735Z |
| 109 | `SupercruiseExit` | `event` | travel | 2,257 | 2026-11-02T03:20:50.587426Z | 2026-11-03T02:28:28.607585Z |
| 110 | `Touchdown` | `event` | travel | 286 | 2026-11-02T04:27:07.809226Z | 2026-11-03T01:51:21.415231Z |
| 111 | `Undocked` | `event` | travel | 1,691 | 2026-11-02T03:20:45.097438Z | 2026-11-03T02:28:30.677806Z |
