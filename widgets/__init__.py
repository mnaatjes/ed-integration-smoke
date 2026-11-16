"""Tailored Elite Dangerous UI composite widgets."""

from __future__ import annotations

from .nav_route import NavigationRouteCard

# Backward compatibility alias
NavigationRouteWidget = NavigationRouteCard

__all__ = [
    "NavigationRouteCard",
    "NavigationRouteWidget",
]
