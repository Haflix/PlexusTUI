"""WidgetDemo — full-Textual-widget tab demo.

Demonstrates Option 1 from `docs/CUSTOM_TABS.md`: the plugin returns a
`get_tui_module_info()` dict pointing at a sibling `tui/` directory.
The Dashboard imports the package via importlib (registering it in
`sys.modules` as `_tui_WidgetDemo` so internal relative imports
resolve), then instantiates the named widget class.

Open this plugin's tab from the Dashboard's Plugins list. The widget
shows a live-updating counter, a small per-tick log, and a button
that calls back into this plugin's `tick` endpoint via the framework's
execute mechanism.

For the lighter declarative-menu alternative (Option 2), see
`examples/TUIDemoSpare/`.
"""

import os
from datetime import datetime

from plexus.utils import Plugin
from plexus.decorators import async_log_errors, log_errors


class WidgetDemo(Plugin):
    @log_errors
    def on_load(self, *args, **kwargs):
        self.description = (
            "Custom-tab demo — implements get_tui_module_info() so the "
            "Dashboard loads a full Textual widget from this plugin's "
            "tui/ directory."
        )
        self._tick_count = 0
        self._tick_log = []  # list[(timestamp, source)]

    @async_log_errors
    async def on_enable(self):
        pass

    @async_log_errors
    async def on_disable(self):
        pass

    # ── Endpoint the widget pokes ────────────────────────────────────

    @async_log_errors
    async def tick(self, source: str = "manual"):
        """Bump the counter and log who triggered it.

        Called from the widget's auto-tick timer (source="auto") and
        from its button (source="manual"). The widget reads the
        plugin's _tick_count + _tick_log fields directly via the
        plugin reference it gets at construction time.
        """
        self._tick_count += 1
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self._tick_log.append((ts, source))
        if len(self._tick_log) > 20:
            self._tick_log = self._tick_log[-20:]
        return {"count": self._tick_count, "log_len": len(self._tick_log)}

    @async_log_errors
    async def reset(self):
        """Zero the counter and clear the log."""
        self._tick_count = 0
        self._tick_log = []
        return {"ok": True}

    # ── Custom tab (Option 1: full Textual widget) ───────────────────

    def get_tui_module_info(self):
        """Tell the Dashboard which TUI package + class to load.

        The Dashboard registers the returned path as a proper Python
        package in sys.modules (as `_tui_WidgetDemo`) before importing,
        so the widget's own `from .css import ...` style relative
        imports work even though Plexus loads this plugin without
        __package__ set.
        """
        return {
            "path": os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "tui",
            ),
            "class_name": "WidgetDemoPanel",
        }
