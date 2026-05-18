"""Textual widget rendered inside the WidgetDemo tab.

Demonstrates the correct cross-loop call pattern for Option 1 custom
tabs:

* The widget runs on the Dashboard's Textual loop (a separate thread
  from Plexus's main loop).
* Plugin endpoints are coroutines bound to the main Plexus loop.
* Calling them directly with `await self._plugin.tick()` would run
  them on the wrong loop and corrupt any asyncio primitives they
  touch.
* The Dashboard exposes `self.app._run_on_main(coro)` which schedules
  the coroutine on the main loop via `run_coroutine_threadsafe` and
  awaits the result on the Textual loop. Always use that.

Both `_auto_tick` and `_refresh` carry a small in-flight flag so a
slow main loop can't pile up concurrent timer invocations.
"""

from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Static

from .css import WIDGET_DEMO_CSS


class WidgetDemoPanel(Vertical):
    """Live-updating panel: counter + tick log + manual button."""

    DEFAULT_CSS = WIDGET_DEMO_CSS

    def __init__(self, plugin, **kwargs):
        super().__init__(**kwargs)
        self._plugin = plugin
        self._tick_in_flight = False
        self._refresh_in_flight = False

    def compose(self):
        with Horizontal(id="counter-row"):
            yield Static("Ticks: 0", id="counter-value")
            yield Button("Tick now", id="tick-button", variant="primary")
        yield DataTable(id="log-table")

    def on_mount(self) -> None:
        table = self.query_one("#log-table", DataTable)
        table.add_columns("Time", "Source")
        table.zebra_stripes = True
        # 0.5s refresh, 1.0s auto-tick — both reasonable for a demo.
        self.set_interval(0.5, self._refresh)
        self.set_interval(1.0, self._auto_tick)

    async def _auto_tick(self) -> None:
        # Drop the call if the previous one is still in flight. Without
        # this, a slow main loop could queue up concurrent ticks.
        if self._tick_in_flight:
            return
        self._tick_in_flight = True
        try:
            await self.app._run_on_main(self._plugin.tick(source="auto"))
        finally:
            self._tick_in_flight = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "tick-button":
            return
        # Same in-flight guard for the manual path.
        if self._tick_in_flight:
            return
        self._tick_in_flight = True
        try:
            await self.app._run_on_main(self._plugin.tick(source="manual"))
        finally:
            self._tick_in_flight = False

    async def _refresh(self) -> None:
        # Skip if a previous snapshot is still in flight — a busy main
        # loop shouldn't make us stack refresh calls.
        if self._refresh_in_flight:
            return
        self._refresh_in_flight = True
        try:
            snapshot = await self.app._run_on_main(self._plugin.get_state())
        finally:
            self._refresh_in_flight = False
        if snapshot is None:
            return  # main loop closed mid-shutdown

        counter = self.query_one("#counter-value", Static)
        counter.update(f"Ticks: {snapshot['count']}")

        # Always rebuild — the log is capped at 20 entries, so a full
        # rebuild every 500 ms is cheap and avoids the row_count-equals-
        # len trap that would freeze the table once the log saturates.
        table = self.query_one("#log-table", DataTable)
        table.clear()
        for ts, source in snapshot["log"]:
            table.add_row(ts, source)
        if table.row_count > 0:
            table.move_cursor(row=table.row_count - 1)
