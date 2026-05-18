"""TUIDemoSpare — minimal demo plugin for the TUI Dashboard.

Demonstrates two things:

1. **Live phase-column updates.** Toggle Enable/Disable from the
   Plugins tab; the row flips DISABLED ↔ LOADING ↔ READY without
   any periodic refresh tick (the Dashboard subscribes to
   `_core/plugin/state_changed`).

2. **Custom plugin tab via `get_tui_menu()`** (Option 2 from
   `docs/CUSTOM_TABS.md`). When this plugin is enabled, "Open Tab"
   on its row in the Plugins list renders the declarative menu
   defined below — no Textual dependency in this file.

Reference for the full-Textual-widget approach (Option 1): see
`examples/WidgetDemo/`.
"""

from datetime import datetime

from plexus.utils import Plugin
from plexus.decorators import async_log_errors, log_errors


class TUIDemoSpare(Plugin):
    @log_errors
    def on_load(self, *args, **kwargs):
        self.description = (
            "Minimal spare plugin — toggle Enable/Disable to demo "
            "live Phase-column updates, or Open Tab to see the "
            "declarative get_tui_menu() panel."
        )
        self._enable_count = 0
        self._last_action = "(none)"
        self._verbose = False
        self._echo_log = []  # last few echo inputs

    @async_log_errors
    async def on_enable(self):
        self._enable_count += 1
        self._last_action = f"enabled at {datetime.now().strftime('%H:%M:%S')}"

    @async_log_errors
    async def on_disable(self):
        self._last_action = f"disabled at {datetime.now().strftime('%H:%M:%S')}"

    # ── Endpoints wired to menu actions ──────────────────────────────

    @async_log_errors
    async def hello(self):
        """Returns a greeting string."""
        return "Hello from TUIDemoSpare!"

    @async_log_errors
    async def reset_counter(self):
        """Resets the enable counter back to zero."""
        self._enable_count = 0
        self._last_action = f"counter reset at {datetime.now().strftime('%H:%M:%S')}"
        return {"ok": True, "new_count": self._enable_count}

    @async_log_errors
    async def echo(self, input: str = ""):
        """Echoes the typed input back; keeps the last 5 in a log."""
        self._echo_log.append(input)
        if len(self._echo_log) > 5:
            self._echo_log = self._echo_log[-5:]
        self._last_action = f"echo at {datetime.now().strftime('%H:%M:%S')}"
        return {"echoed": input, "history": list(self._echo_log)}

    @async_log_errors
    async def set_verbose(self, state: bool = False):
        """Toggle the verbose flag from the menu's toggle_list section."""
        self._verbose = bool(state)
        self._last_action = (
            f"verbose={self._verbose} at {datetime.now().strftime('%H:%M:%S')}"
        )
        return {"verbose": self._verbose}

    # ── Custom tab (Option 2: declarative menu) ──────────────────────

    def get_tui_menu(self):
        """Return a declarative menu dict for the Dashboard to render.

        Read once when the tab opens. To see updated values, close and
        reopen the tab (the get_tui_module_info() approach in
        examples/WidgetDemo/ is the right pick for live-updating panels).
        """
        return {
            "label": "TUIDemoSpare",
            "sections": [
                {
                    "title": "State",
                    "type": "info",
                    "items": [
                        {"label": "Enable count", "value": str(self._enable_count)},
                        {"label": "Last action", "value": self._last_action},
                        {"label": "Verbose", "value": "on" if self._verbose else "off"},
                    ],
                },
                {
                    "title": "Actions",
                    "type": "actions",
                    "items": [
                        {"label": "Say hello", "action": "hello"},
                        {"label": "Reset counter", "action": "reset_counter"},
                    ],
                },
                {
                    "title": "Echo (type and submit)",
                    "type": "input",
                    "action": "echo",
                },
                {
                    "title": "Flags",
                    "type": "toggle_list",
                    "items": [
                        {
                            "label": "Verbose logging",
                            "action": "set_verbose",
                            "state": self._verbose,
                        },
                    ],
                },
            ],
        }
