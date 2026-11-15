"""Telemetry display widgets for legacy_edmc Tkinter UI."""

from __future__ import annotations

import tkinter as tk
import webbrowser

from ed_gui_core.domain.models import TelemetryRow


class HyperlinkLabel(tk.Label):
    """Clickable URL label with right-click copy support."""

    def __init__(
        self,
        master: tk.Misc,
        text: str = "",
        url: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, text=text, cursor="hand2" if url else "", **kwargs)  # type: ignore[arg-type]
        self._url = url
        self.bind("<Button-1>", self._open_url)
        self.bind("<Button-3>", self._copy_url)

    def set_url(self, url: str | None) -> None:
        self._url = url
        self.configure(cursor="hand2" if url else "")

    def _open_url(self, _event: tk.Event[tk.Misc]) -> None:
        if self._url:
            webbrowser.open(self._url)

    def _copy_url(self, _event: tk.Event[tk.Misc]) -> None:
        if self._url:
            self.clipboard_clear()
            self.clipboard_append(self._url)


class KeyValueGrid(tk.Frame):
    """Two-column responsive grid for telemetry key-value pairs."""

    def __init__(self, master: tk.Misc, **kwargs: object) -> None:
        super().__init__(master, **kwargs)  # type: ignore[arg-type]
        self.columnconfigure(1, weight=1)
        self._rows: dict[str, tuple[tk.Label, tk.Label, int]] = {}

    def set_row(self, row_data: TelemetryRow) -> None:
        if row_data.key not in self._rows:
            row_idx = len(self._rows)
            lbl = tk.Label(self, text=f"{row_data.label}:", anchor=tk.W)
            val: tk.Label = (
                HyperlinkLabel(self, text=row_data.value, url=row_data.url, anchor=tk.W)
                if row_data.url
                else tk.Label(self, text=row_data.value, anchor=tk.W)
            )
            lbl.grid(row=row_idx, column=0, sticky=tk.W, padx=(0, 6), pady=1)
            val.grid(row=row_idx, column=1, sticky=tk.EW, pady=1)
            self._rows[row_data.key] = (lbl, val, row_idx)
        else:
            lbl, val, _ = self._rows[row_data.key]
            lbl.configure(text=f"{row_data.label}:")
            val.configure(text=row_data.value)
            if isinstance(val, HyperlinkLabel):
                val.set_url(row_data.url)

        self.set_visible(row_data.key, row_data.visible)

    def set_visible(self, key: str, visible: bool) -> None:
        if key not in self._rows:
            return
        lbl, val, _ = self._rows[key]
        if visible:
            lbl.grid()
            val.grid()
        else:
            lbl.grid_remove()
            val.grid_remove()


class StatusBar(tk.Label):
    """Single-line status indicator anchored west."""

    def __init__(self, master: tk.Misc, text: str = "", **kwargs: object) -> None:
        super().__init__(master, text=text, anchor=tk.W, **kwargs)  # type: ignore[arg-type]

    def set_status(self, text: str) -> None:
        self.configure(text=text)
