__all__ = ("CustomBoxLayout", "CustomCarousel")

from kivy.properties import (
    VariableListProperty,
    ColorProperty,
    NumericProperty,
    BooleanProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel

from components.behaviors import AdaptiveBehavior
from kivy.lang import Builder
from os.path import join, dirname, basename

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class CustomBoxLayout(BoxLayout, AdaptiveBehavior):
    bg_color = ColorProperty([0, 0, 0, 0])
    radius = VariableListProperty(0)
    shadow_color = ColorProperty([0, 0, 0, 0])
    line_color = ColorProperty([0, 0, 0, 0])
    line_width = NumericProperty("1dp")


class CustomCarousel(Carousel):
    lock_swiping = BooleanProperty(False)

    def on_touch_move(self, touch):
        if self.lock_swiping:
            return None
        return super().on_touch_move(touch)
