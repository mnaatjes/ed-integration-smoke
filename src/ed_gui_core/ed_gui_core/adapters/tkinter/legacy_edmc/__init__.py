"""Legacy EDMC Tkinter component library."""

from ed_gui_core.adapters.tkinter.legacy_edmc.bridge import (
    PluginSettingsRegistry,
    PluginSlot,
    TkEventBridge,
)
from ed_gui_core.adapters.tkinter.legacy_edmc.settings import (
    EntryWithContextMenu,
    ScrollableNotebook,
    SettingsTab,
    ThemedButton,
    ThemedCheckbutton,
    ThemedLabel,
    ThemedOptionMenu,
    ThemedRadiobutton,
)
from ed_gui_core.adapters.tkinter.legacy_edmc.shell import (
    AppShell,
    MenuBar,
    ModalDialog,
)
from ed_gui_core.adapters.tkinter.legacy_edmc.telemetry import (
    HyperlinkLabel,
    KeyValueGrid,
    StatusBar,
)
from ed_gui_core.adapters.tkinter.legacy_edmc.theme import (
    DEFAULT_THEME_TOKENS,
    AlternateWidgetPair,
    ThemeManager,
)

__all__ = [
    "AlternateWidgetPair",
    "AppShell",
    "DEFAULT_THEME_TOKENS",
    "EntryWithContextMenu",
    "HyperlinkLabel",
    "KeyValueGrid",
    "MenuBar",
    "ModalDialog",
    "PluginSettingsRegistry",
    "PluginSlot",
    "ScrollableNotebook",
    "SettingsTab",
    "StatusBar",
    "ThemeManager",
    "ThemedButton",
    "ThemedCheckbutton",
    "ThemedLabel",
    "ThemedOptionMenu",
    "ThemedRadiobutton",
    "TkEventBridge",
]
