__all__ = ("CustomLabel", "Icon", "Badge")

from os.path import join, dirname, basename

from kivy.graphics.opengl import glGetIntegerv, GL_MAX_TEXTURE_SIZE
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    StringProperty,
    VariableListProperty,
    ColorProperty,
    NumericProperty,
    AliasProperty,
    ListProperty,
)
from kivy.uix.label import Label

from components import font_path
from components.behaviors import AdaptiveBehavior

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))

lbl = Label(text="a")  # Dummy label to calculate texture size


class CustomLabel(AdaptiveBehavior, Label):
    bg_color = ColorProperty([0, 0, 0, 0])
    radius = VariableListProperty(0)
    shadow_color = ColorProperty([0, 0, 0, 0])
    line_color = ColorProperty([0, 0, 0, 0])
    line_width = NumericProperty("1dp")
    spread_radius = ListProperty([dp(-4), dp(-4)])

    def get_max_characters(self):
        lbl.font_size = self.font_size
        lbl.font_name = self.font_name
        lbl.texture_update()
        char_width, char_height = lbl.texture.size
        max_texture_size = glGetIntegerv(GL_MAX_TEXTURE_SIZE)[0] // 2
        total_characters = (max_texture_size // char_width) + (
            max_texture_size // char_height
        )
        return total_characters

    max_characters = AliasProperty(
        get_max_characters, None, bind=["font_size", "font_name"], cache=True
    )


class Icon(CustomLabel):
    icon = StringProperty()
    font_name = StringProperty(join(font_path, "materialdesignicons-webfont.ttf"))


class Badge(CustomLabel):
    pass
