"""ThemeManager and AlternateWidgetPair for legacy_edmc Tkinter UI."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Any

from ed_gui_core.domain.models import ThemeMode, ThemeTokens

DEFAULT_THEME_TOKENS: dict[ThemeMode, ThemeTokens] = {
    ThemeMode.DEFAULT: ThemeTokens(
        mode=ThemeMode.DEFAULT,
        fg="#000000",
        bg="#f0f0f0",
        highlight="#0066cc",
    ),
    ThemeMode.DARK: ThemeTokens(
        mode=ThemeMode.DARK,
        fg="#ff8000",
        bg="#1e1e1e",
        highlight="#ffb000",
    ),
    ThemeMode.TRANSPARENT: ThemeTokens(
        mode=ThemeMode.TRANSPARENT,
        fg="#ff8000",
        bg="#000000",
        highlight="#ffb000",
    ),
}


@dataclass(slots=True)
class AlternateWidgetPair:
    """Pairs a native ttk widget with a themed tk.Label fallback."""

    primary: tk.Widget
    alternate: tk.Widget

    def show_primary(self) -> None:
        self.alternate.grid_remove()
        self.primary.grid()

    def show_alternate(self) -> None:
        self.primary.grid_remove()
        self.alternate.grid()


class ThemeManager:
    """Manages Default, Dark, and Transparent themes for Tkinter widgets."""

    def __init__(self, root: tk.Misc | None = None) -> None:
        self._root = root
        self._mode = ThemeMode.DEFAULT
        self._alternates: list[AlternateWidgetPair] = []

    @property
    def current_mode(self) -> ThemeMode:
        return self._mode

    @property
    def tokens(self) -> ThemeTokens:
        return DEFAULT_THEME_TOKENS[self._mode]

    def register_alternate(self, primary: Any, alternate: Any) -> None:
        self._alternates.append(AlternateWidgetPair(primary=primary, alternate=alternate))

    def apply_theme(self, mode: ThemeMode) -> None:
        self._mode = mode
        tokens = self.tokens
        use_alternate = mode in (ThemeMode.DARK, ThemeMode.TRANSPARENT)
        for pair in self._alternates:
            if use_alternate:
                pair.show_alternate()
            else:
                pair.show_primary()
        if self._root is not None:
            self._apply_recursive(self._root, tokens)

    def _apply_recursive(self, widget: tk.Misc, tokens: ThemeTokens) -> None:
        if isinstance(widget, (tk.Frame, tk.Label, tk.Tk, tk.Toplevel)):
            try:
                widget.configure(bg=tokens.bg)  # type: ignore[call-overload]
            except tk.TclError:
                pass
        if isinstance(widget, tk.Label):
            try:
                widget.configure(fg=tokens.fg)
            except tk.TclError:
                pass
        for child in widget.winfo_children():
            self._apply_recursive(child, tokens)
