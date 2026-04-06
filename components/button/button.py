__all__ = ('IconButton', 'CustomButton', 'CustomToggleButton')

from kivy.properties import ColorProperty
from kivy.uix.behaviors import TouchRippleButtonBehavior, TouchRippleBehavior, ToggleButtonBehavior
from kivy.lang import Builder
from os.path import join, dirname, basename
from components.label import Icon, CustomLabel

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


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
