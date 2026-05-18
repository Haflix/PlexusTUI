"""CSS constants for the WidgetDemo tab.

Lives in a sibling module so the relative-import story in __init__.py
(`from .main_widget import WidgetDemoPanel`) and main_widget.py
(`from .css import WIDGET_DEMO_CSS`) is demonstrated end-to-end.
"""

WIDGET_DEMO_CSS = """
WidgetDemoPanel {
    layout: vertical;
    height: 1fr;
    padding: 1 2;
}

WidgetDemoPanel > #counter-row {
    layout: horizontal;
    height: 3;
    margin-bottom: 1;
}

WidgetDemoPanel > #counter-row > #counter-value {
    width: 1fr;
    content-align: left middle;
    text-style: bold;
}

WidgetDemoPanel > #counter-row > #tick-button {
    width: auto;
}

WidgetDemoPanel > #log-table {
    height: 1fr;
}
"""
