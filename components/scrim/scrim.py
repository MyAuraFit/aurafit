__all__ = ("DialogScrim",)

from kivy.properties import ColorProperty, VariableListProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.lang import Builder
from os.path import join, dirname, basename

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class DialogScrim(ButtonBehavior, Widget):
    color = ColorProperty([0, 0, 0, 0.5])
    radius = VariableListProperty(0)
    disable_touch_behind = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.disable_touch_behind:
            return False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.disable_touch_behind:
            return False
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.disable_touch_behind:
            return False
        return super().on_touch_up(touch)
