__all__ = ("AccountScreen",)

from pathlib import Path

from kivy.lang import Builder

from features.basescreen import BaseScreen

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class AccountScreen(BaseScreen):
    pass
