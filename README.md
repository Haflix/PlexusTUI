# PlexusTUI

Terminal UI dashboard plugin for the [Plexus](https://pypi.org/project/plexus-core/)
plugin framework. Built on [Textual](https://textual.textualize.io/).

PlexusTUI gives a live, in-terminal view of a running Plexus instance —
plugin state machine, networking peers, request/response throughput,
log stream, and topic subscriptions. Plugins can register their own
TUI panels by implementing `get_tui_module_info()` or `get_tui_menu()`
on the Plugin base class.

## Install

Requires Python 3.11+. Install from PyPI (pulls `plexus-core` automatically):

```bash
pip install plexus-tui
```

Or editable from this checkout:

```bash
pip install -e .
```

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
for the full contract. The shipped [examples/TUIDemoSpare](examples/TUIDemoSpare/)
plugin is the minimal reference implementation.

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
│   └── TUIDemoSpare/       # demo of a custom tab plugin
├── docs/
│   └── CUSTOM_TABS.md      # custom-tab API contract
├── smoke/                  # interactive smoke harnesses
└── tests/                  # pytest suite for headless dashboard tests
```

## License

MIT — see [LICENSE](LICENSE).
