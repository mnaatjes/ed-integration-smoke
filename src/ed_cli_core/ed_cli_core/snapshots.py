"""Rich table renderers for Frontier Developments snapshot files."""

from __future__ import annotations

import json
from collections.abc import Sequence
from enum import StrEnum
from typing import Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table


class SnapshotTarget(StrEnum):
    """Supported Frontier snapshot file targets."""

    MODULES_INFO = "ModulesInfo"
    SHIP_LOCKER = "ShipLocker"
    CARGO = "Cargo"
    MARKET = "Market"
    SHIPYARD = "Shipyard"
    OUTFITTING = "Outfitting"
    BACKPACK = "Backpack"
    NAV_ROUTE = "NavRoute"
    ALL = "all"


def _format_cell(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, bool):
        return "Yes" if val else "No"
    if isinstance(val, float):
        return f"{val:.2f}"
    if isinstance(val, int):
        return f"{val:,}"
    return str(val)


def render_modules_info_table(payload: dict[str, Any]) -> Table:
    """Render fitted ship modules and power distribution."""
    modules = payload.get("Modules", [])
    table = Table(
        title="Fitted Ship Modules (ModulesInfo.json)",
        border_style="cyan",
        header_style="bold cyan",
        show_lines=False,
    )
    table.add_column("Slot", style="bold white", no_wrap=True)
    table.add_column("Item", style="bright_white")
    table.add_column("Power (MW)", justify="right", style="yellow")
    table.add_column("Priority", justify="center", style="magenta")

    for mod in modules:
        slot = mod.get("Slot", "")
        item = mod.get("Item", "")
        power = mod.get("Power", 0.0)
        pri = mod.get("Priority", "-")
        pwr_str = f"{power:.2f}" if power is not None else "0.00"
        pri_str = str(pri) if pri is not None else "-"
        table.add_row(slot, item, pwr_str, pri_str)

    if not modules:
        table.add_row("No modules recorded", "", "", "")
    return table


def render_ship_locker_tables(payload: dict[str, Any]) -> list[Table]:
    """Render Odyssey on-foot inventory categories (Items, Components, Consumables, Data)."""
    categories = [
        ("Components", "Components (Crafting)", "green"),
        ("Consumables", "Consumables (Meds / Cells / E-Breaches)", "magenta"),
        ("Data", "Data Downloads", "cyan"),
        ("Items", "Items / Barter Goods", "yellow"),
    ]
    tables: list[Table] = []

    for key, title, style in categories:
        items = payload.get(key, [])
        table = Table(
            title=f"Ship Locker: {title}",
            border_style=style,
            header_style=f"bold {style}",
            show_lines=False,
        )
        table.add_column("Name", style="bold white")
        table.add_column("Internal Name", style="dim white")
        table.add_column("Count", justify="right", style="bold yellow")

        for item in sorted(items, key=lambda x: str(x.get("Name_Localised") or x.get("Name", ""))):
            name_loc = item.get("Name_Localised") or item.get("Name", "")
            raw_name = item.get("Name", "")
            count = item.get("Count", 0)
            table.add_row(name_loc, raw_name, _format_cell(count))

        if not items:
            table.add_row("Empty", "", "0")
        tables.append(table)

    return tables


def render_market_table(payload: dict[str, Any], limit: int = 50) -> Table:
    """Render station commodity market pricing."""
    station = payload.get("StationName", "Unknown Station")
    system = payload.get("StarSystem", "Unknown System")
    market_id = payload.get("MarketID", "")
    items = payload.get("Items", [])

    title_str = (
        f"Commodity Market: {station} ({system}) [ID: {market_id}] - {len(items)} Commodities"
    )
    table = Table(
        title=title_str,
        border_style="green",
        header_style="bold green",
        show_lines=False,
    )
    table.add_column("Commodity", style="bold white")
    table.add_column("Category", style="dim white")
    table.add_column("Buy Price", justify="right", style="cyan")
    table.add_column("Sell Price", justify="right", style="yellow")
    table.add_column("Mean Price", justify="right", style="dim")
    table.add_column("Demand", justify="right", style="white")
    table.add_column("Stock", justify="right", style="white")

    for item in items[:limit]:
        name = item.get("Name_Localised") or item.get("Name", "")
        cat = item.get("Category_Localised") or item.get("Category", "")
        buy = _format_cell(item.get("BuyPrice", 0))
        sell = _format_cell(item.get("SellPrice", 0))
        mean = _format_cell(item.get("MeanPrice", 0))
        demand = _format_cell(item.get("Demand", 0))
        stock = _format_cell(item.get("Stock", 0))
        table.add_row(name, cat, buy, sell, mean, demand, stock)

    if not items:
        table.add_row("Market Empty / Not Available", "", "", "", "", "", "")
    return table


def render_shipyard_table(payload: dict[str, Any]) -> Table:
    """Render shipyard ships catalog and pricing."""
    station = payload.get("StationName", "Unknown Station")
    system = payload.get("StarSystem", "Unknown System")
    price_list = payload.get("PriceList", [])

    table = Table(
        title=f"Shipyard: {station} ({system}) - {len(price_list)} Ships for Sale",
        border_style="bright_blue",
        header_style="bold bright_blue",
        show_lines=False,
    )
    table.add_column("Ship Model", style="bold white")
    table.add_column("Type ID", style="dim white")
    table.add_column("Base Price (CR)", justify="right", style="bold yellow")

    for ship in sorted(price_list, key=lambda s: int(s.get("ShipPrice", 0)), reverse=True):
        name = ship.get("ShipType_Localised") or ship.get("ShipType", "")
        type_id = ship.get("ShipType", "")
        price = _format_cell(ship.get("ShipPrice", 0))
        table.add_row(name, type_id, price)

    if not price_list:
        table.add_row("Shipyard Empty / No Ships Listed", "", "")
    return table


def render_cargo_table(payload: dict[str, Any]) -> Table:
    """Render vessel cargo hold inventory."""
    vessel = payload.get("Vessel", "Ship")
    count = payload.get("Count", 0)
    inventory = payload.get("Inventory", [])

    table = Table(
        title=f"Cargo Hold ({vessel}): {count} Units Loaded",
        border_style="yellow",
        header_style="bold yellow",
        show_lines=False,
    )
    table.add_column("Commodity", style="bold white")
    table.add_column("Internal Name", style="dim white")
    table.add_column("Count", justify="right", style="bold yellow")
    table.add_column("Stolen", justify="center", style="red")

    for item in inventory:
        name = item.get("Name_Localised") or item.get("Name", "")
        raw = item.get("Name", "")
        c = _format_cell(item.get("Count", 0))
        stolen = _format_cell(item.get("Stolen", False))
        table.add_row(name, raw, c, stolen)

    if not inventory:
        table.add_row("Cargo Hold Empty", "", "0", "No")
    return table


def render_generic_table(target_name: str, payload: dict[str, Any]) -> RenderableType:
    """Fallback renderer for any list or dict snapshot payload."""
    tables: list[Table] = []

    for k, v in payload.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            cols = list(v[0].keys())
            t = Table(title=f"{target_name}: {k}", border_style="blue", show_lines=False)
            for col in cols[:6]:
                t.add_column(str(col), style="white")
            for row in v[:50]:
                t.add_row(*[_format_cell(row.get(c)) for c in cols[:6]])
            tables.append(t)

    if tables:
        return tables[0] if len(tables) == 1 else Panel.fit(
            "\n".join(str(t) for t in tables), title=target_name
        )

    # Simple key-value fallback
    table = Table(title=target_name, border_style="cyan", show_lines=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    for k, v in payload.items():
        if isinstance(v, (dict, list)):
            table.add_row(k, json.dumps(v, default=str))
        else:
            table.add_row(k, str(v))
    return table


def render_snapshot_tables(target: str, raw_payload: str) -> Sequence[RenderableType]:
    """Parse raw JSON string from a snapshot and return appropriate Rich renderables."""
    try:
        payload = json.loads(raw_payload)
    except Exception as exc:
        table = Table(title=f"Error parsing {target}", border_style="red")
        table.add_column("Error", style="bold red")
        table.add_row(str(exc))
        return [table]

    norm = target.removesuffix(".json")
    if norm.lower() == "modulesinfo":
        return [render_modules_info_table(payload)]
    if norm.lower() == "shiplocker":
        return render_ship_locker_tables(payload)
    if norm.lower() == "market":
        return [render_market_table(payload)]
    if norm.lower() == "shipyard":
        return [render_shipyard_table(payload)]
    if norm.lower() == "cargo":
        return [render_cargo_table(payload)]

    return [render_generic_table(target, payload)]
