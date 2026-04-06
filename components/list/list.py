__all__ = ("ChatList",)

from kivy.properties import StringProperty, NumericProperty
from components.layout import CustomBoxLayout
from kivy.lang import Builder
from os.path import join, dirname, basename

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class ChatList(CustomBoxLayout):
    text = StringProperty()
    side = StringProperty("right")
