__all__ = ("CustomCheckBox",)

from pathlib import Path

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.behaviors import TouchRippleBehavior

from components.behaviors.togglebutton import CustomToggleButtonBehavior
from components.label import Icon

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class CustomCheckBox(CustomToggleButtonBehavior, TouchRippleBehavior, Icon):
    checkbox_icon_normal = StringProperty("checkbox-blank-outline")
    checkbox_icon_down = StringProperty("checkbox-marked")
