---
title: "Architectural Notes: EDMC External API, Datafile Sync, and Manifest Integration Inventory"
tags: ["architecture", "findings", "implications", "edmc", "edastro", "fdevids", "plugins", "ed-connectors", "notes"]
created_at: "2026-10-31"
last_updated_at: "2026-10-31"
---

# Architectural Notes: EDMC External API, Datafile Sync, and Manifest Integration Inventory

## 1. Executive Summary

This architectural note documents the comprehensive inventory of external network communication endpoints, dynamic datafile synchronizations, and upstream repository manifests utilized across *EDMarketConnector (EDMC)*.

These endpoints extend beyond primary telemetry targets (EDDN, Inara, EDSM, CAPI) into auxiliary science relays (EDAstro), data normalization lookup tables (`FDevIDs`), core asset matrices (`ships.json`, `modules.json`), and community extension registries (`EDMC-Plugin-Registry`). This catalog serves as the architectural specification for asset bundling and provider adapter scoping within `ed-connectors` and `ed-schema`.

---

## 2. Technical Analysis

### 2.1 Diagnostic: The Three Functional Tiers

EDMC partitions its network interactions into three distinct operational planes:
1. **Tier 1 (Telemetry Egress & Ingestion):** Active outbound HTTP POST or JSON-RPC dispatch pushing live journal events and starport economics to third-party community networks.
2. **Tier 2 (Dynamic Datafile Sync & Fleet Governance):** Scheduled inbound HTTP GET requests pulling static asset databases, commodity token mapping tables, community plugin lists, and emergency event suppression killswitches.
3. **Tier 3 (Web Interop & Local Tool Export):** URL query parameter formatting for browser-based shipyards and file format serialization for local offline trade/outfitting tools.

---

### 2.2 Theory: Complete Inventory Across Tiers

#### Tier 1: Telemetry Egress & Game State APIs (Active Network Dispatch)

| Service | Target URL | Protocol & Method | Payload & Scope |
| :--- | :--- | :--- | :--- |
| **Frontier CAPI** | `https://companion.orerve.net` | HTTPS GET (Bearer Token) | Private account profile, ship modules, station commodities, and fleet carrier state. |
| **EDDN Gateway** | `https://eddn.edcd.io/upload/` | HTTPS POST (JSON) | Public crowd-sourced market, shipyard, outfitting, and exploration data (Draft 04 schemas). |
| **Inara API v1** | `https://inara.cz/inapi/v1/` | HTTPS POST (JSON-RPC) | Authenticated personal flight log, credit balance, engineering inventory, and fleet ledger. |
| **EDSM Journal API** | `https://www.edsm.net/api-journal-v1` | HTTPS POST (Form + JSON) | Unschematized exploration journal events; discard blacklist polled via `GET /discard`. |
| **EDAstro API** | `https://edastro.com/api/journal` | HTTPS POST (JSON) | Whitelisted fleet carrier jump requests, carrier statistics, and system body discoveries. |

#### Tier 2: Dynamic Datafiles, Upstream Manifests & Control (Inbound Ingestion)

| Asset / Source | Upstream Location | Format | Contents & Operational Role |
| :--- | :--- | :--- | :--- |
| **FDevIDs Commodities** | `https://raw.githubusercontent.com/EDCD/FDevIDs/master/commodity.csv` | CSV | Normalizes Frontier internal token IDs (`$grain_name;`) to English names and categories. |
| **FDevIDs Rare Commodities** | `https://raw.githubusercontent.com/EDCD/FDevIDs/master/rare_commodity.csv` | CSV | Mapping of rare commodities to origin starports and allocation limits. |
| **Modules Database** | `raw.githubusercontent.com/EDCD/EDMarketConnector/.../modules.json` | JSON | Static outfitting database mapping module IDs to slot sizes, classes, and base prices. |
| **Ships Database** | `raw.githubusercontent.com/EDCD/EDMarketConnector/.../ships.json` | JSON | Ship hull specifications, base masses, manufacturer names, and landing pad classes. |
| **Plugin Registry** | `raw.githubusercontent.com/EDCD/EDMC-Plugin-Registry/.../master_plugin_list.json` | JSON | Curated manifest of third-party EDMC community plugins powering the Plugin Browser. |
| **Dynamic Killswitches** | `raw.githubusercontent.com/EDCD/EDMarketConnector/.../killswitches_v2.json` | JSON | Emergency operational control list suppressing buggy or exploited events fleet-wide. |
| **GitHub Releases API** | `https://api.github.com/repos/EDCD/EDMarketConnector/releases` | JSON | Polls application releases for automated version checking and update prompts. |

#### Tier 3: Shipyard, Navigation & Export Interops (Outbound URL Formats)

| Target Service | Integration Type | Destination / Target Format | Functionality |
| :--- | :--- | :--- | :--- |
| **Spansh** | Outbound Web Link | `https://www.spansh.co.uk/{search,system,station}/` | Formats deep links for neutron plotting and system/market lookups. |
| **Coriolis** | Web Import URL | `https://coriolis.io/import?data=` (or beta mirror) | Encodes active ship loadout into URL query parameters. |
| **EDSY** | Web Import URL | `https://edsy.org/` | Encodes active ship build into URL query parameters. |
| **Trade Dangerous** | Local File Export | `Market-<timestamp>.td` | Writes local starport market prices in Trade Dangerous format. |
| **E:D Shipyard** | Local File Export | Plain text loadout `.txt` | Writes ship loadouts formatted for E:D Shipyard. |

---

### 2.3 Analysis: Breakdown of Inbound Datafiles and EDAstro

#### 1. EDAstro Telemetry Egress (`plugins/edastro_core.py`)
EDAstro accepts a strict whitelist of telemetry events to generate galactic heatmaps and fleet carrier traffic lanes without compromising pilot anonymity:
* **Ingested Events:** `CarrierJumpRequest`, `CarrierStats`, `FSSDiscoveryScan`, `FSSAllBodiesFound`.
* **Payload Structure:** Flat JSON envelope containing `timestamp`, `event`, `CarrierID`, `SystemName`, `Body`, and `SystemAddress`.
* **PII Redaction:** Pilot credentials, commander names, account `FID`, credit balances, and loadouts are completely omitted.

#### 2. `EDCD/FDevIDs` Normalization Tables
Frontier Journals and CAPI dumps identify commodities using internal symbolic tokens (e.g. `SyntheticFabrics` or `$syntheticfabrics_name;`). `commodity.csv` acts as the definitive cross-reference ledger:
* Columns: `id`, `symbol`, `category`, `name`.
* Downstream consumer: Translates raw journal symbols into human-readable strings before forwarding to EDDN and Inara.

#### 3. `EDCD/EDMarketConnector` Asset Databases (`modules.json`, `ships.json`)
Local game journal events emit equipped modules as internal IDs without hull mass properties:
* `ships.json`: Supplies base hull mass (necessary to calculate jump range and unladen mass) and landing pad size (`small`, `medium`, `large`).
* `modules.json`: Supplies outfitting module human titles, class, rating, mass, and default retail prices.

#### 4. `EDCD/EDMC-Plugin-Registry`
A centrally governed repository maintaining `master_plugin_list.json`:
* Structure: Dictionary of plugin objects containing `pluginName`, `pluginDescription`, `pluginAuthor`, `pluginMainLink`, `pluginHash`, and download tarball URLs.
* Security: Supplies sha256 checksums to verify plugin integrity upon download.

---

### 2.4 Remediation: Architectural Implications for `ed-connectors` & `ed-schema`

1. **Auxiliary EDAstro Provider:** EDAstro maps directly to `SchemaKey("edastro", "/api/journal", None, None)` as a 1:1 direct REST endpoint with a minimal Draft 2020-12 schema.
2. **Build-Time Asset Bundling:** `ed-schema` or `ed-connectors` should vendor `ships.json`, `modules.json`, and `commodity.csv` as version-locked static data packages rather than executing unauthenticated runtime GitHub downloads on startup.
3. **Emergency Redaction Port:** A lightweight `KillswitchPort` should be considered for `ed-connectors` to dynamically disable dispatch for compromised journal events without requiring client application updates.
