__all__ = ("IconButton", "CustomButton", "CustomToggleButton")

from pathlib import Path

from kivy.lang import Builder
from kivy.properties import ColorProperty
from kivy.uix.behaviors import (
    TouchRippleButtonBehavior,
    TouchRippleBehavior,
    ToggleButtonBehavior,
)

from components.label import Icon, CustomLabel

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class IconButton(TouchRippleButtonBehavior, Icon):
    pass


class CustomButton(TouchRippleButtonBehavior, CustomLabel):
    background_color = ColorProperty(None)


class CustomToggleButton(ToggleButtonBehavior, TouchRippleBehavior, CustomLabel):
    background_normal = ColorProperty(None)
    background_down = ColorProperty(None)
    shadow_normal = ColorProperty(None)
    shadow_down = ColorProperty(None)
    color_normal = ColorProperty(None)
    color_down = ColorProperty(None)
