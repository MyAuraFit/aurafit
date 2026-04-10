__all__ = ("CustomBoxLayout", "CustomCarousel")

from pathlib import Path

from kivy.lang import Builder
from kivy.properties import (
    VariableListProperty,
    ColorProperty,
    NumericProperty,
    BooleanProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel

from components.behaviors import AdaptiveBehavior

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class CustomBoxLayout(BoxLayout, AdaptiveBehavior):
    bg_color = ColorProperty([0, 0, 0, 0])
    radius = VariableListProperty(0)
    shadow_color = ColorProperty([0, 0, 0, 0])
    line_color = ColorProperty([0, 0, 0, 0])
    line_width = NumericProperty(1)


class CustomCarousel(Carousel):
    lock_swiping = BooleanProperty(False)

    def on_touch_move(self, touch):
        if self.lock_swiping:
            return None
        return super().on_touch_move(touch)
