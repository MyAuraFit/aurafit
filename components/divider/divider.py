__all__ = ("Divider",)

from pathlib import Path

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class Divider(BoxLayout):
    """
    A divider line.

    .. versionadded:: 2.0.0

    For more information, see in the
    :class:`~kivy.uix.boxlayout.BoxLayout` class documentation.
    """

    color = ColorProperty(None)
    """
    Divider color in (r, g, b, a) or string format.

    :attr:`color` is a :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    divider_width = NumericProperty("1dp")
    """
    Divider width.

    :attr:`divider_width` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `dp(1)`.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.on_orientation)

    def on_orientation(self, *args) -> None:
        """Fired when the values of :attr:`orientation` change."""

        if self.orientation == "vertical":
            self.size_hint_x = None
            self.width = self.divider_width
        elif self.orientation == "horizontal":
            self.size_hint_y = None
            self.height = self.divider_width
