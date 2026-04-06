from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ColorProperty, BooleanProperty, VariableListProperty
from os.path import join, basename, dirname
from kivy.lang import Builder

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))

__all__ = ("Dot",)


class Dot(Widget):
    index = NumericProperty(0)
    normal_color = ColorProperty(None)
    active_color = ColorProperty(None)
    bg_color = ColorProperty([0, 0, 0, 0])
    active = BooleanProperty(False)
    radius = VariableListProperty("2.5dp")
