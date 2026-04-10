from pathlib import Path

from kivy.lang import Builder
from kivy.properties import (
    NumericProperty,
    ColorProperty,
    BooleanProperty,
    VariableListProperty,
)
from kivy.uix.widget import Widget

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))

__all__ = ("Dot",)


class Dot(Widget):
    index = NumericProperty(0)
    normal_color = ColorProperty(None)
    active_color = ColorProperty(None)
    bg_color = ColorProperty([0, 0, 0, 0])
    active = BooleanProperty(False)
    radius = VariableListProperty("2.5dp")
