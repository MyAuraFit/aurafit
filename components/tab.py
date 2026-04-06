__all__ = ("TabsCarousel", )
from kivy.properties import BooleanProperty
from kivy.uix.carousel import Carousel


class TabsCarousel(Carousel):
    """
    Implements a carousel for user-generated content.

    For more information, see in the
    :class:`~kivy.uix.carousel.Carousel` class documentation.
    """

    lock_swiping = BooleanProperty(False)
    """
    If True - disable switching tabs by swipe.

    :attr:`lock_swiping` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    def on_touch_move(self, touch) -> str | bool | None:
        if self.lock_swiping:  # lock a swiping
            return
        super().on_touch_move(touch)

    def add_widget(self, widget, *args, **kwargs):
        super().add_widget(widget, *args, **kwargs)
        if hasattr(self, "_tabs") and self._tabs:
            index = len(self.slides) - 1
            tabs_items = self._tabs.ids.container.children[::-1]
            if index < len(tabs_items):
                tab_item = tabs_items[index]
                tab_item._tab_content = widget
                widget.tab_item = tab_item