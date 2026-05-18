# Custom plugin tabs

Plugins can register their own panels that show up as dedicated tabs in the Dashboard. There are two ways to do it, picked by which method your `Plugin` subclass defines.

## Resolution order

When the Dashboard opens a plugin's tab, it checks the plugin in this order:

1. `get_tui_module_info()` — Dashboard imports the named TUI module and instantiates the named widget class.
2. `get_tui_menu()` — Dashboard renders the returned declarative dict.
3. Auto-generated view from the plugin's endpoints (fallback).

Whichever returns a value first wins. Plugins that define a custom view (module-info or menu) automatically get "Custom View" / "Generated View" toggle buttons so users can flip between the custom panel and the endpoint auto-view — no extra code needed. (For Option 2 the menu dict is read once at tab open, so the toggle doesn't make the menu live-update; reopen the tab to refresh. Option 1 widgets manage their own refresh cadence — see the `set_interval` calls in the WidgetDemo example.)

---

## Option 1: `get_tui_module_info()` — full Textual widget

Return a dict naming a TUI package and a widget class. The Dashboard imports the package via `importlib` and instantiates the widget.

The dance is necessary because Plexus loads plugins as standalone modules with no `__package__`, so a normal `from .css import …` inside the plugin's TUI directory wouldn't resolve. The Dashboard sidesteps that by registering your TUI directory in `sys.modules` as `_tui_{PluginName}` before importing, which makes relative imports work.

### Plugin side — `plugin.py`

No Textual import here, just the dict:

```python
class MyPlugin(Plugin):

    def get_tui_module_info(self):
        """Tell the Dashboard which TUI module + class to load."""
        import os
        return {
            "path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "tui"),
            "class_name": "MyPluginWidget",
        }
```

### Required file structure

```
MyPlugin/
  plugin.py
  tui/
    __init__.py           # MUST export the widget class
    main_widget.py        # the Textual widget itself
    css.py                # optional CSS constants
    sections/             # optional sub-widgets
      __init__.py
      ...
```

### `tui/__init__.py`

```python
from .main_widget import MyPluginWidget
__all__ = ["MyPluginWidget"]
```

### `tui/main_widget.py`

Relative imports work here because the Dashboard registered the parent directory as a proper package:

```python
from textual.widgets import Static, DataTable
from textual.containers import Vertical

from .css import MY_CSS

class MyPluginWidget(Vertical):
    DEFAULT_CSS = MY_CSS

    def __init__(self, plugin, **kwargs):
        super().__init__(**kwargs)
        self._plugin = plugin

    def compose(self):
        yield Static("[bold]My Plugin[/bold]", markup=True)
        yield DataTable(id="my-table")

    def on_mount(self):
        table = self.query_one("#my-table", DataTable)
        table.add_columns("Name", "Value")
        self.set_interval(2.0, self._refresh)

    async def _refresh(self):
        # Pull from self._plugin, update the table here
        pass
```

### Load sequence

1. Dashboard calls `plugin.get_tui_module_info()`, gets path + class_name.
2. Dashboard registers `tui/` as package `_tui_{PluginName}` in `sys.modules`.
3. Dashboard executes `__init__.py` — internal relative imports resolve.
4. Dashboard instantiates the widget with `WidgetClass(plugin_instance)`.
5. The module is cleared from `sys.modules` when the tab closes; reopening the tab re-imports from disk. This means edits to your TUI module are picked up on the next reopen without restarting Plexus. (A plugin only has one open tab at a time today — the Dashboard's open-tab path skips if the tab id already exists — so this "cleanup on close + reimport on reopen" pairing is consistent in practice.)

A working example ships at [`examples/WidgetDemo/`](../examples/WidgetDemo/) — `plugin.py` plus a `tui/` package with `__init__.py` / `css.py` / `main_widget.py`. Read it for the smallest end-to-end version.

---

## Option 2: `get_tui_menu()` — declarative dict (no Textual import)

Return a dict that describes the UI. The Dashboard renders it for you. Your plugin doesn't import Textual at all.

```python
class MyPlugin(Plugin):

    def get_tui_menu(self):
        return {
            "label": "My Plugin",
            "sections": [
                {
                    "title": "Status",
                    "type": "info",
                    "items": [
                        {"label": "State", "value": "Running"},
                        {"label": "Count", "value": str(self._count)},
                    ],
                },
                {
                    "title": "Actions",
                    "type": "actions",
                    "items": [
                        {"label": "Reset Counter", "action": "reset"},
                    ],
                },
                {
                    "title": "Send Command",
                    "type": "input",
                    "action": "run_command",
                },
                {
                    "title": "Toggles",
                    "type": "toggle_list",
                    "items": [
                        {"label": "Verbose logging", "action": "toggle_verbose", "state": False},
                    ],
                },
            ],
        }
```

### Section types

| Type | What it renders |
|---|---|
| `info` | Key-value display rows |
| `actions` | Buttons that fire plugin endpoints |
| `input` | Text input + submit button that fires an endpoint with the typed value |
| `toggle_list` | On/off switches that fire endpoints with the new state |

Each `action` string is a plugin endpoint `access_name`. The Dashboard routes the call through Plexus — effectively `tui_plugin.execute(your_plugin_name, action, args, hosts="any")` — not a direct method call on your plugin object. Inputs from the `input` section come through as `{"input": typed_value}`; toggles come through as `{"state": new_bool}`.

A working example ships at [`examples/TUIDemoSpare/`](../examples/TUIDemoSpare/) — its `get_tui_menu()` wires all four section types (`info`, `actions`, `input`, `toggle_list`) to real endpoints.

---

## Opening a tab

Users open a plugin's tab from the Plugins list — select the plugin, click "Open Tab". The new tab appears alongside the built-in tabs and can be closed via its own "Close Tab" button.

## Limitations

- Custom widgets live inside their own tab; they can't reach into other tabs or app-level state.
- A tab is destroyed and recreated each time it's opened — there's no persistent widget state across open/close cycles.
- Menu dicts are read once at tab creation. To update values you have to close and reopen the tab.
- Widget CSS lives inside the widget's `DEFAULT_CSS`; avoid reusing Dashboard CSS class names.
- `get_tui_widget()` (a hypothetical "return a Textual widget instance directly" API) is **not supported** — Plexus's loader leaves `__package__` unset, which breaks relative imports inside the widget's module tree. Use `get_tui_module_info()` instead.
