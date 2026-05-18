"""Textual widget rendered inside the WidgetDemo tab.

The Dashboard instantiates `WidgetDemoPanel(plugin)` once when the
user opens the tab. The widget reads from `self._plugin` directly
for display (synchronous attribute access, no execute round-trip)
and calls `self._plugin.tick(...)` for state mutations (so the
endpoint runs through the framework's normal dispatch path, with
logging and error wrapping).

The `from .css import …` line below is the relative import that
only works because the Dashboard registered this package in
sys.modules before importing the widget.
"""

import asyncio

from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Static

from .css import WIDGET_DEMO_CSS


class WidgetDemoPanel(Vertical):
    """A small live-updating panel: counter + tick log + manual button."""

    DEFAULT_CSS = WIDGET_DEMO_CSS

    def __init__(self, plugin, **kwargs):
        super().__init__(**kwargs)
        self._plugin = plugin

    def compose(self):
        with Horizontal(id="counter-row"):
            yield Static("Ticks: 0", id="counter-value")
            yield Button("Tick now", id="tick-button", variant="primary")
        yield DataTable(id="log-table")

    def on_mount(self) -> None:
        table = self.query_one("#log-table", DataTable)
        table.add_columns("Time", "Source")
        table.zebra_stripes = True
        # Refresh twice a second — cheap, just reads plugin attrs.
        self.set_interval(0.5, self._refresh)
        # Auto-tick once a second so the panel shows movement even
        # if the user never presses the button.
        self.set_interval(1.0, self._auto_tick)

    async def _auto_tick(self) -> None:
        # Fire-and-forget; tick is async on the plugin side.
        await self._plugin.tick(source="auto")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "tick-button":
            await self._plugin.tick(source="manual")

    def _refresh(self) -> None:
        counter = self.query_one("#counter-value", Static)
        counter.update(f"Ticks: {self._plugin._tick_count}")

        table = self.query_one("#log-table", DataTable)
        # Rebuild with the last 20 entries; the log is small enough
        # that a full rebuild every 500 ms is fine.
        log = list(self._plugin._tick_log)
        if table.row_count != len(log):
            table.clear()
            for ts, source in log:
                table.add_row(ts, source)
            if table.row_count > 0:
                table.move_cursor(row=table.row_count - 1)
