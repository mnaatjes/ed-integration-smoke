"""Tabbed settings and ttk form controls for legacy_edmc Tkinter UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ScrollableNotebook(ttk.Notebook):
    """Notebook container for settings and plugin preference tabs."""

    def __init__(self, master: tk.Misc, **kwargs: object) -> None:
        super().__init__(master, **kwargs)  # type: ignore[arg-type]


class SettingsTab(ttk.Frame):
    """Standardized padded container for preference panes."""

    PADX = 10
    PADY = 2

    def __init__(self, master: tk.Misc, **kwargs: object) -> None:
        super().__init__(master, padding=(self.PADX, self.PADY), **kwargs)  # type: ignore[arg-type]


class ThemedLabel(ttk.Label):
    """Theme-aware ttk.Label wrapper."""


class ThemedButton(ttk.Button):
    """Theme-aware ttk.Button wrapper."""


class ThemedCheckbutton(ttk.Checkbutton):
    """Theme-aware ttk.Checkbutton wrapper."""


class ThemedRadiobutton(ttk.Radiobutton):
    """Theme-aware ttk.Radiobutton wrapper."""


class ThemedOptionMenu(ttk.OptionMenu):
    """Theme-aware ttk.OptionMenu wrapper."""


class EntryWithContextMenu(ttk.Entry):
    """ttk.Entry with right-click Cut/Copy/Paste context menu."""

    def __init__(self, master: tk.Misc, **kwargs: object) -> None:
        super().__init__(master, **kwargs)  # type: ignore[arg-type]
        self._menu = tk.Menu(self, tearoff=0)
        self._menu.add_command(label="Cut", command=lambda: self.event_generate("<<Cut>>"))
        self._menu.add_command(label="Copy", command=lambda: self.event_generate("<<Copy>>"))
        self._menu.add_command(label="Paste", command=lambda: self.event_generate("<<Paste>>"))
        self.bind("<Button-3>", self._show_menu)

    def _show_menu(self, event: tk.Event[tk.Misc]) -> None:
        self._menu.tk_popup(event.x_root, event.y_root)
