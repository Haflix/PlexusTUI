"""PlexusTUI plugin entry point.

Plexus loads this file via importlib.util.spec_from_file_location from
the `path:` declared in the host's config.yml. The loader does NOT add
the plugin's containing directory to sys.path, so the `from plexus_tui
import ...` line below would fail without explicit sys.path injection.

Adding `_PLUGIN_DIR` to sys.path before the package import lets the
plexus_tui package be discovered, after which we re-export the TUI
plugin class so the framework's plugin-class discovery finds it.
"""

import sys
from pathlib import Path

_PLUGIN_DIR = str(Path(__file__).resolve().parent)
if _PLUGIN_DIR not in sys.path:
    sys.path.insert(0, _PLUGIN_DIR)

from plexus_tui.plugin import TUI

__all__ = ["TUI"]
