"""Unit tests for snapshot table formatting components."""

from __future__ import annotations

import json

from ed_cli_core.snapshots import (
    SnapshotTarget,
    render_cargo_table,
    render_market_table,
    render_modules_info_table,
    render_ship_locker_tables,
    render_shipyard_table,
    render_snapshot_tables,
)


def test_render_modules_info_table() -> None:
    data = {
        "event": "ModuleInfo",
        "Modules": [
            {
                "Slot": "MainEngines",
                "Item": "int_engine_size4_class2",
                "Power": 4.28,
                "Priority": 0,
            },
            {
                "Slot": "PowerPlant",
                "Item": "int_powerplant_size4_class5",
                "Power": 0.0,
                "Priority": None,
            },
        ],
    }
    table = render_modules_info_table(data)
    assert table.title == "Fitted Ship Modules (ModulesInfo.json)"
    assert len(table.rows) == 2


def test_render_ship_locker_tables() -> None:
    data = {
        "event": "ShipLocker",
        "Items": [{"Name": "gmeds", "Name_Localised": "G-Meds", "Count": 2}],
        "Components": [{"Name": "circuitboard", "Count": 5}],
        "Consumables": [],
        "Data": [],
    }
    tables = render_ship_locker_tables(data)
    assert len(tables) == 4


def test_render_market_table() -> None:
    data = {
        "event": "Market",
        "StationName": "Garay Terminal",
        "StarSystem": "Deciat",
        "MarketID": 123456,
        "Items": [
            {
                "Name_Localised": "Platinum",
                "Category_Localised": "Metals",
                "BuyPrice": 0,
                "SellPrice": 223789,
                "MeanPrice": 55505,
                "Demand": 1828,
                "Stock": 0,
            }
        ],
    }
    table = render_market_table(data)
    assert "Commodity Market: Garay Terminal" in str(table.title)
    assert len(table.rows) == 1


def test_render_shipyard_table() -> None:
    data = {
        "event": "Shipyard",
        "StationName": "V4X-N6J",
        "StarSystem": "Wolf 397",
        "PriceList": [
            {"ShipType": "cobramkv", "ShipType_Localised": "Cobra Mk V", "ShipPrice": 14634527}
        ],
    }
    table = render_shipyard_table(data)
    assert "Shipyard: V4X-N6J" in str(table.title)
    assert len(table.rows) == 1


def test_render_cargo_table() -> None:
    data = {
        "event": "Cargo",
        "Vessel": "Ship",
        "Count": 4,
        "Inventory": [
            {"Name": "gold", "Name_Localised": "Gold", "Count": 4, "Stolen": False}
        ],
    }
    table = render_cargo_table(data)
    assert "Cargo Hold (Ship)" in str(table.title)
    assert len(table.rows) == 1


def test_render_snapshot_tables_dispatch() -> None:
    raw = json.dumps({"Modules": [{"Slot": "MainEngines", "Item": "thrusters"}]})
    tables = render_snapshot_tables(SnapshotTarget.MODULES_INFO, raw)
    assert len(tables) == 1
