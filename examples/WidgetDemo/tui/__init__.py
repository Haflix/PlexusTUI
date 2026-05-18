"""Custom tab package for WidgetDemo.

The Dashboard registers this directory as `_tui_WidgetDemo` in
sys.modules before importing, which makes the relative
`from .main_widget import WidgetDemoPanel` line below resolve. The
widget class is re-exported at the package root so
`WidgetClass = getattr(module, class_name)` finds it.
"""

from .main_widget import WidgetDemoPanel

__all__ = ["WidgetDemoPanel"]
