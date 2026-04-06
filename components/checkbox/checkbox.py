__all__ = ("CustomCheckBox",)

from kivy.properties import StringProperty, AliasProperty
from kivy.uix.behaviors import TouchRippleBehavior

from components.behaviors.togglebutton import CustomToggleButtonBehavior
from components.label import Icon
from kivy.lang import Builder
from os.path import join, dirname, basename

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class CustomCheckBox(CustomToggleButtonBehavior, TouchRippleBehavior, Icon):
    checkbox_icon_normal = StringProperty("checkbox-blank-outline")
    checkbox_icon_down = StringProperty("checkbox-marked")
