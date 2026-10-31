---
title: "ADR 0001: ed-models Pure Domain Architecture, Catalog Codification, and Driving Facade"
tags: ["adr", "ed-models", "hexagonal-architecture", "domain-driven-design", "catalogs", "normalization"]
created_at: "2026-10-31"
last_updated_at: "2026-10-31"
---

# ADR 0001: ed-models Pure Domain Architecture, Catalog Codification, and Driving Facade

* **Status:** Proposed
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-10-31

---

## 1. Context and Problem Statement

Across the *Elite Dangerous* software fleet (`ed-telemetry`, `ed-transport`, `ed-schema`, `ed-connector`), companion applications require rich representations of game entities:
- Frontier Journal events (`FSDJump`, `CarrierStats`, `Market`, `ScanOrganic`).
- Game domain objects (Ships, Outfitting Modules, Commodities, Minor Factions, Powerplay states).
- Normalization tables translating internal Frontier tokens (`$grain_name;`) to canonical game terms.
- Static specifications (hull mass, landing pad size classes, module masses/ratings) missing from raw journal logs.

Currently, data definitions are fragmented across external CSVs, ad-hoc Python dictionaries, and third-party API wire DTOs. 

We need a centralized, deterministic domain foundation: the planned **`ed-models`** library. We must establish its operational boundaries, ensure it remains strictly decoupled from network transport and third-party wire formats, and define its external integration surface.

---

## 2. Decision Drivers

* **Pure Domain Boundary:** The library must be 100% focused on game logic and domain entities, completely free of network I/O, HTTP clients, ZeroMQ sockets, or transport protocol logic.
* **Separation of Domain vs. Wire:** Wire DTOs and remote API contracts (EDDN schemas, Inara InAPI DTOs, Spansh OpenAPI models, CAPI schemas) belong in `ed-schema` and `ed-transport`, not in `ed-models`.
* **Zero Runtime Network Requirement:** Must provide 100% offline functionality out-of-the-box by bundling pre-compiled static catalogs.
* **Library Package (Not Standalone):** `ed-models` will not have a CLI, daemon, or standalone application runner; it will be an embedded dependency library.
* **Hexagonal Architecture:** Must expose a clean, unified driving facade adapter (`ModelsFacade`) hiding internal collection structures and normalization mechanisms.

---

## 3. Considered Options

* **Option 1: Monolithic Domain & Wire Library.** Combine game domain entities with external API DTOs (EDDN, Inara, Spansh, CAPI) in a single package.
* **Option 2: Raw Datafile Consumer.** Have `ed-models` read raw CSV/JSON files from disk on every invocation at runtime.
* **Option 3: Pure Hexagonal Domain Library with Compiled Static Catalogs and Driving Facade (Selected).** Codify all game logic, raw journal event definitions, enums, and static catalogs into immutable Python types, exposed via a `ModelsFacade`.

---

## 4. Decision Outcome

**Chosen Option:** **Option 3: Pure Hexagonal Domain Library with Compiled Static Catalogs and Driving Facade.**

### 4.1 Boundary Invariants
1. **No External I/O or Wire Schemas:** `ed-models` will contain **zero** references to EDDN, Inara InAPI, Spansh REST endpoints, or Frontier CAPI wire wrappers. It models the *in-game universe* as defined by Frontier Developments, not external web servers.
2. **Library-Only Packaging:** Distributed strictly as an installable Python library (`pyproject.toml`). No CLI console scripts, daemons, or executable entry points.
3. **Pre-Compiled Static Catalogs:** Tabular community datafiles (`commodity.csv`, `ships.json`, `modules.json`) are compiled into frozen dataclasses and `StrEnum` instances at build time (as detailed in Note 0006).
4. **Primary Responsibility for Game Emission Models:** `ed-models` is the **canonical owner of all game-emitted event models** across three distinct source file types:
   - **Journal Event Streams (`Journal.<timestamp>.log`):** Strongly typed models for discrete events (`FsdJumpEvent`, `LocationEvent`, `CarrierStatsEvent`, `ScanOrganicEvent`).
   - **Station & Market Snapshots (`Market.json`, `Outfitting.json`, `Shipyard.json`, `Cargo.json`, `NavRoute.json`):** Strongly typed state snapshots capturing starport market quotes, shipyards, outfitting inventories, and planned navigation routes.
   - **Real-Time Status Telemetry (`Status.json`):** Strongly typed vehicle status models unpacking raw 32-bit integer flags bitfields into ergonomic booleans (`status.flags.landing_gear_down`, `shields_up`, `in_supercruise`) and pips/fuel telemetry.
5. **Decoupled Boundary with `ed-schema`:**
   - **`ed-schema` Owns the Rules (Validation):** Houses Draft 04/07/2020-12 JSON Schemas verifying that raw JSON text emitted by the game or APIs is well-formed.
   - **`ed-models` Owns the Objects (Domain & Logic):** Houses the strongly typed Python dataclasses that instantiate validated dictionaries into routable, portable objects for consumption by `ed-connector` and `ed-router`.

### 4.2 Architecture Structure

```mermaid
flowchart TD
    subgraph Consumers ["Fleet Consumers"]
        Telemetry["ed-telemetry\n(Log Parsing)"]
        Connector["ed-connector\n(Desktop Client & Cache)"]
        Router["ed-router\n(Pathfinding)"]
    end

    subgraph EdModels ["ed-models (Pure Domain Library)"]
        Facade["ModelsFacade (Driving Adapter)"]

        subgraph CoreDomain ["Core Domain & Events"]
            Events["Journal Event Models\n(FSDJump, Market, ScanOrganic)"]
            Entities["Domain Entities\n(Ship, Module, Commodity, System)"]
            Enums["Domain Enums\n(PadSize, Rating, Economy, Power)"]
        end

        subgraph Catalogs ["Compiled Static Catalogs"]
            CommodityCat["Commodity Catalog & Normalizer"]
            ShipCat["Ship Hull Specifications Catalog"]
            ModuleCat["Outfitting Module Catalog"]
        end

        subgraph Interop ["Local Interop Serializers"]
            TDSerializer["Trade Dangerous .td Serializer"]
            CoriolisSerializer["Coriolis Loadout Serializer"]
        end

        Facade --> CoreDomain
        Facade --> Catalogs
        Facade --> Interop
    end

    Consumers -->|Import & Invoke| Facade
```

### 4.3 Driving Facade Contract

`ed-models` exposes a unified entry point:

```python
from ed_models import ModelsFacade, create_models_facade

facade: ModelsFacade = create_models_facade()

# 1. Deterministic Token Normalization (FDevIDs)
commodity = facade.normalize_commodity("$grain_name;")
# -> Commodity(symbol="Grain", category=CommodityCategory.FOODS, id=128049102)

# 2. Static Domain Catalog Lookups
hull_spec = facade.get_ship_spec("anaconda")
# -> ShipHull(symbol="Anaconda", base_mass=400.0, pad_size=PadSize.LARGE)

module_spec = facade.get_module_spec(128049382)
# -> ShipModule(name="5A Frame Shift Drive", class_num=5, rating="A", mass=20.0)

# 3. Strongly Typed Journal Event Deserialization
event = facade.parse_journal_event(raw_json_dict)
# -> FSDJumpEvent(...)
```

### 4.4 Domain Area Scope & Storage Boundary Matrix

To guarantee a lightweight Python package (under 2 MB distribution footprint and under 10 MB active RAM usage), `ed-models` enforces an absolute architectural distinction between **Domain Definitions (Static Code & Blueprints)** and **External Datasets (Databases & Cloud Storage)**:

| Domain Area | ✅ WHAT IS IN `ed-models` (Static Code & Blueprints) | ❌ WHAT IS NOT IN `ed-models` (External Storage / Cloud) | Required Python Data Structures & Classes |
|---|---|---|---|
| **Star Systems & Bodies** | • `StarSystem` & `CelestialBody` dataclasses.<br>• `StarType`, `AtmosphereType`, `Volcanism` enums.<br>• Coordinate math: `Distance(sysA, sysB)`. | • The 200M system database (stored in Spansh, EDSM, or local SQLite). | • `StarSystem`, `CelestialBody`, `AtmosphereComposition`<br>• `Coordinates3D` (frozen tuple/dataclass)<br>• `StarType(StrEnum)`, `BodyType(StrEnum)`, `TerraformState(StrEnum)`<br>• `SystemDistanceCalculator` (pure math) |
| **Commodities** | • Complete static `CommodityCatalog` (~450 items, tiny ~30 KB).<br>• `CommodityCategory` enum.<br>• Token normalizer (`$grain_name;` $\rightarrow$ `Grain`). | • Real-time fluctuating starport prices and stock supplies (queried via EDDN/Inara). | • `CommodityEntity` (canonical record)<br>• `CommodityCategory(StrEnum)`, `CommoditySymbol(StrEnum)`<br>• `CommodityCatalog` (frozen mapping table)<br>• `CommodityNormalizer` (token resolution engine) |
| **Ships & Outfitting** | • Complete static `ShipCatalog` (all 48 flyable ships + base hull mass + pad size).<br>• Complete static `ModuleCatalog` (~150 module specs, slot sizes, ratings). | • The player's active ship inventory or remote fleet carrier cargo (managed in session state). | • `ShipHull`, `ShipModule`, `SlotSpec`<br>• `PadSize(StrEnum)`, `ModuleRating(StrEnum)`, `ModuleClass(IntEnum)`<br>• `ShipCatalog` (immutable dict of all 48 hulls)<br>• `ModuleCatalog` (immutable dict of module specs)<br>• `ShipNormalizer` (slug resolution: `"empire_trader"` $\rightarrow$ `"Imperial Clipper"`) |
| **Journal Events & Telemetry** | • Strongly typed models for all ~100 Frontier Journal events (`FSDJump`, `Scan`, `CarrierJumpRequest`).<br>• Snapshot & Status models. | • The historical log files on the player's disk (read by `ed-telemetry`). | • `JournalEvent` (abstract base class)<br>• `FsdJumpEvent`, `LocationEvent`, `CarrierStatsEvent`, etc.<br>• `MarketSnapshot`, `OutfittingSnapshot`, `NavRouteSnapshot`<br>• `ShipStatus` (with `StatusFlags` bitfield unpacker) |
| **Factions & Politics** | • `Government`, `Allegiance`, `PowerState` enums.<br>• `MinorFaction` & `Powerplay` models. | • Galaxy-wide BGS influence percentages and current expansion states. | • `MinorFactionPresence`, `PowerplayState`<br>• `Government(StrEnum)`, `Allegiance(StrEnum)`, `PowerState(StrEnum)`<br>• `SecurityLevel(StrEnum)`, `EconomyType(StrEnum)` |
| **Calculators & Interop** | • Ship mass & jump range formula.<br>• Coriolis JSON & Trade Dangerous `.td` serializers. | • The network requests to Spansh or Inara. | • `ShipLoadout`, `JumpRangeProfile`<br>• `JumpRangeCalculator` (Frontier FSD formula)<br>• `TradeDangerousMarketRecord` & `TradeDangerousFormatter`<br>• `CoriolisLoadoutDTO` & `CoriolisSerializer` |

### 4.5 Codified Python Data Structure Specifications

The following subsections codify the concrete Python implementations for each domain category in `ed-models`.

#### 4.5.1 Star Systems & Celestial Bodies (`ed_models.domain.systems`)

```python
from dataclasses import dataclass
from enum import StrEnum
import math

class StarType(StrEnum):
    O = "O"
    B = "B"
    A = "A"
    F = "F"
    G = "G"
    K = "K"
    M = "M"
    NEUTRON = "N"
    BLACK_HOLE = "H"

class BodyType(StrEnum):
    STAR = "Star"
    PLANET = "Planet"
    MOON = "Moon"
    ASTEROID_RING = "AsteroidRing"

@dataclass(frozen=True, slots=True)
class Coordinates3D:
    x: float
    y: float
    z: float

    def distance_to(self, other: "Coordinates3D") -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

@dataclass(frozen=True, slots=True)
class CelestialBody:
    id64: int
    body_id: int
    name: str
    body_type: BodyType
    distance_to_arrival_ls: float
    is_landable: bool = False
    gravity_g: float | None = None
    earth_masses: float | None = None

@dataclass(frozen=True, slots=True)
class StarSystem:
    id64: int
    name: str
    coords: Coordinates3D
    population: int = 0
    main_star: StarType | None = None
    bodies: tuple[CelestialBody, ...] = ()
```

#### 4.5.2 Commodities & Normalization (`ed_models.domain.commodities`)

```python
from dataclasses import dataclass
from enum import StrEnum

class CommodityCategory(StrEnum):
    CHEMICALS = "Chemicals"
    CONSUMER_ITEMS = "Consumer Items"
    FOODS = "Foods"
    INDUSTRIAL_MATERIALS = "Industrial Materials"
    LEGAL_DRUGS = "Legal Drugs"
    MACHINERY = "Machinery"
    MEDICINES = "Medicines"
    METALS = "Metals"
    MINERALS = "Minerals"
    SALVAGE = "Salvage"
    TECHNOLOGY = "Technology"
    TEXTILES = "Textiles"
    WASTE = "Waste"
    WEAPONS = "Weapons"

@dataclass(frozen=True, slots=True)
class CommodityEntity:
    id: int
    symbol: str
    category: CommodityCategory
    name: str

class CommodityNormalizer:
    def __init__(self, catalog: dict[str, CommodityEntity]):
        self._lookup = catalog

    def normalize(self, token: str) -> CommodityEntity | None:
        clean = token.lower().strip("$").removesuffix("_name;").strip()
        return self._lookup.get(clean)
```

#### 4.5.3 Ships & Outfitting Modules (`ed_models.domain.ships`)

```python
from dataclasses import dataclass
from enum import IntEnum, StrEnum

class PadSize(StrEnum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"

class ModuleRating(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"

class ModuleClass(IntEnum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8

@dataclass(frozen=True, slots=True)
class ShipHull:
    symbol: str
    name: str
    manufacturer: str
    pad_size: PadSize
    base_hull_mass: float

@dataclass(frozen=True, slots=True)
class ShipModule:
    id: int
    symbol: str
    name: str
    class_num: ModuleClass
    rating: ModuleRating
    mass_tons: float
    base_cost_cr: int

class ShipNormalizer:
    def __init__(self, hulls: dict[str, ShipHull]):
        self._hulls = hulls

    def normalize(self, internal_slug: str) -> ShipHull | None:
        return self._hulls.get(internal_slug.lower().strip())
```

#### 4.5.4 Journal Events, Snapshots & Status Telemetry (`ed_models.domain.events`)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass(frozen=True, slots=True)
class JournalEvent:
    timestamp: datetime
    event: str

@dataclass(frozen=True, slots=True)
class FsdJumpEvent(JournalEvent):
    star_system: str
    system_address: int
    star_pos: tuple[float, float, float]
    jump_dist: float
    fuel_used: float
    fuel_level: float

@dataclass(frozen=True, slots=True)
class StatusFlags:
    docked: bool
    landed: bool
    landing_gear_down: bool
    shields_up: bool
    supercruise: bool
    flight_assist_off: bool
    hardpoints_deployed: bool
    lights_on: bool
    night_vision: bool

    @classmethod
    def from_bitfield(cls, flags: int) -> "StatusFlags":
        return cls(
            docked=bool(flags & (1 << 0)),
            landed=bool(flags & (1 << 1)),
            landing_gear_down=bool(flags & (1 << 2)),
            shields_up=bool(flags & (1 << 3)),
            supercruise=bool(flags & (1 << 4)),
            flight_assist_off=bool(flags & (1 << 5)),
            hardpoints_deployed=bool(flags & (1 << 6)),
            lights_on=bool(flags & (1 << 8)),
            night_vision=bool(flags & (1 << 28)),
        )

@dataclass(frozen=True, slots=True)
class ShipStatus:
    timestamp: datetime
    flags: StatusFlags
    pips: tuple[float, float, float]
    firegroup: int
    fuel_main_tons: float
    fuel_reservoir_tons: float
    gui_focus: int
```

#### 4.5.5 Factions, Politics & System States (`ed_models.domain.factions`)

```python
from dataclasses import dataclass
from enum import StrEnum

class Allegiance(StrEnum):
    FEDERATION = "Federation"
    EMPIRE = "Empire"
    ALLIANCE = "Alliance"
    INDEPENDENT = "Independent"

class Government(StrEnum):
    DEMOCRACY = "Democracy"
    CORPORATE = "Corporate"
    ANARCHY = "Anarchy"
    PATRONAGE = "Patronage"
    COMMUNISM = "Communism"

class PowerState(StrEnum):
    CONTROL = "Control"
    EXPLOITED = "Exploited"
    EXPANSION = "Expansion"

@dataclass(frozen=True, slots=True)
class MinorFactionPresence:
    name: str
    faction_state: str
    influence: float
    allegiance: Allegiance
    government: Government
```

#### 4.5.6 Calculators & Interop Formats (`ed_models.domain.interop`)

```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True, slots=True)
class JumpRangeProfile:
    unladen_ly: float
    laden_ly: float
    max_single_jump_ly: float

@dataclass(frozen=True, slots=True)
class TradeDangerousMarketRecord:
    system_name: str
    station_name: str
    market_id: int
    commodity_name: str
    sell_price_cr: int
    buy_price_cr: int
    demand: int
    stock: int

class TradeDangerousFormatter:
    @staticmethod
    def format_td(records: list[TradeDangerousMarketRecord], timestamp_str: str) -> str:
        if not records:
            return ""
        first = records[0]
        lines = [
            "# Trade Dangerous Market Export",
            f"# Generated at {timestamp_str}",
            f"@ System: {first.system_name}",
            f"+ Station: {first.station_name}",
            f"$ MarketId: {first.market_id}",
            "# Commodity               Sell        Buy       Demand      Stock",
        ]
        for r in records:
            lines.append(f"{r.commodity_name:<24} {r.sell_price_cr:>8} {r.buy_price_cr:>10} {r.demand:>12} {r.stock:>10}")
        return "\n".join(lines) + "\n"
```

### 4.6 Data Structure Typing & Classification Rules

To prevent arbitrary or ad-hoc modeling decisions, all data structures authored within `ed-models` must strictly adhere to the following deterministic classification matrix and filter rules.

#### 4.6.1 Classification Decision Matrix

| Data Characteristic | Target Python Construct | Governing Criteria / Justification | Elite Dangerous Domain Examples |
| :--- | :--- | :--- | :--- |
| **Fixed FDev Canonical Enum** | `enum.StrEnum` (Python 3.11+) | Discrete, bounded set ($\le 50$ items) defined by Frontier. Serializes transparently to native JSON string values without custom serializers. | `Allegiance` (`Federation`, `Empire`), `PadSize` (`S`, `M`, `L`), `StarType`, `BodyType` |
| **Telemetry Hardware State / Bitmask** | `enum.IntFlag` | Compact integer bitfields where multiple states coexist simultaneously. Requires bitwise operators (`&`, `\|`, `~`). | `StatusFlags` (Telemetry `Flags`), `StatusFlags2` (Odyssey `Flags2`) |
| **Read-Only Mathematical / Spatial Struct** | `@dataclass(frozen=True, slots=True)` | Immutable numeric coordinates or physics tuples. Zero mutations allowed, value equality semantics, memory-optimized. | `Coordinates3D` (`x, y, z`), `SystemAddress`, bounding boxes |
| **Dynamic Domain Entity with Identity** | `@dataclass(slots=True)` | Stateful game entity possessing a unique primary key / symbol, attributes, and internal helper methods. | `ShipHull`, `CelestialBody`, `MinorFactionPresence` |
| **Polymorphic Event / Wire Message** | `@dataclass(kw_only=True)` | Event hierarchy inheriting from base `JournalEvent` (`timestamp`, `event`). `kw_only=True` avoids default-value ordering conflicts. | `FsdJumpEvent`, `ScanEvent`, `MarketBuyEvent`, `LocationEvent` |
| **Open / Evolving Game Taxonomy** | Canonical String Symbol (`str`) | Vast, expanding catalogs ($> 100$ items) modified by game patches. Enums risk deserialization crashes on unknown items; strings backed by catalog lookups preserve safety. | `CommoditySymbol` (`str`), `ModuleSymbol` (`str`), `EngineeringBlueprintId` |

#### 4.6.2 The Four Deterministic Filter Rules

1. **The Closed-Set Test (Enum vs. String Symbol):**
   * If Frontier's documentation specifies a fixed, bounded vocabulary that does not change between minor patches $\rightarrow$ **`StrEnum`**.
   * If Frontier frequently adds new items in content updates (commodities, rare goods, engineering modifications, suits, weapons) $\rightarrow$ **Canonical String Symbol (`str`)** backed by an $O(1)$ catalog lookup dictionary.

2. **The Serialization Test (`StrEnum` vs. Standard `Enum`):**
   * Standard `Enum` serializes as a complex object and crashes native JSON unmarshaling (`json.dumps`).
   * All discrete categorical string sets MUST inherit from `StrEnum` so that string comparisons, hashing, and wire serialization function seamlessly without conversion adapters.

3. **The Mutability & Allocation Test (`frozen=True, slots=True` vs. Standard `@dataclass`):**
   * If an object has no valid state transitions after hydration $\rightarrow$ **`frozen=True, slots=True`** (reduces Python object memory overhead by ~60% and enforces mathematical immutability).
   * If an object aggregates child state over time (e.g. ship loadout module swapping, station inventory updates) $\rightarrow$ **Standard `@dataclass(slots=True)`**.

4. **The Event Discriminator Test (`kw_only=True` Base Class):**
   * In standard Python dataclasses, a subclass cannot define fields with defaults if the parent has non-default fields, unless positional ordering is completely decoupled.
   * All Journal and Status event base classes and derived classes MUST declare **`kw_only=True`** to allow independent default field assignment across the entire event hierarchy.

---

## 5. Pros and Cons of the Selected Option

### Pros
* **Ultra-Fast In-Memory Lookups:** Zero runtime disk parsing or JSON unmarshaling for core lookups; operations run at native Python dictionary speeds ($O(1)$).
* **Guaranteed Determinism:** All fleet packages operate against identical, strongly typed enum and class definitions.
* **Complete Offline Safety:** Companion applications function seamlessly in offline environments (e.g. deep-space exploration without internet).
* **Clean Architectural Separation:** Isolates game universe mechanics from shifting third-party web API changes.

### Cons
* **Requires Upstream Build Pipeline:** When Frontier patches the game with new trade goods or ship hulls, `ed-models` must execute its automated codegen pipeline (Note 0006) to cut a patch release. *(Mitigated by runtime cache overlays in `ed-connector`)*.

---

## 6. Implementation and Migration Strategy

Before creating the standalone `ed-models` repository:
1. **Verification Sandbox (`ed-integration-smoke`):**
   - Gather domain research from `ed-telemetry/architecture/research/` (`ed-journal`, `ed-scout`, `target_files_metadata_spec.md`).
   - Collect and cross-reference model definitions from `EDCD/EDMarketConnector` and community sources.
   - Author a unified verification script in `ed-integration-smoke/scripts/` validating normalization accuracy and domain completeness across all Frontier tokens.
2. **Repository Bootstrap (`ed-models`):**
   - Scaffold repository under `~/src/github.com/mnaatjes/ed-models`.
   - Implement hexagonal structure: `core/`, `catalogs/`, `events/`, and `facade/`.
   - Bind existing fleet tests to verify contract compliance.
