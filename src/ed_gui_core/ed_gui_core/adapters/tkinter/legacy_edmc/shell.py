"""Window and dialog shell primitives for legacy_edmc Tkinter UI."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from ed_gui_core.adapters.tkinter.legacy_edmc.telemetry import KeyValueGrid, StatusBar


class MenuBar(tk.Menu):
    """Declarative menu bar builder."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self._menus: dict[str, tk.Menu] = {}

    def add_submenu(self, label: str) -> tk.Menu:
        menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label=label, menu=menu)
        self._menus[label] = menu
        return menu


class ModalDialog(tk.Toplevel):
    """Transient modal dialog with OK/Cancel footer."""

    def __init__(
        self,
        parent: tk.Misc,
        title: str = "Settings",
        on_ok: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.transient(parent)  # type: ignore[arg-type]
        self.resizable(True, True)
        self._on_ok = on_ok

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.body = ttk.Frame(self, padding=10)
        self.body.grid(row=0, column=0, sticky=tk.NSEW)

        self.buttonframe = ttk.Frame(self, padding=(10, 0, 10, 10))
        self.buttonframe.grid(row=1, column=0, sticky=tk.EW)
        self.buttonframe.columnconfigure(0, weight=1)

        ttk.Button(
            self.buttonframe,
            text="OK",
            command=self._handle_ok,
        ).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(self.buttonframe, text="Cancel", command=self.destroy).grid(row=0, column=2)

    def _handle_ok(self) -> None:
        if self._on_ok is not None:
            self._on_ok()
        self.destroy()


class AppShell:
    """Main application window shell implementing WindowShellPort."""

    def __init__(self, master: tk.Tk | None = None, title: str = "EDMarketConnector") -> None:
        self.root = master or tk.Tk()
        self.root.title(title)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        self.frame.columnconfigure(0, weight=1)

        self.telemetry_grid = KeyValueGrid(self.frame)
        self.telemetry_grid.grid(row=0, column=0, sticky=tk.NSEW)

        self.plugin_slot = tk.Frame(self.frame)
        self.plugin_slot.grid(row=1, column=0, sticky=tk.NSEW)

        self.status_bar = StatusBar(self.frame)
        self.status_bar.grid(row=2, column=0, sticky=tk.EW, pady=(4, 0))

        self.menubar = MenuBar(self.root)
        self.root.configure(menu=self.menubar)

    def set_title(self, title: str) -> None:
        self.root.title(title)

    def set_status(self, text: str) -> None:
        self.status_bar.set_status(text)

    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        self.root.destroy()
