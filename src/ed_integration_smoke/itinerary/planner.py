"""Itinerary and tactical mission planner resolving game state against unachieved targets."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from ed_integration_smoke.daemon.storage import TelemetryStorageEngine
from ed_integration_smoke.itinerary.models import ItineraryStep, PlayerContext, WaypointType

# Canonical knowledge base mapping target IDs to actionable in-game steps
TARGET_KNOWLEDGE_BASE: dict[str, dict[str, Any]] = {
    # Phase 1: Carrier Operations (Zero Jump)
    "Repair": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Repair Hull & Modules",
        "instruction": "Open Station Services on Carrier and select Repair All.",
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Station Services -> Repair All",
        "priority": 10,
    },
    "RefuelAll": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Refuel Ship Tanks",
        "instruction": "Open Station Services on Carrier and select Refuel All.",
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Station Services -> Refuel All",
        "priority": 11,
    },
    "BuyAmmo": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Restock Munitions",
        "instruction": "Open Station Services and purchase reloads for weapons or heat sinks.",
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Station Services -> Restock -> Buy Ammo",
        "priority": 12,
    },
    "Restock": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Complete Ship Restock",
        "instruction": "Use Restock All in carrier station services.",
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Station Services -> Restock All",
        "priority": 13,
    },
    "CarrierDepositFuel": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Deposit Tritium to Carrier Depot",
        "instruction": "Access Carrier Management and transfer Tritium from cargo into the depot.",
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Carrier Management -> Tritium Depot -> Deposit",
        "priority": 15,
    },
    "CarrierBankTransfer": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Transfer Credits with Carrier Bank",
        "instruction": (
            "Access Carrier Finances and deposit or withdraw credits from carrier balance."
        ),
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Carrier Management -> Finances -> Transfer Credits",
        "priority": 16,
    },
    "CarrierCrewServices": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Inspect Carrier Crew Services",
        "instruction": "Manage carrier crew tariffs or toggle optional onboard service stations.",
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Carrier Management -> Crew Services",
        "priority": 17,
    },
    "ShipyardSwap": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Swap Active Ship in Carrier Shipyard",
        "instruction": "Access Shipyard on Carrier and switch into another stored vessel.",
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Station Services -> Shipyard -> Stored Ships -> Swap",
        "priority": 18,
    },
    "SetUserShipName": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Rename Ship or Ident",
        "instruction": "Open Livery or Ship Outfitting and modify the ship name/ID tag.",
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Station Services -> Livery / Outfitting -> Ship Name",
        "priority": 19,
    },
    "ModuleBuy": {
        "phase": "1. Fleet Carrier Operations",
        "title": "Purchase Outfitting Module",
        "instruction": (
            "Buy a module or limpet controller from carrier outfitting or a local starport."
        ),
        "waypoint_type": WaypointType.CARRIER,
        "action_hint": "Station Services -> Outfitting -> Buy Module",
        "priority": 20,
    },

    # Phase 2: Local Flight Dynamics (Cockpit toggles in current system)
    "NIGHT_VISION": {
        "phase": "2. Cockpit Flight Dynamics",
        "title": "Toggle Night Vision (In Flight)",
        "instruction": (
            "Activate Night Vision while undocked in space or on surface "
            "(Frontier suppresses NV bitflag while docked)."
        ),
        "waypoint_type": WaypointType.LOCAL_SPACE,
        "action_hint": "Undock -> Default Keybind or Right Panel -> Ship -> Night Vision",
        "priority": 30,
    },
    "LIGHTS_ON": {
        "phase": "2. Cockpit Flight Dynamics",
        "title": "Toggle Ship Exterior Lights",
        "instruction": "Turn on ship floodlights.",
        "waypoint_type": WaypointType.COCKPIT,
        "action_hint": "Default Keybind [L] or Right Cockpit Panel -> Ship -> Lights",
        "priority": 31,
    },
    "SILENT_RUNNING": {
        "phase": "2. Cockpit Flight Dynamics",
        "title": "Engage Silent Running",
        "instruction": "Close heat radiators to engage Silent Running (toggle off shortly after).",
        "waypoint_type": WaypointType.COCKPIT,
        "action_hint": "Default Keybind [Delete] or Right Panel -> Ship -> Silent Running",
        "priority": 32,
    },
    "CARGO_SCOOP_DEPLOYED": {
        "phase": "2. Cockpit Flight Dynamics",
        "title": "Deploy Cargo Scoop",
        "instruction": "Deploy the cargo scoop hatch in space.",
        "waypoint_type": WaypointType.COCKPIT,
        "action_hint": "Default Keybind [Home] or Right Panel -> Ship -> Cargo Scoop",
        "priority": 33,
    },
    "FLIGHT_ASSIST_OFF": {
        "phase": "2. Cockpit Flight Dynamics",
        "title": "Disable Flight Assist (FA Off)",
        "instruction": "Briefly toggle Flight Assist Off.",
        "waypoint_type": WaypointType.COCKPIT,
        "action_hint": "Default Keybind [Z]",
        "priority": 34,
    },
    "HeatSink": {
        "phase": "2. Cockpit Flight Dynamics",
        "title": "Deploy Heat Sink",
        "instruction": "Fire a Heat Sink to purge thermal signature.",
        "waypoint_type": WaypointType.COCKPIT,
        "action_hint": "Default Keybind [V] or Firegroup trigger",
        "priority": 35,
    },
    "SUPERCRUISE": {
        "phase": "2. Cockpit Flight Dynamics",
        "title": "Enter Supercruise",
        "instruction": "Undock from carrier and charge Frame Shift Drive into Supercruise.",
        "waypoint_type": WaypointType.LOCAL_SPACE,
        "action_hint": "Throttle up, align to space, press [J]",
        "priority": 36,
    },

    # Phase 3: Planetary Surface & Odyssey (Planetary body in system)
    "Touchdown": {
        "phase": "3. Planetary Surface Operations",
        "title": "Land Ship on Planetary Surface",
        "instruction": "Approach landable planet in system, complete glide, and touch down.",
        "waypoint_type": WaypointType.PLANETARY_SURFACE,
        "action_hint": "Lower landing gear, throttle zero on level terrain",
        "priority": 50,
    },
    "Liftoff": {
        "phase": "3. Planetary Surface Operations",
        "title": "Liftoff from Planetary Surface",
        "instruction": "Hold vertical thrusters to lift off from planetary surface.",
        "waypoint_type": WaypointType.PLANETARY_SURFACE,
        "action_hint": "Hold [R] / Vertical Thrusters",
        "priority": 51,
    },
    "Disembark": {
        "phase": "3. Planetary Surface Operations",
        "title": "Disembark on Foot (Odyssey)",
        "instruction": "Step out of ship cockpit or SRV onto planetary ground.",
        "waypoint_type": WaypointType.PLANETARY_SURFACE,
        "action_hint": "Lower panel (between legs) -> Disembark on Foot",
        "priority": 52,
    },
    "Embark": {
        "phase": "3. Planetary Surface Operations",
        "title": "Re-embark into Ship or SRV",
        "instruction": "Walk to your vessel's blue boarding circle and board.",
        "waypoint_type": WaypointType.PLANETARY_SURFACE,
        "action_hint": "Interact Prompt [E] in Boarding Circle",
        "priority": 53,
    },
    "LaunchSRV": {
        "phase": "3. Planetary Surface Operations",
        "title": "Deploy Surface Recon Vehicle (SRV)",
        "instruction": "Deploy SRV from planetary hangar while landed.",
        "waypoint_type": WaypointType.PLANETARY_SURFACE,
        "action_hint": "Lower Panel -> SRV -> Deploy",
        "priority": 54,
    },
    "DockSRV": {
        "phase": "3. Planetary Surface Operations",
        "title": "Board and Dock SRV",
        "instruction": "Drive SRV into the ship's bay cargo bay hatch and board.",
        "waypoint_type": WaypointType.PLANETARY_SURFACE,
        "action_hint": "Align in cargo bay yellow box, Lower Panel -> Board Ship",
        "priority": 55,
    },
    "ScanOrganic": {
        "phase": "3. Planetary Surface Operations",
        "title": "Sample Exobiology Organic",
        "instruction": "Use Genetic Sampler tool on foot to sample 3 instances of a flora species.",
        "waypoint_type": WaypointType.PLANETARY_SURFACE,
        "action_hint": "Equip Genetic Sampler [5] -> Right Click Scan",
        "priority": 56,
    },

    # Phase 4: Commerce & Station Services (Nearest Outpost / Starport)
    "MarketBuy": {
        "phase": "4. Commerce & Bubble Transit",
        "title": "Purchase Commodities on Market",
        "instruction": "Dock at a station with a Commodity Market and purchase 1 ton of cargo.",
        "waypoint_type": WaypointType.STATION,
        "action_hint": "Station Services -> Commodities -> Buy",
        "priority": 70,
    },
    "MarketSell": {
        "phase": "4. Commerce & Bubble Transit",
        "title": "Sell Commodities on Market",
        "instruction": "Sell goods from cargo hold to a station market.",
        "waypoint_type": WaypointType.STATION,
        "action_hint": "Station Services -> Commodities -> Sell",
        "priority": 71,
    },
    "PayFines": {
        "phase": "4. Commerce & Bubble Transit",
        "title": "Pay Fines or Legal Fees",
        "instruction": (
            "Visit an Authority Contact or Interstellar Factor to settle outstanding fines."
        ),
        "waypoint_type": WaypointType.STATION,
        "action_hint": "Station Services -> Contacts -> Authority / Interstellar Factor",
        "priority": 72,
    },
    "RedeemVoucher": {
        "phase": "4. Commerce & Bubble Transit",
        "title": "Redeem Combat or Bounty Vouchers",
        "instruction": "Hand in combat bonds or bounty claims at an authority contact.",
        "waypoint_type": WaypointType.STATION,
        "action_hint": "Station Services -> Contacts -> Combat Bond / Bounty Contact",
        "priority": 73,
    },
}


class ItineraryPlanner:
    """Evaluates unachieved targets against player location and generates a mission list."""

    def __init__(self, storage: TelemetryStorageEngine) -> None:
        self.storage = storage

    def resolve_player_context(self) -> PlayerContext:
        """Extract latest player coordinates, active ship, and fleet carrier from SQLite."""
        system = "Unknown System"
        station = ""
        body = ""
        carrier_name = ""
        carrier_callsign = ""
        ship_type = "Ship"
        ship_name = ""
        is_docked = False
        is_landed = False

        with sqlite3.connect(str(self.storage.db_path)) as conn:
            conn.row_factory = sqlite3.Row

            # 1. Location / Status
            row_loc = conn.execute(
                """
                SELECT payload_json FROM raw_journal_events
                WHERE event_name IN ('Location', 'FSDJump', 'Docked', 'SupercruiseEntry')
                ORDER BY id DESC LIMIT 1
                """
            ).fetchone()
            if row_loc:
                try:
                    data = json.loads(row_loc["payload_json"])
                    system = data.get("StarSystem", system)
                    station = data.get("StationName", station)
                    body = data.get("Body", body)
                    is_docked = bool(data.get("Docked", is_docked))
                except json.JSONDecodeError:
                    pass

            # 2. Carrier Stats
            row_carrier = conn.execute(
                """
                SELECT payload_json FROM raw_journal_events
                WHERE event_name = 'CarrierStats'
                ORDER BY id DESC LIMIT 1
                """
            ).fetchone()
            if row_carrier:
                try:
                    data_c = json.loads(row_carrier["payload_json"])
                    carrier_name = data_c.get("Name", carrier_name)
                    carrier_callsign = data_c.get("Callsign", carrier_callsign)
                except json.JSONDecodeError:
                    pass

            # 3. Active Ship Resolution (Loadout or ShipyardSwap)
            row_ship = conn.execute(
                """
                SELECT event_name, payload_json FROM raw_journal_events
                WHERE event_name IN ('Loadout', 'ShipyardSwap', 'ShipyardBuy', 'ShipyardNew')
                ORDER BY id DESC LIMIT 1
                """
            ).fetchone()
            if row_ship:
                try:
                    data_s = json.loads(row_ship["payload_json"])
                    ship_type = (
                        data_s.get("ShipType_Localised")
                        or data_s.get("ShipType")
                        or data_s.get("Ship", ship_type)
                    )
                    ship_name = data_s.get("ShipName", "")
                except json.JSONDecodeError:
                    pass

        # Overlay real-time session state variables (bypasses exemplar sampling caps)
        system = self.storage.get_session_state("active_system", system)
        station = self.storage.get_session_state("active_station", station)
        body = self.storage.get_session_state("active_body", body)
        carrier_name = self.storage.get_session_state("carrier_name", carrier_name)
        carrier_callsign = self.storage.get_session_state("carrier_callsign", carrier_callsign)
        ship_type = self.storage.get_session_state("active_ship_type", ship_type)
        ship_name = self.storage.get_session_state("active_ship_name", ship_name)

        return PlayerContext(
            system=system,
            station=station,
            body=body,
            carrier_name=carrier_name,
            carrier_callsign=carrier_callsign,
            ship_type=ship_type,
            ship_name=ship_name,
            is_docked=is_docked,
            is_landed=is_landed,
        )

    def generate_itinerary(self) -> list[ItineraryStep]:
        """Construct sorted list of prioritized unachieved tasks based on proximity."""
        ctx = self.resolve_player_context()
        unachieved = self.storage.list_unachieved_targets()
        unachieved_ids = {u.target_id: u for u in unachieved}

        steps: list[ItineraryStep] = []

        # Match unachieved targets with knowledge base
        for target_id, meta in TARGET_KNOWLEDGE_BASE.items():
            if target_id in unachieved_ids:
                u_rec = unachieved_ids[target_id]
                waypoint_name = ctx.system
                if meta["waypoint_type"] == WaypointType.CARRIER:
                    waypoint_name = (
                        f"{ctx.carrier_name} ({ctx.carrier_callsign or ctx.station})"
                        if ctx.carrier_name
                        else ctx.station or "Carrier"
                    )
                elif meta["waypoint_type"] == WaypointType.COCKPIT:
                    waypoint_name = f"{ctx.ship_type} Cockpit"
                elif meta["waypoint_type"] == WaypointType.PLANETARY_SURFACE:
                    waypoint_name = f"{ctx.system} (Landable Body)"

                step = ItineraryStep(
                    target_id=target_id,
                    chapter=u_rec.chapter,
                    phase=meta["phase"],
                    title=meta["title"],
                    instruction=meta["instruction"],
                    waypoint_type=meta["waypoint_type"],
                    waypoint_name=waypoint_name,
                    action_hint=meta["action_hint"],
                    priority=meta["priority"],
                )
                steps.append(step)

        # Fallback for remaining generic unachieved targets not in curated catalog
        for target_id, u_rec in unachieved_ids.items():
            if target_id not in TARGET_KNOWLEDGE_BASE:
                step = ItineraryStep(
                    target_id=target_id,
                    chapter=u_rec.chapter,
                    phase="5. Advanced Fleet Objectives",
                    title=f"Execute {target_id}",
                    instruction=u_rec.description or f"Trigger game event '{target_id}'",
                    waypoint_type=WaypointType.STAR_SYSTEM,
                    waypoint_name=ctx.system,
                    action_hint=f"Trigger journal event: {target_id}",
                    priority=200,
                )
                steps.append(step)

        # Sort primarily by priority, then by target_id
        steps.sort(key=lambda s: (s.priority, s.target_id))
        return steps
