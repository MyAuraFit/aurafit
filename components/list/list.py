__all__ = ("ChatList",)

from pathlib import Path

from kivy.lang import Builder
from kivy.properties import StringProperty

from components.layout import CustomBoxLayout

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class ChatList(CustomBoxLayout):
    text = StringProperty()
    side = StringProperty("right")
