from .fsd_target import render_fsd_target_table
from .nav_route import NavigationRouteCard

# Backward compatibility alias
NavigationRouteWidget = NavigationRouteCard

__all__ = [
    "NavigationRouteCard",
    "NavigationRouteWidget",
    "render_fsd_target_table",
]
