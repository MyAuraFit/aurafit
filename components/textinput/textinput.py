__all__ = ("CustomTextInput",)

from pathlib import Path

# from emoji import is_emoji
from kivy.clock import triggered
from kivy.lang import Builder
from kivy.properties import (
    VariableListProperty,
    ColorProperty,
    BooleanProperty,
    OptionProperty,
    NumericProperty,
)
from kivy.uix.textinput import TextInput

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class CustomTextInput(TextInput):
    radius = VariableListProperty(0)
    bg_color = ColorProperty(None)
    keyboard_suggestions = BooleanProperty(True)
    shadow_color = ColorProperty([0, 0, 0, 0])
    line_color = ColorProperty([0, 0, 0, 0])
    line_width = NumericProperty(1)
    input_type = OptionProperty(
        "null",
        options=("null", "text", "number", "url", "mail", "datetime", "tel", "address"),
    )

    __events__ = ("on_keyboard_show", "on_keyboard_hide")

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos) and self.focus:
            self.focus = False
        return super().on_touch_up(touch)

    @triggered(0.3)
    def _bind_keyboard(self):
        super()._bind_keyboard()
        self.dispatch("on_keyboard_show")

    def _unbind_keyboard(self):
        super()._unbind_keyboard()
        self.dispatch("on_keyboard_hide")

    # def insert_text(self, substring, from_undo=False):
    #     if is_emoji(substring):
    #         if platform == "android":
    #             from kvdroid.tools import toast
    #
    #             toast("emojis are not supported")
    #         return None
    #     else:
    #         return super().insert_text(substring, from_undo=from_undo)

    def on_keyboard_show(self):
        pass

    def on_keyboard_hide(self):
        pass
