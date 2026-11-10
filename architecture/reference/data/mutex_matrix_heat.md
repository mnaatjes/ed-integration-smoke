# Mutual Exclusion (Mutex) Invariants in Elite Dangerous

## 1. Flight Regime Partitions
A vessel occupies strictly one flight regime at any given instant:

```
Regime in { DOCKED, LANDED, SUPERCRUISE, GLIDE_MODE, NORMAL_SPACE }
```

## 2. Cockpit Hardware Interlocks

| Primary Flag | Mutually Excluded Flags | Physical / Avionics Rationale |
| :--- | :--- | :--- |
| `SUPERCRUISE` | `HARDPOINTS_DEPLOYED`, `LANDING_GEAR_DOWN`, `CARGO_SCOOP_DEPLOYED`, `DOCKED`, `LANDED` | Avionics inhibit deployables and docking clamps in supercruise. |
| `DOCKED` | `SUPERCRUISE`, `HARDPOINTS_DEPLOYED`, `FLIGHT_ASSIST_OFF`, `IN_WING`, `SCOOPING_FUEL` | Station docking clamps mechanically lock vessel power and flight surfaces. |
| `LANDED` | `SUPERCRUISE`, `SCOOPING_FUEL` | Planetary touchdown precludes high-energy orbital maneuvers. |
| `SILENT_RUNNING` | `SHIELDS_UP` | Silent running closes radiators and immediately collapses shields. |
| `ON_FOOT` | `IN_SRV`, `SUPERCRUISE`, `HARDPOINTS_DEPLOYED`, `LANDING_GEAR_DOWN`, `CARGO_SCOOP_DEPLOYED` | Odyssey on-foot agency is isolated from cockpit flight controls. |

## 3. Transactional Event Inversion Pairs

| Open Event | Close Event | Domain | Inversion Semantic |
| :--- | :--- | :---: | :--- |
| `Docked` | `Undocked` | `station` | `Undocked` strictly invalidates state from `Docked` |
| `SupercruiseEntry` | `SupercruiseExit` | `travel` | `SupercruiseExit` strictly invalidates state from `SupercruiseEntry` |
| `Touchdown` | `Liftoff` | `travel` | `Liftoff` strictly invalidates state from `Touchdown` |
| `Disembark` | `Embark` | `odyssey` | `Embark` strictly invalidates state from `Disembark` |
| `Interdicted` | `EscapeInterdiction` | `combat` | `EscapeInterdiction` strictly invalidates state from `Interdicted` |
| `ApproachBody` | `LeaveBody` | `exploration` | `LeaveBody` strictly invalidates state from `ApproachBody` |
