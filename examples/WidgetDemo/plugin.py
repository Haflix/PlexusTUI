"""WidgetDemo — full-Textual-widget tab demo.

Plugin side of the Option 1 example from docs/CUSTOM_TABS.md. The
widget lives in `tui/`; this file just declares the plugin and the
endpoints the widget calls.

The widget runs on the Dashboard's Textual loop (a separate thread
from Plexus's main loop), so all cross-loop state is protected here
by a single `threading.Lock`. The widget reads state via `get_state`
and triggers mutations via `tick` — both routed through the
Dashboard's `_run_on_main` so the coroutines execute on the right
loop.
"""

import os
import threading
from collections import deque
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
        # All cross-loop state mutations + reads take this lock. The
        # plugin runs its coroutines on the main Plexus loop; the
        # widget calls get_state() / tick() from the Dashboard's
        # Textual loop via _run_on_main. Both sides acquire the lock
        # for the brief windows they touch _tick_count / _tick_log.
        self._lock = threading.Lock()
        self._tick_count = 0
        # Bounded deque — append + popleft are GIL-atomic, and the
        # maxlen=20 cap is enforced by deque itself (no slice rebuild).
        self._tick_log: "deque[tuple[str, str]]" = deque(maxlen=20)

    @async_log_errors
    async def on_enable(self):
        pass

    @async_log_errors
    async def on_disable(self):
        pass

    # ── Endpoints called by the widget ───────────────────────────────

    @async_log_errors
    async def tick(self, source: str = "manual"):
        """Bump the counter and log who triggered it.

        Called from the widget's auto-tick timer (`source="auto"`) and
        its button (`source="manual"`). Runs on the main Plexus loop —
        the widget dispatches via `self.app._run_on_main(...)`.
        """
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with self._lock:
            self._tick_count += 1
            self._tick_log.append((ts, source))
            count = self._tick_count
            log_len = len(self._tick_log)
        return {"count": count, "log_len": log_len}

    @async_log_errors
    async def get_state(self):
        """Return a snapshot of current state for the widget to render.

        Routes through Plexus the same way `tick` does, so the read
        happens on the main loop under the lock — no torn reads even
        if the widget polls while a tick is in flight.
        """
        with self._lock:
            return {
                "count": self._tick_count,
                "log": list(self._tick_log),
            }

    @async_log_errors
    async def reset(self):
        """Zero the counter and clear the log."""
        with self._lock:
            self._tick_count = 0
            self._tick_log.clear()
        return {"ok": True}

    # ── Custom tab (Option 1: full Textual widget) ───────────────────

    def get_tui_module_info(self):
        """Return path + class_name so the Dashboard can import the
        widget package and instantiate the named class."""
        return {
            "path": os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "tui",
            ),
            "class_name": "WidgetDemoPanel",
        }
