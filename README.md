# PlexusTUI

Terminal UI dashboard plugin for the [Plexus](https://pypi.org/project/plexus-core/)
plugin framework. Built on [Textual](https://textual.textualize.io/).

PlexusTUI gives a live, in-terminal view of a running Plexus instance —
plugin state machine, networking peers, request/response throughput,
log stream, and topic subscriptions. Plugins can register their own
TUI panels by implementing `get_tui_module_info()` or `get_tui_menu()`
on the Plugin base class.

## Install

Requires Python 3.11+.

> ⚠ **WIP — not yet on PyPI.** `pip install plexus-tui` is the planned install once `plexus-core` itself ships to PyPI. Until then, install both from source.

Install `plexus-core` first (from a sibling checkout of the framework repo), then install this plugin editable:

```bash
# 1. Get the framework (the PyPI distribution name will be `plexus-core`)
git clone https://github.com/Haflix/AIO_Assistant_Core.git
pip install -e ./AIO_Assistant_Core

# 2. Install this plugin
pip install -e .
```

If you only need the runtime (no editable checkout of the framework), watch the framework repo's Releases. Tracking the unstable framework via an editable install is the usual development setup.

## Register as a Plexus plugin

Add an entry to your host's `config.yml`:

```yaml
plugins:
  - name: TUI
    enabled: true
    path: /absolute/or/relative/path/to/PlexusTUI
```

Then run your Plexus host (`python main_application.py` or equivalent).
The dashboard takes over the terminal Plexus was launched in.

## Custom plugin tabs

A plugin can contribute a custom panel by implementing one of two
methods on its `Plugin` subclass — see [docs/CUSTOM_TABS.md](docs/CUSTOM_TABS.md)
for the full contract. Two shipped reference implementations:

- [`examples/TUIDemoSpare/`](examples/TUIDemoSpare/) — Option 2,
  `get_tui_menu()`. Declarative dict, no Textual dependency. Doubles
  as the live phase-column update demo (enable / disable to watch
  the row state flip in real time).
- [`examples/WidgetDemo/`](examples/WidgetDemo/) — Option 1,
  `get_tui_module_info()`. Full Textual widget with live-updating
  counter, tick log, and a button calling back into the plugin.

## Layout

```
PlexusTUI/
├── plugin.py               # shim re-exporting plexus_tui.plugin.TUI
├── plugin_config.yml       # Plexus-loadable plugin metadata
├── pyproject.toml          # plexus-tui package metadata
├── plexus_tui/             # the importable Python package
│   ├── __init__.py
│   ├── plugin.py           # TUI plugin class
│   ├── app.py              # DashboardApp (the Textual App)
│   ├── log_handler.py      # logging handler routing to TUI buffer
│   └── request_tracker.py  # request-throughput poller
├── examples/
│   ├── TUIDemoSpare/       # Option 2 demo (get_tui_menu)
│   └── WidgetDemo/         # Option 1 demo (full Textual widget)
├── docs/
│   └── CUSTOM_TABS.md      # custom-tab API contract
├── smoke/                  # interactive smoke harnesses
└── tests/                  # pytest suite for headless dashboard tests
```

## License

MIT — see [LICENSE](LICENSE).
