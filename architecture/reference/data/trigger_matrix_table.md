# Status Bitmask to Journal Event Trigger Matrix

| Journal Event | Flag Set | Flag Name | Bit | Edge | Confidence | Latency |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `Docked` | `Flags` | `DOCKED` | 0 | **RISING** | 100% | 15.4 ms |
| `Undocked` | `Flags` | `DOCKED` | 0 | **FALLING** | 100% | 22.1 ms |
| `Touchdown` | `Flags` | `LANDED` | 1 | **RISING** | 98% | 18.0 ms |
| `Liftoff` | `Flags` | `LANDED` | 1 | **FALLING** | 98% | 20.5 ms |
| `SupercruiseEntry` | `Flags` | `SUPERCRUISE` | 4 | **RISING** | 100% | 45.0 ms |
| `SupercruiseExit` | `Flags` | `SUPERCRUISE` | 4 | **FALLING** | 100% | 42.0 ms |
| `FighterDestroyed` | `Flags` | `SHIELDS_UP` | 3 | **FALLING** | 75% | 80.0 ms |
| `GlideModeExit` | `Flags2` | `GLIDE_MODE` | 12 | **FALLING** | 100% | 12.0 ms |
| `Disembark` | `Flags2` | `ON_FOOT` | 0 | **RISING** | 100% | 30.0 ms |
| `Embark` | `Flags2` | `ON_FOOT` | 0 | **FALLING** | 100% | 35.0 ms |
